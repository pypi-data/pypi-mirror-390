import os

import click
from typing_extensions import Tuple, Union

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.adapter.fovus_s3_adapter import FovusS3Adapter
from fovus.util.file_util import FileUtil
from fovus.util.util import Util


@click.command("download")
@click.argument("fovus_path", type=str)
@click.argument("local_path", type=str, required=False)
@click.option(
    "--include-paths",
    "include_paths_tuple",
    metavar="include_paths",
    type=str,
    multiple=True,
    help=r"""
        The relative paths to files or folders inside the FOVUS_PATH that will be downloaded. Paths are provided with support for Unix shell-style wildcards.

        You can only provide either --include-paths or --exclude-paths,  not both.

        Supported wildcards:
        \* - matches any number of characters
        ? - matches any single character

        E.g. taskName/out?/\*.txt matches any .txt file in folders taskName/out1, taskName/out2, etc.

        E.g. taskName???/folder/file.txt matches taskName001/folder/file.txt, taskName123/folder/file.txt, etc.

        To specify multiple paths, this option may be provided multiple times or deliminated by a comma (``,``). To escape a comma, use two commas (``,,``).

        E.g. --include-paths "path1" --include-paths "path2"

        E.g. --include-paths "path1,path2"
        """,
)
@click.option(
    "--exclude-paths",
    "exclude_paths_tuple",
    metavar="exclude_paths",
    type=str,
    multiple=True,
    help=r"""
        The relative paths to files or folders inside the FOVUS_PATH that will not be downloaded. Paths are provided with support for Unix shell-style wildcards.

        You can only provide either --include-paths or --exclude-paths,  not both.

        Supported wildcards:
        \* - matches any number of characters
        ? - matches any single character

        E.g. taskName/out?/\*.txt matches any .txt file in folders taskName/out1, taskName/out2, etc.

        E.g. taskName???/folder/file.txt matches taskName001/folder/file.txt, taskName123/folder/file.txt, etc.

        To specify multiple paths, this option may be provided multiple times or deliminated by a comma (``,``). To escape a comma, use two commas (``,,``).

        E.g. --exclude-paths "path1" --exclude-paths "path2"

        E.g. --exclude-paths "path1,path2"
        """,
)
def storage_download_command(
    fovus_path: str,
    local_path: Union[str, None],
    include_paths_tuple: Tuple[str, ...],
    exclude_paths_tuple: Tuple[str, ...],
):
    r"""
    Download a file or folder from Fovus Storage, including shared files or folders.

    Only new or updated files will be downloaded.

    For files or folders under My Files, FOVUS_PATH is the relative path with respect to /fovus_storage/files/. For example, the FOVUS_PATH for the file under path "/fovus_storage/files/examples/file.txt" should be just "examples/file.txt"

    For shared files or folders under "Shared with me" or "Shared with workspace", FOVUS_PATH is the full path that can be copied from the web UI with the format "/fovus-storage/shared/ACCESS_TOKEN/PATH/TO/FILE_OR_FOLDER/"

    LOCAL_PATH is the local directory where the files will be downloaded to. If not provided, the current working directory will be used.
    """
    include_paths = Util.parse_include_exclude_paths(include_paths_tuple)
    exclude_paths = Util.parse_include_exclude_paths(exclude_paths_tuple)
    current_dir = os.getcwd()

    access_token, folder_path = FileUtil.parse_shared_file_path(fovus_path)

    print("Authenticating...")
    fovus_api_adapter = FovusApiAdapter()

    fovus_s3_adapter = FovusS3Adapter(
        fovus_api_adapter,
        root_directory_path=local_path if local_path else current_dir,
        fovus_path=folder_path if access_token else fovus_path,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        shared_access_token=access_token,
    )
    fovus_s3_adapter.download_files()
