"""Factory for creating HetznerProvider instances with API key management."""

import logging
from typing import Optional

from easyrunner.source.cloud_providers.hetzner_provider import HetznerProvider

from .auth.hetzner_api_key_manager import HetznerApiKeyManager

logger = logging.getLogger(__name__)


def create_hetzner_provider(
    region: str = "nbg1", project_name: str = "default"
) -> HetznerProvider:
    """Create HetznerProvider instance from keychain.

    Loads API key from keychain for the specified project and creates
    a HetznerProvider instance.

    Args:
        region: Hetzner region (default: "nbg1")
        project_name: Hetzner project name (default: "default")

    Returns:
        HetznerProvider: Configured provider instance

    Raises:
        ValueError: If API key is not found in keychain
    """
    api_key: Optional[str] = None

    try:
        api_key_manager = HetznerApiKeyManager(project_name=project_name)
        api_key = api_key_manager.get_api_key()
    except Exception as e:
        logger.debug(f"Failed to retrieve API key from keychain: {e}")

    if not api_key:
        raise ValueError(
            f"Hetzner API key not found for project '{project_name}'. "
            f"Please link Hetzner using 'er link hetzner {project_name} --api-key YOUR_KEY'"
        )

    return HetznerProvider(api_key=api_key, region=region)
