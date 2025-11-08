class Code:
    """Class for logging code artifacts.

    Code artifacts capture source code or configuration files associated with
    runs or episodes. They are stored as text content and can be retrieved later
    for reproducibility and debugging purposes.

    Attributes:
        run_id (str): The unique identifier of the associated run.
        key (str): The artifact key/name for this code.
        code_content (str): The actual code or text content.
        episode_id (str | None): Optional episode identifier if scoped to an episode.
    """
    def __init__(self,
                 run_id: str,
                 key: str,
                 code_content: str,
                 episode_id: str | None = None) -> None:
        super().__init__()
        self._run_id = run_id
        self._key = key
        self._code_content = code_content
        self._episode_id = episode_id

    @property
    def run_id(self) -> str:
        """The unique identifier of the associated run.

        Returns:
            str: The run ID.
        """
        return self._run_id

    @property
    def key(self) -> str:
        """The artifact key/name for this code.

        Returns:
            str: The artifact key.
        """
        return self._key

    @property
    def code_content(self) -> str:
        """The actual code or text content.

        Returns:
            str: The code content.
        """
        return self._code_content

    @property
    def episode_id(self) -> str | None:
        """Optional episode identifier if scoped to an episode.

        Returns:
            str | None: The episode ID, or None if run-scoped.
        """
        return self._episode_id
