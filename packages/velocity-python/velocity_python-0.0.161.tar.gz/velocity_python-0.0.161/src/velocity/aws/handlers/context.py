import json
import os
import boto3
import uuid
import support.app
from velocity.misc.format import to_json
from velocity.misc.merge import deep_merge
from datetime import datetime

import velocity.db

engine = velocity.db.postgres.initialize()


@engine.transaction
class Context:

    def __init__(
        self, aws_event, aws_context, args, postdata, response, session, log=None
    ):
        self.__args = args
        self.__postdata = postdata
        self.__response = response
        self.__session = {} if session is None else session
        self.__aws_event = aws_event
        self.__aws_context = aws_context
        self.__log = log
        self._job_record_cache = {}
        self._job_cancelled_flag = False

    def postdata(self, keys=-1, default=None):
        if keys == -1:
            return self.__postdata
        if not isinstance(keys, list):
            keys = [keys]
        data = self.__postdata
        for key in keys:
            if key in data:
                data = data[key]
            else:
                return default
        return data

    def payload(self, keys=-1, default={}):
        if "payload" not in self.__postdata:
            return default
        if keys == -1:
            return self.__postdata["payload"]
        if not isinstance(keys, list):
            keys = [keys]
        data = self.__postdata["payload"]
        for key in keys:
            if key in data:
                data = data[key]
            else:
                return default
        return data

    def action(self):
        return self.__postdata.get("action", self.__args.get("action", ""))

    def args(self):
        return self.__args

    def response(self):
        return self.__response

    def session(self):
        return self.__session

    def dataset(self):
        return self.payload().get("dataset", {})

    def log(self, message, function=None):
        if self.__log:
            return self.__log(message, function)
        else:
            if function:
                print(f"{function}: {message}")
            else:
                print(f"{message}")

    def update_job(self, tx, data=None):
        """Update job status and message in aws_job_activity table.

        This method only UPDATES existing jobs. For creating new jobs, use create_job.
        """
        if not data:
            return
        if self.postdata("job_id"):
            # Sanitize data before storing in database
            sanitized_data = self._sanitize_job_data(data)
            job_id = self.postdata("job_id")
            tx.table("aws_job_activity").update(sanitized_data, {"job_id": job_id})
            self._job_record_cache.pop(job_id, None)
            tx.commit()

    def create_job(self, tx, job_data=None):
        """Create a new job record in aws_job_activity table using independent transaction."""
        if not job_data:
            return
        sanitized_data = self._sanitize_job_data(job_data)
        tx.table("aws_job_activity").insert(sanitized_data)
        job_id = sanitized_data.get("job_id")
        if job_id:
            self._job_record_cache.pop(job_id, None)
        tx.commit()

    def _sanitize_job_data(self, data):
        """Sanitize sensitive data before storing in aws_job_activity table."""
        if not isinstance(data, dict):
            return data

        sanitized = {}

        # List of sensitive field patterns to sanitize
        sensitive_patterns = [
            "password",
            "token",
            "secret",
            "key",
            "credential",
            "auth",
            "cognito_user",
            "session",
            "cookie",
            "authorization",
        ]

        for key, value in data.items():
            # Check if key contains sensitive patterns
            if any(pattern in key.lower() for pattern in sensitive_patterns):
                sanitized[key] = "[REDACTED]" if value else value
            elif key == "error" and value:
                # Sanitize error messages - keep first 500 chars and remove potential sensitive info
                error_str = str(value)[:500]
                for pattern in sensitive_patterns:
                    if pattern in error_str.lower():
                        # Replace potential sensitive values with placeholder
                        import re

                        # Remove patterns like password=value, token=value, etc.
                        error_str = re.sub(
                            rf"{pattern}[=:]\s*[^\s,\]}}]+",
                            f"{pattern}=[REDACTED]",
                            error_str,
                            flags=re.IGNORECASE,
                        )
                sanitized[key] = error_str
            elif key == "traceback" and value:
                # Sanitize traceback - keep structure but remove sensitive values
                tb_str = str(value)
                for pattern in sensitive_patterns:
                    if pattern in tb_str.lower():
                        import re

                        # Remove patterns like password=value, token=value, etc.
                        tb_str = re.sub(
                            rf"{pattern}[=:]\s*[^\s,\]}}]+",
                            f"{pattern}=[REDACTED]",
                            tb_str,
                            flags=re.IGNORECASE,
                        )
                # Limit traceback size to prevent DB bloat
                sanitized[key] = tb_str[:2000]
            elif key == "message" and value:
                # Sanitize message field
                message_str = str(value)
                for pattern in sensitive_patterns:
                    if pattern in message_str.lower():
                        import re

                        message_str = re.sub(
                            rf"{pattern}[=:]\s*[^\s,\]}}]+",
                            f"{pattern}=[REDACTED]",
                            message_str,
                            flags=re.IGNORECASE,
                        )
                sanitized[key] = message_str[:1000]  # Limit message size
            else:
                # For other fields, copy as-is but check for nested dicts
                if isinstance(value, dict):
                    sanitized[key] = self._sanitize_job_data(value)
                elif isinstance(value, str) and len(value) > 5000:
                    # Limit very large string fields
                    sanitized[key] = value[:5000] + "...[TRUNCATED]"
                else:
                    sanitized[key] = value

        return sanitized

    def _get_job_record(self, tx, job_id=None, refresh=False):
        job_id = job_id or self.postdata("job_id")
        if not job_id:
            return None

        if refresh or job_id not in self._job_record_cache:
            record = tx.table("aws_job_activity").find({"job_id": job_id})
            if record is not None:
                self._job_record_cache[job_id] = record
            elif job_id in self._job_record_cache:
                del self._job_record_cache[job_id]

        return self._job_record_cache.get(job_id)

    def is_job_cancel_requested(self, tx, force_refresh=False):
        job = self._get_job_record(tx, refresh=force_refresh)
        if not job:
            return False

        status = (job.get("status") or "").lower()
        if status in {"cancelrequested", "cancelled"}:
            return True

        message_raw = job.get("message")
        if not message_raw:
            return False

        if isinstance(message_raw, dict):
            message = message_raw
        else:
            try:
                message = json.loads(message_raw)
            except (TypeError, ValueError, json.JSONDecodeError):
                return False

        return bool(message.get("cancel_requested") or message.get("cancelled"))

    def mark_job_cancelled(self, tx, detail=None, requested_by=None):
        job_id = self.postdata("job_id")
        if not job_id:
            return

        job = self._get_job_record(tx, refresh=True) or {}
        message_raw = job.get("message")
        if isinstance(message_raw, dict):
            message = dict(message_raw)
        else:
            try:
                message = json.loads(message_raw) if message_raw else {}
            except (TypeError, ValueError, json.JSONDecodeError):
                message = {}

        message.update(
            {
                "detail": detail or "Job cancelled",
                "cancelled": True,
            }
        )

        tx.table("aws_job_activity").update(
            {
                "status": "Cancelled",
                "message": to_json(message),
                "handler_complete_timestamp": datetime.now(),
                "sys_modified": datetime.now(),
                "sys_modified_by": requested_by
                or self.session().get("email_address")
                or "system",
            },
            {"job_id": job_id},
        )
        tx.commit()
        self._job_record_cache.pop(job_id, None)
        self._job_cancelled_flag = True

    def was_job_cancelled(self):
        return self._job_cancelled_flag

    def enqueue(self, action, payload={}, user=None, suppress_job_activity=False):
        """
        Enqueue jobs to SQS with independent job activity tracking.

        This method uses its own transaction for aws_job_activity updates to ensure
        job tracking is never rolled back with other operations.
        """
        batch_id = str(uuid.uuid4())
        results = {"batch_id": batch_id}
        queue = boto3.resource("sqs").get_queue_by_name(
            QueueName=os.environ["SqsWorkQueue"]
        )
        if isinstance(payload, dict):
            payload = [payload]
        messages = []
        if user is None:
            user = self.session().get("email_address") or "EnqueueTasks"
        for item in payload:
            message = {"action": action, "payload": item}
            id = str(uuid.uuid4()).split("-")[0]
            if suppress_job_activity:
                messages.append({"Id": id, "MessageBody": to_json(message)})
            else:
                message["job_id"] = id
                # Use separate transaction for job activity - this should never be rolled back
                self.create_job(
                    {
                        "action": action,
                        "initial_timestamp": datetime.now(),
                        "created_by": user,
                        "sys_modified_by": user,
                        "payload": to_json(message),
                        "batch_id": str(batch_id),
                        "job_id": id,
                        "status": "Initialized",
                        "message": "Job Initialized",
                    }
                )
                messages.append({"Id": id, "MessageBody": to_json(message)})

            if len(messages) == 10:
                result = queue.send_messages(Entries=messages)
                results = deep_merge(results, result)
                messages.clear()

        if messages:
            result = queue.send_messages(Entries=messages)
            results = deep_merge(results, result)

        return results
