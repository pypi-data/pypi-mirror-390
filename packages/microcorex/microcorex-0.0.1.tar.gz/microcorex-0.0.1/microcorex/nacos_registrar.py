"""
Nacos Service Registrar

Provides service registration, discovery, heartbeat, and other functionalities,
supporting simultaneous registration of HTTP and gRPC ports.
"""

from typing import Optional
from v2.nacos import (
    ClientConfigBuilder, 
    NacosNamingService, 
    RegisterInstanceParam,
    DeregisterInstanceParam
)

from microcorex.config import MicroCoreConfig
from microcorex.logging_setup import get_logger

logger = get_logger(__name__)


class NacosRegistrationError(Exception):
    """Nacos registration exception"""
    pass


class NacosDiscoveryError(Exception):
    """Nacos discovery exception"""
    pass


class NacosRegistrar:
    """
    Nacos Service Registrar and Discovery

    Provides service registration, discovery, heartbeat, and other functionalities.
    Supports simultaneous registration of HTTP and gRPC ports.
    """

    def __init__(self, config: MicroCoreConfig):
        """
        Initialize Nacos registrar

        Args:
            config: Microservice core configuration
        """
        if not config:
            raise NacosRegistrationError("No valid configuration provided")

        self.config = config

        # Nacos client configuration
        self.client_config = (
            ClientConfigBuilder()
            .username(config.nacos.username)
            .password(config.nacos.password)
            .server_address(f'{config.nacos.host}:{config.nacos.port}')
            .namespace_id(config.nacos.namespace if config.nacos.namespace else "public")
            .log_level('INFO')
            .build()
        )

        # Nacos naming service client
        self.nacos_client: Optional[NacosNamingService] = None

    async def register_instance(self):
        """
        Register service instance

        Simultaneously registers HTTP service and gRPC service (if gRPC port is configured).
        """
        try:
            # Create naming service client
            self.nacos_client = await NacosNamingService.create_naming_service(
                self.client_config
            )

            # Register HTTP service
            await self._register_http_service()

            # Register gRPC service (if gRPC port is configured)
            if self.config.server.grpcPort:
                await self._register_grpc_service()

        except Exception as e:
            logger.warning(f"Service registration failed: {e}")
            # Don't throw exception, allow service to continue running when Nacos is unavailable

    async def _register_http_service(self):
        """Register HTTP service"""
        try:
            response = await self.nacos_client.register_instance(
                RegisterInstanceParam(
                    service_name=self.config.app.name,
                    group_name=self.config.nacos.groupName,
                    ip=self.config.server.ip,
                    port=self.config.server.servicePort,
                    metadata={
                        "env": self.config.app.env,
                        "protocol": "http",
                        "version": "1.0.0",
                        "service_name": self.config.app.name,
                        "service_group": self.config.nacos.groupName,
                    },
                    enabled=True,
                    healthy=True,
                    ephemeral=True  # Ephemeral instance, supports heartbeat
                )
            )

            if response:
                logger.info(
                    f"✅ HTTP service registered successfully: {self.config.app.name} "
                    f"({self.config.server.ip}:{self.config.server.servicePort})"
                )
            else:
                logger.error(f"❌ HTTP service registration failed: {self.config.app.name}")

        except Exception as e:
            logger.error(f"HTTP service registration exception: {e}")
            raise

    async def _register_grpc_service(self):
        """Register gRPC service"""
        try:
            grpc_service_name = f"{self.config.app.name}-grpc"

            response = await self.nacos_client.register_instance(
                RegisterInstanceParam(
                    service_name=grpc_service_name,
                    group_name=self.config.nacos.groupName,
                    ip=self.config.server.ip,
                    port=self.config.server.grpcPort,
                    metadata={
                        "env": self.config.app.env,
                        "protocol": "grpc",
                        "version": "1.0.0",
                        "service_name": grpc_service_name,
                        "service_group": self.config.nacos.groupName,
                    },
                    enabled=True,
                    healthy=True,
                    ephemeral=True  # Ephemeral instance, supports heartbeat
                )
            )

            if response:
                logger.info(
                    f"✅ gRPC service registered successfully: {grpc_service_name} "
                    f"({self.config.server.ip}:{self.config.server.grpcPort})"
                )
            else:
                logger.error(f"❌ gRPC service registration failed: {grpc_service_name}")

        except Exception as e:
            logger.error(f"gRPC service registration exception: {e}")
            raise

    async def deregister_instance(self):
        """
        Deregister service instance

        Deregisters HTTP service and gRPC service from Nacos.
        """
        if not self.nacos_client:
            logger.warning("Nacos client not initialized, no need to deregister")
            return

        try:
            # Deregister HTTP service
            await self._deregister_http_service()

            # Deregister gRPC service
            if self.config.server.grpcPort:
                await self._deregister_grpc_service()

            logger.info("✅ Service deregistration completed")

        except Exception as e:
            logger.error(f"Service deregistration failed: {e}")

    async def _deregister_http_service(self):
        """Deregister HTTP service"""
        try:
            await self.nacos_client.deregister_instance(
                DeregisterInstanceParam(
                    service_name=self.config.app.name,
                    group_name=self.config.nacos.groupName,
                    ip=self.config.server.ip,
                    port=self.config.server.servicePort,
                    ephemeral=True
                )
            )
            logger.info(f"HTTP service deregistered successfully: {self.config.app.name}")
        except Exception as e:
            logger.error(f"HTTP service deregistration failed: {e}")

    async def _deregister_grpc_service(self):
        """Deregister gRPC service"""
        try:
            grpc_service_name = f"{self.config.app.name}-grpc"
            await self.nacos_client.deregister_instance(
                DeregisterInstanceParam(
                    service_name=grpc_service_name,
                    group_name=self.config.nacos.groupName,
                    ip=self.config.server.ip,
                    port=self.config.server.grpcPort,
                    ephemeral=True
                )
            )
            logger.info(f"gRPC service deregistered successfully: {grpc_service_name}")
        except Exception as e:
            logger.error(f"gRPC service deregistration failed: {e}")
