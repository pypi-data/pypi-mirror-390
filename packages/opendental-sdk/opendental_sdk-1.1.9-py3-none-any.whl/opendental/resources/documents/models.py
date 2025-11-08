"""documents models for Open Dental SDK."""

from datetime import datetime
from typing import Optional, List
from pydantic import Field

from ...base.models import BaseModel


class Document(BaseModel):
    """Document model."""
    
    # Primary identifiers
    id: int = Field(..., alias="DocNum", description="Document number (primary key)")
    patient_num: Optional[int] = Field(None, alias="PatNum", description="Patient number")
    mount_num: Optional[int] = Field(None, alias="MountNum", description="Mount number (for mounts)")
    
    # File information
    file_name: Optional[str] = Field(None, alias="FileName", description="Document filename")
    file_path: Optional[str] = Field(None, alias="filePath", description="Full file path (empty for InDatabase storage)")
    doc_category: Optional[int] = Field(None, alias="DocCategory", description="Document category DefNum")
    doc_category_name: Optional[str] = Field(None, alias="docCategory", description="Document category name")
    
    # Basic information
    description: Optional[str] = Field(None, alias="Description", description="Document description/name")
    note: Optional[str] = Field(None, alias="Note", description="Additional notes")
    
    # Image details
    img_type: Optional[str] = Field(None, alias="ImgType", description="Document, Radiograph, Photo, File, or Attachment")
    tooth_numbers: Optional[str] = Field(None, alias="ToothNumbers", description="Comma-separated tooth numbers")
    
    # Provider and printing
    provider_num: Optional[int] = Field(None, alias="ProvNum", description="Provider number")
    print_heading: Optional[str] = Field(None, alias="PrintHeading", description="true or false - print additional info")
    
    # Timestamps
    date_created: Optional[datetime] = Field(None, alias="DateCreated", description="Date document was created")
    date_modified: Optional[datetime] = Field(None, alias="DateTStamp", description="Date document was last modified")
    server_date_time: Optional[datetime] = Field(None, alias="serverDateTime", description="Server timestamp")
    
    # File content (for upload/download)
    raw_base64: Optional[str] = Field(None, alias="RawBase64", description="Base64 encoded file content")


class UploadDocumentRequest(BaseModel):
    """Request model for uploading a document with base64 content."""
    
    # Required fields
    patient_num: int = Field(..., alias="PatNum", description="Patient number")
    raw_base64: str = Field(..., alias="RawBase64", description="Base64 encoded file content")
    extension: str = Field(..., alias="extension", description="File extension including the dot (e.g., .pdf, .jpg, .png)")
    
    # Optional fields
    description: Optional[str] = Field(None, alias="Description", description="Document description")
    date_created: Optional[str] = Field(None, alias="DateCreated", description="Date created in 'yyyy-MM-dd HH:mm:ss' format")
    doc_category: Optional[int] = Field(None, alias="DocCategory", description="Document category DefNum")
    img_type: Optional[str] = Field(None, alias="ImgType", description="Document, Radiograph, Photo, File, or Attachment")
    tooth_numbers: Optional[str] = Field(None, alias="ToothNumbers", description="Comma-separated or hyphen-separated ranges")
    provider_num: Optional[int] = Field(None, alias="ProvNum", description="Provider number")
    print_heading: Optional[str] = Field(None, alias="PrintHeading", description="true or false")


class UploadSftpRequest(BaseModel):
    """Request model for uploading a document from SFTP."""
    
    # Required fields
    patient_num: int = Field(..., alias="PatNum", description="Patient number")
    sftp_address: str = Field(..., alias="SftpAddress", description="Full SFTP path to file")
    sftp_username: str = Field(..., alias="SftpUsername", description="SFTP username")
    sftp_password: str = Field(..., alias="SftpPassword", description="SFTP password")
    
    # Optional fields
    description: Optional[str] = Field(None, alias="Description", description="Document description")
    date_created: Optional[str] = Field(None, alias="DateCreated", description="Date created in 'yyyy-MM-dd HH:mm:ss' format")
    doc_category: Optional[int] = Field(None, alias="DocCategory", description="Document category DefNum")
    img_type: Optional[str] = Field(None, alias="ImgType", description="Document, Radiograph, Photo, File, or Attachment")
    tooth_numbers: Optional[str] = Field(None, alias="ToothNumbers", description="Comma-separated or hyphen-separated ranges")
    provider_num: Optional[int] = Field(None, alias="ProvNum", description="Provider number")
    print_heading: Optional[str] = Field(None, alias="PrintHeading", description="true or false")


