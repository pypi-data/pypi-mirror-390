
"""
Configuration Loader

Supports multi-layer configuration loading and merging with priority mechanism.
Priority: Environment Variables > Nacos Configuration Center > Local YAML Files
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Callable, List, Type, TypeVar
import __main__

from microcorex.config import MicroCoreConfig
from microcorex.nacos_config_manager import NacosConfigManager
from microcorex.utils import get_local_ip
from microcorex.logging_setup import get_logger

logger = get_logger(__name__)

# Define a type variable that must be MicroCoreConfig or its subclass
T = TypeVar('T', bound=MicroCoreConfig)

class ConfigLoadError(Exception):
    """Configuration loading exception"""
    pass

class ConfigLoader:
    """
    Configuration Loader

    Supports multi-layer configuration loading and merging:
    1. Load local YAML file (base configuration)
    2. Pull configuration from Nacos Configuration Center (overrides local config)
    3. Read environment variables (final override)

    Supports configuration hot reloading and change monitoring.
    """

    def __init__(self, config_class: Type[T] = MicroCoreConfig):
        """
        Initialize configuration loader

        Args:
            config_class: Pydantic model class for parsing configuration, defaults to MicroCoreConfig
        """
        self.config_model: Type[T] = config_class
        self.config: Optional[T] = None
        self.nacos_config_manager: Optional[NacosConfigManager] = None
        self.config_change_listeners: List[Callable] = []  # Configuration change listeners

    async def load_config(self) -> T:
        """
        Load configuration (by priority)

        Returns:
            Loaded configuration object
        """
        try:
            # 1. Load local YAML configuration
            logger.info("📄 Loading local YAML configuration...")
            config = self._load_yaml_config()

            # 2. Pull and merge configuration from Nacos
            if config.nacos.host:
                logger.info("☁️  Pulling configuration from Nacos Configuration Center...")
                nacos_config_dict = await self._load_nacos_config(config)
                if nacos_config_dict:
                    config = self._merge_config(config, nacos_config_dict)
                    logger.info("✅ Nacos configuration merged successfully")

            # 3. Environment variable overrides
            logger.info("🔧 Applying environment variable overrides...")
            config = self._apply_env_overrides(config)

            # 4. Post-processing
            config = self._post_process_config(config)

            self.config = config
            logger.info("✅ Configuration loading completed")
            return config

        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            raise ConfigLoadError(f"Configuration loading failed: {e}")

    def _load_yaml_config(self) -> T:
        """
        Load local YAML configuration file

        Returns:
            Configuration object
        """
        env = os.getenv("APP_ENV", "dev").lower()

        # Get current script path
        main_path = Path(os.path.abspath(__main__.__file__))
        service_root = main_path.parent

        # Construct configuration file path
        config_path = service_root / "config" / f"config_{env}.yaml"

        if not config_path.exists():
            raise ConfigLoadError(f"Configuration file does not exist: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Use the provided config_model for parsing
        config = self.config_model(**data)
        logger.info(f"Local configuration loaded successfully: {config_path}")
        return config

    async def _load_nacos_config(self, base_config: T) -> Optional[dict]:
        """
        Pull configuration from Nacos Configuration Center

        Args:
            base_config: Base configuration (for connecting to Nacos)

        Returns:
            Nacos configuration dictionary, returns None on failure
        """
        try:
            # Initialize Nacos Configuration Manager
            from v2.nacos import ClientConfigBuilder

            client_config = (
                ClientConfigBuilder()
                .username(base_config.nacos.username)
                .password(base_config.nacos.password)
                .server_address(f'{base_config.nacos.host}:{base_config.nacos.port}')
                .namespace_id(base_config.nacos.namespace if base_config.nacos.namespace else "public")
                .log_level('INFO')
                .build()
            )

            self.nacos_config_manager = NacosConfigManager(client_config)
            success = await self.nacos_config_manager.initialize()
            if not success:
                logger.warning("Using local configuration")
                return None

            # Pull configuration (using service name as data_id)
            data_id = base_config.app.name
            group = base_config.nacos.groupName

            content = await self.nacos_config_manager.get_config(
                data_id=data_id,
                group=group
            )

            if content:
                # Parse YAML configuration
                nacos_config = yaml.safe_load(content)
                logger.info(f"Nacos configuration pulled successfully: data_id={data_id}, group={group}")
                return nacos_config
            else:
                logger.warning(f"Nacos configuration does not exist: data_id={data_id}, group={group}")
                return None

        except Exception as e:
            logger.error(f"Failed to pull configuration from Nacos: {e}")
            return None

    def _merge_config(self, base: T, override: dict) -> T:
        """
        Merge configuration (deep merge)

        Args:
            base: Base configuration object
            override: Override configuration dictionary

        Returns:
            Merged configuration object
        """
        # Convert base configuration to dictionary
        base_dict = base.model_dump()

        # Deep merge
        merged_dict = self._deep_merge(base_dict, override)

        # Convert back to configuration object
        return self.config_model(**merged_dict)

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """
        Deep merge dictionaries

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Direct override
                result[key] = value

        return result

    def _apply_env_overrides(self, config: T) -> T:
        """
        Apply environment variable overrides

        Supported environment variables:
        - APP_NAME, APP_ENV, APP_LOG_LEVEL
        - SERVICE_PORT, GRPC_PORT, SERVER_IP
        - NACOS_HOST, NACOS_PORT, NACOS_NAMESPACE, NACOS_USERNAME, NACOS_PASSWORD
        - DATABASE_URL

        Args:
            config: Configuration object

        Returns:
            Configuration object with environment variables applied
        """
        # App configuration
        if os.getenv("APP_NAME"):
            config.app.name = os.getenv("APP_NAME")
        if os.getenv("APP_ENV"):
            config.app.env = os.getenv("APP_ENV")
        if os.getenv("APP_LOG_LEVEL"):
            config.app.logLevel = os.getenv("APP_LOG_LEVEL")

        # Server configuration
        if os.getenv("SERVER_IP"):
            config.server.ip = os.getenv("SERVER_IP")
        if os.getenv("SERVICE_PORT"):
            config.server.servicePort = int(os.getenv("SERVICE_PORT"))
        if os.getenv("GRPC_PORT"):
            config.server.grpcPort = int(os.getenv("GRPC_PORT"))

        # Nacos configuration
        if os.getenv("NACOS_HOST"):
            config.nacos.host = os.getenv("NACOS_HOST")
        if os.getenv("NACOS_PORT"):
            config.nacos.port = int(os.getenv("NACOS_PORT"))
        if os.getenv("NACOS_NAMESPACE"):
            config.nacos.namespace = os.getenv("NACOS_NAMESPACE")
        if os.getenv("NACOS_USERNAME"):
            config.nacos.username = os.getenv("NACOS_USERNAME")
        if os.getenv("NACOS_PASSWORD"):
            config.nacos.password = os.getenv("NACOS_PASSWORD")

        # Database configuration
        if os.getenv("DATABASE_URL"):
            config.database.url = os.getenv("DATABASE_URL")

        return config

    def _post_process_config(self, config: T) -> T:
        """
        Configuration post-processing

        Args:
            config: Configuration object

        Returns:
            Processed configuration object
        """
        # Automatically get local IP
        if not config.server.ip:
            config.server.ip = get_local_ip()
            logger.info(f"Automatically obtained local IP: {config.server.ip}")

        return config

    async def start_watch(self):
        """
        Start configuration monitoring (hot reload)

        Monitors Nacos configuration changes, automatically reloads configuration and notifies listeners.
        """
        if not self.nacos_config_manager or not self.config:
            logger.warning("Nacos configuration manager not initialized, cannot start configuration monitoring")
            return

        try:
            data_id = self.config.app.name
            group = self.config.nacos.groupName

            await self.nacos_config_manager.add_listener(
                data_id=data_id,
                group=group,
                listener=self._on_config_change
            )

            logger.info(f"✅ Configuration monitoring started: data_id={data_id}, group={group}")

        except Exception as e:
            logger.error(f"Failed to start configuration monitoring: {e}")

    async def _on_config_change(self, tenant: str, data_id: str, group: str, content: str):
        """
        Configuration change callback

        Args:
            tenant: Tenant ID
            data_id: Configuration ID
            group: Configuration group
            content: New configuration content
        """
        logger.info(f"🔄 Configuration change detected: data_id={data_id}, group={group}")

        try:
            # Reload configuration
            new_config = await self.load_config()

            # Notify all listeners
            for listener in self.config_change_listeners:
                try:
                    await listener(new_config)
                except Exception as e:
                    logger.error(f"Configuration change listener execution failed: {e}")

            logger.info("✅ Configuration hot reload completed")

        except Exception as e:
            logger.error(f"Configuration hot reload failed: {e}")

    def add_config_change_listener(self, listener: Callable):
        """
        Add configuration change listener

        Args:
            listener: Listener function (new_config) -> None
        """
        self.config_change_listeners.append(listener)

    async def shutdown(self):
        """Shutdown configuration loader"""
        if self.nacos_config_manager:
            await self.nacos_config_manager.shutdown()
