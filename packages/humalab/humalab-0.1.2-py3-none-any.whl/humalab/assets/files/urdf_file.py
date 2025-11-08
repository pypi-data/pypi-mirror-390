import os
import glob
from datetime import datetime

from humalab.assets.files.resource_file import ResourceFile, ResourceType
from humalab.assets.archive import extract_archive
from humalab.constants import DEFAULT_PROJECT


class URDFFile(ResourceFile):
    """Represents a URDF (Unified Robot Description Format) file resource.

    URDF files describe robot kinematics and geometry. This class handles
    automatic extraction of compressed URDF archives and locates the main
    URDF file within the extracted contents.

    Attributes:
        urdf_filename (str | None): Path to the main URDF file.
        root_path (str): Root directory containing the extracted URDF and assets.
    """
    def __init__(self, 
                 name: str, 
                 version: int,
                 filename: str,
                 project: str = DEFAULT_PROJECT,
                 urdf_filename: str | None = None,
                 description: str | None = None,
                 created_at: datetime | None = None,):
        super().__init__(project=project,
                         name=name, 
                         version=version,
                         description=description,
                         filename=filename,
                         resource_type=ResourceType.URDF, 
                         created_at=created_at)
        self._urdf_base_filename = urdf_filename
        self._urdf_filename, self._root_path = self._extract()
        self._urdf_filename = os.path.join(self._urdf_filename, self._urdf_filename)
        
    def _extract(self):
        """Extract the URDF archive and locate the main URDF file.

        Returns:
            tuple[str, str]: (urdf_filename, root_path)
        """
        working_path = os.path.dirname(self.filename)
        if os.path.exists(self.filename):
            _, ext = os.path.splitext(self.filename)
            ext = ext.lstrip('.')  # Remove leading dot
            if ext.lower() != "urdf":
                extract_archive(self.filename, working_path)
                try:
                    os.remove(self.filename)
                except Exception as e:
                    print(f"Error removing saved file {self.filename}: {e}")
        local_filename = self.search_resource_file(self._urdf_base_filename, working_path)
        if local_filename is None:
            raise ValueError(f"Resource filename {self._urdf_base_filename} not found in {working_path}")
        return local_filename, working_path

    def search_resource_file(self, resource_filename: str | None, working_path: str) -> str | None:
        """Search for a URDF file in the working directory.

        Args:
            resource_filename (str | None): Optional specific filename to search for.
            working_path (str): Directory to search within.

        Returns:
            str | None: Path to the found URDF file, or None if not found.
        """
        found_filename = None
        if resource_filename:
            search_path = os.path.join(working_path, "**")
            search_pattern = os.path.join(search_path, resource_filename)
            files = glob.glob(search_pattern, recursive=True)
            if len(files) > 0:
                found_filename = files[0]
        
        if found_filename is None:
            ext = "urdf"
            search_pattern = os.path.join(working_path, "**", f"*.{ext}")
            files = glob.glob(search_pattern, recursive=True)
            if len(files) > 0:
                found_filename = files[0]
        return found_filename

    @property
    def urdf_filename(self) -> str | None:
        """Path to the main URDF file.

        Returns:
            str | None: The URDF file path.
        """
        return self._urdf_filename

    @property
    def root_path(self) -> str:
        """Root directory containing the extracted URDF and assets.

        Returns:
            str: The root path.
        """
        return self._root_path
