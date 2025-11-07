from humalab.dists.distribution import Distribution

from typing import Any
import numpy as np

class Bernoulli(Distribution):
    """Bernoulli distribution for binary outcomes.

    Samples binary values (0 or 1) with a specified probability of success.
    Supports scalar outputs as well as multi-dimensional arrays with 1D variants.
    """
    def __init__(self,
                 generator: np.random.Generator,
                 p: float | Any,
                 size: int | tuple[int, ...] | None = None) -> None:
        """
        Initialize the Bernoulli distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            p (float | Any): The probability of success.
            size (int | tuple[int, ...] | None): The size of the output.
        """
        super().__init__(generator=generator)
        self._p = p
        self._size = size

    @staticmethod
    def validate(dimensions: int, *args) -> bool:
        """Validate distribution parameters for the given dimensions.

        Args:
            dimensions (int): The number of dimensions (0 for scalar, -1 for any).
            *args: The distribution parameters (p).

        Returns:
            bool: True if parameters are valid, False otherwise.
        """
        arg1 = args[0]
        if dimensions == 0:
            if not isinstance(arg1, (int, float)):
                return False
            return True
        if dimensions == -1:
            return True
        if not isinstance(arg1, (int, float)):
            if isinstance(arg1, (list, np.ndarray)):
                if len(arg1) != dimensions:
                    return False

        return True

    def _sample(self) -> int | float | np.ndarray:
        """Generate a sample from the Bernoulli distribution.

        Returns:
            int | float | np.ndarray: Sampled binary value(s) (0 or 1).
        """
        return self._generator.binomial(n=1, p=self._p, size=self._size)

    def __repr__(self) -> str:
        """String representation of the Bernoulli distribution.

        Returns:
            str: String representation showing p and size.
        """
        return f"Bernoulli(p={self._p}, size={self._size})"
    
    @staticmethod
    def create(generator: np.random.Generator, 
               p: float | Any, 
               size: int | tuple[int, ...] | None = None) -> 'Bernoulli':
        """
        Create a Bernoulli distribution.

        Args:
            generator (np.random.Generator): The random number generator.
            p (float | Any): The probability of success.
            size (int | tuple[int, ...] | None): The size of the output.

        Returns:
            Bernoulli: The created Bernoulli distribution.
        """
        return Bernoulli(generator=generator, p=p, size=size)
