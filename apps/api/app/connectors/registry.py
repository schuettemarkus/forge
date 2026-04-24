from __future__ import annotations

from typing import Dict, Optional, Type

from app.connectors.base import StoreConnector
from app.connectors.manual import ManualConnector
from app.connectors.etsy import EtsyConnector
from app.connectors.shopify import ShopifyConnector

# Register all available store connectors here.
# To add a new platform: create a connector file, then add one line below.
CONNECTOR_REGISTRY: Dict[str, Type[StoreConnector]] = {
    "manual": ManualConnector,
    "etsy": EtsyConnector,
    "shopify": ShopifyConnector,
}


def get_connector(platform: str, credentials: Optional[Dict] = None) -> StoreConnector:
    """Get a connector instance for the given platform."""
    connector_class = CONNECTOR_REGISTRY.get(platform)
    if not connector_class:
        raise ValueError(
            f"Unknown platform: {platform}. "
            f"Available: {', '.join(CONNECTOR_REGISTRY.keys())}"
        )
    return connector_class(credentials=credentials)


def available_platforms() -> list:
    """List all registered platform names."""
    return list(CONNECTOR_REGISTRY.keys())
