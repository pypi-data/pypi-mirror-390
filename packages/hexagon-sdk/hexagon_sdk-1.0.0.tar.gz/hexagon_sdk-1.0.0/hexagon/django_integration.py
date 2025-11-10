"""
Django integration for Hexagon SDK
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from typing import Callable


class HexagonMiddleware(MiddlewareMixin):
    """
    Django middleware for enhancing responses for AI crawlers
    
    Usage in settings.py:
        MIDDLEWARE = [
            ...
            'hexagon.DjangoMiddleware',
            ...
        ]
        
        HEXAGON_MERCHANT_ID = 'your-merchant-id'
        HEXAGON_API_KEY = 'your-api-key'
    """
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        super().__init__(get_response)
        
        # Import here to avoid circular imports
        from django.conf import settings
        from .hexagon import Hexagon
        
        # Initialize Hexagon SDK
        merchant_id = getattr(settings, 'HEXAGON_MERCHANT_ID', None)
        api_key = getattr(settings, 'HEXAGON_API_KEY', None)
        debug = getattr(settings, 'DEBUG', False)
        
        if not merchant_id or not api_key:
            raise ValueError(
                "HEXAGON_MERCHANT_ID and HEXAGON_API_KEY must be set in Django settings"
            )
        
        self.hexagon = Hexagon(
            merchant_id=merchant_id,
            api_key=api_key,
            debug=debug
        )
    
    def process_response(self, request, response: HttpResponse) -> HttpResponse:
        """Process response and enhance if needed"""
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Only enhance for AI crawlers
        if not self.hexagon._is_ai_crawler(user_agent):
            return response
        
        # Only enhance HTML responses
        content_type = response.get('Content-Type', '')
        if 'text/html' not in content_type:
            return response
        
        try:
            # Get HTML content
            html = response.content.decode('utf-8')
            
            # Enhance HTML
            enhanced = self.hexagon.enhance_html(
                html,
                url=request.build_absolute_uri(),
                user_agent=user_agent
            )
            
            # Create new response with enhanced HTML
            new_response = HttpResponse(
                enhanced,
                status=response.status_code,
                content_type=content_type
            )
            
            # Copy headers
            for header, value in response.items():
                if header.lower() not in ['content-length', 'content-type']:
                    new_response[header] = value
            
            return new_response
            
        except Exception as e:
            if self.hexagon.debug:
                print(f"[Hexagon] Error enhancing response: {str(e)}")
            return response

