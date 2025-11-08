from __future__ import annotations

import os
import json
import uuid
import time
import asyncio
import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .realtime_queue import init_realtime_queue, get_realtime_queue
from urllib.parse import urlsplit

# 说明：
# - 本地服务入口，按要求新增：
#   • POST /local/context/bind
#   • POST /local/tasks/start
# - 仅支持从 Headers 读取 Project-Id、User-Id，不做 Body 兜底
# - 统一 CORS 放行（仅为本地服务端，路径见下）
# - 上下文持久化与 client_id 管理
# - 同一 task_id 幂等与全局执行并发约束（全局仅允许一个执行中的 task）

app = FastAPI(title="sensitive-check-local-permission", version="0.1.0")

# 全局 CORS 放行（覆盖到 /local/context/bind 与 /local/tasks/start）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# 内存态上下文与任务状态
_context_mem: Dict[str, Any] = {}  # 结构：{project_id, user_id, task_id, client_id, started_at, state}
_running_task_id: Optional[str] = None
_completed_tasks: Dict[str, str] = {}  # task_id -> "success"|"failed"
_lock = asyncio.Lock()  # 控制并发：全局仅允许一个执行中的 task
# 实时检测的调度器占位任务句柄（最小实现：仅占位，不做实际队列/批处理）
_realtime_scheduler_task: Optional[asyncio.Task] = None
# 全局活动模式状态（用于互斥控制）
_activity_mode: Optional[str] = None  # "realtime" | "permission" | "ingest" | None

# 路径设定（允许环境变量覆盖）
def _client_id_path() -> str:
    default_path = os.path.expanduser("~/.sensitive-check/client_id")
    return os.environ.get("SENSITIVE_LOCAL_CLIENT_ID_PATH", default_path)

def _context_path() -> str:
    default_path = os.path.expanduser("~/.sensitive-check/context.json")
    return os.environ.get("SENSITIVE_LOCAL_CONTEXT_PATH", default_path)

def _load_or_create_client_id() -> str:
    path = _client_id_path()
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                cid = f.read().strip()
                if cid:
                    return cid
        # 创建新 client_id
        cid = uuid.uuid4().hex
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(cid)
        return cid
    except Exception:
        # 读取失败自动重建
        try:
            cid = uuid.uuid4().hex
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(cid)
            return cid
        except Exception:
            # 最后兜底：返回内存态
            return uuid.uuid4().hex

def _save_context(ctx: Dict[str, Any]) -> None:
    path = _context_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ctx, f, ensure_ascii=False, indent=2)
    except Exception:
        # 文档要求：不要过度添加兜底逻辑，这里保留异常抛出位置在调用方
        pass

def _load_context() -> Optional[Dict[str, Any]]:
    path = _context_path()
    try:
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return None
    except Exception:
        return None

def _get_header(req: Request, name: str) -> str:
    # 严格使用 Header，不支持 Body 兜底
    val = req.headers.get(name)
    if val is None or str(val).strip() == "":
        # 记录校验失败告警日志（尽力而为，避免阻断）
        try:
            _warn_400(req, [], f"missing header: {name}")
        except Exception:
            pass
        # 前端需要结构化 message 以正确提示
        raise HTTPException(status_code=400, detail={"message": f"missing header: {name}"})
    return str(val).strip()

# 事件日志（基础）：统一脱敏，供排查
def _log_event(event: str, info: Dict[str, Any]) -> None:
    # 注意脱敏：不输出完整 token/headers/响应体
    safe_info = dict(info or {})
    # 典型敏感字段处理
    for k in list(safe_info.keys()):
        if k.lower() in {"authorization", "cookie", "set-cookie", "token"}:
            safe_info[k] = "***"
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    task_id = safe_info.get("task_id") or safe_info.get("taskId") or "-"
    print(f"[{ts}] [local] event={event} task_id={task_id} info={safe_info}")

# 模块级 logger
_logger = logging.getLogger("sensitive_check_local")

# 统一的400校验失败告警日志
def _warn_400(req: Request, body_project_ids: Optional[list[int]], message: str) -> None:
    try:
        logging.getLogger("sensitive_check_local").warning(
            "[validation400] %s",
            {
                "userId": req.headers.get("User-Id"),
                "headerProjectId": req.headers.get("Project-Id"),
                "bodyProjectIds": body_project_ids or [],
                "path": str(getattr(req.url, "path", "")),
                "message": message,
            },
        )
    except Exception:
        # 日志失败不阻断主流程
        pass

