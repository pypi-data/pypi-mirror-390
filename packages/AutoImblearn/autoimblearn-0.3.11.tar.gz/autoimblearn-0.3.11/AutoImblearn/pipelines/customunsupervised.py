# AutoImblearn/pipelines/customunsupervised.py
"""
Pipeline wrappers for unsupervised learning.

Supports four types of unsupervised learning:
1. Clustering: KMeans, DBSCAN, Hierarchical, GMM, etc.
2. Dimensionality Reduction: PCA, t-SNE, UMAP, etc.
3. Anomaly Detection: IsolationForest, OneClassSVM, LOF, etc.
4. Survival Unsupervised: Survival clustering and risk stratification
"""

import logging
from typing import Dict, Callable, Any, Optional

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

from AutoImblearn.components.unsupervised import (
    RunClusteringModel,
    RunDimensionalityReduction,
    RunAnomalyDetection
)
from AutoImblearn.components.survival import RunSurvivalUnsupervised

try:
    from AutoImblearn.components.model_client.base_model_client import BaseDockerModelClient
except Exception:
    BaseDockerModelClient = None


# Clustering models - factory functions
clustering_models: Dict[str, Callable[..., Any]] = {
    'kmeans': lambda **kw: RunClusteringModel(model='kmeans', **kw),
    'dbscan': lambda **kw: RunClusteringModel(model='dbscan', **kw),
    'hierarchical': lambda **kw: RunClusteringModel(model='hierarchical', **kw),
    'gmm': lambda **kw: RunClusteringModel(model='gmm', **kw),
    'meanshift': lambda **kw: RunClusteringModel(model='meanshift', **kw),
    'spectral': lambda **kw: RunClusteringModel(model='spectral', **kw),
}

# Dimensionality reduction models - factory functions
reduction_models: Dict[str, Callable[..., Any]] = {
    'pca': lambda **kw: RunDimensionalityReduction(model='pca', **kw),
    'tsne': lambda **kw: RunDimensionalityReduction(model='tsne', **kw),
    'umap': lambda **kw: RunDimensionalityReduction(model='umap', **kw),
    'svd': lambda **kw: RunDimensionalityReduction(model='svd', **kw),
    'ica': lambda **kw: RunDimensionalityReduction(model='ica', **kw),
    'nmf': lambda **kw: RunDimensionalityReduction(model='nmf', **kw),
}

# Anomaly detection models - factory functions
anomaly_models: Dict[str, Callable[..., Any]] = {
    'isoforest': lambda **kw: RunAnomalyDetection(model='isoforest', **kw),
    'ocsvm': lambda **kw: RunAnomalyDetection(model='ocsvm', **kw),
    'lof': lambda **kw: RunAnomalyDetection(model='lof', **kw),
    'elliptic': lambda **kw: RunAnomalyDetection(model='elliptic', **kw),
}

# Survival unsupervised models - factory functions
survival_unsupervised_models: Dict[str, Callable[..., Any]] = {
    'survival_tree': lambda **kw: RunSurvivalUnsupervised(model='survival_tree', **kw),
    'survival_kmeans': lambda **kw: RunSurvivalUnsupervised(model='survival_kmeans', **kw),
}

# All unsupervised models combined
unsupervised_models: Dict[str, Callable[..., Any]] = {
    **clustering_models,
    **reduction_models,
    **anomaly_models,
}


