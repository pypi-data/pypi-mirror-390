from typing import Any
from threading import RLock

import numpy as np
from omegaconf import OmegaConf, DictConfig, ListConfig
import yaml
from humalab.dists.bernoulli import Bernoulli
from humalab.dists.categorical import Categorical
from humalab.dists.uniform import Uniform
from humalab.dists.discrete import Discrete
from humalab.dists.log_uniform import LogUniform
from humalab.dists.gaussian import Gaussian
from humalab.dists.truncated_gaussian import TruncatedGaussian
from functools import partial
from humalab.constants import GraphType, MetricDimType
import copy
import uuid

DISTRIBUTION_MAP = {
    # 0D distributions
    "uniform": Uniform,
    "bernoulli": Bernoulli,
    "categorical": Categorical,
    "discrete": Discrete,
    "log_uniform": LogUniform,
    "gaussian": Gaussian,
    "truncated_gaussian": TruncatedGaussian,

    # 1D distributions
    "uniform_1d": Uniform,
    "bernoulli_1d": Bernoulli,
    "categorical_1d": Categorical,
    "discrete_1d": Discrete,
    "log_uniform_1d": LogUniform,
    "gaussian_1d": Gaussian,
    "truncated_gaussian_1d": TruncatedGaussian,

    # 2D distributions
    "uniform_2d": Uniform,
    # "bernoulli_2d": Bernoulli,
    # "categorical_2d": Categorical,
    # "discrete_2d": Discrete,
    # "log_uniform_2d": LogUniform,
    "gaussian_2d": Gaussian,
    "truncated_gaussian_2d": TruncatedGaussian,

    # 3D distributions
    "uniform_3d": Uniform,
    # "bernoulli_3d": Bernoulli,
    # "categorical_3d": Categorical,
    # "discrete_3d": Discrete,
    # "log_uniform_3d": LogUniform,
    "gaussian_3d": Gaussian,
    "truncated_gaussian_3d": TruncatedGaussian,

    # 4D distributions
    # "uniform_4d": Uniform,
    # "bernoulli_4d": Bernoulli,
    # "categorical_4d": Categorical,
    # "discrete_4d": Discrete,
    # "log_uniform_4d": LogUniform,
    # "gaussian_4d": Gaussian,
    # "truncated_gaussian_4d": TruncatedGaussian,
    
    # nD distributions
    # "uniform_nd": Uniform,
    # "bernoulli_nd": Bernoulli,
    # "categorical_nd": Categorical,
    # "discrete_nd": Discrete,
    # "log_uniform_nd": LogUniform,
    # "gaussian_nd": Gaussian,
    # "truncated_gaussian_nd": TruncatedGaussian,
    
}

DISTRIBUTION_DIMENSION_MAP = {
    # 0D distributions
    "uniform": 0,
    "bernoulli": 0,
    "categorical": 0,
    "discrete": 0,
    "log_uniform": 0,
    "gaussian": 0,
    "truncated_gaussian": 0,

    # 1D distributions
    "uniform_1d": 1,
    "bernoulli_1d": 1,
    "categorical_1d": 1,
    "discrete_1d": 1,
    "log_uniform_1d": 1,
    "gaussian_1d": 1,
    "truncated_gaussian_1d": 1,

    # 2D distributions
    "uniform_2d": 2,
    "gaussian_2d": 2,
    "truncated_gaussian_2d": 2,

    # 3D distributions
    "uniform_3d": 3,
    "gaussian_3d": 3,
    "truncated_gaussian_3d": 3,
}

DISTRIBUTION_PARAM_NUM_MAP = {
    # 0D distributions
    "uniform": 2,
    "bernoulli": 1,
    "categorical": 2,
    "discrete": 3,
    "log_uniform": 2,
    "gaussian": 2,
    "truncated_gaussian": 4,

    # 1D distributions
    "uniform_1d": 2,
    "bernoulli_1d": 1,
    "categorical_1d": 2,
    "discrete_1d": 3,
    "log_uniform_1d": 2,
    "gaussian_1d": 2,
    "truncated_gaussian_1d": 4,

    # 2D distributions
    "uniform_2d": 2,
    "gaussian_2d": 2,
    "truncated_gaussian_2d": 4,

    # 3D distributions
    "uniform_3d": 2,
    "gaussian_3d": 2,
    "truncated_gaussian_3d": 4,
}

