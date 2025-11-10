import torch
from abc import ABC, abstractmethod


class Kernel(ABC):
    """Base class for kernels. Constructor takes expected shape of input tensors."""

    def __init__(self, shape: tuple):
        self._shape = shape
        self._batch_shape = (None,) + shape

    def gram_matrix(self, x: torch.Tensor) -> torch.Tensor:
        """Compute the Gram matrix of the input. Equivalent to dot(x[i], x[j]) for all i, j.

        Args:
            x: Input tensor of shape (M, ...).

        Returns:
            torch.Tensor: Gram matrix of shape (M, M).
        """
        Kernel._assert_shape(expected=self._batch_shape, actual=x.shape)
        return torch.vmap(lambda x_i: torch.vmap(lambda x_j: self.dot(x_i, x_j))(x))(x)

    def dot(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Compute the dot product between two input tensors.

        Args:
            x: Input tensor of shape (...).
            y: Input tensor of shape (...).

        Returns:
            torch.Tensor: scalar value of inner product between x and y.
        """
        Kernel._assert_shape(expected=self._shape, actual=x.shape)
        Kernel._assert_shape(expected=self._shape, actual=y.shape)
        return self._dot_impl(x, y)

    @abstractmethod
    def _dot_impl(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        pass

    @staticmethod
    def _assert_shape(expected: tuple, actual: tuple):
        assert len(expected) == len(
            actual
        ), f"Expected tensor to have {len(expected)} dimensions but got {len(actual)}"
        for i, (exp, act) in enumerate(zip(expected, actual)):
            if exp is None:
                continue
            elif exp is ...:
                break
            else:
                assert exp == act, f"Expected tensor to have size {exp} at dim {i} but got {act}"

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)
