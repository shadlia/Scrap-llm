import json
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class ProductRepository:
    def __init__(
        self,
        datasourceid: str,
        redis_client: any,
    ):
        self.datasourceid = datasourceid
        self.redis_client = redis_client

    def get_products_by_datasourceid(self):
        redis_value = self.redis_client.get(self.datasourceid)
        if redis_value is None:
            logger.warning(
                f"No data found in Redis for datasourceid: {self.datasourceid}"
            )
            return []
        try:
            products = json.loads(redis_value)

            logger.info(f"Retrieved {len(products)} products from Redis")
            return products
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            return []

    def set_products_by_datasourceid(self, products: list):
        try:
            self.redis_client.set(self.datasourceid, json.dumps(products))
        except Exception as e:
            logger.error(f"Failed to save products to Redis: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to save products to Redis: {str(e)}"
            )
