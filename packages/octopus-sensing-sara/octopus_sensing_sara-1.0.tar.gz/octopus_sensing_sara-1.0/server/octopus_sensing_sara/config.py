"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Literal
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Sensing module settings
    sensing_address: str = Field(
        default="localhost", description="sensing server endpoint address"
    )

    sensing_port: int = Field(
        default=9331, description="sensing server endpoint port. Sensing server is listening on this port to receive markers"
    )

    sensors_module: str = Field(
        default='octopus_sensing_sara.sensing_module.sensors', description="A module that includes a function for defining sensors"
    )

    sensors_function: str = Field(
        default="define_sensors", description="A function for defining sensors"
    )

    sensors_names: str = Field(
        default="test_device", description="The list of sensors name. It should be matched with sensors in sensors_module. e.g. device1, device2 "
    )

    data_endpoint_address: str = Field(
        default="localhost", description="data endpoint server address"
    )

    data_endpoint_port: int = Field(
        default=9330, description="data endpoint server port"
    )

    # Processing module settings
    processing_address: str = Field(
        default="localhost", description="processing server endpoint address"
    )

    processing_port: int = Field(
        default=9332, description = "processing server endpoint port"
    )

    predict_module: str = Field(
        default='octopus_sensing_sara.perception_module.predict', description="A module that includes a function for "
    )

    predict_function: str = Field(
        default="define_sensors", description="A function for predicting"
    )

    prediction_window: int = Field(
        default=3, description="The time window for prediction in seconds"
    )

