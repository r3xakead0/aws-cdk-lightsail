"""Lightsail stack definition."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import aws_cdk as cdk
from aws_cdk import aws_lightsail as lightsail

MAX_USER_DATA_BYTES = 64 * 1024  # 64 KiB Lightsail limit
DEFAULT_INSTANCE_NAME = "lightsail-server"
DEFAULT_REGION = "us-east-1"
STATIC_IP_SUFFIX = "static-ip"


def _sanitize_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9-]", "-", value.lower())
    normalized = normalized.strip("-")
    return normalized or "lightsail"


def _truncate(value: str, max_length: int = 255) -> str:
    return value[:max_length]


def _load_user_data(path_value: str | None) -> str | None:
    if not path_value:
        return None

    candidate = Path(path_value).expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate

    if not candidate.exists():
        raise FileNotFoundError(
            f"The user data file '{candidate}' does not exist."
        )

    content = candidate.read_text()
    byte_length = len(content.encode("utf-8"))
    if byte_length > MAX_USER_DATA_BYTES:
        raise ValueError(
            "User data exceeds the 64 KiB Lightsail limit."
        )

    return content


class AwsCdkLightsailStack(cdk.Stack):
    """Stack that provisions a Lightsail instance and attaches a static IP."""

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        instance_base_name = (
            self.node.try_get_context("instanceName") or DEFAULT_INSTANCE_NAME
        )
        availability_zone = self._resolve_availability_zone()
        user_data_path = self.node.try_get_context("userDataFile")
        user_data = _load_user_data(user_data_path)

        normalized_instance = _sanitize_name(instance_base_name)
        normalized_stack = _sanitize_name(self.stack_name)
        resource_prefix = _truncate(f"{normalized_instance}-{normalized_stack}")

        instance_name = resource_prefix
        static_ip_name = _truncate(f"{resource_prefix}-{STATIC_IP_SUFFIX}")

        instance_props: dict[str, Any] = {
            "blueprint_id": "ubuntu_22_04",
            "bundle_id": "medium_2_0",
            "instance_name": instance_name,
            "availability_zone": availability_zone,
            "key_pair_name": "LightsailDefaultKeyPair",
            "tags": [cdk.CfnTag(key="Stack", value=self.stack_name)],
        }
        if user_data:
            instance_props["user_data"] = user_data

        instance = lightsail.CfnInstance(self, "LightsailInstance", **instance_props)

        static_ip = lightsail.CfnStaticIp(
            self,
            "LightsailStaticIpResource",
            static_ip_name=static_ip_name,
            attached_to=instance.instance_name,
        )
        static_ip.add_dependency(instance)

        cdk.CfnOutput(
            self,
            "LightsailInstanceName",
            value=instance.instance_name,
            description="Final Lightsail instance name",
        )
        cdk.CfnOutput(
            self,
            "LightsailStaticIp",
            value=static_ip.attr_ip_address,
            description="Allocated static IP address",
        )
        cdk.CfnOutput(
            self,
            "LightsailPublicDns",
            value=instance.attr_public_ip_address,
            description=(
                "Lightsail does not expose a hostname via CloudFormation, so the public IP is repeated."
            ),
        )

    def _resolve_availability_zone(self) -> str:
        context_az = self.node.try_get_context("availabilityZone")
        if context_az:
            return str(context_az)

        region = cdk.Stack.of(self).region or DEFAULT_REGION
        if cdk.Token.is_unresolved(region):
            region = DEFAULT_REGION
        return f"{region}a"
