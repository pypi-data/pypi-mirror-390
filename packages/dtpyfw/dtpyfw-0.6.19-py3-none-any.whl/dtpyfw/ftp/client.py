from contextlib import contextmanager
from datetime import datetime
from ftplib import FTP, error_perm
from io import BytesIO
from os.path import basename
from typing import Dict, Generator, List, Optional, Union

import paramiko
from dateutil import parser
from paramiko.sftp_client import SFTPClient

from ..core import file_folder

__all__ = ("FTPClient",)


class FTPClient:
    """A unified client for FTP and SFTP file transfer operations.

    This class provides a consistent interface for common file operations over both
    FTP and SFTP protocols, including listing directories, uploading, downloading,
    deleting, and renaming files. Protocol selection is automatic based on port or
    can be explicitly specified.

    Attributes:
        server (str): The FTP/SFTP server address.
        port (int): The server port number.
        username (str): Authentication username.
        password (str): Authentication password.
        timeout (int): Connection timeout in seconds.
        is_sftp (bool): True for SFTP protocol, False for FTP protocol.
    """

    def __init__(
        self,
        server: str,
        port: int,
        username: str,
        password: str,
        timeout: int = 20,
        is_sftp: Optional[bool] = None,
    ) -> None:
        """Initialize the FTP/SFTP client with connection parameters.

        Sets up the client configuration for connecting to an FTP or SFTP server.
        Protocol selection is automatic based on port 22 (SFTP) or can be explicitly
        specified via the is_sftp parameter.

        Args:
            server (str): The hostname or IP address of the FTP/SFTP server.
            port (int): The port number to connect to on the server.
            username (str): The username for authentication.
            password (str): The password for authentication.
            timeout (int): Connection timeout in seconds. Defaults to 20.
            is_sftp (Optional[bool]): Protocol selection. True for SFTP, False for FTP,
                None for automatic detection (port 22 = SFTP, otherwise FTP).
                Defaults to None.
        """
        self.server = server
        self.port = int(port)
        self.username = username
        self.password = password
        self.timeout = timeout
        # If protocol not specified, assume SFTP for port 22
        self.is_sftp = is_sftp if is_sftp is not None else (self.port == 22)

    @contextmanager
    def _connect(self) -> Generator[Union[SFTPClient, FTP], None, None]:
        """Establish and yield a protocol-specific connection to the remote
        server.

        Creates either an SFTP or FTP connection based on the client's configuration.
        The connection is automatically closed when exiting the context manager,
        ensuring proper resource cleanup.

        Yields:
            Union[SFTPClient, FTP]: An active connection object. For SFTP, yields a
                paramiko.SFTPClient instance. For FTP, yields an ftplib.FTP instance.

        Raises:
            paramiko.SSHException: If SFTP connection or authentication fails.
            socket.error: If network connection cannot be established.
            ftplib.error_perm: If FTP authentication fails.
        """
        if self.is_sftp:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.server,
                username=self.username,
                password=self.password,
                port=self.port,
                timeout=self.timeout,
            )
            sftp = ssh.open_sftp()
            sftp_channel = sftp.get_channel()
            if sftp_channel is not None:
                sftp_channel.settimeout(self.timeout)
            try:
                yield sftp
            finally:
                sftp.close()
                ssh.close()
        else:
            ftp = FTP()
            ftp.connect(host=self.server, port=self.port)
            ftp.login(user=self.username, passwd=self.password)
            try:
                yield ftp
            finally:
                ftp.quit()

    def content(self, file_path: str) -> Dict[str, Union[str, datetime]]:
        """Retrieve the content and metadata of a remote file.

        Downloads the entire file content and retrieves its last modification timestamp.
        The file content is decoded as UTF-8 text.

        Args:
            file_path (str): The full path to the file on the remote server.

        Returns:
            Dict[str, Union[str, datetime]]: A dictionary with the following keys:
                - 'name' (str): The base filename without path.
                - 'last_modified' (datetime): The file's last modification timestamp.
                - 'content' (str): The file content decoded as UTF-8.

        Raises:
            IOError: If the file cannot be read (SFTP).
            ftplib.error_perm: If the file cannot be accessed (FTP).
            UnicodeDecodeError: If the file content is not valid UTF-8.
        """
        if self.is_sftp:
            with self._connect() as sftp:
                with sftp.open(file_path) as remote_file: # type:ignore[union-attr]
                    file_content = remote_file.read().decode("utf-8")
                utime = sftp.stat(file_path).st_mtime # type:ignore[union-attr]
                if utime is None:
                    raise IOError(f"Could not retrieve modification time for file: {file_path}")
                last_modified = datetime.fromtimestamp(utime)
        else:
            with self._connect() as ftp, BytesIO() as r:
                ftp.retrbinary(f"RETR {file_path}", r.write) # type:ignore[union-attr]
                file_content = r.getvalue().decode("utf-8")
                timestamp = ftp.voidcmd(f"MDTM {file_path}")[4:].strip() # type:ignore[union-attr]
                last_modified = parser.parse(timestamp)

        return {
            "name": basename(file_path),
            "last_modified": last_modified,
            "content": file_content,
        }

    def get_last_modified(self, file_path: str) -> Dict[str, Union[str, datetime, None]]:
        """Get the last modification timestamp of a remote file.

        Retrieves file metadata without downloading the file content. Useful for
        checking if a file has been updated since last access.

        Args:
            file_path (str): The full path to the file on the remote server.

        Returns:
            Dict[str, Union[str, datetime]]: A dictionary with the following keys:
                - 'name' (str): The base filename without path.
                - 'last_modified' (datetime): The file's last modification timestamp.

        Raises:
            IOError: If the file metadata cannot be retrieved (SFTP).
            ftplib.error_perm: If the file cannot be accessed (FTP).
        """
        if self.is_sftp:
            with self._connect() as sftp:
                utime = sftp.stat(file_path).st_mtime # type:ignore[union-attr]
                if utime is None:
                    last_modified = None
                else:
                    last_modified = datetime.fromtimestamp(utime)
        else:
            with self._connect() as ftp:
                timestamp = ftp.voidcmd(f"MDTM {file_path}")[4:].strip() # type:ignore[union-attr]
                last_modified = parser.parse(timestamp)

        return {
            "name": basename(file_path),
            "last_modified": last_modified,
        }

    def get_folder_list(self, folder_path: str = "") -> List[str]:
        """List the contents of a remote directory.

        Retrieves a list of all files and subdirectories in the specified remote
        directory. Returns an empty list if the directory is empty or inaccessible.

        Args:
            folder_path (str): The path to the directory on the remote server.
                If empty string, lists the current working directory. Defaults to "".

        Returns:
            List[str]: A list of filenames and directory names in the specified path.

        Raises:
            IOError: If the directory cannot be accessed (SFTP).
        """
        if self.is_sftp:
            with self._connect() as sftp:
                file_list = sftp.listdir(path=folder_path) # type:ignore[union-attr]
        else:
            with self._connect() as ftp:
                if folder_path:
                    ftp.cwd(folder_path) # type:ignore[union-attr]
                try:
                    file_list = ftp.nlst()  # type:ignore[union-attr]
                except error_perm:
                    file_list = []
        return file_list

    def upload_file(
        self, local_path: str, file_path: str, confirm: bool = True
    ) -> bool:
        """Upload a local file to the remote server.

        Transfers a file from the local filesystem to the specified path on the
        remote server. For SFTP, optionally performs a stat call to verify the
        upload succeeded.

        Args:
            local_path (str): The path to the local file to upload.
            file_path (str): The destination path on the remote server where the
                file will be saved.
            confirm (bool): For SFTP only, whether to perform a stat call after
                upload to confirm success. Defaults to True.

        Returns:
            bool: Always returns True upon successful upload.

        Raises:
            IOError: If the file cannot be uploaded or confirmed (SFTP).
            ftplib.error_perm: If the upload fails due to permissions (FTP).
            FileNotFoundError: If the local file does not exist.
        """
        if self.is_sftp:
            with self._connect() as sftp:
                sftp.put(remotepath=file_path, localpath=local_path, confirm=confirm) # type:ignore[union-attr]
        else:
            with self._connect() as ftp, open(local_path, "rb") as file_obj:
                ftp.storbinary(f"STOR {file_path}", file_obj) # type:ignore[union-attr]
        return True

    def download_file(
        self,
        local_path: str,
        file_path: str,
        make_directory: bool = True,
        remove_file: bool = True,
    ) -> bool:
        """Download a remote file to the local filesystem.

        Transfers a file from the remote server to the specified local path.
        Optionally creates parent directories and removes existing files before
        download.

        Args:
            local_path (str): The local path where the downloaded file will be saved.
            file_path (str): The path to the file on the remote server.
            make_directory (bool): If True, creates the local directory structure
                if it doesn't exist. Defaults to True.
            remove_file (bool): If True, removes the local file before download if
                it already exists. Defaults to True.

        Returns:
            bool: Always returns True upon successful download.

        Raises:
            IOError: If the file cannot be downloaded (SFTP).
            ftplib.error_perm: If the file cannot be accessed (FTP).
            OSError: If local directory creation or file removal fails.
        """
        if make_directory:
            file_folder.make_directory(file_folder.folder_path_of_file(local_path))

        if remove_file:
            file_folder.remove_file(local_path)

        if self.is_sftp:
            with self._connect() as sftp:
                sftp.get(remotepath=file_path, localpath=local_path) # type:ignore[union-attr]
        else:
            with self._connect() as ftp, open(local_path, "wb") as file_obj:
                ftp.retrbinary(f"RETR {file_path}", file_obj.write) # type:ignore[union-attr]
        return True

    def delete_file(self, file_path: str) -> bool:
        """Delete a file from the remote server.

        Permanently removes the specified file from the remote filesystem.

        Args:
            file_path (str): The full path to the file to delete on the remote server.

        Returns:
            bool: Always returns True upon successful deletion.

        Raises:
            IOError: If the file cannot be deleted (SFTP).
            ftplib.error_perm: If the file cannot be deleted due to permissions or
                does not exist (FTP).
        """
        if self.is_sftp:
            with self._connect() as sftp:
                sftp.remove(file_path) # type:ignore[union-attr]
        else:
            with self._connect() as ftp:
                ftp.delete(file_path) # type:ignore[union-attr]
        return True

    def rename_file(self, old_path: str, new_path: str) -> bool:
        """Rename or move a file on the remote server.

        Changes the path of a file on the remote server. Can be used to rename a
        file or move it to a different directory.

        Args:
            old_path (str): The current path of the file on the remote server.
            new_path (str): The new path for the file on the remote server.

        Returns:
            bool: Always returns True upon successful rename/move.

        Raises:
            IOError: If the file cannot be renamed (SFTP).
            ftplib.error_perm: If the operation fails due to permissions or if the
                source file does not exist (FTP).
        """
        if self.is_sftp:
            with self._connect() as ftp:
                ftp.rename(old_path, new_path)
        else:
            with self._connect() as ftp:
                ftp.rename(old_path, new_path)
        return True

    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists on the remote server.

        Verifies the existence of a file at the specified path on the remote server
        without downloading it. For SFTP, uses stat(); for FTP, uses size().

        Args:
            file_path (str): The full path to the file to check on the remote server.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        if self.is_sftp:
            try:
                with self._connect() as ftp:
                    ftp.stat(file_path) # type:ignore[union-attr]
                return True
            except IOError:
                return False
        else:
            try:
                with self._connect() as ftp:
                    ftp.size(file_path) # type:ignore[union-attr]
                return True
            except error_perm:
                return False

    def create_directory(self, directory: str) -> bool:
        """Create a directory on the remote server.

        Creates a new directory at the specified path on the remote server. If the
        directory already exists, the operation succeeds silently without raising
        an error.

        Args:
            directory (str): The full path of the directory to create on the
                remote server.

        Returns:
            bool: Always returns True, whether the directory was created or already
                existed.
        """
        if self.is_sftp:
            with self._connect() as sftp:
                try:
                    sftp.mkdir(directory) # type:ignore[union-attr]
                except IOError:
                    # directory might already exist
                    pass
        else:
            with self._connect() as ftp:
                try:
                    ftp.mkd(directory) # type:ignore[union-attr]
                except error_perm:
                    # directory might already exist
                    pass
        return True