class SetByUrlRequest(BaseModel):
    """Request model for setting a document by URL."""
    
    # Required fields
    patient_num: int = Field(..., alias="PatNum", description="Patient number")
    url: str = Field(..., alias="url", description="URL of the document")
    
    # Optional fields
    description: Optional[str] = Field(None, alias="Description", description="Document description")
    date_created: Optional[str] = Field(None, alias="DateCreated", description="Date created in 'yyyy-MM-dd HH:mm:ss' format")
    doc_category: Optional[int] = Field(None, alias="DocCategory", description="Document category DefNum")
    img_type: Optional[str] = Field(None, alias="ImgType", description="Document, Radiograph, Photo, File, or Attachment")
    tooth_numbers: Optional[str] = Field(None, alias="ToothNumbers", description="Comma-separated or hyphen-separated ranges")
    provider_num: Optional[int] = Field(None, alias="ProvNum", description="Provider number")
    print_heading: Optional[str] = Field(None, alias="PrintHeading", description="true or false")


class DownloadSftpRequest(BaseModel):
    """Request model for downloading a document to SFTP."""
    
    # Required fields (one of DocNum or MountNum)
    doc_num: Optional[int] = Field(None, alias="DocNum", description="Document number")
    mount_num: Optional[int] = Field(None, alias="MountNum", description="Mount number")
    sftp_address: str = Field(..., alias="SftpAddress", description="Full SFTP path for destination")
    sftp_username: str = Field(..., alias="SftpUsername", description="SFTP username")
    sftp_password: str = Field(..., alias="SftpPassword", description="SFTP password")


class ThumbnailsRequest(BaseModel):
    """Request model for generating thumbnails."""
    
    # Required fields
    patient_num: int = Field(..., alias="PatNum", description="Patient number")
    sftp_address: str = Field(..., alias="SftpAddress", description="SFTP directory path")
    sftp_username: str = Field(..., alias="SftpUsername", description="SFTP username")
    sftp_password: str = Field(..., alias="SftpPassword", description="SFTP password")


class DownloadMountRequest(BaseModel):
    """Request model for downloading mount images."""
    
    # Required fields
    mount_num: int = Field(..., alias="MountNum", description="Mount number")
    sftp_address: str = Field(..., alias="SftpAddress", description="SFTP directory path")
    sftp_username: str = Field(..., alias="SftpUsername", description="SFTP username")
    sftp_password: str = Field(..., alias="SftpPassword", description="SFTP password")


class ThumbnailResponse(BaseModel):
    """Response model for thumbnail operations."""
    
    doc_num: int = Field(..., alias="DocNum", description="Document number")
    file_name: str = Field(..., alias="FileName", description="Thumbnail filename")


class UpdateDocumentRequest(BaseModel):
    """Request model for updating an existing document's Image Info."""
    
    # All fields are optional for updates
    description: Optional[str] = Field(None, alias="Description", description="Document description")
    date_created: Optional[str] = Field(None, alias="DateCreated", description="Date created in 'yyyy-MM-dd HH:mm:ss' format")
    doc_category: Optional[int] = Field(None, alias="DocCategory", description="Document category DefNum")
    img_type: Optional[str] = Field(None, alias="ImgType", description="Document, Radiograph, Photo, File, or Attachment")
    tooth_numbers: Optional[str] = Field(None, alias="ToothNumbers", description="Comma-separated or hyphen-separated ranges")
    provider_num: Optional[int] = Field(None, alias="ProvNum", description="Provider number")
    print_heading: Optional[str] = Field(None, alias="PrintHeading", description="true or false")
