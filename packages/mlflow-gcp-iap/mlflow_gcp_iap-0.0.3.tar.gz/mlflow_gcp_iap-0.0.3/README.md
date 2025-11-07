<h1 align="center">
  <br>
  <a href="https://aiboxlab.org/en/"><img src="https://aiboxlab.org/img/logo-aibox.png" alt="AiBox Lab" width="200"></a>
  <br>
  mlflow-gcp-iap
  <br>
</h1>

<h4 align="center">MlFlow add-on to access IAP-enabled tracking server on GCP.</h4>


[![Python](https://img.shields.io/pypi/pyversions/mlflow-gcp-iap.svg)](https://badge.fury.io/py/mlflow-gcp-iap)
[![PyPI](https://badge.fury.io/py/mlflow-gcp-iap.svg)](https://badge.fury.io/py/mlflow-gcp-iap)

# Quickstart

Install the library using your favorite package manager:

```sh
uv add mlflow-gcp-iap
uv pip install mlflow-gcp-iap
pip install mlflow-gcp-iap
```

Once the library is installed, you must configure it by running `mlflow-gcp-iap setup`. The CLI will ask for the required configuration. 

It is essential that the [GCP Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc) is configured locally, and that the user and service account have sufficient permissions. For the user, permissions related to Service Account Impersonation and token creation are required. For the service account, only the permission to access the IAP-protected MlFlow tracking server is mandatory.

To check whether the configuration works correctly, run `mlflow-gcp-iap test`. This command runs the script [`src/mlflow_gcp_iap/test.py`](./src/mlflow_gcp_iap/test.py), which creates a run on the MlFlow server. 

The library provides a simple context manager that automatically refresh tokens and update the MlFlow environment variables. The intended usage is as follows:

```python
import mlflow

from mlflow_gcp_iap import TokenRefresher


if __name__ == "__main__":
    with TokenRefresher():
        with mlflow.start_run(run_name="my-run"):
            mlflow.log_params({"a": 10, "b": 20})
            mlflow.log_metrics({"MSE": 0.0})
```
