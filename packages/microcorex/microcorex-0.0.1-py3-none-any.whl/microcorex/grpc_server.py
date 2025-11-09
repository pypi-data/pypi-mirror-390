"""
gRPC Server Base Class

Provides basic functionality for gRPC servers, including startup, shutdown, and graceful termination.
"""

import grpc.aio
from abc import ABC, abstractmethod
from typing import Optional

from microcorex.config import MicroCoreConfig
from microcorex.logging_setup import get_logger

logger = get_logger(__name__)


class GrpcServerBase(ABC):
    """
    gRPC Server Base Class

    Provides basic functionality for gRPC servers. Subclasses need to implement the register_services method
    to register specific gRPC services.
    """

    def __init__(self, config: MicroCoreConfig):
        """
        Initialize gRPC server

        Args:
            config: Microservice core configuration
        """
        self.config = config
        self.server: Optional[grpc.aio.Server] = None

    @abstractmethod
    def register_services(self, server: grpc.aio.Server):
        """
        Register gRPC services (must be implemented by subclasses)

        Args:
            server: gRPC server instance
        """
        pass

    async def start(self):
        """Start gRPC server"""
        try:
            # Create gRPC server
            self.server = grpc.aio.server(
                options=[
                    # Maximum receive message length (100MB)
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),
                    # Maximum send message length (100MB)
                    ('grpc.max_send_message_length', 100 * 1024 * 1024),
                    # Keepalive time (60 seconds)
                    ('grpc.keepalive_time_ms', 60 * 1000),
                    # Keepalive timeout (20 seconds)
                    ('grpc.keepalive_timeout_ms', 20 * 1000),
                ]
            )

            # Register services (implemented by subclass)
            self.register_services(self.server)

            # Bind port
            listen_addr = f'[::]:{self.config.server.grpcPort}'
            self.server.add_insecure_port(listen_addr)

            # Start server
            await self.server.start()
            logger.info(
                f"✅ gRPC server started successfully: {self.config.server.ip}:{self.config.server.grpcPort}"
            )

        except Exception as e:
            logger.error(f"gRPC server startup failed: {e}")
            raise

    async def stop(self, grace_period: int = 30):
        """
        Stop gRPC server

        Args:
            grace_period: Graceful shutdown wait time in seconds
        """
        if self.server:
            try:
                logger.info(f"Stopping gRPC server (waiting {grace_period} seconds)...")
                await self.server.stop(grace_period)
                logger.info("✅ gRPC server stopped")
            except Exception as e:
                logger.error(f"Failed to stop gRPC server: {e}")

    async def wait_for_termination(self):
        """Wait for server termination"""
        if self.server:
            await self.server.wait_for_termination()
