# AWS CDK Lightsail

Proyecto base en Python administrado con `uv` que despliega una instancia de Amazon Lightsail (Ubuntu 22.04, bundle Small 2 vCPU/4 GB) y le asigna una IP estática. El stack referencia el par de claves existente `LightsailDefaultKeyPair` para permitir el acceso por SSH.

## Requisitos
- Python 3.11 + [`uv`](https://docs.astral.sh/uv/) ≥ 0.4 (`pip install uv` o `curl -LsSf https://astral.sh/uv/install.sh | sh`).
- Node.js 20/22/24 y la CLI de AWS CDK ≥ 2.1105.0 (`npm install -g aws-cdk@latest`).
- Credenciales de AWS configuradas (perfil o variables). Asegúrate de que el par `LightsailDefaultKeyPair` existe en la región objetivo.

## Instalación y bootstrap
```bash
uv sync              # crea/actualiza el entorno virtual en .venv
uv run cdk bootstrap # prepara la cuenta/región si aún no tienen CDK bootstrap
```
> `cdk bootstrap` solo es necesario la primera vez por cuenta/región.

## Comandos principales
```bash
uv run cdk synth         # genera la plantilla CloudFormation
uv run cdk diff          # compara con el estado desplegado
uv run cdk deploy        # crea/actualiza la instancia Lightsail
uv run cdk destroy       # elimina los recursos creados
```
Los comandos se ejecutan dentro del entorno virtual gracias a `uv run`.

## Contexto configurable
Puedes sobreescribir valores en tiempo de síntesis/despliegue vía `-c clave=valor`:

| Clave             | Descripción                                                                 | Valor por defecto            |
|-------------------|-----------------------------------------------------------------------------|------------------------------|
| `instanceName`    | Prefijo legible para el nombre del servidor e IP estática. Se combina con el nombre del stack para evitar colisiones. | `lightsail-server` |
| `availabilityZone`| Zona de disponibilidad de Lightsail (por ejemplo `us-east-1b`).             | `us-east-1a` si la región es indeterminada; de lo contrario `<REGION>a`. |
| `userDataFile`    | Ruta a un archivo `*.sh` o `*.cloud-init` para inicializar la instancia. Debe existir y pesar < 64 KiB. | _Vacío_ |

Ejemplo:
```bash
uv run cdk deploy \
  -c instanceName=blog-server \
  -c availabilityZone=us-east-1b \
  -c userDataFile=scripts/bootstrap.sh
```

## Salidas del stack
- `LightsailInstanceName`: nombre final del recurso en Lightsail.
- `LightsailStaticIp`: dirección IP estática asignada (también visible en la consola de Lightsail).
- `LightsailPublicDns`: IP pública reportada por Lightsail (CloudFormation no expone un hostname, por lo que se repite la IP pública).

## Limpieza
Para evitar cargos, ejecuta `uv run cdk destroy` y verifica en la consola de Lightsail que la instancia y la IP estática hayan sido eliminadas.
