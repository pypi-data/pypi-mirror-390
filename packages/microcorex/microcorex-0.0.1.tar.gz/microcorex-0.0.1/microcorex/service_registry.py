"""
Service Registry

Unified management of all microservice configurations and clients.
"""

from typing import Dict, Any, Optional
from loguru import logger


class ServiceRegistry:
    """
    Service Registry

    Provides global service configuration management for gRPC client usage.
    """

    _config: Optional[Dict[str, Any]] = None
    _services: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def init(cls, config: Any):
        """
        Initialize service registry

        Args:
            config: Configuration object or dictionary
        """
        if hasattr(config, 'dict'):
            cls._config = config.dict()
        else:
            cls._config = config

        # Load service configurations
        cls._services = cls._config.get('services', {})

        logger.info(f"Service registry initialized, {len(cls._services)} services registered")

    @classmethod
    def get_service_config(cls, service_name: str) -> Dict[str, Any]:
        """
        Get service configuration

        Args:
            service_name: Service name (e.g., 'system-service')

        Returns:
            Service configuration dictionary containing host and grpc_port
        """
        if cls._config is None:
            raise RuntimeError("Service registry not initialized, please call ServiceRegistry.init(config) first")

        # Try direct lookup, attempt conversion if not found
        service_config = cls._services.get(service_name, {})

        if not service_config:
            # Try converting system-service to system_service
            service_key = service_name.replace('-', '_')
            service_config = cls._services.get(service_key, {})

        if not service_config:
            logger.warning(f"Service {service_name} not found in configuration, using default configuration")
            return {
                'host': 'localhost',
                'grpc_port': 9000
            }

        return service_config

    @classmethod
    def get_all_services(cls) -> Dict[str, Dict[str, Any]]:
        """Get all service configurations"""
        return cls._services.copy()

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if registry is initialized"""
        return cls._config is not None
