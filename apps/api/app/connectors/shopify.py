from __future__ import annotations

from typing import Dict, List, Optional

import httpx
import structlog

from app.connectors.base import StoreConnector

logger = structlog.get_logger()


class ShopifyConnector(StoreConnector):
    """Shopify Admin API connector."""

    platform = "shopify"

    def _api_url(self, path: str) -> str:
        store_url = self.credentials.get("store_url", "").rstrip("/")
        return f"{store_url}/admin/api/2025-01/{path}"

    def _headers(self) -> Dict[str, str]:
        return {
            "X-Shopify-Access-Token": self.credentials.get("access_token", ""),
            "Content-Type": "application/json",
        }

    async def validate_credentials(self) -> bool:
        if not self.credentials.get("access_token") or not self.credentials.get("store_url"):
            return False

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                self._api_url("shop.json"),
                headers=self._headers(),
            )
            return resp.status_code == 200

    async def fetch_orders(self, since: Optional[str] = None) -> List[Dict]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params: Dict[str, object] = {"limit": 50, "status": "open"}
            if since:
                params["created_at_min"] = since

            resp = await client.get(
                self._api_url("orders.json"),
                headers=self._headers(),
                params=params,
            )

            if resp.status_code != 200:
                logger.warning("shopify.fetch_orders_failed", status=resp.status_code)
                return []

            data = resp.json()
            orders: List[Dict] = []
            for order in data.get("orders", []):
                for item in order.get("line_items", []):
                    orders.append({
                        "external_id": str(order.get("id", "")),
                        "sku": item.get("sku", ""),
                        "price_cents": int(float(item.get("price", "0")) * 100),
                        "customer_hash": str(hash(order.get("email", "")))[:16],
                        "variant": {"title": item.get("variant_title", "")},
                    })
            return orders

    async def sync_listing(self, listing_data: Dict) -> str:
        # TODO: Implement Shopify product creation
        logger.info("shopify.sync_listing", sku=listing_data.get("sku"))
        return ""

    async def update_tracking(self, external_order_id: str, tracking_no: str) -> bool:
        # TODO: Implement Shopify fulfillment tracking
        logger.info("shopify.update_tracking", order_id=external_order_id, tracking=tracking_no)
        return True

    async def remove_listing(self, external_product_id: str) -> bool:
        # TODO: Implement Shopify product archival
        logger.info("shopify.remove_listing", product_id=external_product_id)
        return True
