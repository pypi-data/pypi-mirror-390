"""FTP and SFTP client wrappers for file transfer operations."""

from ..core.require_extra import require_extra

__all__ = ("client",)

require_extra("ftp", "paramiko", "dateutil")
