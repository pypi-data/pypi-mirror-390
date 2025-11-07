"""Token refresher."""

import datetime as dt
import os
import threading
import time

from mlflow_gcp_iap.oidc import OIDClient


class TokenRefresher:
    """Context that automatically
    refreshes GCP ID Tokens for
    impersonated service accounts.

    This class creates a new thread
    that runs concurrently and automatically
    updates the `MLFLOW_TRACKING_TOKEN` and
    `MLFLOW_TRACKING_URI` environment variables.

    The new thread does the following:
        1. Update the ID token;
        2. Sleeps for 1s;
        3. Goes back to 1. until we exit the context;
    """

    def __init__(self):
        self._thread = None
        self._stop = False
        self._client = OIDClient()

    def __enter__(self):
        assert self._thread is None and not self._stop

        # Guarantee that the environment variable is set
        self._base_refresh()

        # Schedule threads to periodic update tokens
        self._thread = threading.Thread(target=self._refresh_mlflow_token)
        self._thread.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._thread is not None:
            self._stop = True
            self._thread.join()
            self._stop = False
            self._thread = None

    def _refresh_mlflow_token(self):
        """Infinite loop that refreshes the access
        token and updates the MLFlow token variable.
        """
        while not self._stop:
            remaining_lifetime = (self._client.id_token.expiry - dt.datetime.now()).total_seconds()

            # If less than 5 minutes, refresh
            if remaining_lifetime < 60 * 5:
                self._base_refresh()

            # Sleep before checking again
            time.sleep(1.0)

    def _base_refresh(self):
        # Refresh token
        self._client.refresh()

        # Update MLFlow environment variables
        os.environ["MLFLOW_TRACKING_TOKEN"] = self._client.id_token.token
        os.environ["MLFLOW_TRACKING_URI"] = self._client.config.mlflow_tracking_server
