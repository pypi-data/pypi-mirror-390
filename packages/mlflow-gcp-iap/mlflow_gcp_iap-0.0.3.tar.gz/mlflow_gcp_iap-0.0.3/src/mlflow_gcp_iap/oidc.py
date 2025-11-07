"""OIDC token management
for GCP.
"""

from google.auth import default, impersonated_credentials
from google.auth.transport.requests import Request

from mlflow_gcp_iap.config import Config


class OIDClient:
    """Wrapper to obtain OIDC
    tokens from the library
    configuration.
    """

    def __init__(self, config: Config | None = None):
        if config is None:
            config = Config()
        self.config = config
        self._credentials = impersonated_credentials.Credentials(
            source_credentials=default()[0],
            target_principal=self.config.target_service_account,
            target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self._sa_credentials = impersonated_credentials.IDTokenCredentials(
            self._credentials,
            target_audience=self.config.iap_client_id,
            include_email=True,
        )

    @property
    def id_token(self) -> impersonated_credentials.IDTokenCredentials:
        return self._sa_credentials

    def refresh(self):
        """Refresh the OIDC credentials."""
        self._credentials.refresh(Request())
        self._sa_credentials.refresh(Request())
