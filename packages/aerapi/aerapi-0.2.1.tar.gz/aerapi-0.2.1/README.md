# AerAPI Python Client - Setup Guide

This package provides a typed, authenticated client for the Aerlytix External API.

You can configure it with **environment variables** (recommended) or an optional **YAML config file** in `~/.aerapi/config.yaml`.

---

## 1. Installation

```bash
pip install aerapi
```

## 2. Configure Credentials

### Option 1: Environment Variables

#### Windows (PowerShell)

```powershell
[System.Environment]::SetEnvironmentVariable("AERAPI_BASE_URL", "https://your-env.aerlytix.com/api/v1", "User")
[System.Environment]::SetEnvironmentVariable("AERAPI_API_KEY_ID", "your-key-id", "User")
[System.Environment]::SetEnvironmentVariable("AERAPI_API_SECRET_KEY", "your-secret-key", "User")
```


#### Linux (bash / zsh)

```bash
export AERAPI_BASE_URL="https://your-env.aerlytix.com/api/v1"
export AERAPI_API_KEY_ID="your-key-id"
export AERAPI_API_SECRET_KEY="your-secret-key"
```

`BaseAPIClient` will automatically read these on instantiation - without need to provide a config object.

### Option 2: Provide config object
The `APIConfig` object can be provided to the `BaseAPIClient` constructor.

```python
api_config = APIConfig(
    base_url="https://your-env.aerlytix.com/api/v1",
    api_key_id="your-key-id",
    api_secret_key="your-secret-key"
)

BaseAPI = BaseAPIClient(api_config=api_config)
```

### Option 3: yaml file
The `ClientEnvConfig` object can be used to construct the BaseAPIClient object.
The configuration will look for a `C:/Users/{your user name}/.aerapi/config.yaml` file to instantiate from. 


```python
client_env_config = ClientEnvConfig(env="preprod", client="preprod-clientName")

BaseAPI = BaseAPIClient(api_config=client_env_config)
```


## 3. Creating API Clients

### 3.1 BaseAPIClient
`BaseAPIClient` is responsible for:
- Loading configuration (APIConfig / ClientEnvConfig / env vars)
- Building auth headers
- Sending authenticated HTTP requests (including multi-send helpers).

Typical usage (env-var based):
```python
from aerapi import BaseAPIClient

base_api = BaseAPIClient()  # reads AERAPI_* env vars
```

### 3.2 ExternalAPIClient
Wraps `BaseAPIClient` and exposes typed methods for the External API resources.

```python
from aerapi.common.base_api import BaseAPIClient
from aerapi.external.api_client import ExternalAPIClient

BaseAPI = BaseAPIClient()                 # or with APIConfig / ClientEnvConfig
ExternalAPI = ExternalAPIClient(BaseAPI)
```
Examples (non-exhaustive):

```python
aircraft = ExternalAPI.get_aircraft_details(aircraftId="...")
companies = ExternalAPI.get_all_companies(limit=100)
```

### 3.3 ExternalUtilsClient
`ExternalUtilsClient` builds on `ExternalAPIClient` to provide higher-level utilities (e.g. bulk fetch helpers).

```python
from aerapi import BaseAPIClient, ExternalAPIClient, ExternalUtilsClient

BaseAIP = BaseAPIClient()
ExternalAPI = ExternalAPIClient(BaseAIP)
ExternalUtils = ExternalUtilsClient(ExternalAPI)

all_assemblies = ExternalUtils.fetch_all_assemblies()
all_engines = ExternalUtils.fetch_all_engines()

```