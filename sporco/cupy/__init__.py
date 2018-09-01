# -*- coding: utf-8 -*-
# Copyright (C) 2018 by Brendt Wohlberg <brendt@ieee.org>
# All rights reserved. BSD 3-clause License.
# This file is part of the SPORCO package. Details of the copyright
# and user license can be found in the 'LICENSE.txt' file distributed
# with the package.

"""Construct variants of solvers and support code that use cupy instead
of numpy"""

from __future__ import absolute_import

import sys
import re
from functools import reduce
try:
    import importlib.util
except ImportError:
    sys.stderr.write('The sporco.cupy subpackage is not supported under '
                     'Python 2.7\n')
    raise

try:
    # Try to import cupy
    import cupy as cp
    # Try to access a device
    cp.cuda.Device(0).compute_capability
    # Flag indicating successful import
    have_cupy = True
    try:
        # Try to import GPUtil
        import GPUtil
    except ImportError:
        GPUtil = None
    # Import appropriate versions of helper functions
    from ._cp_util import *
except:
    # If cupy import or device access fails, import numpy to the same alias
    import numpy as cp
    # Flag indicating unsuccessful import
    have_cupy = False
    # Import appropriate versions of helper functions
    from ._np_util import *

import numpy as np

if not hasattr(cp, 'product'):
    cp.product = cp.prod



def cupy_enabled():
    """Return ``True`` if CuPy is installed and a GPU device is available,
    otherwise return ``False``.
    """

    return have_cupy



def rgetattr(obj, name):
    """Recursive version of :func:`getattr`."""

    return reduce(getattr, name.split('.'), obj)



def rsetattr(obj, name, value):
    """Recursive version of :func:`setattr`."""

    # See goo.gl/BVJ7MN
    path = name.split('.')
    setattr(reduce(getattr, path[:-1], obj), path[-1], value)



def load_module(name):
    """Load the named module without registering it in ``sys.modules``.
    """

    spec = importlib.util.find_spec(name)
    mod = importlib.util.module_from_spec(spec)
    mod.__spec__ = spec
    mod.__loader__ = spec.loader
    spec.loader.exec_module(mod)
    return mod



def patch_module(name, pname, pfile=None, attrib=None):
    """Create a patched copy of the named module and register it in
    ``sys.modules``.
    """

    if attrib is None:
        attrib = {}
    spec = importlib.util.find_spec(name)
    spec.name = pname
    if pfile is not None:
        spec.origin = pfile
    spec.loader.name = pname
    mod = importlib.util.module_from_spec(spec)
    mod.__spec__ = spec
    mod.__loader__ = spec.loader
    sys.modules[pname] = mod
    spec.loader.exec_module(mod)
    for k, v in attrib.items():
        setattr(mod, k, v)
    return mod



def sporco_cupy_patch_module(name, attrib=None):
    """Create a copy of the named sporco module, patch it to replace
    numpy with cupy, and register it in ``sys.modules``.
    """

    pname = re.sub('^sporco.', 'sporco.cupy.', name)
    if attrib is None:
        attrib = {}
    attrib.update({'np': cp})
    mod = patch_module(name, pname, pfile='patched', attrib=attrib)
    mod.__spec__.has_location = False
    return mod



def _list2array(lst):
    if lst and isinstance(lst[0], cp.ndarray):
        return cp.hstack(lst)
    else:
        return cp.asarray(lst)

util = sporco_cupy_patch_module('sporco.util', {'list2array': _list2array})

metric = sporco_cupy_patch_module('sporco.metric')
common = sporco_cupy_patch_module('sporco.common')
cnvrep = sporco_cupy_patch_module('sporco.cnvrep')

def _complex_dtype(dtype):
    dt = cp.dtype(dtype)
    if dt == cp.dtype('float128'):
        return cp.dtype('complex256')
    elif dt == cp.dtype('float64'):
        return cp.dtype('complex128')
    else:
        return cp.dtype('complex64')

def _pyfftw_byte_aligned(array, dtype=None, n=None):
    return array

def _pyfftw_empty_aligned(shape, dtype, order='C', n=None):
    return cp.empty(shape, dtype, order)

def _pyfftw_rfftn_empty_aligned(shape, axes, dtype, order='C', n=None):
    ashp = list(shape)
    raxis = axes[-1]
    ashp[raxis] = ashp[raxis]//2 + 1
    cdtype = _complex_dtype(dtype)
    return cp.empty(ashp, cdtype, order)

def _fftconv(a, b, axes=(0, 1)):
    if cp.isrealobj(a) and cp.isrealobj(b):
        fft = cp.fft.rfftn
        ifft = cp.fft.irfftn
    else:
        fft = cp.fft.fftn
        ifft = cp.fft.ifftn
    dims = cp.maximum(cp.asarray([a.shape[i] for i in axes]),
                      cp.asarray([b.shape[i] for i in axes]))
    dims = [int(d) for d in dims]
    af = fft(a, dims, axes)
    bf = fft(b, dims, axes)
    return ifft(af*bf, dims, axes)

def _inner(x, y, axis=-1):
    return cp.sum(x * y, axis=axis, keepdims=True)

if have_cupy:
    def _zdivide(x, y):
        div = x / y
        div[cp.logical_or(cp.isnan(div), cp.isinf(div))] = 0
        return div
else:
    def _zdivide(x, y):
        return np.divide(x, y, out=np.zeros_like(x), where=(y != 0))


linalg = sporco_cupy_patch_module(
    'sporco.linalg',
    {'have_numexpr': False, 'fftn': cp.fft.fftn, 'ifftn': cp.fft.ifftn,
     'rfftn': cp.fft.rfftn, 'irfftn': cp.fft.irfftn,
     'complex_dtype': _complex_dtype,
     'pyfftw_byte_aligned': _pyfftw_byte_aligned,
     'pyfftw_empty_aligned': _pyfftw_empty_aligned,
     'pyfftw_rfftn_empty_aligned': _pyfftw_rfftn_empty_aligned,
     'fftconv': _fftconv, 'inner': _inner, 'zdivide': _zdivide})

prox = sporco_cupy_patch_module('sporco.prox', {'have_numexpr': False,
                                'sl': linalg})