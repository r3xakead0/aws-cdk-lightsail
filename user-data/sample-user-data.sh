#!/bin/bash
# Fail fast on errors/unbound vars; pipefail unsupported in sh-compatible runners
set -euo
LOG_FILE="/var/log/user-data-bootstrap.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[user-data] Starting bootstrap at $(date --iso-8601=seconds)"

apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y nginx

SERVER_HOSTNAME="$(hostname)"
PUBLIC_IPV4="$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || hostname -I | awk '{print $1}')"

cat <<HTML >/var/www/html/index.html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Lightsail Provisioned via CDK</title>
    <style>
      body { font-family: sans-serif; margin: 3rem; background: #0b1f2a; color: #f4f4f4; }
      .card { background: #112f3f; border-radius: 8px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
      h1 { margin-top: 0; color: #5cc9f5; }
      code { background: rgba(255,255,255,0.1); padding: 0.2rem 0.4rem; border-radius: 4px; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Lightsail ready!</h1>
      <p>This server was provisioned by <code>aws-cdk-lightsail</code></p>
      <p>Hostname: <code>${SERVER_HOSTNAME}</code></p>
      <p>Public IPv4 (static): <code>${PUBLIC_IPV4}</code></p>
    </div>
  </body>
</html>
HTML

systemctl enable --now nginx

echo "[user-data] Completed bootstrap at $(date --iso-8601=seconds)"
