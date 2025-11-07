import json
import logging
import os
import subprocess
from typing import Any

import numpy as np
import pandas as pd

from AutoImblearn.components.api import BaseEstimatorAPI


class RunAutoRSPAPI(BaseEstimatorAPI):
    """Flask-based API serving the AutoRSP hybrid model."""

    def get_hyperparameter_search_space(self) -> dict:
        return {
            "metric": {
                "type": "categorical",
                "choices": ["macro_f1"],
                "default": "macro_f1",
            }
        }

    def fit(self, args, X_train, y_train, X_test, y_test):
        target = getattr(args, "target", None) or getattr(args, "target_name", None)
        if not target:
            raise ValueError("AutoRSP requires a target column name (args.target or args.target_name).")

        metric = getattr(args, "metric", "macro_f1")
        if metric != "macro_f1":
            raise ValueError("AutoRSP currently supports only the 'macro_f1' metric.")

        dataset_name = getattr(args, "dataset_name", None) or getattr(args, "dataset", None)
        if not dataset_name:
            raise ValueError("AutoRSP requires dataset_name information.")

        train_df = self._merge_features_labels(X_train, y_train, target)
        test_df = self._merge_features_labels(X_test, y_test, target)

        run_dir = os.path.join("/data/interim", dataset_name)
        os.makedirs(run_dir, exist_ok=True)

        train_path = os.path.join(run_dir, "autorsp_train.csv")
        test_path = os.path.join(run_dir, "autorsp_test.csv")
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)

        try:
            result = self._invoke_rscript(train_path, test_path, target, metric)
        finally:
            for path in (train_path, test_path):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except OSError:
                    logging.warning("Failed to delete temporary file %s", path)

        self.result = result
        return result

    def predict(self, X_test, y_test=None):
        return self.result

    def predict_proba(self, X_test):
        raise NotImplementedError("predict_proba is not supported for AutoRSP.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _merge_features_labels(self, X: pd.DataFrame, y: Any, target: str) -> pd.DataFrame:
        if isinstance(X, pd.DataFrame):
            df = X.copy()
        else:
            arr = np.asarray(X)
            columns = getattr(X, "columns", None)
            if columns is None:
                columns = [f"feature_{idx}" for idx in range(arr.shape[1])]
            df = pd.DataFrame(arr, columns=columns)

        labels = np.asarray(y).ravel()
        if target in df.columns:
            df = df.drop(columns=[target])
        df[target] = labels
        return df

    def _invoke_rscript(self, train_path: str, test_path: str, target: str, metric: str) -> float:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_autorsp.R")
        cmd = ["Rscript", script_path, train_path, test_path, target, metric]
        logging.info("Running AutoRSP R script: %s", " ".join(cmd))

        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if completed.returncode != 0:
            raise RuntimeError(
                f"AutoRSP R script failed with code {completed.returncode}: {completed.stderr}"
            )

        output = completed.stdout.strip()
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Failed to parse AutoRSP R output: {output}") from exc

        if "error" in payload:
            raise RuntimeError(f"AutoRSP R script error: {payload['error']}")
        if "result" not in payload:
            raise RuntimeError(f"AutoRSP R script missing result field: {payload}")

        return float(payload["result"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    api = RunAutoRSPAPI(__name__)
    api.run(host="0.0.0.0", port=8083, debug=False)
