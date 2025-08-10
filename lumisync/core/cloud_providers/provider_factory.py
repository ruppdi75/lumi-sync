"""
Cloud Provider Factory
Creates and manages cloud provider instances
"""

from typing import Dict, Type, Optional
import logging

from .base_provider import CloudProvider
from .google_drive import GoogleDriveProvider
from .pcloud import PCloudProvider

logger = logging.getLogger(__name__)


class CloudProviderFactory:
    """
    Factory class for creating cloud provider instances.
    
    This factory manages the registration and creation of different
    cloud storage providers, making it easy to add new providers
    in the future.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[CloudProvider]] = {
        'google_drive': GoogleDriveProvider,
        'pcloud': PCloudProvider,
        # Future providers will be added here:
        # 'onedrive': OneDriveProvider,
        # 'box': BoxProvider,
    }
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, str]:
        """
        Get a list of available cloud providers.
        
        Returns:
            Dictionary mapping provider keys to human-readable names
        """
        provider_names = {}
        for key, provider_class in cls._providers.items():
            # Create a temporary instance to get the display name
            temp_instance = provider_class()
            provider_names[key] = temp_instance.provider_name
        
        return provider_names
    
    @classmethod
    def create_provider(cls, provider_type: str) -> CloudProvider:
        """
        Create a cloud provider instance.
        
        Args:
            provider_type: Type of provider to create (e.g., 'google_drive')
            
        Returns:
            CloudProvider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        if provider_type not in cls._providers:
            available = list(cls._providers.keys())
            raise ValueError(f"Unsupported provider type '{provider_type}'. Available: {available}")
        
        provider_class = cls._providers[provider_type]
        instance = provider_class()
        
        logger.info(f"Created {instance.provider_name} provider instance")
        return instance
    
    @classmethod
    def register_provider(cls, provider_key: str, provider_class: Type[CloudProvider]):
        """
        Register a new cloud provider.
        
        Args:
            provider_key: Unique key for the provider
            provider_class: Provider class that implements CloudProvider interface
        """
        if not issubclass(provider_class, CloudProvider):
            raise ValueError("Provider class must inherit from CloudProvider")
        
        cls._providers[provider_key] = provider_class
        logger.info(f"Registered new provider: {provider_key}")
    
    @classmethod
    def is_provider_available(cls, provider_type: str) -> bool:
        """
        Check if a provider type is available.
        
        Args:
            provider_type: Provider type to check
            
        Returns:
            True if provider is available, False otherwise
        """
        return provider_type in cls._providers


# Convenience function for creating providers
def create_cloud_provider(provider_type: str = 'google_drive') -> CloudProvider:
    """
    Convenience function to create a cloud provider.
    
    Args:
        provider_type: Type of provider to create (defaults to Google Drive)
        
    Returns:
        CloudProvider instance
    """
    return CloudProviderFactory.create_provider(provider_type)