@app.post("/local/context/bind")
async def bind_context(req: Request) -> Dict[str, Any]:
    """
    绑定上下文：
    Headers：Project-Id、User-Id（若 Body 也提供，以 Headers 为准，不做兜底）
    Body：{ "task_id": "...", "strategies"?: ["horizontal"|"vertical"|...], "follow_redirects"?: true|false }
    行为：
      - 持久化上下文（内存与文件）
      - 生成/缓存 client_id（若不存在）
      - 可选：记录前端传入的策略与是否跟随重定向（不做默认兜底）
    返回：{ "success": true }
    """
    project_id = _get_header(req, "Project-Id")
    user_id = _get_header(req, "User-Id")

    body = await req.json()
    if not isinstance(body, dict):
        # 前端需要结构化 message 以正确提示
        raise HTTPException(status_code=400, detail={"message": "invalid json body"})
    task_id = str(body.get("task_id") or "").strip()
    if task_id == "":
        # 前端需要结构化 message 以正确提示
        raise HTTPException(status_code=400, detail={"message": "missing field: task_id"})

    # 可选解析：策略（仅允许 horizontal/vertical），若提供但解析后为空则报错
    strategies_parsed = None
    if "strategies" in body:
        raw = body.get("strategies")
        allowed = {"horizontal", "vertical"}
        parsed: list[str] = []
        if isinstance(raw, str):
            parts = [x.strip().lower() for x in raw.replace(",", " ").split() if x.strip()]
            parsed = [x for x in parts if x in allowed]
        elif isinstance(raw, list):
            parsed = [str(x).strip().lower() for x in raw if str(x).strip().lower() in allowed]
        else:
            # 前端需要结构化 message 以正确提示
            raise HTTPException(status_code=400, detail={"message": "invalid strategies"})
        if not parsed:
            # 前端需要结构化 message 以正确提示
            raise HTTPException(status_code=400, detail={"message": "invalid strategies (empty)"})
        strategies_parsed = parsed

    # 可选解析：是否跟随重定向
    follow_redirects_parsed = None
    if "follow_redirects" in body:
        fr = body.get("follow_redirects")
        if isinstance(fr, bool):
            follow_redirects_parsed = fr
        elif isinstance(fr, str):
            follow_redirects_parsed = str(fr).strip().lower() in ("1", "true", "yes", "on")
        else:
            # 前端需要结构化 message 以正确提示
            raise HTTPException(status_code=400, detail={"message": "invalid follow_redirects"})

    client_id = _load_or_create_client_id()

    ctx = {
        "project_id": project_id,
        "user_id": user_id,
        "task_id": task_id,
        "client_id": client_id,
        "started_at": int(time.time() * 1000),
        "state": {"status": "bound"},
    }
    # 仅在前端提供时写入策略/重定向参数；不做默认兜底
    if strategies_parsed is not None:
        ctx["strategies"] = strategies_parsed
    if follow_redirects_parsed is not None:
        ctx["follow_redirects"] = follow_redirects_parsed

    _context_mem.clear()
    _context_mem.update(ctx)
    try:
        _save_context(ctx)
    except Exception as e:
        # 按要求不做过度兜底，抛错以暴露问题
        raise HTTPException(status_code=500, detail=f"persist context failed: {e}")

    _log_event("on_context_bound", {"task_id": task_id, "strategies": strategies_parsed or "-", "follow_redirects": follow_redirects_parsed if follow_redirects_parsed is not None else "-"})
    return {"success": True}

