from humalab.constants import RESERVED_NAMES, ArtifactType
from humalab.humalab_api_client import HumaLabApiClient, EpisodeStatus
from humalab.metrics.code import Code
from humalab.metrics.summary import Summary
from humalab.metrics.metric import Metrics
from omegaconf import DictConfig, ListConfig, OmegaConf
from typing import Any
import pickle
import traceback

from humalab.utils import is_standard_type


class Episode:
    """Represents a single episode within a run.

    An Episode is a context manager that tracks a single execution instance of a
    scenario. It provides access to scenario configuration values, supports metric
    logging, and manages episode lifecycle with various completion statuses.

    Episodes can be finished with different statuses:
    - SUCCESS: Episode completed successfully
    - FAILED: Episode failed
    - CANCELED: Episode was discarded/canceled
    - ERRORED: Episode encountered an error

    Use as a context manager to automatically handle episode lifecycle:
        with episode:
            # Your code here
            pass

    Attributes:
        run_id (str): The unique identifier of the parent run.
        episode_id (str): The unique identifier for this episode.
        scenario (DictConfig | ListConfig): The resolved scenario configuration.
        status (EpisodeStatus): The current status of the episode.
        episode_vals (dict): The sampled values from scenario distributions.
        is_finished (bool): Whether the episode has been finalized.
    """
    def __init__(self, 
                 run_id: str, 
                 episode_id: str, 
                 scenario_conf: DictConfig | ListConfig,
                 episode_vals: dict | None = None,

                 base_url: str | None = None,
                 api_key: str | None = None,
                 timeout: float | None = None,):
        self._run_id = run_id
        self._episode_id = episode_id
        self._episode_status = EpisodeStatus.RUNNING
        self._scenario_conf = scenario_conf
        self._logs = {}
        self._episode_vals = episode_vals or {}
        self._is_finished = False

        self._api_client = HumaLabApiClient(base_url=base_url,
                                            api_key=api_key,
                                            timeout=timeout)

    @property
    def run_id(self) -> str:
        """The unique identifier of the parent run.

        Returns:
            str: The run ID.
        """
        return self._run_id

    @property
    def episode_id(self) -> str:
        """The unique identifier for this episode.

        Returns:
            str: The episode ID.
        """
        return self._episode_id

    @property
    def scenario(self) -> DictConfig | ListConfig:
        """The resolved scenario configuration for this episode.

        Returns:
            DictConfig | ListConfig: The scenario configuration.
        """
        return self._scenario_conf

    @property
    def status(self) -> EpisodeStatus:
        """The current status of the episode.

        Returns:
            EpisodeStatus: The episode status.
        """
        return self._episode_status

    @property
    def episode_vals(self) -> dict:
        """The sampled values from scenario distributions.

        Returns:
            dict: Dictionary mapping scenario variable names to their sampled values.
        """
        return self._episode_vals

    @property
    def is_finished(self) -> bool:
        """Whether the episode has been finalized.

        Returns:
            bool: True if the episode is finished, False otherwise.
        """
        return self._is_finished
    
    def __enter__(self):
        """Enter the episode context."""
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """Exit the episode context and finalize the episode."""
        if self._is_finished:
            return
        if exception_type is not None:
            err_msg = "".join(traceback.format_exception(exception_type, exception_value, exception_traceback))
            self.finish(status=EpisodeStatus.ERRORED, err_msg=err_msg)
        else:
            self.finish(status=EpisodeStatus.SUCCESS)

    def __getattr__(self, name: Any) -> Any:
        """Access scenario configuration values as attributes.

        Allows accessing scenario configuration using dot notation (e.g., episode.my_param).

        Args:
            name (Any): The attribute/key name from scenario configuration.

        Returns:
            Any: The value from scenario configuration.

        Raises:
            AttributeError: If the attribute is not in scenario configuration.
        """
        if name in self._scenario_conf:
            return self._scenario_conf[name]
        raise AttributeError(f"'Scenario' object has no attribute '{name}'")

    def __getitem__(self, key: Any) -> Any:
        """Access scenario configuration values using subscript notation.

        Allows accessing scenario configuration using bracket notation (e.g., episode['my_param']).

        Args:
            key (Any): The key name from scenario configuration.

        Returns:
            Any: The value from scenario configuration.

        Raises:
            KeyError: If the key is not in scenario configuration.
        """
        if key in self._scenario_conf:
            return self._scenario_conf[key]
        raise KeyError(f"'Scenario' object has no key '{key}'")

    def add_metric(self, name: str, metric: Metrics) -> None:
        """Add a metric to track for this episode.

        Args:
            name (str): The name of the metric.
            metric (Metrics): The metric instance to add.

        Raises:
            ValueError: If the name is already used.
        """
        if name in self._logs:
            raise ValueError(f"{name} is a reserved name and is not allowed.")
        self._logs[name] = metric
    
    def log_code(self, key: str, code_content: str) -> None:
        """Log code content as an artifact.

        Args:
            key (str): The key for the code artifact.
            code_content (str): The code content to log.
        """
        if key in RESERVED_NAMES:
            raise ValueError(f"{key} is a reserved name and is not allowed.")
        self._logs[key] = Code(
            run_id=self._run_id,
            key=key,
            code_content=code_content,
            episode_id=self._episode_id
        )

    def log(self, data: dict, x: dict | None = None, replace: bool = False) -> None:
        """Log data points or values for the episode.

        Args:
            data (dict): Dictionary of key-value pairs to log.
            x (dict | None): Optional dictionary of x-axis values for each key.
            replace (bool): Whether to replace existing values. Defaults to False.

        Raises:
            ValueError: If a key is reserved or logging fails.
        """
        for key, value in data.items():
            if key in RESERVED_NAMES:
                raise ValueError(f"{key} is a reserved name and is not allowed.")
            if key not in self._logs:
                self._logs[key] = value
            else:
                cur_val = self._logs[key]
                if isinstance(cur_val, Metrics):
                    cur_x = x.get(key) if x is not None else None
                    cur_val.log(value, x=cur_x, replace=replace)
                else:
                    if replace:
                        self._logs[key] = value
                    else:
                        raise ValueError(f"Cannot log value for key '{key}' as there is already a value logged.")

    @property
    def yaml(self) -> str:
        """The current scenario configuration as a YAML string.

        Returns:
            str: The current scenario as a YAML string.
        """
        return OmegaConf.to_yaml(self._scenario_conf)
    
    def discard(self) -> None:
        """Mark the episode as discarded/canceled."""
        self._finish(EpisodeStatus.CANCELED)

    def success(self) -> None:
        """Mark the episode as successfully completed."""
        self._finish(EpisodeStatus.SUCCESS)

    def fail(self) -> None:
        """Mark the episode as failed."""
        self._finish(EpisodeStatus.FAILED)

    def finish(self, status: EpisodeStatus, err_msg: str | None = None) -> None:
        """Finish the episode with a specific status.

        Args:
            status (EpisodeStatus): The final status of the episode.
            err_msg (str | None): Optional error message if the episode errored.
        """
        if self._is_finished:
            return
        self._is_finished = True
        self._episode_status = status

        self._api_client.upload_code(
            artifact_key="scenario",
            run_id=self._run_id,
            episode_id=self._episode_id,
            code_content=self.yaml
        )

        # TODO: submit final metrics
        for key, value in self._logs.items():
            if isinstance(value, Summary):
                metric_val = value.finalize()
                pickled = pickle.dumps(metric_val["value"])
                self._api_client.upload_python(
                    artifact_key=key,
                    run_id=self._run_id,
                    episode_id=self._episode_id,
                    pickled_bytes=pickled
                )
            elif isinstance(value, Metrics):
                metric_val = value.finalize()
                pickled = pickle.dumps(metric_val)
                self._api_client.upload_metrics(
                    artifact_key=key,
                    run_id=self._run_id,
                    episode_id=self._episode_id,
                    pickled_bytes=pickled,
                    graph_type=value.graph_type.value,
                )
            elif isinstance(value, Code):
                self._api_client.upload_code(
                    artifact_key=value.key,
                    run_id=value.run_id,
                    episode_id=value.episode_id,
                    code_content=value.code_content
                )
            else:
                if not is_standard_type(value):
                    raise ValueError(f"Value for key '{key}' is not a standard type.")
                pickled = pickle.dumps(value)
                self._api_client.upload_python(
                    artifact_key=key,
                    run_id=self._run_id,
                    episode_id=self._episode_id,
                    pickled_bytes=pickled
                )
        
        self._api_client.update_episode(
            run_id=self._run_id,
            episode_id=self._episode_id,
            status=status,
            err_msg=err_msg
        )
