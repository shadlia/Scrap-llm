import aiohttp
import logging
import os

logger = logging.getLogger(__name__)


class FastlyService:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def send_message(self, topic: str, message: dict) -> bool:
        """
        Envoie un message à Fastly via l'API REST.


        Args:
            topic: L'identifiant du topic
            message: Le message à envoyer


        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        url = f"{os.getenv('FASTLY_WEBSOCKET_URL')}/events?topic={topic}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, headers=self.headers, json=message
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        logger.error(
                            f"Erreur lors de l'envoi du message à Fastly: {response.status}"
                        )
                        return False
        except Exception as e:
            logger.error(f"Exception lors de l'envoi du message à Fastly: {str(e)}")
            return False
