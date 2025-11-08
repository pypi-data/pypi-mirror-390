"""
The Getter - Gets data from the internet, YOUR way
"""
import httpx
from .converter import to_json

class DataGetter:
    """Gets data and always returns JSON"""
    
    def data(self, url, timeout=30):
        """
        Get data from a URL, always returns JSON
        
        Args:
            url (str): The URL to fetch
            timeout (int): How long to wait in seconds (default: 30)
            
        Returns:
            dict: Clean JSON data, always. Even errors are JSON.
        """
        try:
            response = httpx.get(url, timeout=timeout, follow_redirects=True)
            
            # Check if request worked
            if response.status_code != 200:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": f"HTTP {response.status_code}: Failed to get data from {url}",
                    "url": url
                }
            
            # Get content type
            content_type = response.headers.get('content-type', 'text/plain')
            
            # Convert to JSON using our converter
            json_data = to_json(response.content, content_type)
            
            # Add metadata (but keep it clean)
            if not isinstance(json_data, dict):
                json_data = {"data": json_data}
            
            return json_data
            
        except httpx.TimeoutException:
            return {
                "error": True,
                "message": f"Request timeout after {timeout} seconds",
                "url": url
            }
        except httpx.RequestError as e:
            return {
                "error": True,
                "message": f"Network error: {str(e)}",
                "url": url
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Unexpected error: {str(e)}",
                "url": url
            }

# Create the singleton instance
get = DataGetter()
