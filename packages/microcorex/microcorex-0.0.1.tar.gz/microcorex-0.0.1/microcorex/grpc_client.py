"""
gRPC Client Base Class

Provides common gRPC client functionality, including connection management,
timeout control, error handling, etc.
"""

import grpc
from typing import Optional
from loguru import logger


class GrpcClientBase:
    """
    gRPC Client Base Class

    Provides common gRPC client functionality.
    """

    def __init__(
        self,
        host: str,
        port: int,
        timeout: int = 5,
        max_retries: int = 3
    ):
        """
        Initialize gRPC client

        Args:
            host: Server address
            port: Server port
            timeout: Request timeout in seconds
            max_retries: Maximum retry count
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.address = f"{host}:{port}"
        self._channel: Optional[grpc.Channel] = None

    def connect(self):
        """Establish gRPC connection"""
        if self._channel is None:
            self._channel = grpc.insecure_channel(self.address)
            logger.info(f"gRPC client connected successfully: {self.address}")
        return self._channel

    def close(self):
        """Close gRPC connection"""
        if self._channel:
            self._channel.close()
            self._channel = None
            logger.info(f"gRPC client connection closed: {self.address}")

    @property
    def channel(self) -> grpc.Channel:
        """Get gRPC channel"""
        if self._channel is None:
            self.connect()
        return self._channel

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
