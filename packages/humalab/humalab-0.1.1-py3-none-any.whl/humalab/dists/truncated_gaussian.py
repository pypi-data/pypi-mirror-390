from humalab.dists.distribution import Distribution
from typing import Any
import numpy as np


class TruncatedGaussian(Distribution):
    """Truncated Gaussian (normal) distribution.

    Samples values from a normal distribution with specified mean (loc) and
    standard deviation (scale), but constrained to lie within [low, high].
    Values outside the bounds are resampled until they fall within range.
    Supports scalar outputs as well as multi-dimensional arrays with 1D, 2D, or 3D variants.
    """
    def __init__(self,
                 generator: np.random.Generator,
                 loc: float | Any,
                 scale: float | Any,
                 low: float | Any,
                 high: float | Any,
                 size: int | tuple[int, ...] | None = None) -> None:
        """
        Initialize the truncated Gaussian (normal) distribution.
        
        Args:
            generator (np.random.Generator): The random number generator.
            loc (float | Any): The mean of the distribution.
            scale (float | Any): The standard deviation of the distribution.
            low (float | Any): The lower truncation bound.
            high (float | Any): The upper truncation bound.
            size (int | tuple[int, ...] | None): The size of the output.
        """
        super().__init__(generator=generator)
        self._loc = loc
        self._scale = scale
        self._low = low
        self._high = high
        self._size = size

    @staticmethod
    def validate(dimensions: int, *args) -> bool:
        """Validate distribution parameters for the given dimensions.

        Args:
            dimensions (int): The number of dimensions (0 for scalar, -1 for any).
            *args: The distribution parameters (loc, scale, low, high).

        Returns:
            bool: True if parameters are valid, False otherwise.
        """
        arg1 = args[0]
        arg2 = args[1]
        arg3 = args[2]
        arg4 = args[3]
        if dimensions == 0:
            if not isinstance(arg1, (int, float)):
                return False
            if not isinstance(arg2, (int, float)):
                return False
            if not isinstance(arg3, (int, float)):
                return False
            if not isinstance(arg4, (int, float)):
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
        if not isinstance(arg3, (int, float)):
            if isinstance(arg3, (list, np.ndarray)):
                if len(arg3) != dimensions:
                    return False
        if not isinstance(arg4, (int, float)):
            if isinstance(arg4, (list, np.ndarray)):
                if len(arg4) != dimensions:
                    return False
        return True
    
    def _sample(self) -> int | float | np.ndarray:
        """Generate a sample from the truncated Gaussian distribution.

        Samples are generated from N(loc, scale) and resampled if they fall
        outside [low, high].

        Returns:
            int | float | np.ndarray: Sampled value(s) within [low, high].
        """
        samples = self._generator.normal(loc=self._loc, scale=self._scale, size=self._size)
        mask = (samples < self._low) | (samples > self._high)
        while np.any(mask):
            samples[mask] = self._generator.normal(loc=self._loc, scale=self._scale, size=np.sum(mask))
            mask = (samples < self._low) | (samples > self._high)
        return samples

    def __repr__(self) -> str:
        """String representation of the truncated Gaussian distribution.

        Returns:
            str: String representation showing loc, scale, low, high, and size.
        """
        return f"TruncatedGaussian(loc={self._loc}, scale={self._scale}, low={self._low}, high={self._high}, size={self._size})"
    
    @staticmethod
    def create(generator: np.random.Generator, 
               loc: float | Any, 
               scale: float | Any, 
               low: float | Any, 
               high: float | Any, 
               size: int | tuple[int, ...] | None = None) -> 'TruncatedGaussian':
        """
        Create a truncated Gaussian (normal) distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            loc (float | Any): The mean of the distribution.
            scale (float | Any): The standard deviation of the distribution.
            low (float | Any): The lower truncation bound.
            high (float | Any): The upper truncation bound.
            size (int | tuple[int, ...] | None): The size of the output.

        Returns:
            TruncatedGaussian: The created truncated Gaussian distribution.
        """
        return TruncatedGaussian(generator=generator, loc=loc, scale=scale, low=low, high=high, size=size)