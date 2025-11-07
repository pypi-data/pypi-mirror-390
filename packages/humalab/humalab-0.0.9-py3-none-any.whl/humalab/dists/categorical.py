from humalab.dists.distribution import Distribution

import numpy as np

class Categorical(Distribution):
    """Categorical distribution for discrete choices.

    Samples from a list of choices with optional weights. If weights are not
    provided, samples uniformly from all choices. Weights are automatically
    normalized to sum to 1.
    """
    def __init__(self,
                 generator: np.random.Generator,
                 choices: list, 
                 weights: list[float] | None = None,
                 size: int | tuple[int, ...] | None = None) -> None:
        """
        Initialize the categorical distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            choices (list): The list of choices.
            weights (list[float] | None): The weights for each choice.
            size (int | tuple[int, ...] | None): The size of the output.
        """
        super().__init__(generator=generator)
        self._choices = choices
        self._size = size
        if weights is not None and not np.isclose(sum(weights), 1.0):
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]
        self._weights = weights

    @staticmethod
    def validate(dimensions: int, *args) -> bool:
        """Validate distribution parameters for the given dimensions.

        Args:
            dimensions (int): The number of dimensions (0 for scalar, -1 for any).
            *args: The distribution parameters (choices, weights).

        Returns:
            bool: Always returns True as categorical accepts any parameters.
        """
        return True

    def _sample(self) -> int | float | np.ndarray:
        """Generate a sample from the categorical distribution.

        Returns:
            int | float | np.ndarray: Sampled choice(s) from the list.
        """
        return self._generator.choice(self._choices, size=self._size, p=self._weights)

    def __repr__(self) -> str:
        """String representation of the categorical distribution.

        Returns:
            str: String representation showing choices, size, and weights.
        """
        return f"Categorical(choices={self._choices}, size={self._size}, weights={self._weights})"
    
    @staticmethod
    def create(generator: np.random.Generator, 
               choices: list, 
               weights: list[float] | None = None,
               size: int | tuple[int, ...] | None = None
               ) -> 'Categorical':
        """
        Create a categorical distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            choices (list): The list of choices.
            size (int | tuple[int, ...] | None): The size of the output.
            weights (list[float] | None): The weights for each choice.

        Returns:
            Categorical: The created categorical distribution.
        """
        return Categorical(generator=generator, choices=choices, size=size, weights=weights)