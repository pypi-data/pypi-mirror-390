"""Operations for managing and retrieving scenarios."""

from typing import Optional
from dataclasses import dataclass

from humalab.humalab_api_client import HumaLabApiClient
from humalab.scenarios.scenario import Scenario
from humalab.constants import DEFAULT_PROJECT

@dataclass
class ScenarioMetadata:
    """Metadata for a scenario stored in HumaLab.

    Attributes:
        id (str): Unique identifier for the scenario.
        version (int): Version number of the scenario.
        project (str): Project name the scenario belongs to.
        name (str): Human-readable scenario name.
        description (str | None): Optional scenario description.
        created_at (str): ISO timestamp when scenario was created.
        updated_at (str): ISO timestamp when scenario was last updated.
    """
    id: str
    version: int
    project: str
    name: str
    description: str | None
    created_at: str
    updated_at: str


def list_scenarios(project: str = DEFAULT_PROJECT,
                   limit: int = 20,
                   offset: int = 0,
                   include_inactive: bool = False,
                   search: Optional[str] = None,
                   status_filter: Optional[str] = None,

                   base_url: str | None = None,
                   api_key: str | None = None,
                   timeout: float | None = None,
                   ) -> list[ScenarioMetadata]:
    """
    List all scenarios for a given project.

    Args:
        project (str): The project name to list scenarios from. Defaults to DEFAULT_PROJECT.
        limit (int): Maximum number of scenarios to return. Defaults to 20.
        offset (int): Number of scenarios to skip for pagination. Defaults to 0.
        include_inactive (bool): Whether to include inactive scenarios. Defaults to False.
        search (Optional[str]): Search query to filter scenarios by name or description. Defaults to None.
        status_filter (Optional[str]): Filter scenarios by status. Defaults to None.
        base_url (str | None): The base URL of the HumaLab API. If None, uses configured value.
        api_key (str | None): The API key for authentication. If None, uses configured value.
        timeout (float | None): The timeout for API requests in seconds. If None, uses configured value.

    Returns:
        list[ScenarioMetadata]: A list of scenario metadata objects.
    """
    api_client = HumaLabApiClient(base_url=base_url,
                                  api_key=api_key,
                                  timeout=timeout)
    resp = api_client.get_scenarios(project_name=project,
                                    limit=limit,
                                    offset=offset,
                                    include_inactive=include_inactive,
                                    search=search,
                                    status_filter=status_filter)
    ret_list = []
    for scenario in resp.get("scenarios", []):
        scenario["project"] = project
        ret_list.append(ScenarioMetadata(id=scenario["uuid"],
                                         version=scenario["version"],
                                         project=project,
                                         name=scenario["name"],
                                         description=scenario.get("description"),
                                         created_at=scenario.get("created_at"),
                                         updated_at=scenario.get("updated_at")))
    return ret_list

def get_scenario(scenario_id: str,
                 version: int | None = None,
                 project: str = DEFAULT_PROJECT,
                 seed: int | None=None,

                 base_url: str | None = None,
                 api_key: str | None = None,
                 timeout: float | None = None,) -> Scenario:
    """Retrieve and initialize a scenario from HumaLab.

    Args:
        scenario_id (str): The unique identifier of the scenario.
        version (int | None): Optional specific version to retrieve.
        project (str): The project name. Defaults to DEFAULT_PROJECT.
        seed (int | None): Optional seed for scenario randomization.
        base_url (str | None): Optional API host override.
        api_key (str | None): Optional API key override.
        timeout (float | None): Optional timeout override.

    Returns:
        Scenario: The initialized scenario instance.
    """
    api_client = HumaLabApiClient(base_url=base_url,
                                  api_key=api_key,
                                  timeout=timeout)
    scenario_resp = api_client.get_scenario(
        project_name=project,
        uuid=scenario_id, version=version)
    scenario = Scenario()

    scenario.init(scenario=scenario_resp["yaml_content"],
                  seed=seed,
                  scenario_id=f"{scenario_id}:{version}" if version is not None else scenario_id)
    return scenario