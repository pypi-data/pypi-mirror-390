import torch
from nn_lib.analysis.kernels.base import Kernel


class BrownianKernel(Kernel):
    def __init__(self, q: float=1.0):
        super().__init__(shape=(...,))
        self.q = q

    def gram_matrix(self, x: torch.Tensor) -> torch.Tensor:
        """Compute the Gram matrix of the input. Equivalent to dot(x[i], x[j]) for all i, j.

        Args:
            x: Input tensor of shape (M, ...).

        Returns:
            torch.Tensor: Gram matrix of shape (M, M).
        """
        Kernel._assert_shape(self._batch_shape, x.shape)
        xxT = torch.einsum("i...,j...->ij", x, x)
        diag = xxT.diag()
        squared_pairwise_distance = -2 * xxT + diag[:, None] + diag[None, :]
        


    def _dot_impl(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        return torch.sum(x * y)
