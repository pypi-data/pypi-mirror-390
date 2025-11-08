"""documents resource module."""

from .client import DocumentsClient
from .models import (
    Document,
    UploadDocumentRequest,
    UploadSftpRequest,
    SetByUrlRequest,
    DownloadSftpRequest,
    ThumbnailsRequest,
    DownloadMountRequest,
    ThumbnailResponse,
    UpdateDocumentRequest,
)

__all__ = [
    "DocumentsClient",
    "Document",
    "UploadDocumentRequest",
    "UploadSftpRequest",
    "SetByUrlRequest",
    "DownloadSftpRequest",
    "ThumbnailsRequest",
    "DownloadMountRequest",
    "ThumbnailResponse",
    "UpdateDocumentRequest",
]
