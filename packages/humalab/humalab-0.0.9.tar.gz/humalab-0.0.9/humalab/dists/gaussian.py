from humalab.dists.distribution import Distribution
from typing import Any
import numpy as np


class Gaussian(Distribution):
    """Gaussian (normal) distribution.

    Samples values from a normal distribution with specified mean (loc) and
    standard deviation (scale). Supports scalar outputs as well as multi-dimensional
    arrays with 1D, 2D, or 3D variants.
    """
    def __init__(self,
                 generator: np.random.Generator,
                 loc: float | Any,
                 scale: float | Any,
                 size: int | tuple[int, ...] | None = None) -> None:
        """
        Initialize the Gaussian (normal) distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            loc (float | Any): The mean of the distribution.
            scale (float | Any): The standard deviation of the distribution.
            size (int | tuple[int, ...] | None): The size of the output.
        """
        super().__init__(generator=generator)
        self._loc = loc
        self._scale = scale
        self._size = size

    @staticmethod
    def validate(dimensions: int, *args) -> bool:
        """Validate distribution parameters for the given dimensions.

        Args:
            dimensions (int): The number of dimensions (0 for scalar, -1 for any).
            *args: The distribution parameters (loc, scale).

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
                if len(arg1) != dimensions:
                    return False
        if not isinstance(arg2, (int, float)):
            if isinstance(arg2, (list, np.ndarray)):
                if len(arg2) != dimensions:
                    return False
        return True

    def _sample(self) -> int | float | np.ndarray:
        """Generate a sample from the Gaussian distribution.

        Returns:
            int | float | np.ndarray: Sampled value(s) from N(loc, scale).
        """
        return self._generator.normal(loc=self._loc, scale=self._scale, size=self._size)

    def __repr__(self) -> str:
        """String representation of the Gaussian distribution.

        Returns:
            str: String representation showing loc, scale, and size.
        """
        return f"Gaussian(loc={self._loc}, scale={self._scale}, size={self._size})"
    
    @staticmethod
    def create(generator: np.random.Generator, 
               loc: float | Any, 
               scale: float | Any, 
               size: int | tuple[int, ...] | None = None) -> 'Gaussian':
        """
        Create a Gaussian (normal) distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            loc (float | Any): The mean of the distribution.
            scale (float | Any): The standard deviation of the distribution.
            size (int | tuple[int, ...] | None): The size of the output.

        Returns:
            Gaussian: The created Gaussian distribution.
        """
        return Gaussian(generator=generator, loc=loc, scale=scale, size=size)