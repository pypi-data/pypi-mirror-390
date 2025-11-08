from humalab.metrics.metric import Metrics
from humalab.constants import ArtifactType, GraphType, MetricDimType
from humalab.humalab_api_client import EpisodeStatus
from typing import Any


SCENARIO_STATS_NEED_FLATTEN = {
    "uniform_1d",
    "bernoulli_1d",
    "categorical_1d",
    "discrete_1d",
    "log_uniform_1d",
    "gaussian_1d",
    "truncated_gaussian_1d"
}


DISTRIBUTION_GRAPH_TYPE = {
    # 0D distributions
    "uniform": GraphType.HISTOGRAM,
    "bernoulli": GraphType.HISTOGRAM,
    "categorical": GraphType.BAR,
    "discrete": GraphType.BAR,
    "log_uniform": GraphType.HISTOGRAM,
    "gaussian": GraphType.GAUSSIAN,
    "truncated_gaussian": GraphType.GAUSSIAN,

    # 1D distributions
    "uniform_1d": GraphType.HISTOGRAM,
    "bernoulli_1d": GraphType.HISTOGRAM,
    "categorical_1d": GraphType.BAR,
    "discrete_1d": GraphType.BAR,
    "log_uniform_1d": GraphType.HISTOGRAM,
    "gaussian_1d": GraphType.GAUSSIAN,
    "truncated_gaussian_1d": GraphType.GAUSSIAN,

    # 2D distributions
    "uniform_2d": GraphType.SCATTER,
    "gaussian_2d": GraphType.SCATTER,
    "truncated_gaussian_2d": GraphType.SCATTER,

    # 3D distributions
    "uniform_3d": GraphType.THREE_D_MAP,
    "gaussian_3d": GraphType.THREE_D_MAP,
    "truncated_gaussian_3d": GraphType.THREE_D_MAP,
}

class ScenarioStats(Metrics):
    """Metric to track scenario statistics across episodes.

    This class logs sampled values from scenario distributions and tracks episode
    statuses. It supports various distribution types and automatically handles
    flattening for 1D distributions.

    Attributes:
        name (str): The name of the scenario statistic.
        distribution_type (str): The type of distribution (e.g., 'uniform', 'gaussian').
        artifact_type (ArtifactType): The artifact type, always SCENARIO_STATS.
    """

    def __init__(self, 
                 name: str,
                 distribution_type: str,
                 ) -> None:
        super().__init__(
            graph_type=DISTRIBUTION_GRAPH_TYPE[distribution_type]
        )
        self._name = name
        self._distribution_type = distribution_type
        self._artifact_type = ArtifactType.SCENARIO_STATS
        self._values = {}
        self._results = {}

    @property
    def name(self) -> str:
        """The name of the scenario statistic.

        Returns:
            str: The statistic name.
        """
        return self._name

    @property
    def distribution_type(self) -> str:
        """The type of distribution used for this statistic.

        Returns:
            str: The distribution type (e.g., 'uniform', 'gaussian').
        """
        return self._distribution_type

    @property
    def artifact_type(self) -> ArtifactType:
        """The artifact type, always SCENARIO_STATS.

        Returns:
            ArtifactType: The artifact type.
        """
        return self._artifact_type
    
    def log(self, data: Any, x: Any = None, replace: bool = False) -> None:
        """Log a sampled value from the scenario distribution.

        Args:
            data (Any): The sampled value to log.
            x (Any | None): The key/identifier for this sample (typically episode_id).
                If None, auto-incrementing step is used.
            replace (bool): Whether to replace an existing value. Defaults to False.

        Raises:
            ValueError: If data for the given x already exists and replace is False.
        """
        if x in self._values:
            if replace:
                if self._distribution_type in SCENARIO_STATS_NEED_FLATTEN:
                    data = data[0]
                self._values[x] = data
            else:   
                raise ValueError(f"Data for episode_id {x} already exists. Use replace=True to overwrite.")
        else:
            if self._distribution_type in SCENARIO_STATS_NEED_FLATTEN:
                data = data[0]
            self._values[x] = data
    
    def log_status(self,
                   episode_id: str,
                   episode_status: EpisodeStatus,
                   replace: bool = False) -> None:
        """Log the status of an episode.

        Args:
            episode_id (str): The unique identifier of the episode.
            episode_status (EpisodeStatus): The status of the episode.
            replace (bool): Whether to replace an existing status for this episode.
                Defaults to False.

        Raises:
            ValueError: If status for the episode_id already exists and replace is False.
        """
        if episode_id in self._results:
            if replace:
                self._results[episode_id] = episode_status.value
            else:   
                raise ValueError(f"Data for episode_id {episode_id} already exists. Use replace=True to overwrite.")
        else:
            self._results[episode_id] = episode_status.value

    def _finalize(self) -> dict:
        """Finalize and return all collected scenario statistics.

        Returns:
            dict: Dictionary containing values, results, and distribution type.
        """
        ret_val = {
            "values": self._values,
            "results": self._results,
            "distribution_type": self._distribution_type,
        }
        self._values = {}
        self._results = {}
        return ret_val
        
    