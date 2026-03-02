# AWS CDK Lightsail

Python project managed with [`uv`](https://docs.astral.sh/uv/) that deploys an Amazon Lightsail instance (Ubuntu 22.04, Medium bundle 2 vCPU / 4 GB) and attaches a static IP. The stack references the existing `LightsailDefaultKeyPair` to enable SSH access.

## Requirements
- Python 3.11 and `uv` ≥ 0.4 (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`).
- Node.js 20/22/24 and the AWS CDK CLI ≥ 2.1105.0 (`npm install -g aws-cdk@latest`).
- AWS credentials configured (profile or environment). Ensure the `LightsailDefaultKeyPair` is present in the target region.

## Setup and bootstrap
```bash
uv sync              # creates/updates the virtual environment
uv run cdk bootstrap # run once per account/region to bootstrap CDK resources
```

## Common commands
```bash
uv run cdk synth         # generate the CloudFormation template
uv run cdk diff          # show changes vs. deployed stack
uv run cdk deploy        # create/update the Lightsail resources
uv run cdk destroy       # delete all provisioned resources
```
All commands run inside the managed virtualenv via `uv run`.

## Configurable context
Override values at synth/deploy time with `-c key=value`:

| Key              | Description                                                                                      | Default                            |
|------------------|--------------------------------------------------------------------------------------------------|------------------------------------|
| `instanceName`   | Friendly prefix for the Lightsail instance and static IP. Combined with the stack name.          | `lightsail-server`                 |
| `availabilityZone` | Lightsail availability zone (e.g., `us-east-1b`).                                              | `<REGION>a` (falls back to `us-east-1a`). |
| `userDataFile`   | Path to a `*.sh` or `cloud-init` file. Must exist and be smaller than 64 KiB.                    | _(empty)_                          |

Example:
```bash
uv run cdk deploy \
  -c instanceName=blog-server \
  -c availabilityZone=us-east-1b \
  -c userDataFile=user-data/sample-user-data.sh
```

## Sample user data file
`user-data/sample-user-data.sh` updates the OS, installs NGINX, and publishes a landing page that prints the instance hostname plus its current public/static IPv4 (queried from the instance metadata service). Duplicate or adjust this script and point the stack to your version via `-c userDataFile=...`.

## Stack outputs
- `LightsailInstanceName`: final Lightsail resource name.
- `LightsailStaticIp`: allocated static IP (also visible in the Lightsail console).
- `LightsailPublicDns`: public IP reported by Lightsail (CloudFormation does not expose a hostname).

## GitHub Actions workflows
Located in `.github/workflows` and triggered manually via **Run workflow** in GitHub:

1. **Deploy Lightsail Stack** (`deploy.yml`): installs toolchains, applies optional context overrides, and runs `uv run cdk deploy --require-approval never`.
2. **Destroy Lightsail Stack** (`destroy.yml`): mirrors the setup but runs `uv run cdk destroy --force`.

Both workflows expect AWS credentials to be available as repo/organization secrets named `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and (if using temporary credentials) `AWS_SESSION_TOKEN`. Optional manual inputs let you override `instanceName`, `availabilityZone`, and `userDataFile`, plus the AWS region (default `us-east-1`).

## Cleanup
To avoid ongoing charges, run `uv run cdk destroy` and confirm in the Lightsail console that both the instance and static IP were removed.

## License
This project is released under the MIT License – see [LICENSE](LICENSE) for details.