SCENARIO_STATS_DIM_TYPE_MAP = {
    # 0D distributions
    "uniform": MetricDimType.ONE_D,
    "bernoulli": MetricDimType.ONE_D,
    "categorical": MetricDimType.ONE_D,
    "discrete": MetricDimType.ONE_D,
    "log_uniform": MetricDimType.ONE_D,
    "gaussian": MetricDimType.ONE_D,
    "truncated_gaussian": MetricDimType.ONE_D,

    # 1D distributions
    "uniform_1d": MetricDimType.ONE_D,
    "bernoulli_1d": MetricDimType.ONE_D,
    "categorical_1d": MetricDimType.ONE_D,
    "discrete_1d": MetricDimType.ONE_D,
    "log_uniform_1d": MetricDimType.ONE_D,
    "gaussian_1d": MetricDimType.ONE_D,
    "truncated_gaussian_1d": MetricDimType.ONE_D,

    # 2D distributions
    "uniform_2d": MetricDimType.TWO_D,
    "gaussian_2d": MetricDimType.TWO_D,
    "truncated_gaussian_2d": MetricDimType.TWO_D,

    # 3D distributions
    "uniform_3d": MetricDimType.THREE_D,
    "gaussian_3d": MetricDimType.THREE_D,
    "truncated_gaussian_3d": MetricDimType.THREE_D,
}

