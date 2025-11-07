# AutoImblearn/pipelines/customsurvival.py
import logging
from typing import Dict, Callable, Any, Optional

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

from AutoImblearn.components.survival import RunSkSurvivalModel, RunSurvivalResampler

try:
    from AutoImblearn.components.model_client.base_transformer import BaseTransformer
    from AutoImblearn.components.model_client.base_model_client import BaseDockerModelClient
except Exception:
    BaseTransformer = None
    BaseDockerModelClient = None


# Docker-based survival models - factory functions
survival_models: Dict[str, Callable[..., Any]] = {
    'CPH': lambda **kw: RunSkSurvivalModel(model='CPH', **kw),
    'RSF': lambda **kw: RunSkSurvivalModel(model='RSF', **kw),
    'SVM': lambda **kw: RunSkSurvivalModel(model='SVM', **kw),
    'KSVM': lambda **kw: RunSkSurvivalModel(model='KSVM', **kw),
    'LASSO': lambda **kw: RunSkSurvivalModel(model='LASSO', **kw),
    'L1': lambda **kw: RunSkSurvivalModel(model='L1', **kw),
    'L2': lambda **kw: RunSkSurvivalModel(model='L2', **kw),
    'CSA': lambda **kw: RunSkSurvivalModel(model='CSA', **kw),
    'LRSF': lambda **kw: RunSkSurvivalModel(model='LRSF', **kw),
}

# Docker-based survival resamplers - factory functions
survival_resamplers: Dict[str, Callable[..., Any]] = {
    'rus': lambda **kw: RunSurvivalResampler(model='rus', **kw),
    'ros': lambda **kw: RunSurvivalResampler(model='ros', **kw),
    'smote': lambda **kw: RunSurvivalResampler(model='smote', **kw),
}


def value_counter(Y: np.ndarray):
    """Count and log events and censored observations in survival data"""
    values, counts = np.unique(Y['Status'], return_counts=True)
    for value, count in zip(values, counts):
        dist = count / Y.shape[0] * 100
        label = "Event" if value else "Censored"
        logging.info("\t\t {}={}, n={},\t ({:.2f}%)".format(label, value, count, dist))


