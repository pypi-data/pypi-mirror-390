#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Author Cleoner S. Pietralonga
# e-mail: cleonerp@gmail.com
# Apache License

import importlib.util
import warnings

import numpy as np
import tensornetwork as tn
from sympy.physics.quantum import TensorProduct
from logicqubit.utils import *

try:
    import torch
except ImportError:  # pragma: no cover - torch is optional at runtime
    torch = None

"""
Hilbert space
"""
class Hilbert():
    __number_of_qubits = 1
    __numeric = True
    __first_left = True
    __tn_backend = "numpy"
    __cuda_enabled = False

    @staticmethod
    def ket(value):  # get ket state
        result = Matrix([[Utils.onehot(i, value)] for i in range(2)], Hilbert.__numeric)
        return result

    @staticmethod
    def bra(value):  # get bra state
        result = Matrix([Utils.onehot(i, value) for i in range(2)], Hilbert.__numeric)
        return result

    @staticmethod
    def getState():  # get state of all qubits
        if Hilbert.getIsNumeric():
            state = Hilbert.kronProduct([Hilbert.ket(0) for i in range(Hilbert.getNumberOfQubits())])
        else:
            if Hilbert.isFirstLeft():
                a = sp.symbols([str(i) + "a" + str(i) + "_0" for i in range(1, Hilbert.getNumberOfQubits() + 1)])
                b = sp.symbols([str(i) + "b" + str(i) + "_1" for i in range(1, Hilbert.getNumberOfQubits() + 1)])
            else:
                a = sp.symbols([str(Hilbert.getNumberOfQubits() + 1 - i) + "a" + str(i) + "_0" for i in
                                reversed(range(1, Hilbert.getNumberOfQubits() + 1))])
                b = sp.symbols([str(Hilbert.getNumberOfQubits() + 1 - i) + "b" + str(i) + "_1" for i in
                                reversed(range(1, Hilbert.getNumberOfQubits() + 1))])
            state = Hilbert.kronProduct([Hilbert.ket(0) * a[i] + Hilbert.ket(1) * b[i] for i in range(Hilbert.getNumberOfQubits())])
        return state

    @staticmethod
    def getAdjoint(psi):  # get adjoint matrix
        result = psi.adjoint()
        return result

    @staticmethod
    def product(Operator, psi):  # performs an operation between the operator and the psi state
        result = Operator * psi
        return result

    @staticmethod
    def kronProduct(list):  # Kronecker product
        A = list[0]  # acts in qubit 1 which is the left most
        for M in list[1:]:
            A = A.kron(M)
        return A

    @staticmethod
    def setNumberOfQubits(number):
        Hilbert.__number_of_qubits = number

    @staticmethod
    def getNumberOfQubits():
        return Hilbert.__number_of_qubits

    @staticmethod
    def setNumeric(numeric):
        Hilbert.__numeric = numeric

    @staticmethod
    def getIsNumeric():
        return Hilbert.__numeric

    @staticmethod
    def setFirstLeft(value):
        Hilbert.__first_left = value

    @staticmethod
    def isFirstLeft():
        return Hilbert.__first_left

    @staticmethod
    def configureTensorBackend(backend=None, enable_cuda=False):
        resolved_backend = _TensorNetworkNumeric.resolve_backend(backend, enable_cuda)
        backend_used, cuda_enabled = _TensorNetworkNumeric.set_backend(resolved_backend, enable_cuda)
        Hilbert.__tn_backend = backend_used
        Hilbert.__cuda_enabled = cuda_enabled

    @staticmethod
    def getTensorBackend():
        return Hilbert.__tn_backend

    @staticmethod
    def isCudaEnabled():
        return Hilbert.__cuda_enabled