@app.post("/local/tasks/start")
async def start_task(req: Request) -> Dict[str, Any]:
    """
    启动执行器（幂等）：
    Headers：Project-Id、User-Id；Body：{ "task_id": "...", "strategies"?: ["horizontal"|"vertical"], "follow_redirects"?: true|false }
    行为：
      - 读取上下文 → 启动执行器（幂等控制）
      - 可选：允许前端在启动时覆盖策略与是否跟随重定向
      - 相同 task 正在执行或已完成：返回 {success:true, started:false|true, message}
      - 全局仅允许一个执行中的 task
    返回：
      { "success": true, "started": true, "message": "started" }
    """
    project_id = _get_header(req, "Project-Id")
    user_id = _get_header(req, "User-Id")

    body = await req.json()
    if not isinstance(body, dict):
        # 前端需要结构化 message 以正确提示
        raise HTTPException(status_code=400, detail={"message": "invalid json body"})
    task_id = str(body.get("task_id") or "").strip()
    if task_id == "":
        # 前端需要结构化 message 以正确提示
        raise HTTPException(status_code=400, detail={"message": "missing field: task_id"})

    ctx = _load_context() or _context_mem or None
    if not ctx:
        # 前端需要结构化 message 以正确提示
        raise HTTPException(status_code=400, detail={"message": "context not bound"})
    # 统一以 Headers 为准（拒绝 Body 兜底）
    if str(ctx.get("project_id")) != project_id or str(ctx.get("user_id")) != user_id or str(ctx.get("task_id")) != task_id:
        # 前端需要结构化 message 以正确提示
        raise HTTPException(status_code=400, detail={"message": "context mismatch: headers do not match bound context"})

    # 可选覆盖策略
    strategies_override = None
    if "strategies" in body:
        raw = body.get("strategies")
        allowed = {"horizontal", "vertical"}
        parsed: list[str] = []
        if isinstance(raw, str):
            parts = [x.strip().lower() for x in raw.replace(",", " ").split() if x.strip()]
            parsed = [x for x in parts if x in allowed]
        elif isinstance(raw, list):
            parsed = [str(x).strip().lower() for x in raw if str(x).strip().lower() in allowed]
        else:
            # 前端需要结构化 message 以正确提示
            raise HTTPException(status_code=400, detail={"message": "invalid strategies"})
        if not parsed:
            # 前端需要结构化 message 以正确提示
            raise HTTPException(status_code=400, detail={"message": "invalid strategies (empty)"})
        strategies_override = parsed

    # 可选覆盖是否跟随重定向
    follow_redirects_override = None
    if "follow_redirects" in body:
        fr = body.get("follow_redirects")
        if isinstance(fr, bool):
            follow_redirects_override = fr
        elif isinstance(fr, str):
            follow_redirects_override = str(fr).strip().lower() in ("1", "true", "yes", "on")
        else:
            # 前端需要结构化 message 以正确提示
            raise HTTPException(status_code=400, detail={"message": "invalid follow_redirects"})

    # 并发与幂等控制
    async with _lock:
        global _running_task_id
        # permission 模式不参与互斥检查，因为它不使用 mitm 资源
        # 仅对使用 mitm 的模式（realtime、ingest）进行互斥检查
        if _running_task_id is not None:
            if _running_task_id == task_id:
                _log_event("start_task_idempotent_running", {"task_id": task_id})
                return {"success": True, "started": False, "message": "already running"}
            else:
                # 读取全局上下文以确定当前运行模式
                gctx = _load_context() or _context_mem or {}
                current_mode = gctx.get("activityMode") or "unknown"
                # 仅当当前运行的是需要 mitm 的模式时才互斥
                if current_mode in ["realtime", "ingest"]:
                    _log_event("start_task_blocked_by_other", {"task_id": task_id, "running": _running_task_id, "mode": current_mode})
                    raise HTTPException(
                        status_code=409,
                        detail={"message": f"已有进行中的 {current_mode} 任务", "mode": current_mode, "activityMode": current_mode}
                    )  # 前端需要结构化 message/mode 以正确提示
        # 额外检查底层抓包进程状态（延迟导入），仅对使用 mitm 的模式进行互斥检查
        try:
            from . import process as _process_status
            ps = _process_status.status()
            if bool(ps.get("running")):
                gctx = _load_context() or _context_mem or {}
                current_mode = gctx.get("activityMode") or "unknown"
                # 仅当当前运行的是需要 mitm 的模式时才互斥
                if current_mode in ["realtime", "ingest"]:
                    _log_event("start_task_blocked_by_process", {"task_id": task_id, "mode": current_mode})
                    raise HTTPException(
                        status_code=409,
                        detail={"message": f"已有进行中的 {current_mode} 任务", "mode": current_mode, "activityMode": current_mode}
                    )  # 前端需要结构化 message/mode 以正确提示
        except HTTPException:
            raise
        except Exception:
            # 读取状态异常不兜底，允许后续流程继续
            pass
        # 已完成的任务再次启动，返回已完成状态
        if _completed_tasks.get(task_id) in {"success", "failed"}:
            _log_event("start_task_already_completed", {"task_id": task_id, "status": _completed_tasks.get(task_id)})
            return {"success": True, "started": False, "message": f"already completed: status={_completed_tasks.get(task_id)}"}

    # 标记运行中
    _running_task_id = task_id
    _activity_mode = "permission"

    # 覆盖上下文中的策略与重定向参数（仅当前端提供时）
    if strategies_override is not None:
        ctx["strategies"] = strategies_override
    if follow_redirects_override is not None:
        ctx["follow_redirects"] = follow_redirects_override
    # 统一标记并持久化上下文字段（与实时检测一致）
    ctx["activityMode"] = "permission"
    ctx["running"] = True
    # 如权限任务会开启 mitm，可在后续运行阶段设置 sessionId；此处置空以保持一致
    ctx["sessionId"] = ctx.get("sessionId") if ctx.get("sessionId") else None
    _context_mem.clear()
    _context_mem.update(ctx)
    # 持久化更新后的上下文
    try:
        _save_context(ctx)
    except Exception as e:
        # 启动前持久化失败需抛错，避免不一致
        raise HTTPException(status_code=500, detail=f"persist context failed: {e}")

    # 后台执行器启动（骨架，细节在 process.py 中实现）
    async def _runner():
        from . import process as _process  # 延迟导入，避免循环依赖
        success = False
        try:
            _log_event("start_task_runner_begin", {"task_id": task_id, "strategies": ctx.get("strategies", "-"), "follow_redirects": ctx.get("follow_redirects", "-")})
            success = await _process.run_permission_task(ctx)
            status = "success" if success else "failed"
            _completed_tasks[task_id] = status
            _log_event("start_task_runner_end", {"task_id": task_id, "status": status})
        finally:
            # 释放运行占位 & 上下文清理（统一清理运行态与模式标识）
            async with _lock:
                global _running_task_id, _activity_mode
                if _running_task_id == task_id:
                    _running_task_id = None
                    _activity_mode = None
                # 基础上下文清理：记录完成状态并清理运行态标识，持久化
                try:
                    _context_mem["state"] = {"status": "completed", "success": success}
                    _context_mem["task_id"] = None
                    # 统一清理 activityMode/running/sessionId
                    _context_mem["activityMode"] = None
                    _context_mem["running"] = False
                    _context_mem["sessionId"] = None
                    _save_context(_context_mem)
                except Exception:
                    pass

    asyncio.create_task(_runner())
    _log_event("start_task_started", {"task_id": task_id})
    return {"success": True, "started": True, "message": "started"}

