from __future__ import annotations

from typing import Dict, List, Optional

import structlog

from app.connectors.base import StoreConnector

logger = structlog.get_logger()


class ManualConnector(StoreConnector):
    """No-op connector for stores without API integration.

    Orders are entered manually via the dashboard. Listings are managed
    externally. This connector always validates and never syncs.
    """

    platform = "manual"

    async def validate_credentials(self) -> bool:
        return True

    async def fetch_orders(self, since: Optional[str] = None) -> List[Dict]:
        # Manual orders are entered through the dashboard, not fetched
        return []

    async def sync_listing(self, listing_data: Dict) -> str:
        logger.info("manual.sync_listing", msg="Manual store — listing managed externally")
        return "manual-" + listing_data.get("sku", "unknown")

    async def update_tracking(self, external_order_id: str, tracking_no: str) -> bool:
        logger.info("manual.update_tracking", order_id=external_order_id, tracking=tracking_no)
        return True

    async def remove_listing(self, external_product_id: str) -> bool:
        return True