class _TensorNetworkNumeric:
    """Helper methods that rely on TensorNetwork operations for numeric work."""

    _DEFAULT_BACKEND = "numpy"
    _GPU_BACKENDS = (("jax", "jax"), ("pytorch", "torch"), ("tensorflow", "tensorflow"))
    _GPU_BACKEND_NAMES = tuple(name for name, _ in _GPU_BACKENDS)
    _current_backend = _DEFAULT_BACKEND
    _cuda_enabled = False
    _torch_device = None
    _torch_real_dtype = None
    _torch_complex_dtype = None

    @classmethod
    def resolve_backend(cls, requested_backend, enable_cuda):
        if requested_backend:
            return requested_backend
        if enable_cuda:
            for backend_name, module_name in cls._GPU_BACKENDS:
                if importlib.util.find_spec(module_name):
                    return backend_name
            warnings.warn("CUDA flag requested, but no GPU-capable backend was found. Falling back to numpy.",
                          RuntimeWarning)
        return cls._DEFAULT_BACKEND

    @classmethod
    def set_backend(cls, backend, enable_cuda):
        try:
            tn.set_default_backend(backend)
            cls._current_backend = backend
            cls._cuda_enabled = cls._activate_cuda(enable_cuda, backend)
        except Exception as error:
            warnings.warn(f"TensorNetwork backend '{backend}' is unavailable ({error}). Reverting to numpy.",
                          RuntimeWarning)
            tn.set_default_backend(cls._DEFAULT_BACKEND)
            cls._current_backend = cls._DEFAULT_BACKEND
            cls._cuda_enabled = False
            cls._torch_device = None
        return cls._current_backend, cls._cuda_enabled

    @classmethod
    def get_backend(cls):
        return cls._current_backend

    @classmethod
    def is_cuda_enabled(cls):
        return cls._cuda_enabled

    @classmethod
    def _is_gpu_backend(cls, backend):
        return backend in cls._GPU_BACKEND_NAMES

    @classmethod
    def _activate_cuda(cls, enable_cuda, backend):
        if not enable_cuda:
            cls._torch_device = None
            if torch is not None:
                cls._torch_real_dtype = torch.float64
                cls._torch_complex_dtype = torch.complex128
            return False
        if not cls._is_gpu_backend(backend):
            warnings.warn(f"CUDA was requested, but backend '{backend}' does not provide GPU acceleration.",
                          RuntimeWarning)
            cls._torch_device = None
            if torch is not None:
                cls._torch_real_dtype = torch.float64
                cls._torch_complex_dtype = torch.complex128
            return False
        if backend != "pytorch":
            return True
        if torch is None:
            warnings.warn("PyTorch backend selected but torch is not installed. Falling back to CPU numpy backend.",
                          RuntimeWarning)
            tn.set_default_backend(cls._DEFAULT_BACKEND)
            cls._current_backend = cls._DEFAULT_BACKEND
            cls._torch_device = None
            cls._torch_real_dtype = torch.float64
            cls._torch_complex_dtype = torch.complex128
            return False
        if not torch.cuda.is_available():
            warnings.warn("CUDA was requested, but PyTorch could not find a CUDA-capable device. Running on CPU.",
                          RuntimeWarning)
            cls._torch_device = torch.device("cpu")
            cls._torch_real_dtype = torch.float64
            cls._torch_complex_dtype = torch.complex128
            return False
        cls._torch_device = torch.device("cuda")
        cls._torch_real_dtype = torch.float32
        cls._torch_complex_dtype = torch.complex64
        return True

    @staticmethod
    def _to_ndarray(value):
        if isinstance(value, np.ndarray):
            return value
        return np.array(value)

    @staticmethod
    def _promote_dtype(*arrays):
        if not arrays:
            return tuple()
        backend = _TensorNetworkNumeric._current_backend
        if backend == "pytorch":
            return _TensorNetworkNumeric._promote_torch_dtype(*arrays)
        if backend != "numpy":
            return arrays
        target_dtype = np.result_type(*arrays)
        return tuple(np.asarray(array, dtype=target_dtype) for array in arrays)

    @staticmethod
    def _promote_torch_dtype(*tensors):
        if torch is None or not tensors:
            return tensors
        target_dtype = tensors[0].dtype
        for tensor in tensors[1:]:
            target_dtype = torch.promote_types(target_dtype, tensor.dtype)
        promoted = tuple(tensor.to(target_dtype) if tensor.dtype != target_dtype else tensor for tensor in tensors)
        return promoted

    @staticmethod
    def matmul(left, right):
        left_tensor = _TensorNetworkNumeric.to_tensor(left)
        right_tensor = _TensorNetworkNumeric.to_tensor(right)
        left_tensor, right_tensor = _TensorNetworkNumeric._promote_dtype(left_tensor, right_tensor)
        if left_tensor.ndim == 0 or right_tensor.ndim == 0:
            return left_tensor * right_tensor

        backend = _TensorNetworkNumeric._current_backend
        if backend == "pytorch" and torch is not None:
            return torch.matmul(left_tensor, right_tensor)
        if backend == "numpy":
            return np.matmul(left_tensor, right_tensor)

        left_node = tn.Node(left_tensor, name="matrix_left")
        right_node = tn.Node(right_tensor, name="matrix_right")
        if not left_node.edges or not right_node.edges:
            return left_tensor * right_tensor

        tn.connect(left_node.edges[-1], right_node.edges[0])
        result = tn.contract_between(left_node, right_node, name="matrix_product")
        return result.tensor

    @staticmethod
    def kron(left, right):
        left_tensor = _TensorNetworkNumeric.to_tensor(left)
        right_tensor = _TensorNetworkNumeric.to_tensor(right)
        left_tensor, right_tensor = _TensorNetworkNumeric._promote_dtype(left_tensor, right_tensor)
        if left_tensor.ndim == 0 or right_tensor.ndim == 0:
            return left_tensor * right_tensor

        left_shape, right_shape = _TensorNetworkNumeric._match_shapes(left_tensor.shape, right_tensor.shape)
        left_view = _TensorNetworkNumeric._reshape(left_tensor, left_shape)
        right_view = _TensorNetworkNumeric._reshape(right_tensor, right_shape)

        backend = _TensorNetworkNumeric._current_backend
        if backend == "pytorch" and torch is not None:
            tensor = _TensorNetworkNumeric._torch_kron(left_view, right_view, left_shape, right_shape)
        elif backend == "numpy":
            tensor = _TensorNetworkNumeric._numpy_kron(left_view, right_view, left_shape, right_shape)
        else:
            kron_node = tn.outer_product(
                tn.Node(left_view, name="kron_left"),
                tn.Node(right_view, name="kron_right"),
                name="kron_outer"
            )
            tensor = _TensorNetworkNumeric.to_tensor(kron_node.tensor)
            order = _TensorNetworkNumeric._interleave_order(len(left_shape))
            tensor = _TensorNetworkNumeric._transpose(tensor, order)
            result_shape = tuple(l * r for l, r in zip(left_shape, right_shape))
            tensor = _TensorNetworkNumeric._reshape(tensor, result_shape)
            return tensor

        return tensor

    @staticmethod
    def _match_shapes(left_shape, right_shape):
        left_shape = tuple(left_shape) if left_shape else (1,)
        right_shape = tuple(right_shape) if right_shape else (1,)
        if len(left_shape) < len(right_shape):
            left_shape = (1,) * (len(right_shape) - len(left_shape)) + left_shape
        elif len(right_shape) < len(left_shape):
            right_shape = (1,) * (len(left_shape) - len(right_shape)) + right_shape
        return left_shape, right_shape

    @staticmethod
    def _interleave_order(rank):
        order = []
        for i in range(rank):
            order.extend([i, i + rank])
        return order

    @staticmethod
    def _numpy_kron(left_view, right_view, left_shape, right_shape):
        left_flat = left_view.reshape(-1)
        right_flat = right_view.reshape(-1)
        outer = np.outer(left_flat, right_flat)
        tensor = outer.reshape(left_shape + right_shape)
        order = _TensorNetworkNumeric._interleave_order(len(left_shape))
        tensor = tensor.transpose(order)
        result_shape = tuple(l * r for l, r in zip(left_shape, right_shape))
        return tensor.reshape(result_shape)

    @staticmethod
    def _torch_kron(left_view, right_view, left_shape, right_shape):
        left_flat = left_view.reshape(-1)
        right_flat = right_view.reshape(-1)
        outer = torch.outer(left_flat, right_flat)
        tensor = outer.reshape(left_shape + right_shape)
        order = _TensorNetworkNumeric._interleave_order(len(left_shape))
        tensor = tensor.permute(order)
        result_shape = tuple(l * r for l, r in zip(left_shape, right_shape))
        return tensor.reshape(result_shape)

    @staticmethod
    def to_host(value):
        if isinstance(value, np.ndarray):
            return value
        if torch is not None and isinstance(value, torch.Tensor):
            return value.detach().cpu().numpy()
        return np.array(value)

    @classmethod
    def to_tensor(cls, value):
        if cls._current_backend == "pytorch":
            return cls._to_torch_tensor(value)
        array = cls._to_ndarray(value)
        if np.iscomplexobj(array):
            return np.asarray(array, dtype=np.complex128)
        if not np.issubdtype(array.dtype, np.floating):
            return np.asarray(array, dtype=np.float64)
        return array

    @classmethod
    def _to_torch_tensor(cls, value):
        if torch is None:
            raise RuntimeError("PyTorch backend requested, but torch is not installed.")
        if isinstance(value, torch.Tensor):
            tensor = value
        else:
            np_value = np.array(value)
            dtype = cls._torch_complex_dtype if np.iscomplexobj(np_value) else cls._torch_real_dtype
            tensor = torch.as_tensor(np_value, dtype=dtype)
        # Ensure tensors used for linear algebra are floating/complex types.
        if tensor.dtype in (torch.int8, torch.int16, torch.int32, torch.int64, torch.uint8, torch.bool):
            tensor = tensor.to(cls._torch_real_dtype)
        elif tensor.is_floating_point() and tensor.dtype != cls._torch_real_dtype:
            tensor = tensor.to(cls._torch_real_dtype)
        elif tensor.is_complex() and tensor.dtype != cls._torch_complex_dtype:
            tensor = tensor.to(cls._torch_complex_dtype)
        device = cls._torch_device if cls._cuda_enabled and cls._torch_device is not None else torch.device("cpu")
        return tensor.to(device)

    @staticmethod
    def _reshape(tensor, shape):
        if isinstance(tensor, np.ndarray):
            return tensor.reshape(shape)
        if torch is not None and isinstance(tensor, torch.Tensor):
            return tensor.reshape(shape)
        return np.reshape(tensor, shape)

    @staticmethod
    def _transpose(tensor, order):
        if isinstance(tensor, np.ndarray):
            return np.transpose(tensor, order)
        if torch is not None and isinstance(tensor, torch.Tensor):
            return tensor.permute(order)
        return np.transpose(np.array(tensor), order)


