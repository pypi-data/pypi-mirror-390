"""
Core Hexagon SDK Class
"""

import requests
import hashlib
from typing import Optional, Dict, Any
from functools import wraps


class Hexagon:
    """
    Main Hexagon SDK class for Python applications
    """
    
    def __init__(
        self,
        merchant_id: str,
        api_key: str,
        api_url: str = "https://joinhexagon.com/api/v1",
        debug: bool = False
    ):
        """
        Initialize Hexagon SDK
        
        Args:
            merchant_id: Your Hexagon merchant ID
            api_key: Your Hexagon API key
            api_url: Hexagon API base URL (default: production)
            debug: Enable debug logging
        """
        if not merchant_id:
            raise ValueError("merchant_id is required")
        if not api_key:
            raise ValueError("api_key is required")
            
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.debug = debug
        self._cache: Dict[str, str] = {}  # Simple in-memory cache
    
    def _is_ai_crawler(self, user_agent: str) -> bool:
        """Detect if request is from an AI crawler"""
        if not user_agent:
            return False
            
        ai_crawlers = [
            'gptbot', 'chatgpt', 'claude', 'anthropic',
            'perplexity', 'cohere', 'bingbot', 'googlebot'
        ]
        user_agent_lower = user_agent.lower()
        return any(bot in user_agent_lower for bot in ai_crawlers)
    
    def _get_cache_key(self, html: str) -> str:
        """Generate cache key from HTML content"""
        return hashlib.md5(html.encode()).hexdigest()
    
    def enhance_html(
        self,
        html: str,
        url: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Enhance HTML for AI crawlers
        
        Args:
            html: The HTML content to enhance
            url: The URL of the page (optional)
            user_agent: User agent string (optional)
            
        Returns:
            Enhanced HTML string
        """
        # Only enhance for AI crawlers
        if user_agent and not self._is_ai_crawler(user_agent):
            return html
        
        # Check cache
        cache_key = self._get_cache_key(html)
        if cache_key in self._cache:
            if self.debug:
                print(f"[Hexagon] Using cached enhanced HTML")
            return self._cache[cache_key]
        
        try:
            # Call Hexagon API to enhance HTML
            response = requests.post(
                f"{self.api_url}/sdk/enhance-html",
                json={
                    "html": html,
                    "url": url,
                    "merchantId": self.merchant_id
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=5  # 5 second timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                enhanced_html = data.get('data', {}).get('html', html)
                
                # Cache the result
                self._cache[cache_key] = enhanced_html
                
                if self.debug:
                    print(f"[Hexagon] HTML enhanced successfully")
                    
                return enhanced_html
            else:
                if self.debug:
                    print(f"[Hexagon] API error: {response.status_code}")
                return html
                
        except requests.exceptions.Timeout:
            if self.debug:
                print("[Hexagon] API timeout, returning original HTML")
            return html
        except Exception as e:
            if self.debug:
                print(f"[Hexagon] Error: {str(e)}")
            return html
    
    def enhance(self, func):
        """
        Decorator to enhance Flask route responses for AI crawlers
        
        Usage:
            @app.route('/')
            @hexagon.enhance
            def home():
                return render_template('index.html')
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, make_response
            
            # Call the original function
            result = func(*args, **kwargs)
            
            # Get user agent
            user_agent = request.headers.get('User-Agent', '')
            
            # Only enhance for AI crawlers
            if not self._is_ai_crawler(user_agent):
                return result
            
            # If result is a string (HTML), enhance it
            if isinstance(result, str):
                enhanced = self.enhance_html(
                    result,
                    url=request.url,
                    user_agent=user_agent
                )
                return make_response(enhanced)
            
            # If result is a response object, enhance its data
            if hasattr(result, 'get_data'):
                html = result.get_data(as_text=True)
                enhanced = self.enhance_html(
                    html,
                    url=request.url,
                    user_agent=user_agent
                )
                response = make_response(enhanced)
                response.headers = result.headers
                response.status_code = result.status_code
                return response
            
            return result
        
        return wrapper
    
    def get_blogs(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Fetch blogs from Hexagon API
        
        Args:
            page: Page number (default: 1)
            limit: Items per page (default: 20)
            
        Returns:
            Dictionary with blogs and pagination info
        """
        try:
            response = requests.get(
                f"{self.api_url}/sdk/blogs/{self.merchant_id}",
                params={"page": page, "limit": limit},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                if self.debug:
                    print(f"[Hexagon] API error fetching blogs: {response.status_code}")
                return {"blogs": [], "pagination": {}}
                
        except Exception as e:
            if self.debug:
                print(f"[Hexagon] Error fetching blogs: {str(e)}")
            return {"blogs": [], "pagination": {}}
    
    def get_blog(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single blog by slug
        
        Args:
            slug: Blog slug
            
        Returns:
            Blog data dictionary or None
        """
        try:
            response = requests.get(
                f"{self.api_url}/sdk/blogs/{self.merchant_id}/{slug}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('data')
            else:
                if self.debug:
                    print(f"[Hexagon] API error fetching blog: {response.status_code}")
                return None
                
        except Exception as e:
            if self.debug:
                print(f"[Hexagon] Error fetching blog: {str(e)}")
            return None

