from fastapi import Request
import os
import json
import grpc
import logging

logger = logging.getLogger(__name__)

BACKEND_API_URL = os.getenv("BACKEND_API_URL")
CLOUD_TASK_QUEUE = (
    os.getenv("CLOUD_TASK_QUEUE") or "projects/dev/locations/here/queues/anotherq"
)


class TaskInvoker:
    def __init__(self, client: any, request: Request, endpoint: str):
        self.client = client
        self.endpoint = endpoint
        self.request = request

    def invoke_task(self):
        logger.info(
            f"Invoking task {BACKEND_API_URL}/{self.endpoint} with request {self.request}"
        )
        self.client.create_task(
            task={
                "http_request": {
                    "http_method": "POST",
                    "url": f"{BACKEND_API_URL}/{self.endpoint}",
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(self.request.model_dump()).encode(),
                }
            },
            parent=CLOUD_TASK_QUEUE,
        )