class Matrix:

    def __init__(self, matrix, numeric=True):
        self.__numeric = numeric
        if isinstance(matrix, Matrix):
            self.__matrix = matrix._data()
        elif self.__numeric:
            self.__matrix = _TensorNetworkNumeric.to_tensor(matrix)
        else:
            if isinstance(matrix, list):
                self.__matrix = sp.Matrix(matrix)
            else:
                self.__matrix = matrix

    def __add__(self, other):  # sum of the matrices
        operand = other._data() if isinstance(other, Matrix) else other
        result = self.__matrix + operand
        return Matrix(result, self.__numeric)

    def __sub__(self, other):  # subtraction of the matrices
        operand = other._data() if isinstance(other, Matrix) else other
        result = self.__matrix - operand
        return Matrix(result, self.__numeric)

    def __mul__(self, other):  # product of the matrices
        if isinstance(other, Matrix):
            other = other._data()
            if self.__numeric:
                result = _TensorNetworkNumeric.matmul(self.__matrix, other)
            else:
                result = self.__matrix * other
        else:
            result = self.__matrix * other
        return Matrix(result, self.__numeric)

    def __truediv__(self, other):
        result = self.__matrix * (1./other)
        return Matrix(result, self.__numeric)

    def __eq__(self, other):
        operand = other._data() if isinstance(other, Matrix) else other
        return self.__matrix == operand

    def __str__(self):
        if self.__numeric:
            return str(self.get())
        return str(self.__matrix)

    def kron(self, other):  # Kronecker product
        if self.__numeric:
            result = _TensorNetworkNumeric.kron(self.__matrix, other._data())
        else:
            result = TensorProduct(self.__matrix, other.get())
        return Matrix(result, self.__numeric)

    def get(self):
        if self.__numeric:
            return _TensorNetworkNumeric.to_host(self.__matrix)
        return self.__matrix

    def _data(self):
        return self.__matrix

    def getAngles(self):  # converts state coefficients into angles
        angles = []
        if self.__numeric:
            host_matrix = _TensorNetworkNumeric.to_host(self.__matrix)
            angles = np.angle(host_matrix)
        else:
            print("This session is symbolic!")
        return angles

    def trace(self):  # get matrix trace
        if self.__numeric:
            matrix = self.__matrix
            if isinstance(matrix, np.ndarray):
                result = matrix.trace()
            elif torch is not None and isinstance(matrix, torch.Tensor):
                result = torch.trace(matrix)
            else:
                result = np.trace(np.array(matrix))
        else:
            result = self.__matrix.trace()
        return Matrix(result, self.__numeric)

    def adjoint(self):  # get matrix adjoint
        if self.__numeric:
            matrix = self.__matrix
            if isinstance(matrix, np.ndarray):
                result = matrix.transpose().conj()
            elif torch is not None and isinstance(matrix, torch.Tensor):
                result = matrix.transpose(-2, -1).conj()
            else:
                result = np.transpose(np.array(matrix)).conj()
        else:
            result = self.__matrix.transpose().conjugate()
        return Matrix(result, self.__numeric)


# Ensure TensorNetwork starts on the default backend.
Hilbert.configureTensorBackend()
