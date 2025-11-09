"""
MicroCoreX - Python Microservices Framework Core Library

Provides core functionality for microservices development:
- Configuration management (multi-environment support, Nacos integration, hot reload)
- Service lifecycle management (FastAPI + gRPC dual protocol support)
- Service registration and discovery (Nacos integration)
- gRPC client/server base classes
- Logging management
"""

__version__ = "0.1.0"
__author__ = "xiaoke"

from microcorex.config import MicroCoreConfig, AppConfig, ServerConfig, NacosConfig, DatabaseConfig
from microcorex.config_loader import ConfigLoader
from microcorex.app_service import AppService
from microcorex.grpc_server import GrpcServerBase
from microcorex.base_grpc_client import BaseGrpcClient
from microcorex.service_registry import ServiceRegistry
from microcorex.logging_setup import setup_logging, get_logger

__all__ = [
    "MicroCoreConfig",
    "AppConfig",
    "ServerConfig",
    "NacosConfig",
    "DatabaseConfig",
    "ConfigLoader",
    "AppService",
    "GrpcServerBase",
    "BaseGrpcClient",
    "ServiceRegistry",
    "setup_logging",
    "get_logger",
]
