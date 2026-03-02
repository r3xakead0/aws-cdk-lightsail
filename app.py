#!/usr/bin/env python3
"""CDK entrypoint for the Lightsail stack."""

from __future__ import annotations

import os

import aws_cdk as cdk

from aws_cdk_lightsail import AwsCdkLightsailStack


def main() -> None:
    """Instantiate the app and synthesize the Lightsail stack."""

    app = cdk.App()

    env = cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
    )

    AwsCdkLightsailStack(app, "AwsCdkLightsailStack", env=env)

    app.synth()


if __name__ == "__main__":
    main()