class CustomSurvivalResamplar(BaseEstimator):
    """Unified survival resampler wrapper built on registry `survival_resamplers`.

    Survival-aware resampler that preserves censoring information.

    method:            key in `registry` (e.g., 'rus', 'ros', 'smote').
    registry:          mapping from method name -> factory that returns a resampler.
    data_folder:       base folder where data is stored.
    sampling_strategy: ratio for resampling (None uses resampler defaults).
    **resampler_kwargs: forwarded to the underlying resampler factory.
    """

    def __init__(self,
                 method: str = "smote",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 sampling_strategy: Optional[float] = None,
                 **resampler_kwargs: Any):

        self.method = method
        self.registry = survival_resamplers if registry is None else registry
        self.data_folder = data_folder
        self.sampling_strategy = sampling_strategy
        self.resampler_kwargs = dict(resampler_kwargs)

        self._impl = self._build_impl()

    def fit_resample(self, args, X: np.ndarray, y: np.ndarray):
        """
        Fit and resample the survival data.

        Args:
            args: Arguments object with .path for data_folder
            X: Feature matrix
            y: Structured survival array with 'Status' and 'Survival_in_days'

        Returns:
            Tuple of (X_resampled, y_resampled)
        """
        logging.info("\t Before Re-Sampling")
        value_counter(y)

        # Update data_folder if provided via args
        if hasattr(args, 'path') and args.path:
            if hasattr(self._impl, 'set_params'):
                self._impl.set_params(data_folder=args.path)

        # Update sampling strategy if set
        if self.sampling_strategy is not None and hasattr(self._impl, 'set_params'):
            self._impl.set_params(sampling_strategy=self.sampling_strategy)

        # Perform resampling
        if isinstance(self._impl, BaseTransformer):
            X_res, y_res = self._impl.fit_resample(args, X, y)
        else:
            # For non-Docker resamplers (if any exist in the future)
            X_res, y_res = self._impl.fit_resample(X, y)

        logging.info("\t After Re-Sampling")
        value_counter(y_res)

        return X_res, y_res

    def need_resample(self, Y: np.ndarray, samratio: Optional[float] = None):
        """
        Test if resampling is needed based on event/censored ratio.

        Args:
            Y: Structured survival array
            samratio: Threshold ratio for resampling decision

        Returns:
            bool: True if resampling is needed
        """
        if samratio is None:
            return True

        _, counts = np.unique(Y['Status'], return_counts=True)
        if len(counts) < 2:
            return False

        # ratio of events to censored
        ratio = counts[1] / counts[0]
        return ratio < samratio

    def get_params(self, deep: bool = True):
        """Get parameters for this estimator."""
        params = {
            "method": self.method,
            "registry": self.registry,
            "data_folder": self.data_folder,
            "sampling_strategy": self.sampling_strategy,
            **{f"impl__{k}": v for k, v in self.resampler_kwargs.items()},
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
        if "sampling_strategy" in params:
            self.sampling_strategy = params.pop("sampling_strategy")

        impl_updates = {k[len("impl__"):]: v for k, v in list(params.items()) if k.startswith("impl__")}
        for k in list(params.keys()):
            if k.startswith("impl__"):
                params.pop(k)

        self.resampler_kwargs.update(params)
        self._impl = self._build_impl()

        if impl_updates and hasattr(self._impl, "set_params"):
            self._impl.set_params(**impl_updates)
        return self

    def _build_impl(self):
        """
        Instantiate the underlying resampler from the registry.

        Looks up `self.method` in the registry and instantiates the factory.
        """
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown survival resampling method '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        # registry values are factories (lambda **kw)
        self.resampler_kwargs["data_folder"] = self.data_folder
        factory = self.registry[self.method]
        impl = factory(**self.resampler_kwargs)

        # Set data_folder if provided and supported
        if self.data_folder is not None:
            if hasattr(impl, "set_params") and hasattr(impl, "data_folder"):
                impl.set_params(data_folder=self.data_folder)

        # Set sampling_strategy if provided and supported
        if self.sampling_strategy is not None:
            if hasattr(impl, "set_params"):
                impl.set_params(sampling_strategy=self.sampling_strategy)

        return impl

    def cleanup(self):
        """Release Docker resources held by the resampler implementation."""
        impl = getattr(self, "_impl", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()


class CustomSurvivalModel(BaseEstimator):
    """Unified survival model wrapper built on registry `survival_models`.

    Wrapper for survival analysis models from scikit-survival:
    - Cox Proportional Hazards (CPH)
    - Random Survival Forest (RSF)
    - Survival SVM variants (SVM, KSVM)
    - Regularized Cox models (LASSO, L1, L2, CSA)

    method:           key in `registry` (e.g., 'CPH', 'RSF', ...).
    registry:         mapping from method name -> factory that returns a survival model.
    data_folder:      base folder where data is stored.
    metric:           evaluation metric (default: 'c_index').
    **model_kwargs:   forwarded to the underlying model factory.
    """

    def __init__(self,
                 method: str = "CPH",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 metric: str = "c_index",
                 **model_kwargs: Any):

        self.method = method
        self.registry = survival_models if registry is None else registry
        self.data_folder = data_folder
        self.metric = metric
        self.model_kwargs = dict(model_kwargs)

        self._impl = self._build_impl()
        self.result = None

    def fit(self, args, X_train: np.ndarray, y_train: np.ndarray):
        """
        Train survival model.

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

    def cleanup(self):
        """Release Docker resources held by the survival model implementation."""
        impl = getattr(self, "_impl", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()

    def predict(self, X_test: np.ndarray):
        """
        Make risk predictions.

        Args:
            X_test: Test features

        Returns:
            Risk scores
        """
        return self._impl.predict(X_test)

    def score(self, X_test: np.ndarray, y_test: np.ndarray, y_train: Optional[np.ndarray] = None):
        """
        Evaluate the survival model using the specified metric.

        Args:
            X_test: Test features
            y_test: Test survival data
            y_train: Training survival data (needed for Uno's C-index)

        Returns:
            Evaluation score
        """
        if self.metric == "c_index":
            # Get risk scores
            predictions = self.predict(X_test)

            # Calculate concordance indices
            from sksurv.metrics import concordance_index_censored, concordance_index_ipcw

            c_index = concordance_index_censored(
                y_test['Status'],
                y_test['Survival_in_days'],
                predictions
            )[0]

            c_uno = None
            if y_train is not None:
                try:
                    c_uno = concordance_index_ipcw(y_train, y_test, predictions)[0]
                except:
                    c_uno = None

            self.result = {
                'c_index': c_index,
                'c_uno': c_uno,
                'n_events': int(y_test['Status'].sum())
            }

            logging.info(
                "\t Survival Model: {}, C-index: {:.4f}, C-uno: {}, Events: {}".format(
                    self.method,
                    c_index,
                    f"{c_uno:.4f}" if c_uno else "N/A",
                    int(y_test['Status'].sum())
                )
            )

            return c_index
        else:
            raise ValueError(f"Metric '{self.metric}' is not supported for survival analysis")

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
        Instantiate the underlying survival model from the registry.

        Looks up `self.method` in the registry and instantiates the factory.
        """
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown survival model '{self.method}'. "
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
