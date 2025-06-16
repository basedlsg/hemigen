"""
Cost monitoring and alerting system for Hemi-gen
"""

import os
import json
from datetime import datetime, timedelta
import redis
from http.server import BaseHTTPRequestHandler

# Redis connection for usage tracking
REDIS_URL = os.environ.get('REDIS_URL')
redis_client = None
if REDIS_URL:
    try:
        import redis
        redis_client = redis.from_url(REDIS_URL)
    except:
        pass

# Cost thresholds and limits
DAILY_REQUEST_LIMIT = 1000  # Max requests per day
MONTHLY_COST_LIMIT = 50.0   # Max cost in USD per month
COST_PER_REQUEST = 0.001    # Estimated cost per Gemini API call

def log_request(session_id=None, cost=COST_PER_REQUEST):
    """Log a successful request for monitoring."""
    if not redis_client:
        return
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        # Increment daily counter
        daily_key = f"requests:daily:{today}"
        redis_client.incr(daily_key)
        redis_client.expire(daily_key, 86400)  # 24 hours
        
        # Increment monthly counter
        monthly_key = f"requests:monthly:{month}"
        redis_client.incr(monthly_key)
        redis_client.expire(monthly_key, 2592000)  # 30 days
        
        # Track costs
        cost_key = f"cost:monthly:{month}"
        redis_client.incrbyfloat(cost_key, cost)
        redis_client.expire(cost_key, 2592000)  # 30 days
        
        # Log timestamp for analytics
        usage_log = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'cost': cost
        }
        
        log_key = f"usage:log:{today}"
        redis_client.lpush(log_key, json.dumps(usage_log))
        redis_client.expire(log_key, 604800)  # 7 days
        
    except Exception as e:
        print(f"Monitoring error: {e}")

def check_limits():
    """Check if we're approaching or exceeding limits."""
    if not redis_client:
        return {"status": "monitoring_disabled"}
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        # Get current usage
        daily_requests = int(redis_client.get(f"requests:daily:{today}") or 0)
        monthly_requests = int(redis_client.get(f"requests:monthly:{month}") or 0)
        monthly_cost = float(redis_client.get(f"cost:monthly:{month}") or 0.0)
        
        status = {
            "daily_requests": daily_requests,
            "monthly_requests": monthly_requests,
            "monthly_cost": monthly_cost,
            "limits": {
                "daily_request_limit": DAILY_REQUEST_LIMIT,
                "monthly_cost_limit": MONTHLY_COST_LIMIT
            },
            "warnings": [],
            "blocked": False
        }
        
        # Check for warnings and blocks
        if daily_requests >= DAILY_REQUEST_LIMIT:
            status["blocked"] = True
            status["warnings"].append("Daily request limit exceeded")
        elif daily_requests >= DAILY_REQUEST_LIMIT * 0.8:
            status["warnings"].append("Approaching daily request limit")
        
        if monthly_cost >= MONTHLY_COST_LIMIT:
            status["blocked"] = True
            status["warnings"].append("Monthly cost limit exceeded")
        elif monthly_cost >= MONTHLY_COST_LIMIT * 0.8:
            status["warnings"].append("Approaching monthly cost limit")
        
        return status
        
    except Exception as e:
        print(f"Limit check error: {e}")
        return {"status": "error", "message": str(e)}

def get_analytics():
    """Get usage analytics for the past 7 days."""
    if not redis_client:
        return {"status": "monitoring_disabled"}
    
    try:
        analytics = {
            "daily_usage": {},
            "total_requests": 0,
            "total_cost": 0.0,
            "peak_day": None,
            "peak_requests": 0
        }
        
        # Get data for past 7 days
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_requests = int(redis_client.get(f"requests:daily:{date}") or 0)
            
            analytics["daily_usage"][date] = daily_requests
            analytics["total_requests"] += daily_requests
            
            if daily_requests > analytics["peak_requests"]:
                analytics["peak_requests"] = daily_requests
                analytics["peak_day"] = date
        
        # Get monthly cost
        month = datetime.now().strftime('%Y-%m')
        analytics["total_cost"] = float(redis_client.get(f"cost:monthly:{month}") or 0.0)
        
        return analytics
        
    except Exception as e:
        print(f"Analytics error: {e}")
        return {"status": "error", "message": str(e)}

def send_alert(message, level="warning"):
    """Send alert via webhook (configure with your preferred service)."""
    # This is a placeholder - you can integrate with:
    # - Discord webhook
    # - Slack webhook  
    # - Email service
    # - SMS service
    
    alert_data = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "service": "hemi-gen"
    }
    
    print(f"ALERT [{level.upper()}]: {message}")
    
    # Example Discord webhook (uncomment and configure):
    # webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    # if webhook_url:
    #     try:
    #         import requests
    #         payload = {"content": f"🚨 Hemi-gen Alert: {message}"}
    #         requests.post(webhook_url, json=payload)
    #     except:
    #         pass

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle monitoring endpoint requests."""
        
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        try:
            # Parse path
            path = self.path.strip('/')
            
            if path == 'monitor/status':
                # Return current status and limits
                status = check_limits()
                self.wfile.write(json.dumps(status).encode())
                
            elif path == 'monitor/analytics':
                # Return usage analytics
                analytics = get_analytics()
                self.wfile.write(json.dumps(analytics).encode())
                
            elif path == 'monitor/health':
                # Simple health check
                health = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "redis_connected": redis_client is not None
                }
                self.wfile.write(json.dumps(health).encode())
                
            else:
                # Invalid endpoint
                self.send_response(404)
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
                
        except Exception as e:
            self.send_response(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())

# For logging requests from the main generate endpoint
def middleware_log_request(func):
    """Decorator to log requests and check limits."""
    def wrapper(*args, **kwargs):
        # Check limits before processing
        limits = check_limits()
        if limits.get("blocked"):
            return {
                "error": "Service temporarily unavailable due to usage limits",
                "code": "USAGE_LIMIT_EXCEEDED",
                "limits": limits
            }
        
        # Process request
        result = func(*args, **kwargs)
        
        # Log successful request
        if isinstance(result, dict) and result.get("success"):
            log_request()
            
            # Check for warnings after logging
            new_limits = check_limits()
            for warning in new_limits.get("warnings", []):
                send_alert(warning, "warning")
        
        return result
    
    return wrapper