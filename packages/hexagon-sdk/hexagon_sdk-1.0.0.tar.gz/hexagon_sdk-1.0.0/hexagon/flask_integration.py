"""
Flask integration for Hexagon SDK
"""

from flask import request, make_response
from functools import wraps
from typing import Callable


def hexagon_middleware(hexagon_instance):
    """
    Create Flask middleware for Hexagon
    
    Usage:
        from flask import Flask
        from hexagon import Hexagon, flask_middleware
        
        app = Flask(__name__)
        hexagon = Hexagon(merchant_id='xxx', api_key='xxx')
        
        app.before_request(flask_middleware(hexagon))
    """
    def middleware():
        # Store hexagon instance in flask g object for use in routes
        from flask import g
        g.hexagon = hexagon_instance
    
    return middleware


def enhance_route(hexagon_instance):
    """
    Decorator for Flask routes to enhance responses for AI crawlers
    
    Usage:
        @app.route('/')
        @enhance_route(hexagon)
        def home():
            return render_template('index.html')
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Call the original function
            result = func(*args, **kwargs)
            
            # Get user agent
            user_agent = request.headers.get('User-Agent', '')
            
            # Only enhance for AI crawlers
            if not hexagon_instance._is_ai_crawler(user_agent):
                return result
            
            # If result is a string (HTML), enhance it
            if isinstance(result, str):
                enhanced = hexagon_instance.enhance_html(
                    result,
                    url=request.url,
                    user_agent=user_agent
                )
                return make_response(enhanced)
            
            # If result is a response object, enhance its data
            if hasattr(result, 'get_data'):
                html = result.get_data(as_text=True)
                enhanced = hexagon_instance.enhance_html(
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
    
    return decorator

