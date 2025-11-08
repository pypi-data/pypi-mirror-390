"""
Hypz SDK for Python
A Python client library for interacting with the Hypz file storage API.

Author: Hypz Team
License: MIT
"""

import requests
import os
import json
from typing import Optional, Dict, List, Any, BinaryIO, Union
from pathlib import Path


class HypzError(Exception):
    """Base exception for Hypz SDK errors."""
    pass


class HypzClient:
    """
    Main client for interacting with the Hypz API.
    
    Example:
        >>> client = HypzClient(api_key='your_api_key_here')
        >>> buckets = client.buckets.list()
        >>> for bucket in buckets:
        ...     print(bucket['name'])
    """
    
    def __init__(self, api_key: str, base_url: str = 'http://localhost:5000/api/v1'):
        """
        Initialize the Hypz client.
        
        Args:
            api_key: Your Hypz API key
            base_url: Base URL of the Hypz API (default: http://localhost:5000/api/v1)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Accept': 'application/json'
        })
        
        # Initialize resource managers
        self.buckets = BucketManager(self)
        self.files = FileManager(self)
        self.usage = UsageManager(self)
        self.plans = PlanManager(self)
        self.api_keys = APIKeyManager(self)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (will be appended to base_url)
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response data as dictionary
            
        Raises:
            HypzError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204:
                return {'success': True}
            
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get('message', str(e))
            except:
                error_message = str(e)
            raise HypzError(f"API Error: {error_message}")
        except requests.exceptions.RequestException as e:
            raise HypzError(f"Request failed: {str(e)}")


class BucketManager:
    """Manager for bucket operations."""
    
    def __init__(self, client: HypzClient):
        self.client = client
    
    def create(self, name: str, description: str = '', visibility: str = 'private') -> Dict[str, Any]:
        """
        Create a new bucket.
        
        Args:
            name: Bucket name
            description: Bucket description (optional)
            visibility: 'public' or 'private' (default: 'private')
            
        Returns:
            Created bucket data
        """
        data = {
            'name': name,
            'description': description,
            'visibility': visibility
        }
        response = self.client._request('POST', '/buckets', json=data)
        return response.get('data', response)
    
    def list(self, page: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List all buckets.
        
        Args:
            page: Page number (default: 1)
            limit: Items per page (default: 10)
            
        Returns:
            List of buckets
        """
        params = {'page': page, 'limit': limit}
        response = self.client._request('GET', '/buckets', params=params)
        return response.get('data', {}).get('buckets', [])
    
    def get(self, bucket_id: str) -> Dict[str, Any]:
        """
        Get bucket details.
        
        Args:
            bucket_id: Bucket ID
            
        Returns:
            Bucket data
        """
        response = self.client._request('GET', f'/buckets/{bucket_id}')
        return response.get('data', response)
    
    def update(self, bucket_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a bucket.
        
        Args:
            bucket_id: Bucket ID
            **kwargs: Fields to update (name, description, visibility)
            
        Returns:
            Updated bucket data
        """
        response = self.client._request('PUT', f'/buckets/{bucket_id}', json=kwargs)
        return response.get('data', response)
    
    def delete(self, bucket_id: str) -> bool:
        """
        Delete a bucket.
        
        Args:
            bucket_id: Bucket ID
            
        Returns:
            True if successful
        """
        self.client._request('DELETE', f'/buckets/{bucket_id}')
        return True
    
    def stats(self, bucket_id: str) -> Dict[str, Any]:
        """
        Get bucket statistics.
        
        Args:
            bucket_id: Bucket ID
            
        Returns:
            Bucket statistics
        """
        response = self.client._request('GET', f'/buckets/{bucket_id}/stats')
        return response.get('data', response)


class FileManager:
    """Manager for file operations."""
    
    def __init__(self, client: HypzClient):
        self.client = client
    
    def upload(
        self,
        bucket_id: str,
        file_path: Optional[str] = None,
        file_data: Optional[BinaryIO] = None,
        filename: Optional[str] = None,
        is_public: bool = False,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to a bucket.
        
        Args:
            bucket_id: Bucket ID to upload to
            file_path: Path to file (either this or file_data required)
            file_data: File-like object (either this or file_path required)
            filename: Filename to use (required if using file_data)
            is_public: Whether file should be public (default: False)
            tags: List of tags (optional)
            metadata: Additional metadata (optional)
            progress_callback: Callback function for upload progress
            
        Returns:
            Uploaded file data
            
        Example:
            >>> # Upload from file path
            >>> client.files.upload('bucket123', file_path='./image.png')
            
            >>> # Upload from file object with progress
            >>> def progress(current, total):
            ...     print(f"Progress: {current}/{total} bytes")
            >>> with open('file.pdf', 'rb') as f:
            ...     client.files.upload('bucket123', file_data=f, filename='file.pdf', 
            ...                        progress_callback=progress)
        """
        if not file_path and not file_data:
            raise ValueError("Either file_path or file_data must be provided")
        
        if file_data and not filename:
            raise ValueError("filename must be provided when using file_data")
        
        # Open file if path provided
        if file_path:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            file_data = open(file_path, 'rb')
            filename = filename or file_path.name
        
        try:
            # Prepare form data
            files = {'file': (filename, file_data)}
            data = {}
            
            if tags:
                data['tags'] = json.dumps(tags)
            if metadata:
                data['metadata'] = json.dumps(metadata)
            
            # Make request
            response = self.client._request(
                'POST',
                f'/files/{bucket_id}/upload',
                files=files,
                data=data
            )
            return response.get('data', response)
        finally:
            # Close file if we opened it
            if file_path:
                file_data.close()
    
    def list(self, bucket_id: str, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List files in a bucket.
        
        Args:
            bucket_id: Bucket ID
            page: Page number (default: 1)
            limit: Items per page (default: 20)
            
        Returns:
            List of files
        """
        params = {'page': page, 'limit': limit}
        response = self.client._request('GET', f'/files/{bucket_id}/files', params=params)
        return response.get('data', {}).get('files', [])
    
    def get(self, file_id: str) -> Dict[str, Any]:
        """
        Get file details.
        
        Args:
            file_id: File ID
            
        Returns:
            File data
        """
        response = self.client._request('GET', f'/files/file/{file_id}')
        return response.get('data', response)
    
    def download(self, file_id: str, save_path: Optional[str] = None) -> Union[bytes, str]:
        """
        Download a file.
        
        Args:
            file_id: File ID
            save_path: Path to save file (optional, returns bytes if not provided)
            
        Returns:
            File path if save_path provided, otherwise file bytes
        """
        url = f"{self.client.base_url}/files/file/{file_id}/download"
        response = self.client.session.get(url, stream=True)
        response.raise_for_status()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return str(save_path)
        else:
            return response.content
    
    def delete(self, file_id: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_id: File ID
            
        Returns:
            True if successful
        """
        self.client._request('DELETE', f'/files/file/{file_id}')
        return True
    
    def update(self, file_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update file metadata.
        
        Args:
            file_id: File ID
            **kwargs: Fields to update (tags, metadata, is_public)
            
        Returns:
            Updated file data
        """
        response = self.client._request('PATCH', f'/files/file/{file_id}', json=kwargs)
        return response.get('data', response)
    
    def create_signed_url(self, file_id: str, expires_in: int = 3600) -> Dict[str, Any]:
        """
        Generate a signed URL for temporary file access (max 7 days = 604800 seconds).
        
        Args:
            file_id: File ID
            expires_in: Expiry time in seconds (max 604800 = 7 days)
            
        Returns:
            Signed URL data with url, expiresAt, expiresIn
        """
        # Cap at 7 days
        expires_in = min(max(1, int(expires_in)), 604800)
        response = self.client._request(
            'POST',
            f'/files/file/{file_id}/signed-url',
            json={'expiresIn': expires_in}
        )
        return response.get('data', response)
    
    def bulk_delete(self, file_ids: List[Union[int, str]]) -> Dict[str, Any]:
        """
        Delete multiple files at once (max 100 files).
        
        Args:
            file_ids: List of file IDs
            
        Returns:
            Result with deletedCount, totalSize, etc.
        """
        if not file_ids or not isinstance(file_ids, list):
            raise ValueError("file_ids must be a non-empty list")
        if len(file_ids) > 100:
            raise ValueError("Maximum 100 files can be deleted at once")
        
        response = self.client._request('POST', '/files/bulk/delete', json={'fileIds': file_ids})
        return response.get('data', response)

    def initiate_presigned_upload(
        self,
        bucket_id: str,
        file_name: str,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate a direct-to-B2 presigned upload.

        Args:
            bucket_id: Target bucket ID
            file_name: Name of the file to upload
            file_size: Optional file size in bytes
            mime_type: Optional MIME type (defaults to application/octet-stream)
            tags: Optional list of tags
            metadata: Optional metadata dictionary

        Returns:
            Presigned upload payload containing uploadUrl, uploadAuthToken, fileId, etc.
        """
        if not bucket_id:
            raise ValueError('bucket_id is required')
        if not file_name:
            raise ValueError('file_name is required')

        payload: Dict[str, Any] = {
            'filename': file_name,
            'mimeType': mime_type or 'application/octet-stream',
            'size': file_size,
            'tags': tags,
            'metadata': metadata
        }

        # Remove empty values to avoid sending nulls
        cleaned_payload = {k: v for k, v in payload.items() if v is not None}

        response = self.client._request(
            'POST',
            f'/files/{bucket_id}/files/presigned',
            json=cleaned_payload
        )
        return response.get('data', response)

    def complete_presigned_upload(
        self,
        file_id: Union[int, str],
        b2_file_id: Optional[str] = None,
        final_size: Optional[int] = None,
        sha1: Optional[str] = None,
        part_count: Optional[int] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a presigned upload after the file has been uploaded to B2.

        Args:
            file_id: The temporary file ID received from initiate_presigned_upload
            b2_file_id: Required Backblaze file ID returned by the upload step
            final_size: Optional final file size in bytes (recommended)
            sha1: Optional SHA1 checksum if available
            part_count: Optional number of uploaded parts for multipart uploads
            tags: Optional list of tags to store with the file
            metadata: Optional metadata dictionary to persist with the file

        Returns:
            Finalized file metadata from the Hypz API.
        """
        if not file_id:
            raise ValueError('file_id is required')

        if not b2_file_id:
            raise ValueError('b2_file_id is required to complete presigned uploads')

        payload: Dict[str, Any] = {
            'b2FileId': b2_file_id,
            'finalSize': final_size,
            'sha1': sha1,
            'partCount': part_count,
            'tags': tags,
            'metadata': metadata
        }

        cleaned_payload = {k: v for k, v in payload.items() if v is not None}

        request_kwargs: Dict[str, Any] = {}
        if cleaned_payload:
            request_kwargs['json'] = cleaned_payload

        response = self.client._request(
            'POST',
            f'/files/file/{file_id}/complete',
            **request_kwargs
        )
        return response.get('data', response)
    
    def bulk_update(self, file_ids: List[Union[int, str]], tags: Optional[List[str]] = None, 
                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update multiple files at once (max 100 files).
        Note: Cannot change file visibility - it's inherited from bucket.
        
        Args:
            file_ids: List of file IDs
            tags: Tags to set for all files
            metadata: Metadata to set for all files
            
        Returns:
            Result with updatedCount
        """
        if not file_ids or not isinstance(file_ids, list):
            raise ValueError("file_ids must be a non-empty list")
        if len(file_ids) > 100:
            raise ValueError("Maximum 100 files can be updated at once")
        
        data = {'fileIds': file_ids}
        if tags:
            data['tags'] = tags
        if metadata:
            data['metadata'] = metadata
            
        response = self.client._request('POST', '/files/bulk/update', json=data)
        return response.get('data', response)
    
    def bulk_download(self, file_ids: List[Union[int, str]]) -> Dict[str, Any]:
        """
        Get download URLs for multiple files (max 50 files).
        
        Args:
            file_ids: List of file IDs
            
        Returns:
            Result with files list containing download URLs
        """
        if not file_ids or not isinstance(file_ids, list):
            raise ValueError("file_ids must be a non-empty list")
        if len(file_ids) > 50:
            raise ValueError("Maximum 50 files can be downloaded at once")
        
        response = self.client._request('POST', '/files/bulk/download', json={'fileIds': file_ids})
        return response.get('data', response)
    
    def bulk_move(self, file_ids: List[Union[int, str]], target_bucket_id: str) -> Dict[str, Any]:
        """
        Move multiple files to another bucket (max 100 files).
        
        Args:
            file_ids: List of file IDs
            target_bucket_id: Target bucket ID
            
        Returns:
            Result with movedCount
        """
        if not file_ids or not isinstance(file_ids, list):
            raise ValueError("file_ids must be a non-empty list")
        if not target_bucket_id:
            raise ValueError("target_bucket_id is required")
        if len(file_ids) > 100:
            raise ValueError("Maximum 100 files can be moved at once")
        
        response = self.client._request('POST', '/files/bulk/move', 
                                        json={'fileIds': file_ids, 'targetBucketId': target_bucket_id})
        return response.get('data', response)


class APIKeyManager:
    """Manager for API key operations."""
    
    def __init__(self, client: HypzClient):
        self.client = client
    
    def create(self, name: str, permissions: List[str], expires_at: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new API key.
        
        Args:
            name: API key name
            permissions: List of permissions (e.g., ['files:read', 'files:write'])
            expires_at: Optional expiry date (ISO format)
            
        Returns:
            Created API key data
        """
        data = {'name': name, 'permissions': permissions}
        if expires_at:
            data['expiresAt'] = expires_at
        response = self.client._request('POST', '/api-keys', json=data)
        return response.get('data', response)
    
    def list(self) -> List[Dict[str, Any]]:
        """List all API keys."""
        response = self.client._request('GET', '/api-keys')
        return response.get('data', [])
    
    def get(self, key_id: str) -> Dict[str, Any]:
        """Get API key details."""
        response = self.client._request('GET', f'/api-keys/{key_id}')
        return response.get('data', response)
    
    def update(self, key_id: str, **kwargs) -> Dict[str, Any]:
        """Update API key."""
        response = self.client._request('PUT', f'/api-keys/{key_id}', json=kwargs)
        return response.get('data', response)
    
    def delete(self, key_id: str) -> bool:
        """Delete/revoke API key."""
        self.client._request('DELETE', f'/api-keys/{key_id}')
        return True
    
    def revoke(self, key_id: str) -> bool:
        """Revoke API key (alias for delete)."""
        return self.delete(key_id)
    
    def regenerate(self, key_id: str) -> Dict[str, Any]:
        """Regenerate API key."""
        response = self.client._request('POST', f'/api-keys/{key_id}/regenerate')
        return response.get('data', response)


class UsageManager:
    """Manager for usage tracking and analytics."""
    
    def __init__(self, client: HypzClient):
        self.client = client
    
    def current(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        response = self.client._request('GET', '/usage/current')
        return response.get('data', response)
    
    def history(self, days: Optional[int] = None) -> Dict[str, Any]:
        """Get usage history."""
        params = {'days': days} if days else {}
        response = self.client._request('GET', '/usage/history', params=params)
        return response.get('data', response)
    
    def analytics(self) -> Dict[str, Any]:
        """Get usage analytics."""
        response = self.client._request('GET', '/usage/analytics')
        return response.get('data', response)


class PlanManager:
    """Manager for subscription plans."""
    
    def __init__(self, client: HypzClient):
        self.client = client
    
    def list(self) -> List[Dict[str, Any]]:
        """List all available plans."""
        response = self.client._request('GET', '/plans')
        return response.get('data', [])
    
    def get(self, plan_id: str) -> Dict[str, Any]:
        """Get plan details."""
        response = self.client._request('GET', f'/plans/{plan_id}')
        return response.get('data', response)
    
    def get_user_plan(self) -> Dict[str, Any]:
        """Get current user's plan."""
        response = self.client._request('GET', '/plans/user/current')
        return response.get('data', response)
    
    def update_user_plan(self, plan_id: str) -> Dict[str, Any]:
        """Update user's plan."""
        response = self.client._request('PUT', '/plans/user/update', json={'planId': plan_id})
        return response.get('data', response)


class NotificationManager:
    """Manager for notifications."""
    
    def __init__(self, client: HypzClient):
        self.client = client
    
    def list(self, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """List user notifications."""
        params = {'page': page, 'limit': limit}
        response = self.client._request('GET', '/notifications', params=params)
        return response.get('data', [])
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read."""
        self.client._request('PUT', f'/notifications/{notification_id}/read')
        return True
    
    def mark_all_as_read(self) -> bool:
        """Mark all notifications as read."""
        self.client._request('PUT', '/notifications/read-all')
        return True
    
    def delete(self, notification_id: str) -> bool:
        """Delete notification."""
        self.client._request('DELETE', f'/notifications/{notification_id}')
        return True


class UserManager:
    """Manager for user profile operations."""
    
    def __init__(self, client: HypzClient):
        self.client = client
    
    def get_profile(self) -> Dict[str, Any]:
        """Get user profile."""
        response = self.client._request('GET', '/user/profile')
        return response.get('data', response)
    
    def update_profile(self, **kwargs) -> Dict[str, Any]:
        """Update user profile."""
        response = self.client._request('PUT', '/user/profile', json=kwargs)
        return response.get('data', response)
    
    def change_password(self, current_password: str, new_password: str) -> bool:
        """Change password."""
        self.client._request('PUT', '/user/change-password', 
                           json={'currentPassword': current_password, 'newPassword': new_password})
        return True
    
    def get_notification_preferences(self) -> Dict[str, Any]:
        """Get notification preferences."""
        response = self.client._request('GET', '/user/notifications')
        return response.get('data', response)
    
    def update_notification_preferences(self, **kwargs) -> Dict[str, Any]:
        """Update notification preferences."""
        response = self.client._request('PUT', '/user/notifications', json=kwargs)
        return response.get('data', response)
    
    def delete_account(self, password: str) -> bool:
        """Delete user account."""
        self.client._request('DELETE', '/user/account', json={'password': password})
        return True


# Convenience functions
def create_client(api_key: str, base_url: str = 'http://localhost:5000/api/v1') -> HypzClient:
    """
    Create a Hypz client instance.
    
    Args:
        api_key: Your Hypz API key
        base_url: Base URL of the Hypz API
        
    Returns:
        HypzClient instance
    """
    return HypzClient(api_key, base_url)


if __name__ == '__main__':
    # Example usage
    print("Hypz Python SDK")
    print("===============")
    print("\nQuick Start:")
    print("  from hypz import HypzClient")
    print("  client = HypzClient(api_key='your_api_key_here')")
    print("  buckets = client.buckets.list()")
    print("  client.files.upload('bucket_id', file_path='./file.png')")
