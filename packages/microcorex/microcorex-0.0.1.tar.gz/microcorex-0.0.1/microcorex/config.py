import os
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import Field, BaseModel, ConfigDict

from pydantic_settings import BaseSettings
import yaml
import __main__

from microcorex.utils import get_local_ip


class AppConfig(BaseModel):
    name: str = Field(..., description="Application name")
    env: str = Field(..., description="Runtime environment")
    logLevel: str = Field(default="INFO", description="Log level")

    model_config = ConfigDict(extra='allow')


class ServerConfig(BaseModel):
    ip: str = Field(default="", description="Service IP address")
    servicePort: int = Field(..., description="HTTP service port")
    grpcPort: int = Field(..., description="gRPC service port")

    model_config = ConfigDict(extra='allow')


class NacosConfig(BaseModel):
    host: Optional[str] = Field(default="127.0.0.1", description="Nacos server address")
    port: Optional[int] = Field(default=8848, description="Nacos server port")
    groupName: Optional[str] = Field(default="DEFAULT_GROUP", description="Nacos service group name")
    heartbeatInterval: Optional[int] = Field(default=5, description="Heartbeat interval in seconds")
    namespace: Optional[str] = Field(default="", description="Nacos namespace")
    username: Optional[str] = Field(default="", description="Nacos username")
    password: Optional[str] = Field(default="", description="Nacos password")

    model_config = ConfigDict(extra='allow')


class DatabaseConfig(BaseModel):
    url: str


class MicroCoreConfig(BaseSettings):
    """Microservice core configuration"""
    # Allow services to add custom configuration fields in config.yaml, microcore will preserve them as-is
    model_config = ConfigDict(extra='allow')

    app: AppConfig = AppConfig(name="service", env="dev")
    server: ServerConfig = ServerConfig(servicePort=8001, grpcPort=8002)
    nacos: NacosConfig = NacosConfig()
    database: DatabaseConfig = DatabaseConfig(url="")
    services: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Service discovery configuration")


def load_config():
    """Automatically load config/config_<env>.yaml file from the current service directory"""
    env = os.getenv("APP_ENV", "dev")

    # Get current script path
    main_path = Path(os.path.abspath(__main__.__file__))
    service_root = main_path.parent

    # Build configuration file path
    config_path = service_root / "config" / f"config_{env}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"❌ Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    config = MicroCoreConfig(**data)

    service_port = os.getenv("SERVICE_PORT", config.server.servicePort)
    config.server.servicePort = int(service_port)

    if not config.server.ip:
        config.server.ip = get_local_ip()

    return config