class Scenario:
    """Manages scenario configurations with probabilistic distributions.

    A Scenario encapsulates a configuration template that can contain distribution
    resolvers (e.g., ${uniform:0,1}). When resolved, these distributions are sampled
    to produce concrete scenario instances. Each resolution creates a new episode
    with different sampled values.

    Supported distributions include uniform, gaussian, bernoulli, categorical,
    discrete, log_uniform, and truncated_gaussian, with support for 0D-3D variants.

    Attributes:
        template (DictConfig | ListConfig): The template scenario configuration.
        yaml (str): The current scenario configuration as a YAML string.
    """
    dist_cache = {}
    def __init__(self) -> None:
        self._generator = np.random.default_rng()
        self._scenario_template = OmegaConf.create()
        self._cur_scenario = OmegaConf.create()
        self._scenario_id = None
        self._seed = None

        self._episode_vals = {}
        self._lock = RLock()

    def init(self,
             scenario: str | list | dict | None = None,
             seed: int | None=None,
             scenario_id: str | None=None,
             # num_env: int | None = None
             ) -> None:
        """
        Initialize the scenario with the given parameters.

        Args:
            scenario (str | list | dict | None): The scenario configuration. Can be a YAML
                string, list, or dict. If None, an empty configuration is used.
            seed (int | None): Optional seed for random number generation. If None, uses
                a non-deterministic seed.
            scenario_id (str | None): Optional scenario ID in the format 'id' or 'id:version'.
                If None, a new UUID is generated.
        """
        self._num_env = None # num_env
        self._seed = seed

        # Parse scenario id
        scenario_version = 1
        if scenario_id is not None:
            scenario_arr = scenario_id.split(":")
            if len(scenario_arr) < 1:
                raise ValueError("Invalid scenario_id format. Expected 'scenario_id' or 'scenario_name:version'.")
            scenario_id = scenario_arr[0]
            scenario_version = int(scenario_arr[1]) if len(scenario_arr) > 1 else None
        self._scenario_id = scenario_id or str(uuid.uuid4())
        self._scenario_version = scenario_version

        self._generator = np.random.default_rng(seed)
        self._configure()
        scenario = scenario or {}

        self._scenario_template = OmegaConf.create(scenario)
    
    def _validate_distribution_params(self, dist_name: str, *args: tuple) -> None:
        dimensions = DISTRIBUTION_DIMENSION_MAP[dist_name]
        if not DISTRIBUTION_MAP[dist_name].validate(dimensions, *args):
            raise ValueError(f"Invalid parameters for distribution {dist_name} with dimensions {dimensions}: {args}")

    def _get_final_size(self, size: int | tuple[int, ...] | None) -> int | tuple[int, ...] | None:
        n = self._num_env
        if size is None:
            return n
        if n is None:
            return size
        if isinstance(size, int):
            return (n, size)
        return (n, *size)
    
    def _get_node_path(self, root: dict | list, node: str) -> str:
        if isinstance(root, list):
            root = {str(i): v for i, v in enumerate(root)}
        
        for key, value in root.items():
            if value == node:
                return str(key)
            if isinstance(value, dict):
                sub_path = self._get_node_path(value, node)
                if sub_path:
                    return f"{key}.{sub_path}"
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    if item == node:
                        return f"{key}[{idx}]"
                    if isinstance(item, (dict, list)):
                        sub_path = self._get_node_path(item, node)
                        if sub_path:
                            return f"{key}[{idx}].{sub_path}"
        return ""

    @staticmethod
    def _convert_to_python(obj) -> Any:
        if not isinstance(obj, (np.ndarray, np.generic)):
            return obj

        # NumPy scalar (np.generic) or 0-D ndarray
        if isinstance(obj, np.generic) or (isinstance(obj, np.ndarray) and obj.ndim == 0):
            return obj.item()

        # Regular ndarray (1-D or higher)
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        return obj

    def _configure(self) -> None:
        self._clear_resolvers()
        def distribution_resolver(dist_name: str, *args, _node_, _root_, _parent_, **kwargs):
            if len(args) > DISTRIBUTION_PARAM_NUM_MAP[dist_name]:
                args = args[:DISTRIBUTION_PARAM_NUM_MAP[dist_name]]
                print(f"Warning: Too many parameters for {dist_name}, expected {DISTRIBUTION_PARAM_NUM_MAP[dist_name]}, got {len(args)}. Extra parameters will be ignored.")
            
            self._validate_distribution_params(dist_name, *args)
            # print("_node_: ", _node_, type(_node_))
            # print("_root_: ", _root_, type(_root_))
            # print("_parent_: ", _parent_, type(_parent_))
            # print("Args: ", args, len(args))
            # print("Kwargs: ", kwargs)

            root_yaml = yaml.safe_load(OmegaConf.to_yaml(_root_))
            key_path = self._get_node_path(root_yaml, str(_node_))
            
            shape = None 
            
            if DISTRIBUTION_DIMENSION_MAP[dist_name] == -1:
                shape = args[DISTRIBUTION_PARAM_NUM_MAP[dist_name] - 1]
                args = args[:-1]
            else:
                shape = DISTRIBUTION_DIMENSION_MAP[dist_name] if DISTRIBUTION_DIMENSION_MAP[dist_name] > 0 else None
            shape = self._get_final_size(shape)

            key = str(_node_)
            if key not in Scenario.dist_cache:
                Scenario.dist_cache[key] = DISTRIBUTION_MAP[dist_name].create(self._generator, *args, size=shape, **kwargs)
            ret_val = Scenario.dist_cache[key].sample()
            ret_val = Scenario._convert_to_python(ret_val)

            if isinstance(ret_val, list):
                ret_val = ListConfig(ret_val)
            
            self._episode_vals[key_path] = {
                    "value": ret_val,
                    "distribution": dist_name,
                }
            return ret_val

        for dist_name in DISTRIBUTION_MAP.keys():
            OmegaConf.register_new_resolver(dist_name, partial(distribution_resolver, dist_name))

    def _clear_resolvers(self) -> None:
        self.dist_cache.clear()
        OmegaConf.clear_resolvers()
    
    def resolve(self) -> tuple[DictConfig | ListConfig, dict]:
        """Resolve the scenario configuration, sampling all distributions.

        Returns:
            tuple[DictConfig | ListConfig, dict]: The resolved scenario and episode values.
        """
        with self._lock:
            cur_scenario = copy.deepcopy(self._scenario_template)
            self._episode_vals = {}
            OmegaConf.resolve(cur_scenario)
            episode_vals = copy.deepcopy(self._episode_vals)
            return cur_scenario, episode_vals

    @property
    def scenario_id(self) -> str | None:
        """The scenario ID.

        Returns:
            str | None: The scenario ID, or None if not set.
        """
        return self._scenario_id

    @property
    def seed(self) -> int | None:
        """The random seed for the scenario.

        Returns:
            int | None: The random seed, or None if not set.
        """
        return self._seed

    @property
    def template(self) -> Any:
        """The template scenario configuration.
        
        Returns:
            Any: The template scenario as an OmegaConf object.
        """
        return self._scenario_template
    
    @property
    def yaml(self) -> str:
        """The current scenario configuration as a YAML string.

        Returns:
            str: The current scenario as a YAML string.
        """
        return OmegaConf.to_yaml(self._scenario_template)