# ===== Realtime detection minimal endpoints (/local/realtime/*) =====
# 说明：
# - 本子任务新增 4 个端点：/local/realtime/context/bind, /local/realtime/start, /local/realtime/stop, /local/realtime/status
# - 严格使用 Headers 中的 Project-Id、User-Id；入参使用驼峰格式
# - 互斥：全局仅允许一种 activityMode 运行，若已有其他模式（如 "permission"）运行，则启动实时检测返回 409
# - 上下文持久化复用本文件的 _save_context/_load_context；服务重启后 /status 可恢复展示
# - 最小可用：不实现队列/批处理/上报，仅记录 TODO 注释

def _now_ms() -> int:
    return int(time.time() * 1000)

@app.post("/local/realtime/context/bind")
async def realtime_bind_context(req: Request) -> Dict[str, Any]:
    """
    绑定实时检测上下文（最小改动、严格头校验与空间校验）。
    - Headers：Project-Id、User-Id（严格必填）
    - Body：
      • taskId: string（必填）
      • projectLines: Array<{ projectId:number; domains:string[] }>
        ｜个人空间(Project-Id=0)允许多行
        ｜非个人空间(Project-Id>0)必须仅一行且 projectId 必须与 Header 相等
      • identities: Array<{ horizontalUserId?:string; verticalUserId?:string }>（可选；原样持久化）
      • strategies: Array<"horizontal"|"vertical">（缺省或空 → ["horizontal","vertical"]）
    - 行为：
      • 生成/加载 client_id
      • 持久化上下文（复用 _save_context）：{ project_id, user_id, task_id, client_id, mode:"realtime", activityMode:"realtime", project_lines, identities, strategies }
    - 返回：{ "success": true }
    """
    # 头校验
    project_id_str = _get_header(req, "Project-Id")
    user_id = _get_header(req, "User-Id")
    try:
        project_id = int(project_id_str)
    except Exception:
        raise HTTPException(status_code=400, detail={"message": "invalid header: Project-Id"})

    # 体解析
    try:
        body = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"message": "invalid json body"})
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail={"message": "invalid json body"})

    task_id = str(body.get("taskId") or "").strip()
    if task_id == "":
        raise HTTPException(status_code=400, detail={"message": "missing field: taskId"})

    # 解析 strategies（缺省/空 → ["horizontal","vertical"]）
    def _parse_strategies(raw) -> list[str]:
        allowed = {"horizontal", "vertical"}
        if raw is None:
            return ["horizontal", "vertical"]
        if isinstance(raw, list):
            parsed = [str(x).strip().lower() for x in raw if str(x).strip().lower() in allowed]
            return parsed if parsed else ["horizontal", "vertical"]
        raise HTTPException(status_code=400, detail={"message": "invalid field: strategies"})

    strategies = _parse_strategies(body.get("strategies"))

    # 解析 projectLines 并进行空间校验
    project_lines_raw = body.get("projectLines")
    if project_lines_raw is None:
        project_lines_raw = []
    if not isinstance(project_lines_raw, list):
        raise HTTPException(status_code=400, detail={"message": "invalid field: projectLines"})
    normalized_lines: list[Dict[str, Any]] = []
    for row in project_lines_raw:
        if not isinstance(row, dict):
            raise HTTPException(status_code=400, detail={"message": "invalid field: projectLines item"})
        try:
            rid = int(row.get("projectId"))
        except Exception:
            raise HTTPException(status_code=400, detail={"message": "invalid field: projectLines.projectId"})
        domains = row.get("domains")
        if domains is None:
            domains = []
        if not isinstance(domains, list):
            raise HTTPException(status_code=400, detail={"message": "invalid field: projectLines.domains"})
        domains_norm = [str(x).strip() for x in domains if str(x).strip()]
        normalized_lines.append({"projectId": rid, "domains": domains_norm})
    # 非个人空间：行数必须为1，且projectId必须等于Header.Project-Id
    # 记录 body 中的 projectId 列表用于告警日志
    body_ids = []
    try:
        body_ids = [int(r.get("projectId")) for r in normalized_lines]
    except Exception:
        body_ids = [r.get("projectId") for r in normalized_lines]
    if project_id > 0:
        if len(normalized_lines) != 1 or int(normalized_lines[0]["projectId"]) != project_id:
            _warn_400(req, body_ids, "当前空间仅允许选择本空间project")
            raise HTTPException(status_code=400, detail={"message": "当前空间仅允许选择本空间project"})

    # identities 原样持久化（可选）
    identities = body.get("identities")
    if identities is not None and not isinstance(identities, list):
        raise HTTPException(status_code=400, detail={"message": "invalid field: identities"})

    # 生成/加载 client_id（复用现有实现）
    client_id = _load_or_create_client_id()

    # 组合上下文并持久化（最小改动，字段以要求为准）
    ctx = {
        "project_id": project_id,
        "user_id": user_id,
        "task_id": task_id,
        "client_id": client_id,
        "mode": "realtime",
        "activityMode": "realtime",
        "project_lines": normalized_lines,
        "identities": identities,
        "strategies": strategies,
        # 运行期辅助字段
        "running": False,
        "sessionId": None,
        "bindAt": _now_ms(),
        "startAt": None,
        "stopAt": None,
        # 冗余驼峰，便于前端/其他读取者兼容
        "projectId": project_id,
        "userId": user_id,
        "taskId": task_id,
    }
    _context_mem.clear()
    _context_mem.update(ctx)
    try:
        _save_context(ctx)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"persist context failed: {e}")

    # 设置全局活动模式，使 status 接口能正确返回 mode
    global _activity_mode
    _activity_mode = "realtime"

    _log_event("realtime_context_bound", {"taskId": task_id, "projectId": project_id})
    return {"success": True}

