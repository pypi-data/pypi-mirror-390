"""documents client for Open Dental SDK."""

from typing import List, Optional, Union
from ...base.resource import BaseResource
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


class DocumentsClient(BaseResource):
    """Client for managing documents in Open Dental."""
    
    def __init__(self, client):
        """Initialize the documents client."""
        super().__init__(client, "documents")
    
    def get(self, doc_num: Union[int, str]) -> Document:
        """
        Get a single document by DocNum.
        
        Args:
            doc_num: Document number
            
        Returns:
            Document object (without the actual file content)
        """
        doc_num = self._validate_id(doc_num)
        endpoint = self._build_endpoint(doc_num)
        response = self._get(endpoint)
        return self._handle_response(response, Document)
    
    def list_by_patient(self, patient_num: int) -> List[Document]:
        """
        Get all documents and mounts for a patient.
        
        Args:
            patient_num: Patient number
            
        Returns:
            List of Document objects (without the actual file content)
        """
        endpoint = self._build_endpoint()
        params = {"PatNum": patient_num}
        response = self._get(endpoint, params=params)
        
        if isinstance(response, list):
            return [Document(**item) for item in response]
        return []
    
    def upload(self, request: UploadDocumentRequest) -> Document:
        """
        Upload a document with base64 encoded content.
        
        Args:
            request: UploadDocumentRequest with patient_num, raw_base64, extension (required), 
                    and optional fields like doc_category, img_type, etc.
            
        Returns:
            Created Document object
            
        Example:
            >>> request = UploadDocumentRequest(
            ...     patient_num=101,
            ...     raw_base64="base64content==",
            ...     extension=".pdf",  # Required!
            ...     description="Patient Report",
            ...     doc_category=14
            ... )
            >>> document = client.documents.upload(request)
        """
        endpoint = self._build_endpoint("Upload")
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, Document)
    
    def upload_sftp(self, request: UploadSftpRequest) -> Document:
        """
        Upload a document from an SFTP site.
        Prior to calling this, upload the file to your SFTP site first.
        
        Args:
            request: UploadSftpRequest with SFTP credentials and file path
            
        Returns:
            Created Document object with file path information
        """
        endpoint = self._build_endpoint("UploadSftp")
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, Document)
    
    def set_by_url(self, request: SetByUrlRequest) -> Document:
        """
        Create a document reference by URL.
        The URL is stored in the database and downloaded when the user clicks on it.
        
        Args:
            request: SetByUrlRequest with patient_num, url, and optional fields
            
        Returns:
            Created Document object
        """
        endpoint = self._build_endpoint("SetByUrl")
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, Document)
    
    def download_sftp(self, request: DownloadSftpRequest) -> str:
        """
        Download a document or mount to an SFTP site.
        After calling this, download the file from your SFTP site.
        
        Args:
            request: DownloadSftpRequest with doc_num or mount_num and SFTP credentials
            
        Returns:
            Full filepath of the saved file on SFTP
        """
        endpoint = self._build_endpoint("DownloadSftp")
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._post(endpoint, json_data=data)
        
        if isinstance(response, dict) and "location" in response:
            return response["location"]
        return str(response) if response else ""
    
    def generate_thumbnails(self, request: ThumbnailsRequest) -> List[ThumbnailResponse]:
        """
        Generate thumbnails for all images for a patient.
        Thumbnails are placed on the specified SFTP site.
        
        Args:
            request: ThumbnailsRequest with patient_num and SFTP credentials
            
        Returns:
            List of ThumbnailResponse objects with DocNum and FileName
        """
        endpoint = self._build_endpoint("Thumbnails")
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._post(endpoint, json_data=data)
        
        if isinstance(response, list):
            return [ThumbnailResponse(**item) for item in response]
        return []
    
    def download_mount(self, request: DownloadMountRequest) -> List[ThumbnailResponse]:
        """
        Download all individual images from a mount to SFTP.
        Note: This returns individual images, not the composite mount.
        Use download_sftp() instead if you want the composite mount image.
        
        Args:
            request: DownloadMountRequest with mount_num and SFTP credentials
            
        Returns:
            List of downloaded image info with DocNum and FileName
        """
        endpoint = self._build_endpoint("DownloadMount")
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._post(endpoint, json_data=data)
        
        if isinstance(response, list):
            return [ThumbnailResponse(**item) for item in response]
        return []
    
    def update(self, doc_num: Union[int, str], request: UpdateDocumentRequest) -> Document:
        """
        Update Image Info of an existing document.
        
        Args:
            doc_num: Document number
            request: UpdateDocumentRequest with fields to update
            
        Returns:
            Updated Document object
        """
        doc_num = self._validate_id(doc_num)
        endpoint = self._build_endpoint(doc_num)
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, Document)
    
    def delete(self, doc_num: Union[int, str]) -> bool:
        """
        Delete a document (both database row and file).
        
        Args:
            doc_num: Document number
            
        Returns:
            True if successful
        """
        doc_num = self._validate_id(doc_num)
        endpoint = self._build_endpoint(doc_num)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
