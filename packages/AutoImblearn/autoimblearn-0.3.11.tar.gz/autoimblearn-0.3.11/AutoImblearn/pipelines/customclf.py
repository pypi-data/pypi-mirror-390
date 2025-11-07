# AutoImblearn/pipelines/customclf.py
import logging
import os
from typing import Dict, Callable, Any, Optional

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

from AutoImblearn.components.classifiers import RunSklearnClf, RunXGBoostClf

try:
    from AutoImblearn.components.model_client.base_model_client import BaseDockerModelClient
except Exception:
    BaseDockerModelClient = None


# Docker-based classifiers - factory functions similar to imputers
clfs: Dict[str, Callable[..., Any]] = {
    "lr": lambda **kw: RunSklearnClf(model='lr', **kw),
    "mlp": lambda **kw: RunSklearnClf(model='mlp', **kw),
    "ada": lambda **kw: RunSklearnClf(model='ada', **kw),
    "svm": lambda **kw: RunSklearnClf(model='svm', **kw),
    # "ensemble": lambda **kw: RunXGBoostClf(model='ensemble', **kw),
}


class CustomClassifier(BaseEstimator):
    """Unified classifier wrapper built on registry `clfs`.

    method:             key in `registry` (e.g., 'lr', 'mlp', ...).
    registry:           mapping from method name -> factory that returns a classifier.
    data_folder:        base folder where data is stored.
    dataset_name:       dataset identifier for metadata/caching.
    metric:             evaluation metric ('auroc' or 'macro_f1').
    **classifier_kwargs: forwarded to the underlying classifier factory.
    """

    def __init__(self,
                 method: str = "lr",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 dataset_name: Optional[str] = None,
                 metric: str = "auroc",
                 result_file_path: Optional[str] = None,
                 **classifier_kwargs: Any):

        self.method = method
        self.registry = clfs if registry is None else registry
        self.data_folder = data_folder
        self.dataset_name = dataset_name
        self.metric = metric
        self.classifier_kwargs = dict(classifier_kwargs)

        self.result_file_path = result_file_path
        self.result_file_name = None
        self._ensure_result_paths()

        self._impl = self._build_impl()
        self.result = None
        self.training_metrics = None

    def fit(
        self,
        args,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_eval: Optional[np.ndarray] = None,
        y_eval: Optional[np.ndarray] = None,
    ):
        """
        Train the classifier.

        Args:
            args: Arguments object with .path for data_folder
            X_train: Training features
            y_train: Training labels
            X_eval: Optional evaluation features (defaults to X_train if not provided)
            y_eval: Optional evaluation labels (defaults to y_train if not provided)

        Returns:
            self
        """
        # Update data_folder if provided via args
        if hasattr(args, 'path') and args.path:
            if hasattr(self._impl, 'set_params'):
                self._impl.set_params(data_folder=args.path)

        # Classifier containers expect evaluation data to compute metrics.
        if X_eval is None or y_eval is None:
            X_eval = X_train
            y_eval = y_train

        # Fit the classifier
        if isinstance(self._impl, BaseDockerModelClient):
            metrics = self._impl.fit(
                args,
                X_train,
                y_train,
                X_eval,
                y_eval,
                result_file_name=self.result_file_name,
                result_file_path=self.result_file_path,
            )
            self.training_metrics = metrics
        else:
            # For non-Docker classifiers (if any exist in the future)
            self._impl.fit(X_train, y_train)

        return self

    def predict(self, X_test: np.ndarray):
        """
        Make predictions.

        Args:
            X_test: Test features

        Returns:
            Predictions
        """
        return self._impl.predict(X_test)

    def predict_proba(self, X_test: np.ndarray):
        """
        Predict class probabilities.

        Args:
            X_test: Test features

        Returns:
            Class probabilities
        """
        if hasattr(self._impl, 'predict_proba'):
            return self._impl.predict_proba(X_test)
        else:
            raise AttributeError(f"Classifier '{self.method}' does not support predict_proba")

    def score(self, X_test: np.ndarray, y_test: np.ndarray):
        """
        Evaluate the classifier using the specified metric.

        Args:
            X_test: Test features
            y_test: Test labels

        Returns:
            Evaluation score
        """
        if self.metric == "auroc":
            y_proba = self.predict_proba(X_test)[:, 1]
            score = roc_auc_score(y_test, y_proba)
            self.result = score
            logging.info(f"\t Classifier: {self.method}, AUROC: {score:.4f}")
            return score
        elif self.metric == "macro_f1":
            y_pred = self.predict(X_test)
            _, _, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro')
            self.result = f1
            logging.info(f"\t Classifier: {self.method}, Macro F1: {f1:.4f}")
            return f1
        else:
            raise ValueError(f"Metric '{self.metric}' is not supported for classifier '{self.method}'")

    def get_params(self, deep: bool = True):
        """Get parameters for this estimator."""
        params = {
            "method": self.method,
            "registry": self.registry,
            "data_folder": self.data_folder,
            "dataset_name": self.dataset_name,
            "metric": self.metric,
            "result_file_path": self.result_file_path,
            "result_file_name": self.result_file_name,
            **{f"impl__{k}": v for k, v in self.classifier_kwargs.items()},
        }
        if deep and hasattr(self._impl, "get_params"):
            for k, v in self._impl.get_params(deep=True).items():
                params.setdefault(f"impl__{k}", v)
        return params

    def set_params(self, **params):
        """Set parameters for this estimator."""
        if "method" in params:
            self.method = params.pop("method")
        if "registry" in params:
            self.registry = params.pop("registry")
        if "data_folder" in params:
            self.data_folder = params.pop("data_folder")
        if "dataset_name" in params:
            self.dataset_name = params.pop("dataset_name")
        if "metric" in params:
            self.metric = params.pop("metric")
        if "result_file_path" in params:
            self.result_file_path = params.pop("result_file_path")
        if "result_file_name" in params:
            self.result_file_name = params.pop("result_file_name")

        self._ensure_result_paths()

        impl_updates = {k[len("impl__"):]: v for k, v in list(params.items()) if k.startswith("impl__")}
        for k in list(params.keys()):
            if k.startswith("impl__"):
                params.pop(k)

        self.classifier_kwargs.update(params)
        self._impl = self._build_impl()

        if impl_updates and hasattr(self._impl, "set_params"):
            self._impl.set_params(**impl_updates)
        return self

    def _build_impl(self):
        """
        Instantiate the underlying classifier from the registry.

        Looks up `self.method` in the registry and instantiates the factory.
        """
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown classifier method '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        # registry values are factories (lambda **kw)
        self.classifier_kwargs["data_folder"] = self.data_folder
        self.classifier_kwargs["result_file_path"] = self.result_file_path
        self.classifier_kwargs["result_file_name"] = self.result_file_name
        factory = self.registry[self.method]
        impl = factory(**self.classifier_kwargs)

        # Set data_folder if provided and supported
        if self.data_folder is not None:
            if hasattr(impl, "set_params") and hasattr(impl, "data_folder"):
                impl.set_params(data_folder=self.data_folder)

        return impl

    def cleanup(self):
        """Release Docker resources held by the classifier implementation."""
        impl = getattr(self, "_impl", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()

    def _ensure_result_paths(self):
        """Ensure result file path/name are set consistently."""
        if self.result_file_path is None and self.data_folder and self.dataset_name:
            self.result_file_path = os.path.join(
                self.data_folder,
                "interim",
                self.dataset_name,
                f"model_{self.method}.p"
            )

        if self.result_file_path:
            os.makedirs(os.path.dirname(self.result_file_path), exist_ok=True)
            self.result_file_name = os.path.basename(self.result_file_path)
        if self.result_file_name is None:
            self.result_file_name = f"model_{self.method}.p"