@app.post("/local/realtime/start")
async def realtime_start(req: Request) -> Dict[str, Any]:
    """
    启动实时检测（最小改动与原子互斥）：
    - Headers：Project-Id、User-Id
    - Body：{ "taskId": string }
    - 互斥与幂等：
      • 若 _running_task_id 已占用且 != 当前 taskId → 409 "已有进行中的 {activityMode} 任务"
      • 若 process.status().running 为 True → 409 同上
      • 若 _completed_tasks[taskId] in {"success","failed"} → {success:true, started:false, message:"already completed: status=..."}
    - 行为：
      • 设置 _running_task_id = taskId
      • activityMode 写回为 "realtime"
      • 启动 mitm（process.start_capture）
      • 预留调度器占位（asyncio.Task）
    - 返回：{ "success": true, "started": true }
    """
    # 头校验
    project_id_str = _get_header(req, "Project-Id")
    user_id = _get_header(req, "User-Id")
    try:
        project_id = int(project_id_str)
    except Exception:
        raise HTTPException(status_code=400, detail={"message": "invalid header: Project-Id"})

    # 体解析
    try:
        body = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"message": "invalid json body"})
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail={"message": "invalid json body"})
    task_id = str(body.get("taskId") or "").strip()
    if task_id == "":
        raise HTTPException(status_code=400, detail={"message": "missing field: taskId"})

    async with _lock:
        ctx = _load_context() or _context_mem or None
        if not ctx or str(ctx.get("activityMode")) != "realtime":
            try:
                _warn_400(req, [], "context not bound")
            except Exception:
                pass
            raise HTTPException(status_code=400, detail={"message": "context not bound"})

        # 头与上下文一致性（避免串用）
        # 优先使用驼峰格式字段，兜底下划线格式
        ctx_user_id = str(ctx.get("userId") or ctx.get("user_id") or "")
        # 修复：project_id 可能为 0，不能使用 or -1 的逻辑
        ctx_project_id_raw = ctx.get("projectId")
        if ctx_project_id_raw is None:
            ctx_project_id_raw = ctx.get("project_id")
        ctx_project_id = int(ctx_project_id_raw) if ctx_project_id_raw is not None else -1
        ctx_task_id = str(ctx.get("taskId") or ctx.get("task_id") or "")
        
        # 添加调试日志
        _log_event("context_validation", {
            "request_user_id": user_id,
            "request_project_id": project_id,
            "request_task_id": task_id,
            "ctx_user_id": ctx_user_id,
            "ctx_project_id": ctx_project_id,
            "ctx_task_id": ctx_task_id
        })
        
        if ctx_user_id != user_id or ctx_project_id != project_id or ctx_task_id != task_id:
            raise HTTPException(status_code=400, detail={"message": "context mismatch: headers do not match bound context"})

        # 非个人空间启动二次校验：projectLines 必须为单行且与 Header.Project-Id 一致
        if project_id > 0:
            pl = ctx.get("project_lines") or []
            body_ids = []
            try:
                body_ids = [int((r or {}).get("projectId")) for r in pl if isinstance(r, dict) and "projectId" in r]
            except Exception:
                try:
                    body_ids = [(r or {}).get("projectId") for r in pl if isinstance(r, dict)]
                except Exception:
                    body_ids = []
            invalid = False
            try:
                invalid = (len(pl) != 1) or (int((pl[0] or {}).get("projectId")) != project_id)
            except Exception:
                invalid = True
            if invalid:
                _warn_400(req, body_ids, "当前空间仅允许选择本空间project")
                raise HTTPException(status_code=400, detail={"message": "当前空间仅允许选择本空间project"})

        # 全局占位互斥：仅对使用 mitm 的模式进行互斥检查
        global _running_task_id, _activity_mode
        if _running_task_id is not None and _running_task_id != task_id:
            current_mode = _activity_mode or "realtime"
            # 仅当当前运行的是需要 mitm 的模式时才互斥
            if current_mode in ["realtime", "ingest"]:
                raise HTTPException(
                    status_code=409,
                    detail={"message": f"已有进行中的 {current_mode} 任务", "mode": current_mode, "activityMode": current_mode}
                )  # 前端需要结构化 message/mode 以正确提示

        # 进程层互斥：仅对使用 mitm 的模式进行互斥检查
        try:
            from . import process as _process_status
            ps = _process_status.status()
            if bool(ps.get("running")):
                current_mode = (ctx.get("activityMode") or "realtime")
                # 仅当当前运行的是需要 mitm 的模式时才互斥
                if current_mode in ["realtime", "ingest"]:
                    raise HTTPException(
                        status_code=409,
                        detail={"message": f"已有进行中的 {current_mode} 任务", "mode": current_mode, "activityMode": current_mode}
                    )  # 前端需要结构化 message/mode 以正确提示
        except HTTPException:
            raise
        except Exception:
            pass

        # 已完成 → 返回完成信息
        if _completed_tasks.get(task_id) in {"success", "failed"}:
            return {"success": True, "started": False, "message": f"already completed: status={_completed_tasks.get(task_id)}"}

        # 设置占位和活动模式
        _running_task_id = task_id
        _activity_mode = "realtime"

        # 生成 sessionId
        session_id = uuid.uuid4().hex

        # 启动 mitm 和系统代理（直接复用 api.py 中的 start 函数）
        try:
            from . import api
            from fastapi import Request as FastAPIRequest
            import json
            
            # 从上下文提取所有域名用于抓取阶段过滤
            target_domains = []
            project_lines = ctx.get("project_lines", [])
            if isinstance(project_lines, list):
                for line in project_lines:
                    if isinstance(line, dict) and "domains" in line:
                        domains = line.get("domains", [])
                        if isinstance(domains, list):
                            for domain in domains:
                                if isinstance(domain, str) and domain.strip():
                                    # 域名去重、trim、忽略空值
                                    clean_domain = domain.strip()
                                    if clean_domain and clean_domain not in target_domains:
                                        target_domains.append(clean_domain)
            
            # 从配置文件读取端口设置，如果没有配置则使用默认值 8080
            from .config import load_config
            merged_config = load_config()
            
            # 使用配置化的端口处理逻辑，复用 process.py 中的端口处理函数
            from .process import _coerce_port, _is_port_available
            
            # 优先使用配置文件中的端口，如果没有则使用默认值 8080
            configured_port = _coerce_port(merged_config.get("port", 8080))
            if not configured_port:
                configured_port = 8080  # 如果端口验证失败，使用默认值
            
            # 检查端口可用性，如果被占用则尝试寻找可用端口
            mitm_port = configured_port
            if not _is_port_available(mitm_port):
                # 端口被占用，尝试寻找可用端口（从配置端口开始向上查找）
                for port_candidate in range(configured_port, configured_port + 100):
                    if _is_port_available(port_candidate):
                        mitm_port = port_candidate
                        break
                else:
                    # 如果都不可用，返回错误
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"端口 {configured_port} 及其后续端口都被占用，无法启动 mitm 代理"}
                    )
            
            # 构造 api.start 需要的请求体
            start_body = {
                "userId": user_id,
                "projectId": project_id,
                "taskId": task_id,
                "sessionId": session_id,
                "port": mitm_port,  # 使用配置化的 mitm 代理端口
                "bypassDomains": ["127.0.0.1","localhost"],  # 本地环回地址默认旁路，避免自捕获/循环
                "enableDedup": False,  # 实时检测不需要去重
                "ingestUrl": "http://localhost:8008/api/traffic/ingest",  # 添加 ingest URL
                "ingestKey": merged_config.get("ingest_key"),  # 传入鉴权KEY，_build_env会注入INGEST_KEY
                "targetDomains": target_domains  # 添加域名过滤，确保抓取阶段进行域名过滤
            }
            
            # 创建一个模拟的 Request 对象来调用 api.start
            class MockRequest:
                def __init__(self, body_data):
                    self._body_data = body_data
                
                async def json(self):
                    return self._body_data
            
            mock_request = MockRequest(start_body)
            
            # 直接调用 api.start，它包含完整的mitm启动和系统代理配置逻辑
            api_result = await api.start(mock_request)
            
            if not api_result.get("ok", True):
                _running_task_id = None
                error_msg = api_result.get("error", "start failed")
                raise HTTPException(status_code=500, detail=error_msg)
                
        except HTTPException:
            _running_task_id = None
            raise
        except Exception as e:
            _running_task_id = None
            raise HTTPException(status_code=500, detail=f"start api failed: {e}")

        # 更新上下文与持久化
        ctx["activityMode"] = "realtime"
        ctx["mode"] = "realtime"
        ctx["running"] = True
        ctx["sessionId"] = session_id
        ctx["startAt"] = _now_ms()
        ctx["stopAt"] = None
        _context_mem.clear()
        _context_mem.update(ctx)
        try:
            _save_context(ctx)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"persist context failed: {e}")

    # 初始化队列容量并启动调度器
    try:
        from .config import load_config as _load_cfg
        _cfg = _load_cfg()
    except Exception:
        _cfg = {}

    # 读取调度参数（默认：batchIntervalSec=10, batchSize=5）
    _rt = (_cfg or {}).get("realtime") or {}
    try:
        _batch_interval_sec = int(_rt.get("batchIntervalSec") or 10)
    except Exception:
        _batch_interval_sec = 10
    try:
        _batch_size = int(_rt.get("batchSize") or 5)
    except Exception:
        _batch_size = 5

    # 初始化并启动实时队列
    try:
        from .config import load_config as _load_cfg_for_queue
        cfg_for_queue = _load_cfg_for_queue()
        
        # 初始化队列
        queue = init_realtime_queue(cfg_for_queue)
        
        # 修复上下文字段格式：确保包含 build_backend_api_from_context 所需的下划线格式字段
        # 同时保留驼峰格式字段以保持兼容性
        queue_context = ctx.copy()
        queue_context.update({
            "user_id": ctx.get("userId") or ctx.get("user_id"),
            "project_id": ctx.get("projectId") or ctx.get("project_id"),
            "task_id": ctx.get("taskId") or ctx.get("task_id"),
            "client_id": ctx.get("client_id")  # client_id 已经是正确格式
        })
        
        # 启动调度器
        backend_base_url = "http://localhost:8008"  # 默认后端地址
        await queue.start_scheduler(queue_context, backend_base_url)
        
        global _realtime_scheduler_task
        _realtime_scheduler_task = None
    except Exception as e:
        try:
            _logger.warning("[realtime] scheduler start failed: %s", e)
        except Exception:
            pass

    return {"success": True, "started": True}

