from .fastly import FastlyService
import jwt
import time
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
KEY_ID = os.getenv("JWT_KEY_ID")


class NotificationService:
    def __init__(self, client_id: str):
        self.client_id = client_id
        token = generate_token(client_id)
        self.fastly_service = FastlyService(token)

    async def send_progress_update(self, progress: int, current_url: str) -> bool:
        """
        Send a progress update.
        """
        message = {"type": "progress", "progress": progress, "currentUrl": current_url}
        success = await self.fastly_service.send_message(self.client_id, message)
        if success:
            logger.info(
                f"✅ Progress notification sent successfully: {progress}% - {current_url}"
            )
        else:
            logger.error(
                f"❌ Failed to send progress notification: {progress}% - {current_url}"
            )
        return success

    async def send_product_done(self, product: dict) -> bool:
        """
        Send a product done notification.
        """
        message = {"type": "product_done", "product": product}
        success = await self.fastly_service.send_message(self.client_id, message)
        if success:
            logger.info(
                f"✅ Product notification sent successfully: {product.get('product_name', 'Unknown product')}"
            )
        else:
            logger.error(
                f"❌ Failed to send product notification: {product.get('product_name', 'Unknown product')}"
            )
        return success

    async def send_completion_notification(self, elapsed_time: int) -> bool:
        """
        Send a completion notification.
        """
        message = {"type": "complete", "elapsedTime": elapsed_time}
        success = await self.fastly_service.send_message(self.client_id, message)
        if success:
            logger.info(
                f"✅ Completion notification sent successfully. Elapsed time: {elapsed_time}s"
            )
        else:
            logger.error(
                f"❌ Failed to send completion notification. Elapsed time: {elapsed_time}s"
            )
        return success

    async def send_connection_status(self, status: str = "connected") -> bool:
        """
        Send the connection status.
        """
        message = {"type": "connection", "status": status, "client_id": self.client_id}
        success = await self.fastly_service.send_message(self.client_id, message)
        if success:
            logger.info(f"✅ Status notification sent successfully: {status}")
        else:
            logger.error(f"❌ Failed to send status notification: {status}")
        return success


def generate_token(client_id: str) -> str:
    """
    Generate a JWT token for Fastly authentication.

    Args:
        client_id: The client identifier

    Returns:
        str: The generated JWT token
    """
    if not JWT_SECRET or not KEY_ID:
        raise ValueError(
            "JWT_SECRET and JWT_KEY_ID should be defined in environment variables"
        )

    payload = {
        "exp": int(time.time()) + 3600,  # Expires in 1 hour
        "x-fastly-write": [client_id],
    }

    headers = {"kid": KEY_ID, "alg": "HS256"}

    token = jwt.encode(
        payload=payload, key=JWT_SECRET, algorithm="HS256", headers=headers
    )

    return token
