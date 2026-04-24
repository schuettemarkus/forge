from __future__ import annotations

from typing import Dict, List, Optional

import httpx
import structlog

from app.connectors.base import StoreConnector

logger = structlog.get_logger()

ETSY_API_BASE = "https://openapi.etsy.com/v3"


class EtsyConnector(StoreConnector):
    """Etsy Open API v3 connector."""

    platform = "etsy"

    async def validate_credentials(self) -> bool:
        api_key = self.credentials.get("api_key", "")
        if not api_key:
            return False

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{ETSY_API_BASE}/application/openapi-ping",
                headers={"x-api-key": api_key},
            )
            return resp.status_code == 200

    async def fetch_orders(self, since: Optional[str] = None) -> List[Dict]:
        api_key = self.credentials.get("api_key", "")
        shop_id = self.credentials.get("shop_id", "")
        if not api_key or not shop_id:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            params: Dict[str, object] = {"limit": 25, "sort_on": "created"}
            if since:
                params["min_created"] = since

            resp = await client.get(
                f"{ETSY_API_BASE}/application/shops/{shop_id}/receipts",
                headers={"x-api-key": api_key},
                params=params,
            )

            if resp.status_code != 200:
                logger.warning("etsy.fetch_orders_failed", status=resp.status_code)
                return []

            data = resp.json()
            orders: List[Dict] = []
            for receipt in data.get("results", []):
                for txn in receipt.get("transactions", []):
                    orders.append({
                        "external_id": str(receipt.get("receipt_id", "")),
                        "sku": txn.get("sku", txn.get("listing_id", "")),
                        "price_cents": int(float(txn.get("price", {}).get("amount", 0))),
                        "customer_hash": str(hash(receipt.get("buyer_email", "")))[:16],
                        "variant": txn.get("variations", None),
                    })
            return orders

    async def sync_listing(self, listing_data: Dict) -> str:
        # TODO: Implement Etsy listing creation via API
        logger.info("etsy.sync_listing", sku=listing_data.get("sku"))
        return ""

    async def update_tracking(self, external_order_id: str, tracking_no: str) -> bool:
        # TODO: Implement Etsy tracking update via API
        logger.info("etsy.update_tracking", order_id=external_order_id, tracking=tracking_no)
        return True

    async def remove_listing(self, external_product_id: str) -> bool:
        # TODO: Implement Etsy listing deactivation
        logger.info("etsy.remove_listing", product_id=external_product_id)
        return True
