from humalab.dists.distribution import Distribution

from typing import Any
import numpy as np

class Uniform(Distribution):
    """Uniform distribution over a continuous or discrete range.

    Samples values uniformly from the half-open interval [low, high). Supports
    scalar outputs as well as multi-dimensional arrays with 1D, 2D, or 3D variants.
    """
    def __init__(self, 
                 generator: np.random.Generator,
                 low: float | Any, 
                 high: float | Any, 
                 size: int | tuple[int, ...] | None = None, ) -> None:
        """
        Initialize the uniform distribution.
        
        Args:
            generator (np.random.Generator): The random number generator.
            low (float | Any): The lower bound (inclusive).
            high (float | Any): The upper bound (exclusive).
            size (int | tuple[int, ...] | None): The size of the output.
        """
        super().__init__(generator=generator)
        self._low = np.array(low)
        self._high = np.array(high)
        self._size = size

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
            if not isinstance(arg1, (int, float)):
                return False
            if not isinstance(arg2, (int, float)):
                return False
            return True
        if dimensions == -1:
            return True
        if not isinstance(arg1, (int, float)):
            if isinstance(arg1, (list, np.ndarray)):
                if len(arg1) > dimensions:
                    return False
        if not isinstance(arg2, (int, float)):
            if isinstance(arg2, (list, np.ndarray)):
                if len(arg2) > dimensions:
                    return False
        return True

    def _sample(self) -> int | float | np.ndarray:
        """Generate a sample from the uniform distribution.

        Returns:
            int | float | np.ndarray: Sampled value(s) from [low, high).
        """
        return self._generator.uniform(self._low, self._high, size=self._size)

    def __repr__(self) -> str:
        """String representation of the uniform distribution.

        Returns:
            str: String representation showing low, high, and size.
        """
        return f"Uniform(low={self._low}, high={self._high}, size={self._size})"
    
    @staticmethod
    def create(generator: np.random.Generator, 
               low: float | Any, 
               high: float | Any, 
               size: int | tuple[int, ...] | None = None) -> 'Uniform':
        """
        Create a uniform distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            low (float | Any): The lower bound (inclusive).
            high (float | Any): The upper bound (exclusive).
            size (int | tuple[int, ...] | None): The size of the output.

        Returns:
            Uniform: The created uniform distribution.
        """
        return Uniform(generator=generator, low=low, high=high, size=size)