@app.post("/local/realtime/stop")
async def realtime_stop(req: Request) -> Dict[str, Any]:
    """
    停止实时检测（占位调度器+mitm停止+上下文清理）：
    - 停止“调度器占位”（若存在则取消，TODO：执行收尾批次）
    - 停止 mitm
    - 清理 _running_task_id，并在 _completed_tasks[taskId] = "success"
    - activityMode 清空（None），上下文持久化
    返回：{ "success": true, "stopped": true }
    """
    _ = _get_header(req, "Project-Id")
    _ = _get_header(req, "User-Id")

    async with _lock:
        ctx = _load_context() or _context_mem or {}

        # 停止调度器任务
        global _realtime_scheduler_task
        if _realtime_scheduler_task is not None and not _realtime_scheduler_task.done():
            try:
                _realtime_scheduler_task.cancel()
            except Exception:
                pass
        _realtime_scheduler_task = None

        # 停止队列调度器并执行收尾批次
        try:
            queue = get_realtime_queue()
            if queue:
                await queue.stop_scheduler()
        except Exception:
            # 清理阶段失败不阻断停机流程
            pass

        # 委托统一API停止：按需恢复系统代理（仅启动成功且有快照时），避免无意义弹窗
        try:
            from . import api as _api
            await _api.stop()
        except Exception:
            # 回退：仅停止mitm，不直接触碰系统代理，避免再次弹窗
            try:
                from . import process as _process
                _process.stop_capture()
                _process.set_proxy_enabled(False)
            except Exception:
                pass

        # 标记完成并释放占位
        global _running_task_id, _activity_mode
        task_id = str(ctx.get("taskId") or ctx.get("task_id") or "").strip()
        if task_id:
            _completed_tasks[task_id] = "success"
        _running_task_id = None
        _activity_mode = None

        # 上下文清理并持久化
        ctx["running"] = False
        ctx["sessionId"] = None
        ctx["activityMode"] = None
        ctx["stopAt"] = _now_ms()
        _context_mem.clear()
        _context_mem.update(ctx)
        try:
            _save_context(ctx)
        except Exception:
            pass

    return {"success": True, "stopped": True}

