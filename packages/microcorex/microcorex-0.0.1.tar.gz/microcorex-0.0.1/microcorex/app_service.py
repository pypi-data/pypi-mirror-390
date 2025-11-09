"""
Microservice Application Service Manager

Provides unified service startup, registration, and lifecycle management.
Supports concurrent operation of FastAPI and gRPC in the same process.
"""

import asyncio
import signal
from typing import Optional, Type
from datetime import datetime
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from colorama import Fore, Style

from microcorex.config import MicroCoreConfig
from microcorex.config_loader import ConfigLoader
from microcorex.nacos_registrar import NacosRegistrar
from microcorex.grpc_server import GrpcServerBase
from microcorex.logging_setup import setup_logging, get_logger

logger = get_logger(__name__)


class AppService:
    """
    Microservice Application Service Manager

    Provides unified service startup, registration, and lifecycle management.
    Supports concurrent operation of FastAPI and gRPC in the same process.
    """

    def __init__(
            self,
            fastapi_app: FastAPI,
            grpc_server: Optional[GrpcServerBase] = None,
            config: Optional[MicroCoreConfig] = None,
            config_class: Type[MicroCoreConfig] = MicroCoreConfig  # Parameter for injecting custom configuration class
    ):
        """
        Initialize the application service manager

        Args:
            fastapi_app: FastAPI application instance
            grpc_server: gRPC server instance (optional)
            config: Configuration object (optional, auto-loaded if not provided)
            config_class: Pydantic model class for parsing configuration (optional)
        """
        self.fastapi_app = fastapi_app
        self.grpc_server = grpc_server
        self.config = config
        # Pass config_class to ConfigLoader
        self.config_loader = ConfigLoader(config_class=config_class)
        self.nacos_registrar: Optional[NacosRegistrar] = None
        self._shutdown_event = asyncio.Event()
        self._uvicorn_server: Optional[uvicorn.Server] = None

    async def initialize(self):
        """Initialize the service"""
        try:
            # 1. Load configuration
            if not self.config:
                logger.info("📋 Loading configuration...")
                self.config = await self.config_loader.load_config()

            # 2. Setup logging
            setup_logging(self.config.app.logLevel)

            # 3. Save configuration to FastAPI state for use by routes
            if hasattr(self.fastapi_app, 'state'):
                # Use model_dump() to ensure all nested models are properly converted to dictionaries
                self.fastapi_app.state.config = self.config

            # 4. Initialize Nacos registrar
            if self.config.nacos.host:
                self.nacos_registrar = NacosRegistrar(self.config)

            logger.info("✅ Service initialization completed")

        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            raise

    async def start(self):
        """Start the service"""
        try:
            # 1. Initialize
            await self.initialize()

            # 2. Register with Nacos
            if self.nacos_registrar:
                try:
                    await self.nacos_registrar.register_instance()
                except Exception as e:
                    logger.warning(f"Nacos service registration failed: {e}, continuing service startup")

            # 3. Start configuration listening (hot reload)
            if self.config_loader.nacos_config_manager:
                await self.config_loader.start_watch()

            # 4. Register signal handlers
            self._register_signal_handlers()

            # 5. Print startup success information
            self._print_startup_banner()

            # 6. Start FastAPI + gRPC concurrently
            await self._start_servers()

        except Exception as e:
            logger.error(f"Service startup failed: {e}")
            await self.shutdown()
            raise

    async def _start_servers(self):
        """Start FastAPI and gRPC servers concurrently"""
        tasks = []

        # Start FastAPI
        fastapi_task = asyncio.create_task(self._run_fastapi())
        tasks.append(fastapi_task)

        # Start gRPC (if configured)
        if self.grpc_server:
            grpc_task = asyncio.create_task(self._run_grpc())
            tasks.append(grpc_task)

        # Wait for shutdown signal
        shutdown_task = asyncio.create_task(self._shutdown_event.wait())
        tasks.append(shutdown_task)

        # Wait for any task to complete
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Cancel other tasks
        for task in pending:
            task.cancel()

        # Graceful shutdown
        await self.shutdown()

    async def _run_fastapi(self):
        """Run FastAPI server"""
        try:
            config = uvicorn.Config(
                self.fastapi_app,
                host="0.0.0.0",
                port=self.config.server.servicePort,
                log_config=None,  # Use custom logging
                loop="asyncio"
            )
            self._uvicorn_server = uvicorn.Server(config)
            await self._uvicorn_server.serve()
        except asyncio.CancelledError:
            logger.info("FastAPI server task cancelled")
        except Exception as e:
            logger.error(f"FastAPI server exception: {e}")
            self._shutdown_event.set()

    async def _run_grpc(self):
        """Run gRPC server"""
        try:
            await self.grpc_server.start()
            await self.grpc_server.wait_for_termination()
        except asyncio.CancelledError:
            logger.info("gRPC server task cancelled")
        except Exception as e:
            logger.error(f"gRPC server exception: {e}")
            self._shutdown_event.set()

    def _register_signal_handlers(self):
        """Register signal handlers"""

        def handle_signal(signum, _frame):
            logger.info(f"Received signal {signum}, starting graceful shutdown...")
            self._shutdown_event.set()

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Starting service shutdown...")

        try:
            # 1. Deregister from Nacos
            if self.nacos_registrar:
                await self.nacos_registrar.deregister_instance()

            # 2. Stop gRPC server
            if self.grpc_server:
                await self.grpc_server.stop(grace_period=10)

            # 3. Stop FastAPI server
            if self._uvicorn_server:
                self._uvicorn_server.should_exit = True

            # 4. Close configuration loader
            if self.config_loader:
                await self.config_loader.shutdown()

            logger.info("✅ Service shutdown completed")

        except Exception as e:
            logger.error(f"Error during service shutdown: {e}")

    def _print_startup_banner(self):
        """Print startup success banner"""
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(Fore.GREEN + "─────────────────────────────────────────────")
        print(Fore.CYAN + f"🚀 {self.config.app.name} Started Successfully!")
        print(Fore.YELLOW + "─────────────────────────────────────────────")
        print(f"🧩 Environment: {self.config.app.env}")
        print(f"🌐 HTTP Service: {self.config.server.ip}:{self.config.server.servicePort}")
        print(f"📚 API Docs: http://{self.config.server.ip}:{self.config.server.servicePort}/docs")

        if self.grpc_server:
            print(f"⚡ gRPC Service: {self.config.server.ip}:{self.config.server.grpcPort}")

        if self.config.nacos.host:
            print(f"📦 Registry: {self.config.nacos.host}:{self.config.nacos.port}")

        print(f"🕒 Start Time: {start_time}")
        print(Fore.GREEN + "─────────────────────────────────────────────" + Style.RESET_ALL)
