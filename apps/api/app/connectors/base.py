from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import structlog

logger = structlog.get_logger()


class StoreConnector(ABC):
    """Base class for marketplace/store integrations.

    To add a new platform:
    1. Create a new file in app/connectors/ (e.g., woocommerce.py)
    2. Subclass StoreConnector and implement all abstract methods
    3. Register it in app/connectors/registry.py
    """

    platform: str = "unknown"

    def __init__(self, credentials: Optional[Dict] = None) -> None:
        self.credentials = credentials or {}

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Test that the stored credentials are valid and the store is reachable."""
        ...

    @abstractmethod
    async def fetch_orders(self, since: Optional[str] = None) -> List[Dict]:
        """Fetch new orders from the store.

        Returns a list of dicts with at minimum:
            external_id: str — the store's order ID
            sku: str — maps to our listing SKU
            price_cents: int — order total in cents
            customer_hash: str — hashed customer identifier
            variant: Optional[dict] — color, size, etc.
        """
        ...

    @abstractmethod
    async def sync_listing(self, listing_data: Dict) -> str:
        """Push a listing to the store. Returns the external product ID."""
        ...

    @abstractmethod
    async def update_tracking(self, external_order_id: str, tracking_no: str) -> bool:
        """Update tracking number on a shipped order. Returns success."""
        ...

    @abstractmethod
    async def remove_listing(self, external_product_id: str) -> bool:
        """Remove/deactivate a listing from the store. Returns success."""
        ...

    async def test_connection(self) -> Dict[str, object]:
        """Test the connection and return status info."""
        try:
            valid = await self.validate_credentials()
            return {
                "platform": self.platform,
                "connected": valid,
                "error": None,
            }
        except Exception as e:
            return {
                "platform": self.platform,
                "connected": False,
                "error": str(e),
            }
