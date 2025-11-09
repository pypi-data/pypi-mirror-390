"""
Base gRPC Client

Provides base class for gRPC clients, encapsulating common logic for client creation,
connection management, connection pooling, and other utilities.
"""

from typing import Dict, ClassVar
from loguru import logger

from microcorex.grpc_client import GrpcClientBase
from microcorex.service_registry import ServiceRegistry


class BaseGrpcClient:
    """
    Base gRPC Client Class

    Encapsulates common logic for client creation, connection management, and connection pooling,
    avoiding code duplication across different client classes.

    Usage:
        class SystemUserServiceGrpc(BaseGrpcClient):
            _service_name = "system-service"  # Set service name

            @classmethod
            @grpc_call(...)
            def get_by_id(cls, user_id: int):
                return system_pb2.GetUserRequest(user_id=user_id)

    Features:
        - Automatic client connection pool management
        - Automatic service configuration retrieval from service registry
        - Connection reuse for multiple service addresses
        - Unified connection shutdown method
    """
    
    # Class-level connection pool, shared by all subclasses
    _client_pool: ClassVar[Dict[str, GrpcClientBase]] = {}

    # Service name, must be set by subclasses
    _service_name: ClassVar[str] = ""
    
    @classmethod
    def _get_client(cls) -> GrpcClientBase:
        """
        Get or create gRPC client

        Retrieves service configuration from service registry, creates or reuses client connection.

        Returns:
            GrpcClientBase: gRPC client instance

        Raises:
            ValueError: If subclass has not set _service_name
        """
        if not cls._service_name:
            raise ValueError(f"{cls.__name__} must set _service_name class attribute")

        # Get service configuration from service registry
        service_config = ServiceRegistry.get_service_config(cls._service_name)
        host = service_config.get('host', 'localhost')
        port = service_config.get('grpc_port', 9002)

        # Use host:port as connection pool key
        key = f"{host}:{port}"

        # Create new connection if not in connection pool
        if key not in cls._client_pool:
            client = GrpcClientBase(host=host, port=port, timeout=5)
            client.connect()
            cls._client_pool[key] = client
            logger.debug(f"Created {cls._service_name} gRPC client: {key}")

        return cls._client_pool[key]
    
    @classmethod
    def close_all(cls):
        """
        Close all client connections

        Iterates through connection pool, closes all client connections and clears the pool.
        Typically called during application shutdown.
        """
        for key, client in cls._client_pool.items():
            try:
                client.close()
                logger.debug(f"Closed gRPC client: {key}")
            except Exception as e:
                logger.error(f"Failed to close client {key}: {e}")

        cls._client_pool.clear()
        logger.info("All gRPC client connections closed")
