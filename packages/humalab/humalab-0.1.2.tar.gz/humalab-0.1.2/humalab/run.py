import uuid
import traceback
import pickle
import base64

from humalab.metrics.code import Code
from humalab.metrics.summary import Summary

from humalab.constants import DEFAULT_PROJECT, RESERVED_NAMES, ArtifactType
from humalab.metrics.scenario_stats import ScenarioStats
from humalab.humalab_api_client import EpisodeStatus, HumaLabApiClient, RunStatus
from humalab.metrics.metric import Metrics
from humalab.episode import Episode
from humalab.utils import is_standard_type

from humalab.scenarios.scenario import Scenario

class Run:
    """Represents a run containing multiple episodes for a scenario.

    A Run is a context manager that tracks experiments or evaluations using a specific
    scenario. It manages episode creation, metric logging, and code artifacts. The run
    can contain multiple episodes, each representing a single execution instance.

    Use as a context manager to automatically handle run lifecycle:
        with Run(scenario=my_scenario) as run:
            # Your code here
            pass

    Attributes:
        project (str): The project name under which the run is created.
        id (str): The unique identifier for the run.
        name (str): The name of the run.
        description (str): A description of the run.
        tags (list[str]): A list of tags associated with the run.
        scenario (Scenario): The scenario associated with the run.
    """
    def __init__(self,
                 scenario: Scenario,
                 project: str = DEFAULT_PROJECT,
                 name: str | None = None,
                 description: str | None = None,
                 id: str | None = None,
                 tags: list[str] | None = None,

                 base_url: str | None = None,
                 api_key: str | None = None,
                 timeout: float | None = None,
                 ) -> None:
        """
        Initialize a new Run instance.
        
        Args:
            project (str): The project name under which the run is created.
            scenario (Scenario): The scenario instance for the run.
            name (str | None): The name of the run.
            description (str | None): A description of the run.
            id (str | None): The unique identifier for the run. If None, a UUID is generated.
            tags (list[str] | None): A list of tags associated with the run.
        """
        self._project = project
        self._id = id or str(uuid.uuid4())
        self._name = name or ""
        self._description = description or ""
        self._tags = tags or []

        self._scenario = scenario
        self._logs = {}
        self._episodes = {}
        self._is_finished = False

        self._api_client = HumaLabApiClient(base_url=base_url,
                                            api_key=api_key,
                                            timeout=timeout)

    
    @property
    def project(self) -> str:
        """The project name under which the run is created.
        
        Returns:
            str: The project name.
        """
        return self._project
    
    @property
    def id(self) -> str:
        """The unique identifier for the run.
        
        Returns:
            str: The run ID.
        """
        return self._id
    
    @property
    def name(self) -> str:
        """The name of the run.

        Returns:
            str: The run name.
        """
        return self._name
    
    @property
    def description(self) -> str:
        """The description of the run.

        Returns:
            str: The run description.
        """
        return self._description
    
    @property
    def tags(self) -> list[str]:
        """The tags associated with the run.

        Returns:
            list[str]: The list of tags.
        """
        return self._tags
    
    @property
    def scenario(self) -> Scenario:
        """The scenario associated with the run.

        Returns:
            Scenario: The scenario instance.
        """
        return self._scenario
    
    def __enter__(self):
        """Enter the run context."""
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """Exit the run context and finalize the run."""
        if self._is_finished:
            return
        if exception_type is not None:
            err_msg = "".join(traceback.format_exception(exception_type, exception_value, exception_traceback))
            self.finish(status=RunStatus.ERRORED, err_msg=err_msg)
        else:
            self.finish()

    def create_episode(self, episode_id: str | None = None) -> Episode:
        """Create a new episode for this run.

        Args:
            episode_id (str | None): Optional unique identifier for the episode.
                If None, a UUID is generated automatically.

        Returns:
            Episode: The newly created episode instance.
        """
        episode = None
        episode_id = episode_id or str(uuid.uuid4())
        cur_scenario, episode_vals = self._scenario.resolve()
        episode = Episode(run_id=self._id,
                          episode_id=episode_id,
                          scenario_conf=cur_scenario,
                          episode_vals=episode_vals)
        self._handle_scenario_stats(episode, episode_vals)
        
        return episode

    def _handle_scenario_stats(self, episode: Episode, episode_vals: dict) -> None:
        for metric_name, value in episode_vals.items():
            if metric_name not in self._logs:
                stat = ScenarioStats(name=metric_name,
                                    distribution_type=value["distribution"])
                self._logs[metric_name] = stat
            self._logs[metric_name].log(data=value["value"],
                                        x=episode.episode_id)
        self._episodes[episode.episode_id] = episode
    
    def add_metric(self, name: str, metric: Metrics) -> None:
        """Add a metric to track for this run.

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
            run_id=self._id,
            key=key,
            code_content=code_content,
        )

        
    def log(self, data: dict, x: dict | None = None, replace: bool = False) -> None:
        """Log data points or values for the run.

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
    def _finish_episodes(self,
                         status: RunStatus,
                         err_msg: str | None = None) -> None:
        for episode in self._episodes.values():
            if not episode.is_finished:
                if status == RunStatus.FINISHED:
                    episode.finish(status=EpisodeStatus.SUCCESS, err_msg=err_msg)
                elif status == RunStatus.ERRORED:
                    episode.finish(status=EpisodeStatus.ERRORED, err_msg=err_msg)
                elif status == RunStatus.CANCELED:
                    episode.finish(status=EpisodeStatus.CANCELED, err_msg=err_msg)
        

    def finish(self,
               status: RunStatus = RunStatus.FINISHED,
               err_msg: str | None = None) -> None:
        """Finish the run and submit final metrics.

        Args:
            status (RunStatus): The final status of the run.
            err_msg (str | None): An optional error message.
        """
        if self._is_finished:
            return
        self._is_finished = True
        self._finish_episodes(status=status, err_msg=err_msg)

        self._api_client.upload_code(
            artifact_key="scenario",
            run_id=self._id,
            code_content=self.scenario.yaml
        )

        self._api_client.upload_python(
            artifact_key="seed",
            run_id=self._id,
            pickled_bytes=pickle.dumps(self.scenario.seed)
        )
        # TODO: submit final metrics
        for key, value in self._logs.items():
            if isinstance(value, ScenarioStats):
                for episode_id, episode in self._episodes.items():
                    episode_status = episode.status
                    value.log_status(
                        episode_id=episode_id,
                        episode_status=episode_status
                    )
                metric_val = value.finalize()
                pickled = pickle.dumps(metric_val)
                self._api_client.upload_scenario_stats_artifact(
                    artifact_key=key,
                    run_id=self._id,
                    pickled_bytes=pickled,
                    graph_type=value.graph_type.value,
                )
            elif isinstance(value, Summary):
                metric_val = value.finalize()
                pickled = pickle.dumps(metric_val["value"])
                self._api_client.upload_python(
                    artifact_key=key,
                    run_id=self._id,
                    pickled_bytes=pickled
                )
            elif isinstance(value, Metrics):
                metric_val = value.finalize()
                pickled = pickle.dumps(metric_val)
                self._api_client.upload_metrics(
                    artifact_key=key,
                    run_id=self._id,
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
                    run_id=self._id,
                    pickled_bytes=pickled
                )

        self._api_client.update_run(
            run_id=self._id,
            status=status,
            err_msg=err_msg
        )