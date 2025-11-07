"""
Docker client for survival unsupervised learning models.

Supports:
- Survival Clustering: SurvivalTree (for subgroup discovery), KMeans on survival data
- Risk Stratification: Automatically discover patient subgroups with different survival patterns
"""

from AutoImblearn.components.model_client.base_estimator import BaseEstimator


class RunSurvivalUnsupervised(BaseEstimator):
    """
    Docker client for survival unsupervised learning models.

    Args:
        model: Model name (e.g., 'survival_tree', 'survival_kmeans')
        data_folder: Path to data folder for volume mounting
    """

    def __init__(self, model="survival_tree", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"survival-unsupervised-api",
            container_name=f"{model}_survival_unsupervised_container",
            volume_mounts={
                "/tmp": {
                    'bind': '/tmp',
                    'mode': 'rw'
                },
                data_folder: {
                    'bind': '/data',
                    'mode': 'rw'
                },
            },
            api_base_url="http://localhost",
            port_bindings={5000: None}  # Random host port
        )

        self.model_name = model
        self.supported_metrics = [
            'log_rank',        # Log-rank statistic for cluster separation
            'c_index',         # Within-cluster C-index
            'silhouette',      # Silhouette score adapted for survival
        ]
