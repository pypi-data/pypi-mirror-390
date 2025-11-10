import contextlib
import functools
import os.path
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from cloudpathlib import CloudPath, S3Client, S3Path
from rich.progress import BarColumn, DownloadColumn, Progress, TaskID, TextColumn, TransferSpeedColumn

__all__ = [
    "TransferCallbackS3Client",
    "make_progress_callback",
    "make_progressed_s3_client",
]

TransferDirection = Literal["download", "upload"]
TransferState = Literal["start", "update", "stop"]


@contextlib.contextmanager
def make_transfer_callback(
    callback: Callable[[CloudPath, TransferDirection, TransferState, int], None],
    path: Path | CloudPath,
    direction: TransferDirection,
):
    if callback is None:
        yield None
        return

    callback(path, direction, "start", 0)
    try:
        yield functools.partial(callback, path, direction, "update")
    finally:
        callback(path, direction, "stop", 0)


class TransferCallbackS3Client(S3Client):
    def __init__(
        self,
        *args,
        transfer_callback: Callable[[CloudPath, TransferDirection, TransferState, int], None],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.transfer_callback = transfer_callback

    def _download_file(self, cloud_path: S3Path, local_path: str | os.PathLike) -> Path:
        local_path = Path(local_path)

        obj = self.s3.Object(cloud_path.bucket, cloud_path.key)

        with make_transfer_callback(self.transfer_callback, cloud_path, "download") as callback:
            obj.download_file(
                str(local_path),
                Config=self.boto3_transfer_config,
                ExtraArgs=self.boto3_dl_extra_args,
                Callback=callback,
            )
        return local_path

    def _upload_file(self, local_path: str | os.PathLike, cloud_path: S3Path) -> S3Path:
        local_path = Path(local_path)

        obj = self.s3.Object(cloud_path.bucket, cloud_path.key)

        extra_args = self.boto3_ul_extra_args.copy()

        if self.content_type_method is not None:
            content_type, content_encoding = self.content_type_method(str(local_path))
            if content_type is not None:
                extra_args["ContentType"] = content_type
            if content_encoding is not None:
                extra_args["ContentEncoding"] = content_encoding

        with make_transfer_callback(self.transfer_callback, local_path, "upload") as callback:
            obj.upload_file(
                str(local_path),
                Config=self.boto3_transfer_config,
                ExtraArgs=extra_args,
                Callback=callback,
            )
        return cloud_path


def make_progress_callback(progress: Progress) -> Callable[[CloudPath, TransferDirection, TransferState, int], None]:
    task_ids: dict[Path | CloudPath, TaskID] = {}

    def progress_callback(path: Path | CloudPath, direction: TransferDirection, state: TransferState, bytes_sent: int):
        if state == "start":
            size = path.stat().st_size
            task_ids[path] = progress.add_task(direction, total=size, filename=path.name)
        elif state == "stop":
            if path in task_ids:
                progress.remove_task(task_ids[path])
                del task_ids[path]
        else:
            progress.update(task_ids[path], advance=bytes_sent)

    return progress_callback


@contextlib.contextmanager
def make_progressed_s3_client(aws_access_key_id: str, aws_secret_access_key: str, endpoint_url: str):
    aws_access_key_id = aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
    endpoint_url = endpoint_url or os.environ.get("AWS_ENDPOINT_URL")

    with Progress(
        TextColumn("[blue]{task.fields[filename]}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
    ) as progress:
        yield TransferCallbackS3Client(aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_access_key,
                                       endpoint_url=endpoint_url,
                                       transfer_callback=make_progress_callback(progress))
