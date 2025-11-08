from contextlib import contextmanager
import sys
import traceback

from omegaconf import OmegaConf

from humalab.constants import DEFAULT_PROJECT
from humalab.run import Run
from humalab.humalab_config import HumalabConfig
from humalab.humalab_api_client import HumaLabApiClient, RunStatus, EpisodeStatus
import requests

import uuid

from collections.abc import Generator

from humalab.scenarios.scenario import Scenario

_cur_run: Run | None = None

def _pull_scenario(client: HumaLabApiClient,
                   project: str,
                   seed: int | None = None,
                   scenario: str | list | dict | Scenario | None = None,
                   scenario_id: str | None = None,) -> Scenario:
    """Pull a scenario from the server if scenario_id is provided.

    Args:
        client (HumaLabApiClient): API client instance.
        project (str): Project name.
        scenario (str | list | dict | None): Local scenario configuration.
        scenario_id (str | None): ID of scenario to pull from server.

    Returns:
        str | list | dict | None: The scenario configuration.
    """
    if scenario_id is not None:
        scenario_arr = scenario_id.split(":")
        if len(scenario_arr) < 1:
            raise ValueError("Invalid scenario_id format. Expected 'scenario_id' or 'scenario_name:version'.")
        scenario_real_id = scenario_arr[0]
        scenario_version = int(scenario_arr[1]) if len(scenario_arr) > 1 else None

        scenario_response = client.get_scenario(
            project_name=project,
            uuid=scenario_real_id, 
            version=scenario_version)
        final_scenario = scenario_response["yaml_content"]
    else:
        final_scenario = scenario

    if isinstance(final_scenario, Scenario):
        scenario_inst = final_scenario
    else:
        scenario_inst = Scenario()
        scenario_inst.init(scenario=final_scenario, 
                           seed=seed, 
                           scenario_id=scenario_id,
                           #num_env=num_env,
                           )
    return scenario_inst

@contextmanager
def init(project: str | None = None,
         name: str | None = None,
         description: str | None = None,
         id: str | None = None,
         tags: list[str] | None = None,
         scenario: str | list | dict | Scenario | None = None,
         scenario_id: str | None = None,
         seed: int | None=None,
         auto_create_scenario: bool = False,
         # num_env: int | None = None,

         base_url: str | None = None,
         api_key: str | None = None,
         timeout: float | None = None,
         ) -> Generator[Run, None, None]:
    """
    Initialize a new HumaLab run.
    
    Args:
        project: The project name under which to create the run.
        name: The name of the run.
        description: A description of the run.
        id: The unique identifier for the run. If None, a new UUID will be generated.
        tags: A list of tags to associate with the run.
        scenario: The scenario configuration as a string, list, or dict.
        scenario_id: The unique identifier of a pre-defined scenario to use.
        base_url: The base URL of the HumaLab server.
        api_key: The API key for authentication.
        seed: An optional seed for scenario randomization.
        timeout: The timeout for API requests.
        auto_create_scenario: Whether to automatically create the scenario if it does not exist.
        # num_env: The number of parallel environments to run. (Not supported yet.)
    """
    global _cur_run
    run = None
    try:
        project = project or DEFAULT_PROJECT
        name = name or ""
        description = description or ""
        id = id or str(uuid.uuid4())

        api_client = HumaLabApiClient(base_url=base_url,
                                      api_key=api_key,
                                      timeout=timeout)
        scenario_inst = _pull_scenario(client=api_client, 
                                        project=project,
                                        seed=seed,
                                        scenario=scenario, 
                                        scenario_id=scenario_id)
        
        project_resp = api_client.create_project(name=project)
        
        if scenario_id is None and scenario is not None and auto_create_scenario:
            scenario_response = api_client.create_scenario(
                project_name=project_resp['name'],
                name=f"{name} scenario",
                description="Auto-created scenario",
                yaml_content=OmegaConf.to_yaml(scenario_inst.template),
            )
            scenario_id = scenario_response['uuid']
        try:
            run_response = api_client.get_run(run_id=id)
            api_client.update_run(
                run_id=run_response['run_id'],
                name=name,
                description=description,
                tags=tags,
                status=RunStatus.RUNNING,
            )

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                # If not found then create a new run,
                # so ignore not found error.
                run_response = None
            else:
                # Otherwise re-raise the exception.
                raise

        if run_response is None:
            run_response = api_client.create_run(name=name,
                                                 project_name=project_resp['name'],
                                                 description=description,
                                                 tags=tags)
            id = run_response['run_id']
            api_client.update_run(
                run_id=id,
                description=description,
            )

        run = Run(
            project=project_resp['name'],
            name=run_response["name"],
            description=run_response.get("description"),
            id=run_response['run_id'],
            tags=run_response.get("tags"),
            scenario=scenario_inst,

            base_url=base_url,
            api_key=api_key,
            timeout=timeout
        )

        _cur_run = run
        yield run
    except Exception as e:
        if _cur_run:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted_traceback = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            finish(status=RunStatus.ERRORED,
                   err_msg=formatted_traceback)
        raise
    else:
        if _cur_run:
            print("Finishing run...")
            finish(status=RunStatus.FINISHED)

def discard() -> None:
    """Discard the current run by finishing it with CANCELED status."""
    finish(status=RunStatus.CANCELED)

def finish(status: RunStatus = RunStatus.FINISHED,
           err_msg: str | None = None) -> None:
    """Finish the current run.

    Args:
        status (RunStatus): The final status of the run. Defaults to FINISHED.
        err_msg (str | None): Optional error message if the run errored.
    """
    global _cur_run
    if _cur_run:
        _cur_run.finish(status=status, err_msg=err_msg)
        _cur_run = None

def login(api_key: str | None = None,
          relogin: bool | None = None,
          host: str | None = None,
          force: bool | None = None,
          timeout: float | None = None) -> bool:
    """Configure HumaLab authentication and connection settings.

    Args:
        api_key (str | None): API key for authentication.
        relogin (bool | None): Unused parameter (for compatibility).
        host (str | None): API host URL.
        force (bool | None): Unused parameter (for compatibility).
        timeout (float | None): Request timeout in seconds.

    Returns:
        bool: Always returns True.
    """
    humalab_config = HumalabConfig()
    humalab_config.api_key = api_key or humalab_config.api_key
    humalab_config.base_url = host or humalab_config.base_url
    humalab_config.timeout = timeout or humalab_config.timeout
    return True
