"""
Activity Tracker Mixin for Lambda Handlers.

Provides standardized activity tracking and logging functionality
for Lambda handlers using the aws_api_activity table.
"""

import copy
import json
import os
import time
from abc import ABC
from datetime import date, datetime
from typing import Dict, Any


class ActivityTracker(ABC):
    """
    Mixin class providing standardized activity tracking for Lambda handlers.

    Tracks API calls to the aws_api_activity table with consistent data structure
    and automatic duration calculation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activity_log_key = None
        self.start_time = None
        self.end_time = None
        self.activity_data = {}

    def track_activity_start(self, tx, context):
        """Start tracking activity for the current request"""
        self.start_time = time.time()

        # Gather common activity data
        postdata = context.postdata()
        payload = context.payload()

        self.activity_data = {
            "action": context.action(),
            "args": json.dumps(context.args()),
            "postdata": self._sanitize_postdata(postdata),
            "handler_name": self.__class__.__name__,
            "function_name": os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "Unknown"),
            "user_branch": os.environ.get("USER_BRANCH", "Unknown"),
            "start_timestamp": self.start_time,
        }

        # Add user information if available
        user_info = self._extract_user_info(payload)
        if user_info:
            self.activity_data.update(user_info)

        # Add session information
        session_data = context.session()
        if session_data:
            self.activity_data.update(self._sanitize_session_data(session_data))

        # Ensure all values are serializable before persisting
        self.activity_data = {
            key: self._normalize_activity_value(value)
            for key, value in self.activity_data.items()
            if value is not None
        }

        # Create the activity record
        try:
            self.activity_log_key = tx.table("aws_api_activity").new(self.activity_data).pk
        except Exception as exc:
            context.log(
                f"ActivityTracker.track_activity_start failed: {exc}; keys={list(self.activity_data.keys())}",
                "ActivityTracker.track_activity_start",
            )
            raise

        return self.activity_log_key
    
    def track_activity_success(self, tx, context):
        """Update activity record with success information"""
        if not self.activity_log_key:
            return
            
        self.end_time = time.time()
        update_data = {
            "end_timestamp": self.end_time,
            "duration": self.end_time - self.start_time,
            "status": "success"
        }
        
        tx.table("aws_api_activity").update(update_data, self.activity_log_key)
    
    def track_activity_error(self, tx, context, exception, tb_string):
        """Update activity record with error information"""
        if not self.activity_log_key:
            return
            
        self.end_time = time.time()
        update_data = {
            "end_timestamp": self.end_time,
            "duration": self.end_time - self.start_time if self.start_time else 0,
            "status": "error",
            "exception_type": exception.__class__.__name__,
            "exception_message": str(exception),
            "traceback": tb_string,
        }
        
        # Handle legacy field names for backward compatibility
        update_data["exception"] = exception.__class__.__name__
        
        tx.table("aws_api_activity").update(update_data, self.activity_log_key)
    
    def _sanitize_postdata(self, postdata: Dict) -> str:
        """Remove sensitive information from postdata before logging"""
        if not postdata:
            return "{}"
            
        sanitized = copy.deepcopy(postdata)
        
        # Remove cognito user data from payload if present
        if "payload" in sanitized and isinstance(sanitized["payload"], dict):
            sanitized["payload"].pop("cognito_user", None)
            
        # Remove other sensitive fields as needed
        sensitive_fields = ["password", "token", "secret", "key", "auth", "cognito_user"]
        self._recursive_sanitize(sanitized, sensitive_fields)
        
        return json.dumps(sanitized)
    
    def _recursive_sanitize(self, data: Any, sensitive_fields: list):
        """Recursively remove sensitive fields from nested data structures"""
        if isinstance(data, dict):
            for key in list(data.keys()):
                if any(field in key.lower() for field in sensitive_fields):
                    data[key] = "[REDACTED]"
                else:
                    self._recursive_sanitize(data[key], sensitive_fields)
        elif isinstance(data, list):
            for item in data:
                self._recursive_sanitize(item, sensitive_fields)
    
    def _extract_user_info(self, payload: Dict) -> Dict:
        """Extract user information from payload"""
        user_info = {}
        
        if payload and "cognito_user" in payload:
            try:
                attrs = payload["cognito_user"]["attributes"]
                if "email" in attrs:
                    user_info["email_address"] = attrs["email"].lower()
                if "sub" in attrs:
                    user_info["user_id"] = attrs["sub"]
            except (KeyError, TypeError):
                pass
                
        return user_info

    def _sanitize_session_data(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive session keys and normalize value types"""
        sanitized = {}

        for key, value in session.items():
            if key == "cognito_user":
                continue

            sanitized[key] = self._normalize_activity_value(value)

        return sanitized

    def _normalize_activity_value(self, value: Any) -> Any:
        """Convert activity data values into types acceptable by psycopg2"""
        if isinstance(value, (dict, list, tuple, set)):
            try:
                return json.dumps(value)
            except (TypeError, ValueError):
                return str(value)
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, (bytes, bytearray)):
            return value.decode("utf-8", errors="ignore")
        return value
