from __future__ import annotations

from typing import Optional

from pydantic import Field

from .utils.api import Auth
from .utils.baseapiclient import BaseApiClient, auto_args_call_api
from .utils.checkdata import DataResponse


class File2(BaseApiClient):
    def __init__(self, auth: Optional[Auth] = None) -> None:
        super().__init__(filepath="file2", auth=auth)

    @auto_args_call_api("create")
    def create(
        self,
        parentFileID: int,
        filename: str,
        etag: str = Field(default="", max_length=32),
        size: int = Field(default=0, gt=0),
        duplicate: int = 1,
        containDir: bool = False,
        skip: bool = False,
    ) -> DataResponse:  # type: ignore
        """
        创建文件上传任务.

        - 文件名不能全部是空格
        - 开发者上传单文件大小限制10GB

        Args:
            parentFileID: 父目录id,上传到根目录时填写 0
            filename: 文件名要小于255个字符且不能包含一些特殊字符(不建议重名)
            etag: 文件的md5值, 如果不传入,则自动计算
            size: 文件大小, 单位字节
            duplicate: 当有相同文件名时,文件处理策略(1保留两者,新文件名将自动添加后缀,2覆盖原文件)
            containDir: 上传文件是否包含路径,默认false
            skip: 是否跳过响应数据的模式校验
        """

    @auto_args_call_api("slice")
    def slice(
        self,
        preuploadID: int,
        sliceNo: int,
        sliceMD5: str,
        slice: bytes,
        skip: bool = False,
    ) -> DataResponse:  # type: ignore
        """上传文件分片.

        Args:
            preuploadID:  预上传ID
            sliceNo: 分片序号，从1开始自增
            sliceMD5: 当前分片md5
            slice: 分片二进制流
            skip: 是否跳过响应数据的模式校验
        """

    @auto_args_call_api("upload_complete")
    def upload_complete(
        self,
        preuploadID: int,
        skip: bool = False,
    ) -> DataResponse:  # type: ignore
        """完成文件上传.

        Args:
            preuploadID: 预上传ID
            skip: 是否跳过响应数据的模式校验
        """

    @auto_args_call_api("domain")
    def domain(
        self,
        skip: bool = False,
    ) -> DataResponse:  # type: ignore
        """获取上传域名.

        Args:
            skip: 是否跳过响应数据的模式校验
        """

    @auto_args_call_api("single_create")
    def single_create(
        self,
        parentFileID: int,
        filename: str,
        etag: str = Field(default="", max_length=32),
        size: int = Field(default=0, gt=0),
        file: bytes = Field(default=b""),
        duplicate: int = 1,
        containDir: bool = False,
        skip: bool = False,
    ) -> DataResponse:  # type: ignore
        """单步上传

        - 文件名要小于256个字符且不能包含以下任何字符
        - 文件名不能全部是空格
        - 此接口限制开发者上传单文件大小为1GB
        - 上传域名是获取上传域名接口响应中的域名
        - 此接口用于实现小文件单步上传一次HTTP请求交互即可完成上传

        Args:
            parentFileID: 父目录id,上传到根目录时填写 0
            filename: 文件名要小于255个字符且不能包含一些特殊字符(不建议重名)
            etag: 文件的md5值, 如果不传入,则自动计算
            size: 文件大小, 单位字节
            file: 文件二进制流
            duplicate: 当有相同文件名时,文件处理策略(1保留两者,新文件名将自动添加后缀,2覆盖原文件)
            containDir: 上传文件是否包含路径,默认false
            skip: 是否跳过响应数据的模式校验
        """