class CustomUnsupervisedModel(BaseEstimator):
    """Unified unsupervised model wrapper built on registry `unsupervised_models`.

    Wrapper for unsupervised learning models (clustering, reduction, anomaly detection).

    method:           key in `registry` (e.g., 'kmeans', 'pca', 'isoforest').
    registry:         mapping from method name -> factory that returns a model.
    data_folder:      base folder where data is stored.
    metric:           evaluation metric (e.g., 'silhouette', 'calinski', 'f1').
    **model_kwargs:   forwarded to the underlying model factory.
    """

    def __init__(self,
                 method: str = "kmeans",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 metric: str = "silhouette",
                 **model_kwargs: Any):

        self.method = method
        self.registry = unsupervised_models if registry is None else registry
        self.data_folder = data_folder
        self.metric = metric
        self.model_kwargs = dict(model_kwargs)

        # Determine model type before building impl
        self.model_type = self._determine_model_type()
        self._impl = self._build_impl()
        self.result = None

    def _determine_model_type(self) -> str:
        """Determine the model type based on the method name."""
        if self.method in clustering_models:
            return 'clustering'
        elif self.method in reduction_models:
            return 'reduction'
        elif self.method in anomaly_models:
            return 'anomaly'
        else:
            raise ValueError(f"Unknown unsupervised model: {self.method}")

    def fit(self, args, X_train: np.ndarray, y_train: Optional[np.ndarray] = None):
        """
        Train unsupervised model.

        Args:
            args: Arguments object with .path for data_folder
            X_train: Training features
            y_train: Optional labels (not used for training, only for evaluation)

        Returns:
            self
        """
        # Update data_folder if provided via args
        if hasattr(args, 'path') and args.path:
            if hasattr(self._impl, 'set_params'):
                self._impl.set_params(data_folder=args.path)

        # Fit the model
        if isinstance(self._impl, BaseDockerModelClient):
            self._impl.fit(args, X_train, y_train)
        else:
            # For non-Docker models (if any exist in the future)
            self._impl.fit(X_train, y_train)

        return self

    def cleanup(self):
        """Release Docker resources held by the unsupervised model implementation."""
        impl = getattr(self, "_impl", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()

    def predict(self, X_test: np.ndarray):
        """
        Make predictions.

        Args:
            X_test: Test features

        Returns:
            Predictions (cluster labels, reduced dimensions, or anomaly scores)
        """
        return self._impl.predict(X_test)

    def score(self, X_test: np.ndarray, y_test: Optional[np.ndarray] = None):
        """
        Evaluate the unsupervised model using the specified metric.

        Args:
            X_test: Test features
            y_test: Optional ground truth labels (for evaluation)

        Returns:
            Evaluation score
        """
        predictions = self.predict(X_test)

        # Evaluate based on metric
        if self.metric == "silhouette" and self.model_type == 'clustering':
            from sklearn.metrics import silhouette_score
            unique_labels = np.unique(predictions)
            if len(unique_labels) > 1:
                score = silhouette_score(X_test, predictions)
            else:
                score = 0.0

        elif self.metric == "calinski" and self.model_type == 'clustering':
            from sklearn.metrics import calinski_harabasz_score
            score = calinski_harabasz_score(X_test, predictions)

        elif self.metric == "davies_bouldin" and self.model_type == 'clustering':
            from sklearn.metrics import davies_bouldin_score
            score = davies_bouldin_score(X_test, predictions)
            # Lower is better, so negate for consistency
            score = -score

        elif self.metric == "reconstruction" and self.model_type == 'reduction':
            # Reconstruction error
            if hasattr(self._impl, 'inverse_transform'):
                X_reconstructed = self._impl.inverse_transform(predictions)
                score = -np.mean((X_test - X_reconstructed) ** 2)  # Negative MSE (higher is better)
            else:
                score = 0.0

        elif self.metric == "f1" and self.model_type == 'anomaly':
            # F1 score for anomaly detection (requires ground truth)
            if y_test is not None:
                from sklearn.metrics import f1_score
                y_pred_binary = (predictions == -1).astype(int)
                score = f1_score(y_test, y_pred_binary, zero_division=0)
            else:
                score = 0.0

        else:
            # Default: use the first available metric for the model type
            if self.model_type == 'clustering':
                from sklearn.metrics import silhouette_score
                unique_labels = np.unique(predictions)
                if len(unique_labels) > 1:
                    score = silhouette_score(X_test, predictions)
                else:
                    score = 0.0
            elif self.model_type == 'anomaly':
                # For anomaly detection, return anomaly ratio as default metric
                n_anomalies = np.sum(predictions == -1)
                score = n_anomalies / len(predictions)
            else:
                score = 0.0

        self.result = score

        logging.info(
            f"\t {self.model_type.capitalize()} Model: {self.method}, "
            f"Metric: {self.metric}, Score: {score:.4f}"
        )

        return score

    def get_params(self, deep: bool = True):
        """Get parameters for this estimator."""
        params = {
            "method": self.method,
            "registry": self.registry,
            "data_folder": self.data_folder,
            "metric": self.metric,
            **{f"impl__{k}": v for k, v in self.model_kwargs.items()},
        }
        if deep and hasattr(self._impl, "get_params"):
            for k, v in self._impl.get_params(deep=True).items():
                params.setdefault(f"impl__{k}", v)
        return params

    def set_params(self, **params):
        """Set parameters for this estimator."""
        if "method" in params:
            self.method = params.pop("method")
            self.model_type = self._determine_model_type()
        if "registry" in params:
            self.registry = params.pop("registry")
        if "data_folder" in params:
            self.data_folder = params.pop("data_folder")
        if "metric" in params:
            self.metric = params.pop("metric")

        impl_updates = {k[len("impl__"):]: v for k, v in list(params.items()) if k.startswith("impl__")}
        for k in list(params.keys()):
            if k.startswith("impl__"):
                params.pop(k)

        self.model_kwargs.update(params)
        self._impl = self._build_impl()

        if impl_updates and hasattr(self._impl, "set_params"):
            self._impl.set_params(**impl_updates)
        return self

    def _build_impl(self):
        """
        Instantiate the underlying model from the registry.

        Looks up `self.method` in the registry and instantiates the factory.
        """
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown unsupervised model '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        # registry values are factories (lambda **kw)
        self.model_kwargs["data_folder"] = self.data_folder
        factory = self.registry[self.method]
        impl = factory(**self.model_kwargs)

        # Set data_folder if provided and supported
        if self.data_folder is not None:
            if hasattr(impl, "set_params") and hasattr(impl, "data_folder"):
                impl.set_params(data_folder=self.data_folder)

        return impl


class CustomSurvivalUnsupervisedModel(BaseEstimator):
    """Unified survival unsupervised model wrapper built on registry `survival_unsupervised_models`.

    Wrapper for survival unsupervised learning models.

    method:           key in `registry` (e.g., 'survival_tree', 'survival_kmeans').
    registry:         mapping from method name -> factory that returns a model.
    data_folder:      base folder where data is stored.
    metric:           evaluation metric (default: 'log_rank').
    **model_kwargs:   forwarded to the underlying model factory.
    """

    def __init__(self,
                 method: str = "survival_kmeans",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 metric: str = "log_rank",
                 **model_kwargs: Any):

        self.method = method
        self.registry = survival_unsupervised_models if registry is None else registry
        self.data_folder = data_folder
        self.metric = metric
        self.model_kwargs = dict(model_kwargs)

        self._impl = self._build_impl()
        self.result = None

    def fit(self, args, X_train: np.ndarray, y_train: np.ndarray):
        """
        Train survival unsupervised model.

        Args:
            args: Arguments object with .path for data_folder
            X_train: Training features
            y_train: Structured survival array with 'Status' and 'Survival_in_days'

        Returns:
            self
        """
        # Update data_folder if provided via args
        if hasattr(args, 'path') and args.path:
            if hasattr(self._impl, 'set_params'):
                self._impl.set_params(data_folder=args.path)

        # Fit the model
        if isinstance(self._impl, BaseDockerModelClient):
            self._impl.fit(args, X_train, y_train)
        else:
            # For non-Docker models (if any exist in the future)
            self._impl.fit(X_train, y_train)

        return self

    def predict(self, X_test: np.ndarray):
        """
        Make cluster predictions.

        Args:
            X_test: Test features

        Returns:
            Cluster labels or risk groups
        """
        return self._impl.predict(X_test)

    def score(self, X_test: np.ndarray, y_test: np.ndarray):
        """
        Evaluate the survival unsupervised model using the specified metric.

        Args:
            X_test: Test features
            y_test: Test survival data (structured array)

        Returns:
            Evaluation score (log-rank statistic or other)
        """
        predictions = self.predict(X_test)

        # Evaluate using log-rank statistic for cluster separation
        if self.metric == "log_rank":
            try:
                from sksurv.compare import compare_survival

                # Group by cluster
                unique_clusters = np.unique(predictions)
                if len(unique_clusters) > 1:
                    cluster_groups = [y_test[predictions == c] for c in unique_clusters]
                    chisq, pvalue = compare_survival(cluster_groups)
                    score = chisq  # Higher chi-square = better cluster separation
                else:
                    score = 0.0
            except Exception as e:
                logging.error(f"Log-rank test failed: {e}")
                score = 0.0

        elif self.metric == "silhouette":
            # Silhouette score on survival times
            from sklearn.metrics import silhouette_score
            survival_times = y_test['Survival_in_days'].reshape(-1, 1)
            unique_clusters = np.unique(predictions)
            if len(unique_clusters) > 1:
                score = silhouette_score(survival_times, predictions)
            else:
                score = 0.0

        else:
            # Default: use log-rank statistic
            try:
                from sksurv.compare import compare_survival
                unique_clusters = np.unique(predictions)
                if len(unique_clusters) > 1:
                    cluster_groups = [y_test[predictions == c] for c in unique_clusters]
                    chisq, pvalue = compare_survival(cluster_groups)
                    score = chisq
                else:
                    score = 0.0
            except:
                score = 0.0

        self.result = score

        logging.info(
            f"\t Survival Unsupervised Model: {self.method}, "
            f"Metric: {self.metric}, Score: {score:.4f}, "
            f"N_clusters: {len(np.unique(predictions))}"
        )

        return score

    def get_params(self, deep: bool = True):
        """Get parameters for this estimator."""
        params = {
            "method": self.method,
            "registry": self.registry,
            "data_folder": self.data_folder,
            "metric": self.metric,
            **{f"impl__{k}": v for k, v in self.model_kwargs.items()},
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
        if "metric" in params:
            self.metric = params.pop("metric")

        impl_updates = {k[len("impl__"):]: v for k, v in list(params.items()) if k.startswith("impl__")}
        for k in list(params.keys()):
            if k.startswith("impl__"):
                params.pop(k)

        self.model_kwargs.update(params)
        self._impl = self._build_impl()

        if impl_updates and hasattr(self._impl, "set_params"):
            self._impl.set_params(**impl_updates)
        return self

    def _build_impl(self):
        """
        Instantiate the underlying survival unsupervised model from the registry.

        Looks up `self.method` in the registry and instantiates the factory.
        """
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown survival unsupervised model '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        # registry values are factories (lambda **kw)
        self.model_kwargs["data_folder"] = self.data_folder
        factory = self.registry[self.method]
        impl = factory(**self.model_kwargs)

        # Set data_folder if provided and supported
        if self.data_folder is not None:
            if hasattr(impl, "set_params") and hasattr(impl, "data_folder"):
                impl.set_params(data_folder=self.data_folder)

        return impl
