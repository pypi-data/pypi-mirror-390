# IMPORTANT
# After changing this file, run `missim generate`
# To re-generate the json schemas

import json
from enum import Enum
from typing import Any, Literal, Union
import yaml
import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

MISSIM_CONFIG_FILE_NAME = "missim.yml"
MISSIM_SCHEMA_URL = "https://greenroom-robotics.github.io/missim/schemas/missim.schema.json"


def join_lines(*lines: str) -> str:
    return "\n".join(lines)


class Mode(str, Enum):
    UE_EDITOR = "ue-editor"
    UE_STANDALONE = "ue-standalone"
    LOW_FIDELITY = "low-fidelity"

    def __str__(self):
        return self.value


class LogLevel(str, Enum):
    INFO = "info"
    DEBUG = "debug"

    def __str__(self):
        return self.value


class Network(str, Enum):
    SHARED = "shared"
    HOST = "host"

    def __str__(self):
        return self.value


class DiscoverySimple(BaseModel):
    type: Literal["simple"] = "simple"
    ros_domain_id: int = Field(
        default=0,
        description="ROS domain ID",
    )
    own_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface address of the primary network interface. This is where DDS traffic will route to.",
    )
    discovery_range: Literal["subnet", "localhost"] = Field(
        default="localhost",
        description="Discovery range: 'localhost' sets ROS_AUTOMATIC_DISCOVERY_RANGE to LOCALHOST, 'subnet' sets it to SUBNET.",
    )


class DiscoveryFastDDS(BaseModel):
    type: Literal["fastdds"] = "fastdds"
    with_discovery_server: bool = Field(
        default=True, description="Run the discovery server. It will bind to 0.0.0.0:11811"
    )
    discovery_server_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface of the discovery server. Assumes port of 11811",
    )
    own_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface address of the primary network interface. This is where DDS traffic will route to.",
    )


class DiscoveryZenoh(BaseModel):
    type: Literal["zenoh"] = "zenoh"
    with_discovery_server: bool = Field(default=True, description="Run the zenoh router")
    discovery_server_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface of the discovery server. Assumes port of 11811",
    )


Discovery = Union[DiscoveryZenoh, DiscoveryFastDDS, DiscoverySimple]


class MissimConfig(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            Mode: lambda v: v.value,
            LogLevel: lambda v: v.value,
            Network: lambda v: v.value,
        },
    )
    log_level: LogLevel = LogLevel.INFO
    mode: Mode = Mode.LOW_FIDELITY
    network: Network = Network.HOST
    use_https: bool = False
    components: dict = Field(default_factory=dict)
    prod: bool = False
    log_directory: str = "~/greenroom/missim/logs"
    recording_directory: str = "~/greenroom/missim/recordings"
    charts_directory: str = "~/greenroom/charts"
    discovery: Discovery = Field(
        default_factory=DiscoverySimple,
        discriminator="type",
    )


def find_config() -> Path:
    """Returns the path to the .config/greenroom directory"""
    return Path.home().joinpath(".config/greenroom")


def get_path():
    return find_config() / MISSIM_CONFIG_FILE_NAME


def parse(config: dict[str, Any]) -> MissimConfig:
    return MissimConfig(**config)


def read() -> MissimConfig:
    """Reads the missim.yml file and returns a MissimConfig object."""
    path = get_path()
    with open(path) as stream:
        return parse(yaml.safe_load(stream))


def read_env() -> MissimConfig:
    """Reads the MISSIM_CONFIG environment variable and returns a MissimConfig object."""
    missim_config_str = os.environ.get("MISSIM_CONFIG")
    if missim_config_str is None:
        raise ValueError("MISSIM_CONFIG environment variable is not set")
    return parse(yaml.safe_load(missim_config_str))


def write(config: MissimConfig):
    path = get_path()
    # Make the parent dir if it doesn't exist
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w") as stream:
        print(f"Writing: {path}")
        headers = f"# yaml-language-server: $schema={MISSIM_SCHEMA_URL}"
        data = "\n".join([headers, yaml.dump(json.loads(config.model_dump_json()))])
        stream.write(data)


def serialise(config: MissimConfig):
    return yaml.dump(config.model_dump_json())
