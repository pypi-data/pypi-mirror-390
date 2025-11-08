from datetime import datetime
from enum import Enum

from humalab.constants import DEFAULT_PROJECT

class ResourceType(Enum):
    """Enumeration of supported resource file types.

    Supported types include URDF, MJCF, USD formats for robot descriptions,
    MESH for 3D models, VIDEO and IMAGE for media files, and DATA for generic data.
    """
    URDF = "urdf"
    MJCF = "mjcf"
    USD = "usd"
    MESH = "mesh"
    VIDEO = "video"
    IMAGE = "image"
    DATA = "data"



class ResourceFile:
    """Represents a resource file stored in HumaLab.

    Resource files are versioned assets that can be downloaded and used in runs.
    They include robot descriptions, meshes, media files, and other data.

    Attributes:
        project (str): The project name this resource belongs to.
        name (str): The resource name.
        version (int): The version number of this resource.
        filename (str): The local filesystem path to the resource file.
        resource_type (ResourceType): The type of resource.
        created_at (datetime | None): When the resource was created.
        description (str | None): Optional description of the resource.
    """
    def __init__(self, 
                 name: str, 
                 version: int, 
                 filename: str,
                 resource_type: str | ResourceType,
                 project: str = DEFAULT_PROJECT,
                 description: str | None = None,
                 created_at: datetime | None = None):
        self._project = project
        self._name = name
        self._version = version
        self._filename = filename
        self._resource_type = ResourceType(resource_type)
        self._description = description
        self._created_at = created_at

    @property
    def project(self) -> str:
        """The project name this resource belongs to.

        Returns:
            str: The project name.
        """
        return self._project

    @property
    def name(self) -> str:
        """The resource name.

        Returns:
            str: The resource name.
        """
        return self._name

    @property
    def version(self) -> int:
        """The version number of this resource.

        Returns:
            int: The version number.
        """
        return self._version

    @property
    def filename(self) -> str:
        """The local filesystem path to the resource file.

        Returns:
            str: The file path.
        """
        return self._filename

    @property
    def resource_type(self) -> ResourceType:
        """The type of resource.

        Returns:
            ResourceType: The resource type.
        """
        return self._resource_type

    @property
    def created_at(self) -> datetime | None:
        """When the resource was created.

        Returns:
            datetime | None: The creation timestamp, or None if not available.
        """
        return self._created_at

    @property
    def description(self) -> str | None:
        """Optional description of the resource.

        Returns:
            str | None: The description, or None if not provided.
        """
        return self._description

    def __repr__(self) -> str:
        """String representation of the resource file.

        Returns:
            str: String representation with all attributes.
        """
        return f"ResourceFile(project={self._project}, name={self._name}, version={self._version}, filename={self._filename}, resource_type={self._resource_type}, description={self._description}, created_at={self._created_at})"

    def __str__(self) -> str:
        """String representation of the resource file.

        Returns:
            str: Same as __repr__.
        """
        return self.__repr__()

