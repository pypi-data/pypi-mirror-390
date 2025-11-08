"""
Photo and media management API endpoints.
"""

from typing import List, Dict, Any, Optional
from ..models.media import Photo, Album


class MediaAPI:
    """
    Photo and media management endpoints.
    """
    
    def __init__(self, http_client, state: Optional[Any] = None):
        """
        Initialize Media API.
        
        Args:
            http_client: HTTP client instance
            state: InterpalState instance for object caching
        """
        self.http = http_client
        self._state = state
    
    def upload_photo(
        self,
        file_path: str,
        caption: Optional[str] = None,
        album_id: Optional[str] = None,
    ) -> Photo:
        """
        Upload a photo.
        
        Args:
            file_path: Path to the photo file
            caption: Photo caption
            album_id: Album ID to add photo to
            
        Returns:
            Photo object
        """
        with open(file_path, 'rb') as f:
            files = {'photo': f}
            data = {}
            
            if caption:
                data['caption'] = caption
            if album_id:
                data['album_id'] = album_id
            
            response = self.http.post("/v1/photo", data=data, files=files)
            if self._state:
                return self._state.create_photo(response)
            return Photo(state=self._state, data=response)
    
    def get_photo(self, photo_id: str) -> Photo:
        """
        Get photo details.
        
        Args:
            photo_id: Photo ID
            
        Returns:
            Photo object
        """
        data = self.http.get(f"/v1/photo/{photo_id}")
        if self._state:
            return self._state.create_photo(data)
        return Photo(state=self._state, data=data)
    
    def delete_photo(self, photo_id: str) -> Dict[str, Any]:
        """
        Delete a photo.
        
        Args:
            photo_id: Photo ID to delete
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/photo/{photo_id}")
    
    def get_user_photos(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Photo]:
        """
        Get photos for a user.
        
        Args:
            user_id: User ID
            limit: Maximum photos
            offset: Pagination offset
            
        Returns:
            List of Photo objects
        """
        params = {"limit": limit, "offset": offset}
        data = self.http.get(f"/v1/user/{user_id}/photos", params=params)
        
        if isinstance(data, list):
            if self._state:
                return [self._state.create_photo(photo) for photo in data]
            return [Photo(state=self._state, data=photo) for photo in data]
        elif isinstance(data, dict) and "photos" in data:
            if self._state:
                return [self._state.create_photo(photo) for photo in data["photos"]]
            return [Photo(state=self._state, data=photo) for photo in data["photos"]]
        return []
    
    def get_album(self, album_id: str) -> Album:
        """
        Get album details.
        
        Args:
            album_id: Album ID
            
        Returns:
            Album object
        """
        data = self.http.get(f"/v1/album/{album_id}")
        if self._state:
            return self._state.create_album(data)
        return Album(state=self._state, data=data)
    
    def get_user_albums(self, user_id: str) -> List[Album]:
        """
        Get albums for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Album objects
        """
        data = self.http.get(f"/v1/user/{user_id}/albums")
        
        if isinstance(data, list):
            if self._state:
                return [self._state.create_album(album) for album in data]
            return [Album(state=self._state, data=album) for album in data]
        elif isinstance(data, dict) and "albums" in data:
            if self._state:
                return [self._state.create_album(album) for album in data["albums"]]
            return [Album(state=self._state, data=album) for album in data["albums"]]
        return []
    
    def create_album(self, name: str, description: Optional[str] = None) -> Album:
        """
        Create a new album.
        
        Args:
            name: Album name
            description: Album description
            
        Returns:
            Album object
        """
        data = {"name": name}
        if description:
            data["description"] = description
        
        response = self.http.post("/v1/album", data=data)
        if self._state:
            return self._state.create_album(response)
        return Album(state=self._state, data=response)
    
    def update_album(
        self,
        album_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Album:
        """
        Update an album.
        
        Args:
            album_id: Album ID
            name: New album name
            description: New album description
            
        Returns:
            Updated Album object
        """
        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        
        response = self.http.put(f"/v1/album/{album_id}", data=data)
        if self._state:
            return self._state.create_album(response)
        return Album(state=self._state, data=response)
    
    def delete_album(self, album_id: str) -> Dict[str, Any]:
        """
        Delete an album.
        
        Args:
            album_id: Album ID to delete
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/album/{album_id}")
    
    def get_photo_count(self, user_id: str) -> int:
        """
        Get total photo count for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total photo count
        """
        data = self.http.get(f"/v1/total/{user_id}/photos")
        
        if isinstance(data, dict):
            return data.get("total", data.get("count", 0))
        elif isinstance(data, int):
            return data
        return 0
    
    def get_upload_status(self, upload_token: str) -> Dict[str, Any]:
        """
        Check the status of a photo upload.
        
        Args:
            upload_token: Upload token/JWT returned from upload initiation
            
        Returns:
            Upload status information
        """
        return self.http.get(f"/v1/upload-status/{upload_token}")
    
    def upload_photo_async(
        self,
        file_path: str,
        caption: Optional[str] = None,
        album_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a photo asynchronously (returns upload token for status checking).
        
        Args:
            file_path: Path to the photo file
            caption: Photo caption
            album_id: Album ID to add photo to
            
        Returns:
            Upload initiation response with token
        """
        with open(file_path, 'rb') as f:
            files = {'photo': f}
            data = {'async': True}
            
            if caption:
                data['caption'] = caption
            if album_id:
                data['album_id'] = album_id
            
            response = self.http.post("/v1/photo", data=data, files=files)
            return response
    
    def upload_photo_with_token(
        self,
        file_path: str,
        use_token: bool = True
    ) -> Dict[str, Any]:
        """
        Upload a photo and get an upload token.
        
        Args:
            file_path: Path to the photo file
            use_token: Whether to use token-based upload (default: True)
            
        Returns:
            Response with token field
            Example: {"token": "eyJhbGc..."}
        """
        import os
        import mimetypes
        from requests_toolbelt.multipart.encoder import MultipartEncoder
        
        # Get filename and detect content type
        filename = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Create multipart encoder with file and use_token fields
        multipart_data = MultipartEncoder(
            fields={
                'file': (filename, open(file_path, 'rb'), content_type),
                'use_token': 'true' if use_token else 'false'
            }
        )
        
        # Post with multipart content type header
        response = self.http.post(
            "/v1/photo",
            data=multipart_data,
            headers={'Content-Type': multipart_data.content_type}
        )
        
        return response
    
    def send_photo_message(
        self,
        thread_id: str,
        file_path: Optional[str] = None,
        image_url: Optional[str] = None,
        tmp_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a photo and send it as a message in a thread.
        
        This method handles the complete flow:
        1. Download image if URL provided, or use local file
        2. Upload photo to get token
        3. Check upload status to get photo ID
        4. Send message with photo attachment
        
        Args:
            thread_id: Thread ID to send the photo to
            file_path: Path to the local photo file (optional if image_url provided)
            image_url: URL of the image to download and send (optional if file_path provided)
            tmp_id: Temporary ID for the message (optional, auto-generated if not provided)
            
        Returns:
            Dictionary with message data including:
            - id: Message ID
            - thread_id: Thread ID
            - sender_id: Sender's user ID
            - created: Timestamp
            - fake_id: Temporary fake ID
            - tmp_id: Temporary ID
            - attachments: List of attachment objects with photo data
            
        Example:
            >>> # Send from local file
            >>> response = client.media.send_photo_message(
            ...     thread_id="1445991291881700208",
            ...     file_path="path/to/image.jpg"
            ... )
            >>> 
            >>> # Send from URL
            >>> response = client.media.send_photo_message(
            ...     thread_id="1445991291881700208",
            ...     image_url="https://example.com/image.jpg"
            ... )
            >>> print(f"Message ID: {response['id']}")
            >>> photo = response['attachments'][0]['photo']
            >>> print(f"Photo URL: {photo['url']}")
        """
        import time
        import random
        import string
        import os
        import tempfile
        import requests
        
        # Validate that either file_path or image_url is provided
        if not file_path and not image_url:
            raise ValueError("Either file_path or image_url must be provided")
        
        if file_path and image_url:
            raise ValueError("Provide either file_path or image_url, not both")
        
        # Handle image URL - download to temporary file
        temp_file = None
        try:
            if image_url:
                # Download image from URL
                response = requests.get(image_url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Get file extension from URL or content-type
                ext = os.path.splitext(image_url)[1]
                if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    # Try to get from content-type
                    content_type = response.headers.get('content-type', '')
                    ext_map = {
                        'image/jpeg': '.jpg',
                        'image/png': '.png',
                        'image/gif': '.gif',
                        'image/webp': '.webp'
                    }
                    ext = ext_map.get(content_type, '.jpg')
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file.close()
                
                # Use the temporary file path
                file_path = temp_file.name
            
            # Step 1: Upload photo and get token
            upload_response = self.upload_photo_with_token(file_path)
            token = upload_response.get('token')
            
            if not token:
                raise ValueError("Failed to get upload token from response")
            
            # Step 2: Check upload status to get photo ID
            status_response = self.get_upload_status(token)
            
            # Check if upload was successful
            if status_response.get('status') != 'success':
                raise ValueError(f"Photo upload failed with status: {status_response.get('status')}")
            
            # Extract photo data from payload
            payload = status_response.get('payload')
            if not payload or not payload.get('id'):
                raise ValueError("Failed to get photo ID from upload status")
            
            photo_id = payload.get('id')
            
            # Generate tmp_id if not provided (4 character random string)
            if not tmp_id:
                tmp_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            
            # Step 3: Send message with photo attachment
            data = {
                'thread_id': thread_id,
                'attachment_type': 'photo',
                'attachment_id': photo_id,
                'tmp_id': tmp_id
            }
            
            # Return raw response dict (contains fake_id, tmp_id, and rich attachment data)
            response = self.http.post("/v1/message", data=data)
            return response
            
        finally:
            # Clean up temporary file if it was created
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception:
                    pass  # Ignore cleanup errors