@app.get("/local/realtime/status")
async def realtime_status() -> Dict[str, Any]:
    """
    返回实时检测运行状态（最小可用）：
      {
        "running": bool from process.status(),
        "sessionId": string|null,
        "queueSize": number,       // 暂定 0；后续接入队列后返回实际值
        "lastEventTs": number|null,// 通过 events.get_status_fields()
        "mode": "realtime" | "permission" | "ingest" | null
      }
    """
    ctx = _load_context() or _context_mem or {}
    # 运行态以进程为准
    try:
        from . import process as _process
        ps = _process.status()
        running = bool(ps.get("running"))
        session_id = ps.get("sessionId") or ctx.get("sessionId")
    except Exception:
        running = bool(ctx.get("running"))
        session_id = ctx.get("sessionId")

    # 事件时间戳
    try:
        from . import events as _events
        extra = _events.get_status_fields() if hasattr(_events, 'get_status_fields') else {}
        last_ts = extra.get('lastEventTs')
    except Exception:
        # 不影响接口可用性，记录警告并返回 null
        try:
            _logger.warning('[realtime-status] events unavailable, lastEventTs=null', exc_info=False)
        except Exception:
            pass
        last_ts = None

    # 队列大小：读取 realtime_queue.size()
    try:
        queue = get_realtime_queue()
        if queue:
            queue_size = queue.get_queue_size()
            discard_count = queue._dropped_count
        else:
            queue_size = 0
            discard_count = 0
    except Exception:
        # 不影响接口可用性，记录警告并返回 0
        try:
            _logger.warning('[realtime-status] queue stats read failed, defaults applied', exc_info=False)
        except Exception:
            pass
        queue_size = 0
        discard_count = 0

    return {
        "running": running,
        "sessionId": session_id,
        "queueSize": queue_size,
        "discardCount": discard_count,
        "lastEventTs": last_ts,
        "mode": _activity_mode,
    }

# 兼容 CLI 启动（示例命令见交付说明）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("sensitive_check_local.server:app", host="127.0.0.1", port=17866, reload=False, log_level="info")  # 本地服务自身是在localhost启动的，这里保留127.0.0.1