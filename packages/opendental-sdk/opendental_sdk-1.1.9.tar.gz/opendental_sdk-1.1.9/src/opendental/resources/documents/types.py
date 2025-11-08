"""document types and enums for Open Dental SDK."""

from enum import Enum


class ImageType(str, Enum):
    """Image type enum for documents."""
    DOCUMENT = "Document"
    RADIOGRAPH = "Radiograph"
    PHOTO = "Photo"
    FILE = "File"
    ATTACHMENT = "Attachment"
