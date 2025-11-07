"""Sample test run to validate
the configuration.
"""

import mlflow

from mlflow_gcp_iap import TokenRefresher

_EXPERIMENT_NAME = "mlflow-gcp-iap-tests"


def run():
    # Automatically configures the MlFlow environment
    #   variables to access the tracking server.
    with TokenRefresher():
        # Maybe create experiment
        experiment = mlflow.get_experiment_by_name(name=_EXPERIMENT_NAME)
        if experiment is None:
            experiment = mlflow.create_experiment(name=_EXPERIMENT_NAME)
        else:
            experiment = experiment.experiment_id

        # Run sample run
        with mlflow.start_run(experiment_id=experiment, run_name="token-refresher"):
            mlflow.log_params({"message": "The connection is working correctly!"})


if __name__ == "__main__":
    run()
