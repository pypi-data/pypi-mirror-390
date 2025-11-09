"""
Nacos Configuration Manager

Provides encapsulated operations for configuration center, including configuration
pulling, publishing, deletion, and monitoring functionalities.
"""

from typing import Optional, Callable
from v2.nacos import NacosConfigService, ClientConfigBuilder, ConfigParam

from microcorex.logging_setup import get_logger

logger = get_logger(__name__)


class NacosConfigError(Exception):
    """Nacos configuration exception"""
    pass


class NacosConfigManager:
    """
    Nacos Configuration Manager

    Encapsulates Nacos Configuration Center operations, providing configuration
    pulling, publishing, deletion, and monitoring functionalities.
    Supports configuration caching and disaster recovery.
    """

    def __init__(self, client_config):
        """
        Initialize configuration manager

        Args:
            client_config: Nacos client configuration
        """
        self.client_config = client_config
        self.config_client: Optional[NacosConfigService] = None
        self._listeners = {}  # Store listeners {(data_id, group): [listeners]}

    async def initialize(self):
        """Initialize configuration client"""
        try:
            self.config_client = await NacosConfigService.create_config_service(
                self.client_config
            )
            logger.info("Nacos configuration client initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"Nacos configuration client initialization failed: {e}")
            return False

    async def get_config(
        self,
        data_id: str,
        group: str = "DEFAULT_GROUP"
    ) -> Optional[str]:
        """
        Get configuration

        Priority strategy:
        1. Read from local failover directory
        2. Get from server (save to snapshot after success)
        3. Read from snapshot directory

        Args:
            data_id: Configuration Data ID
            group: Configuration group name

        Returns:
            Configuration content, returns None on failure
        """
        if not self.config_client:
            logger.error("Configuration client not initialized")
            return None

        try:
            content = await self.config_client.get_config(
                ConfigParam(data_id=data_id, group=group)
            )
            if content:
                logger.info(f"Configuration retrieved successfully: data_id={data_id}, group={group}")
            else:
                logger.warning(f"Configuration does not exist: data_id={data_id}, group={group}")
            return content
        except Exception as e:
            logger.error(f"Failed to get configuration: data_id={data_id}, group={group}, error={e}")
            return None

    async def publish_config(
        self,
        data_id: str,
        group: str,
        content: str
    ) -> bool:
        """
        Publish configuration

        Creates configuration if it doesn't exist, updates content if it exists.

        Args:
            data_id: Configuration Data ID
            group: Configuration group name
            content: Configuration content

        Returns:
            Returns True on success, False on failure
        """
        if not self.config_client:
            logger.error("Configuration client not initialized")
            return False

        try:
            result = await self.config_client.publish_config(
                ConfigParam(data_id=data_id, group=group, content=content)
            )
            if result:
                logger.info(f"Configuration published successfully: data_id={data_id}, group={group}")
            else:
                logger.error(f"Configuration publishing failed: data_id={data_id}, group={group}")
            return result
        except Exception as e:
            logger.error(f"Configuration publishing exception: data_id={data_id}, group={group}, error={e}")
            return False

    async def remove_config(
        self,
        data_id: str,
        group: str = "DEFAULT_GROUP"
    ) -> bool:
        """
        Remove configuration

        Args:
            data_id: Configuration Data ID
            group: Configuration group name

        Returns:
            Returns True on success, False on failure
        """
        if not self.config_client:
            logger.error("Configuration client not initialized")
            return False

        try:
            result = await self.config_client.remove_config(
                ConfigParam(data_id=data_id, group=group)
            )
            if result:
                logger.info(f"Configuration removed successfully: data_id={data_id}, group={group}")
            else:
                logger.error(f"Configuration removal failed: data_id={data_id}, group={group}")
            return result
        except Exception as e:
            logger.error(f"Configuration removal exception: data_id={data_id}, group={group}, error={e}")
            return False

    async def add_listener(
        self,
        data_id: str,
        group: str,
        listener: Callable
    ):
        """
        Add configuration listener

        Triggers callback when configuration changes or is deleted. If configuration exists,
        triggers callback immediately.

        Args:
            data_id: Configuration Data ID
            group: Configuration group name
            listener: Configuration monitoring callback function (tenant, data_id, group, content) -> None
        """
        if not self.config_client:
            logger.error("Configuration client not initialized")
            return

        try:
            await self.config_client.add_listener(
                data_id=data_id,
                group=group,
                listener=listener
            )

            # Record listener
            key = (data_id, group)
            if key not in self._listeners:
                self._listeners[key] = []
            self._listeners[key].append(listener)

            logger.info(f"Configuration listener added successfully: data_id={data_id}, group={group}")
        except Exception as e:
            logger.error(f"Failed to add configuration listener: data_id={data_id}, group={group}, error={e}")

    async def remove_listener(
        self,
        data_id: str,
        group: str,
        listener: Callable
    ):
        """
        Remove configuration listener

        Args:
            data_id: Configuration Data ID
            group: Configuration group name
            listener: Configuration monitoring callback function
        """
        if not self.config_client:
            logger.error("Configuration client not initialized")
            return

        try:
            await self.config_client.remove_listener(
                data_id=data_id,
                group=group,
                listener=listener
            )

            # Remove record
            key = (data_id, group)
            if key in self._listeners and listener in self._listeners[key]:
                self._listeners[key].remove(listener)

            logger.info(f"Configuration listener removed successfully: data_id={data_id}, group={group}")
        except Exception as e:
            logger.error(f"Failed to remove configuration listener: data_id={data_id}, group={group}, error={e}")

    async def shutdown(self):
        """Shutdown configuration client"""
        if self.config_client:
            try:
                await self.config_client.shutdown()
                logger.info("Nacos configuration client closed")
            except Exception as e:
                logger.error(f"Failed to close configuration client: {e}")
