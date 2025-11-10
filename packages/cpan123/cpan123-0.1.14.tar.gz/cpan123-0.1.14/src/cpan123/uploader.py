from __future__ import annotations

import hashlib
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from .file2 import File2
from .utils.api import Api, Auth
from .utils.md5 import calculate_md5


class Uploader:
    """高层次上传器，封装 file2 接口，支持：
    - 单个文件分片上传
    - 单个文件单步上传
    - 目录上传（可多线程，策略可选）

    约定：
    - 单步上传服务域名通过 domain 接口获取
    - 分片上传 slice 使用 create 返回的 servers 任意其一
    """

    def __init__(self, auth: Optional[Auth] = None) -> None:
        self.auth = auth or Auth()
        self.api = File2(auth=self.auth)

    # ---------------------- 单文件：分片上传 ----------------------
    def upload_file_chunked(
        self,
        file_path: str | Path,
        parentFileID: int = 0,
        duplicate: int = 1,
        containDir: bool = False,
        server: Optional[str] = None,
        slice_size: Optional[int] = None,
        poll_timeout_sec: int = 300,
        remote_path: Optional[str] = None,
    ) -> dict:
        """按分片上传单个文件。

        Args:
            file_path: 本地文件路径
            parentFileID: 父目录 id
            duplicate: 重名策略（1 保留两者，2 覆盖原文件）
            containDir: 是否携带路径（为 True 时 filename 传相对路径）
            server: 指定上传域名（可选，不传使用 create 返回 servers[0]）
            slice_size: 指定分片大小（可选，不传使用服务端下发 sliceSize）
            poll_timeout_sec: upload_complete 轮询超时时间

        Returns:
            服务端最终响应 data 字段
        """
        path = Path(file_path)
        assert path.exists() and path.is_file(), f"文件不存在: {path}"

        size = path.stat().st_size
        etag = calculate_md5(path)
        # 生成 filename，是否带目录由 containDir 决定
        if not containDir:
            filename = path.name
        else:
            # 允许外部传入远程相对路径，避免把本机绝对路径上传
            if remote_path:
                filename = remote_path if remote_path.startswith("/") else f"/{remote_path}"
            else:
                # 兜底：使用文件名（不带目录）
                filename = path.name

        # 1) 创建上传任务
        resp = self.api.create(
            parentFileID=parentFileID,
            filename=filename,
            etag=etag,
            size=size,
            duplicate=duplicate,
            containDir=containDir,
        )
        data = resp.data or {}
        # 秒传
        if data.get("reuse") is True and data.get("fileID", 0) != 0:
            return data

        preuploadID = data.get("preuploadID")
        if not preuploadID:
            raise RuntimeError("创建分片任务失败：缺少 preuploadID")

        real_slice = int(slice_size or data.get("sliceSize") or 16 * 1024 * 1024)
        upload_server = server or (data.get("servers") or [None])[0]
        if not upload_server:
            raise RuntimeError("创建分片任务失败：缺少可用上传域名 servers")

        slice_url = f"{upload_server.rstrip('/')}/upload/v2/file/slice"

        # 2) 逐片上传
        total_parts = math.ceil(size / real_slice) if real_slice else 0
        with path.open("rb") as f:
            for part_no in range(1, total_parts + 1):
                chunk = f.read(real_slice)
                if not chunk:
                    break
                # 构造 multipart，直接用 Api 发送
                files = {"slice": ("blob", chunk, "application/octet-stream")}
                _ = Api(
                    method="POST",
                    url=slice_url,
                    data={
                        "preuploadID": preuploadID,
                        "sliceNo": part_no,
                        "sliceMD5": Uploader.__md5_bytes(chunk),
                    },
                    auth=self.auth,
                    files=files,
                    skip=True,
                ).result

        # 3) 完成上传（必要时轮询）
        start = time.time()
        while True:
            done = self.api.upload_complete(preuploadID=preuploadID)
            d = done.data or {}
            if d.get("completed") and d.get("fileID", 0) != 0:
                return d
            if time.time() - start > poll_timeout_sec:
                raise TimeoutError("上传完成确认超时")
            time.sleep(1)

    # ---------------------- 单文件：单步上传 ----------------------
    def upload_file_single(
        self,
        file_path: str | Path,
        parentFileID: int = 0,
        duplicate: int = 1,
        containDir: bool = False,
        domain: Optional[str] = None,
        single_limit_bytes: int = 1 * 1024 * 1024 * 1024,  # 1GB（接口限制）
        remote_path: Optional[str] = None,
    ) -> dict:
        """单步上传单个文件（小文件）。

        Args:
            file_path: 本地文件路径
            parentFileID: 父目录 id
            duplicate: 重名策略（1 保留两者，2 覆盖原文件）
            containDir: 是否携带路径
            domain: 指定上传域名（不传则自动获取）
            single_limit_bytes: 单步上传大小限制
        """
        path = Path(file_path)
        assert path.exists() and path.is_file(), f"文件不存在: {path}"
        size = path.stat().st_size
        if size > single_limit_bytes:
            raise ValueError("文件过大，请使用分片上传")

        etag = calculate_md5(path)
        if not containDir:
            filename = path.name
        else:
            if remote_path:
                filename = remote_path if remote_path.startswith("/") else f"/{remote_path}"
            else:
                filename = path.name

        # 选择上传域名
        upload_domain = domain
        if not upload_domain:
            domains = self.api.domain()
            arr = domains.data or []
            upload_domain = (arr or [None])[0]
        if not upload_domain:
            raise RuntimeError("获取上传域名失败")

        single_url = f"{upload_domain.rstrip('/')}/upload/v2/file/single/create"

        # 用文件对象避免占用大量内存
        with path.open("rb") as fp:
            files = {"file": (path.name, fp, "application/octet-stream")}
            res = Api(
                method="POST",
                url=single_url,
                data={
                    "parentFileID": parentFileID,
                    "filename": filename,
                    "etag": etag,
                    "size": size,
                    "duplicate": duplicate,
                    "containDir": containDir,
                },
                files=files,
                auth=self.auth,
            ).result
        data = (res or {}).get("data", {}) if isinstance(res, dict) else {}
        if data.get("completed") and data.get("fileID", 0) != 0:
            return res
        raise RuntimeError(f"单步上传失败: {res}")

    # ---------------------- 目录上传 ----------------------
    def upload_folder(
        self,
        folder_path: str | Path,
        parentFileID: int = 0,
        method: str = "auto",  # 'single' | 'chunked' | 'auto'
        max_workers: int = 4,
        single_limit_bytes: int = 1 * 1024 * 1024 * 1024,
        duplicate: int = 1,
        contain_dir: bool = True,
    ) -> dict:
        """上传整个文件夹。

        - method='single'：全部使用单步上传（大于限制的文件会自动切换分片）
        - method='chunked'：全部使用分片上传
        - method='auto'：小于单步限制走单步，其他分片
        - 当 contain_dir=True 时，远程路径会包含根目录本身，例如：/文件夹名/子目录/文件

        返回 (本地文件, data) 列表
        """
        root = Path(folder_path)
        assert root.exists() and root.is_dir(), f"目录不存在: {root}"

        files: list[tuple[Path, str]] = []  # (真实路径, 远程相对路径)
        for p in root.rglob("*"):
            if p.is_file():
                # 统一相对路径（用于 containDir）
                rel = p.relative_to(root)
                if contain_dir:
                    # 包含根目录本身
                    remote = f"/{root.name}/{rel.as_posix()}"
                else:
                    remote = p.name
                files.append((p, remote))

        results: list[tuple[Path, dict]] = []

        def _task(item: tuple[Path, str]) -> tuple[Path, dict]:
            real_path, remote = item
            size = real_path.stat().st_size
            try:
                if method == "chunked" or (method == "auto" and size > single_limit_bytes):
                    data = self.upload_file_chunked(
                        real_path,
                        parentFileID=parentFileID,
                        duplicate=duplicate,
                        containDir=contain_dir,
                        remote_path=remote,
                    )
                else:
                    data = self.upload_file_single(
                        real_path,
                        parentFileID=parentFileID,
                        duplicate=duplicate,
                        containDir=contain_dir,
                        single_limit_bytes=single_limit_bytes,
                        remote_path=remote,
                    )
                return (real_path, data)
            except Exception as e:  # 汇总错误，便于一次性查看
                return (real_path, {"error": str(e)})

        # 多线程提交任务
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            fut_map = {ex.submit(_task, item): item for item in files}
            for fut in as_completed(fut_map):
                results.append(fut.result())

        # 规范化每个文件的返回，统一为 {code, message, success, data}
        normalized: dict[str, dict] = {}
        for real_path, item in results:
            key = str(real_path)
            # 异常场景
            if isinstance(item, dict) and "error" in item:
                normalized[key] = {
                    "code": 1,
                    "message": str(item.get("error")),
                    "success": False,
                    "data": None,
                }
                continue

            # 解包外层 {code,message,data} 与直接 data 两种形态
            inner = item.get("data") if isinstance(item, dict) and isinstance(item.get("data"), dict) else item
            if not isinstance(inner, dict):
                normalized[key] = {
                    "code": 1,
                    "message": "unexpected response",
                    "success": False,
                    "data": None,
                }
                continue

            file_id = int(inner.get("fileID", 0) or 0)
            completed = bool(inner.get("completed"))
            reuse = bool(inner.get("reuse"))
            success = file_id != 0 and (completed or reuse)

            normalized[key] = {
                "code": 0 if success else 1,
                "message": "ok" if success else "failed",
                "success": success,
                "data": inner,
            }

        # 统计
        total = len(normalized)
        succeeded = sum(1 for v in normalized.values() if v.get("success"))
        failed = total - succeeded

        return {
            "code": 0,
            "message": "ok",
            "total": total,
            "succeeded": succeeded,
            "failed": failed,
            "data": normalized,
        }

    @staticmethod
    def __md5_bytes(b: bytes) -> str:
        h = hashlib.md5()
        h.update(b)
        return h.hexdigest()

    # 如果选择的是文件,则调用 upload_file_chunked
    # 如果是目录,则调用 upload_folder
    def upload(
        self,
        file_path: Path,
        parentFileID: int = 0,
        duplicate: bool = False,
        contain_dir: bool = False,
    ) -> dict:
        """根据路径类型选择上传方式。

        Args:
            file_path: 本地文件或目录路径
            parentFileID: 父目录 id
            duplicate: 重名策略（True 保留两者，False 覆盖原文件）

        Returns:
            服务端最终响应 data 字段

        """
        path = Path(file_path)

        if path.is_file():  # 10MB 及以上走分片上传
            size = path.stat().st_size
            if size >= 10 * 1024 * 1024:
                return self.upload_file_chunked(
                    file_path=path,
                    parentFileID=parentFileID,
                    duplicate=duplicate,
                    containDir=contain_dir,
                )
            else:
                return self.upload_file_single(
                    file_path=path,
                    parentFileID=parentFileID,
                    duplicate=duplicate,
                    containDir=contain_dir,
                )
        elif path.is_dir():
            return self.upload_folder(
                folder_path=path,
                parentFileID=parentFileID,
                duplicate=int(1 if duplicate else 2),
                contain_dir=contain_dir,
            )
        else:
            raise ValueError(f"路径既不是文件也不是目录: {path}")
