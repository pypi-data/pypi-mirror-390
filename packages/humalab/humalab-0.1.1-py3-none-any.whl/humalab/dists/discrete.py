from humalab.dists.distribution import Distribution
from typing import Any

import numpy as np

class Discrete(Distribution):
    """Discrete uniform distribution over integers.

    Samples integer values uniformly from a range [low, high). The endpoint
    parameter controls whether the upper bound is inclusive or exclusive.
    Supports scalar outputs as well as multi-dimensional arrays with 1D variants.
    """
    def __init__(self, 
                 generator: np.random.Generator,
                 low: int | Any, 
                 high: int | Any,
                 endpoint: bool | None = None,
                 size: int | tuple[int, ...] | None = None,
                 ) -> None:
        """
        Initialize the discrete distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            low (int | Any): The lower bound (inclusive).
            high (int | Any): The upper bound (exclusive).
            endpoint (bool | None): Whether to include the endpoint.
            size (int | tuple[int, ...] | None): The size of the output.
        """
        super().__init__(generator=generator)
        self._low = np.array(low)
        self._high = np.array(high)
        self._size = size
        self._endpoint = endpoint if endpoint is not None else True
    
    @staticmethod
    def validate(dimensions: int, *args) -> bool:
        """Validate distribution parameters for the given dimensions.

        Args:
            dimensions (int): The number of dimensions (0 for scalar, -1 for any).
            *args: The distribution parameters (low, high).

        Returns:
            bool: True if parameters are valid, False otherwise.
        """
        arg1 = args[0]
        arg2 = args[1]
        if dimensions == 0:
            if not isinstance(arg1, int):
                return False
            if not isinstance(arg2, int):
                return False
            return True
        if dimensions == -1:
            return True
        if not isinstance(arg1, int):
            if isinstance(arg1, (list, np.ndarray)):
                if len(arg1) != dimensions:
                    return False
        if not isinstance(arg2, int):
            if isinstance(arg2, (list, np.ndarray)):
                if len(arg2) != dimensions:
                    return False
        return True

    def _sample(self) -> int | float | np.ndarray:
        """Generate a sample from the discrete distribution.

        Returns:
            int | float | np.ndarray: Sampled integer value(s) from [low, high).
        """
        return self._generator.integers(self._low, self._high, size=self._size, endpoint=self._endpoint)

    def __repr__(self) -> str:
        """String representation of the discrete distribution.

        Returns:
            str: String representation showing low, high, size, and endpoint.
        """
        return f"Discrete(low={self._low}, high={self._high}, size={self._size}, endpoint={self._endpoint})"
    
    @staticmethod
    def create(generator: np.random.Generator, 
               low: int | Any, 
               high: int | Any, 
               endpoint: bool = True,
               size: int | tuple[int, ...] | None = None, 
               ) -> 'Discrete':
        """
        Create a discrete distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            low (int | Any): The lower bound (inclusive).
            high (int | Any): The upper bound (exclusive).
            endpoint (bool): Whether to include the endpoint.
            size (int | tuple[int, ...] | None): The size of the output.

        Returns:
            Discrete: The created discrete distribution.
        """
        return Discrete(generator=generator, low=low, high=high, size=size, endpoint=endpoint)