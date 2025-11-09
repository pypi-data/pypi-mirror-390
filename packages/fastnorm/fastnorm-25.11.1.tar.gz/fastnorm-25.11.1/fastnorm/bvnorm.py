# -*- coding: utf-8 -*-
"""
Some code for the bivariate normal distribution

The code is based on the code by Alan Genz, which is available at
http://www.math.wsu.edu/faculty/genz/software/tvn.m

Copyright (C) 2011, Alan Genz,  All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided the following conditions are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.
  3. The contributor name(s) may not be used to endorse or promote
     products derived from this software without specific prior
     written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import numpy as np

from .util import type_wrapper


@type_wrapper(xloc=0)
def bivar_norm_pdf(x, rho):
    r"""
    Evaluate the bivariate (standard) normal distribution function with correlation :math:`\rho`

    .. math::
        f([x_0,x_1],\rho)=\frac{e^{-\frac{x_0^2+x_1^2-2\rho x_0 x_1}{2(1-\rho ^2)}}}{2 \pi  \sqrt{1-\rho ^2}}
    """
    if x.shape[-1] != 2:
        raise ValueError("x is assumed to be an arraow with 2 dimensional vectors")
    if np.abs(rho) >= 1:
        raise ValueError("rho should be between -1 and 1")
    if np.any(np.isinf(x)):
        return 0
    else:
        return (
            1
            / (2 * np.pi * np.sqrt(1 - rho**2))
            * np.exp(
                -1 * (x.T[0] ** 2 + x.T[1] ** 2 - 2 * rho * x.T[0] * x.T[1]) / 2 / (1 - rho**2)
            )
        )


@type_wrapper(xloc=0)
def bivar_norm_cdf(x, rho=0):
    r"""
    Evaluate bivariate cummulative standard normal distribution function

    .. math::
        \int_{-\infty}^{a} \int_{-\infty}^{b} \phi(x,y,\rho) dxdy

    with correlation coefficient :math:`\rho`.

    This function is based on the method described by
    Drezner, Z and G.O. Wesolowsky, (1989), On the computation of the bivariate normal inegral, Journal of Statist. Comput. Simul. 35, pp. 101-107.
    """
    assert x.ndim == 1 or x.ndim == 2, "x should be 1 or 2 dimensional array"
    return bvnl(x.T[0], x.T[1], rho)


_w_bvnu_1 = np.array([0.1713244923791705, 0.3607615730481384, 0.4679139345726904])
_x_bvnu_1 = np.array([0.9324695142031522, 0.6612093864662647, 0.2386191860831970])
_w_bvnu_2 = np.array(
    [
        0.04717533638651177,
        0.1069393259953183,
        0.1600783285433464,
        0.2031674267230659,
        0.2334925365383547,
        0.2491470458134029,
    ]
)
_x_bvnu_2 = np.array(
    [
        0.9815606342467191,
        0.9041172563704750,
        0.7699026741943050,
        0.5873179542866171,
        0.3678314989981802,
        0.1252334085114692,
    ]
)
_w_bvnu_3 = np.array(
    [
        0.01761400713915212,
        0.04060142980038694,
        0.06267204833410906,
        0.08327674157670475,
        0.1019301198172404,
        0.1181945319615184,
        0.1316886384491766,
        0.1420961093183821,
        0.1491729864726037,
        0.1527533871307259,
    ]
)
_x_bvnu_3 = np.array(
    [
        0.9931285991850949,
        0.9639719272779138,
        0.9122344282513259,
        0.8391169718222188,
        0.7463319064601508,
        0.6360536807265150,
        0.5108670019508271,
        0.3737060887154196,
        0.2277858511416451,
        0.07652652113349733,
    ]
)
_w_bvnu_1 = np.hstack((_w_bvnu_1, _w_bvnu_1))
_x_bvnu_1 = np.hstack((1 - _x_bvnu_1, 1 + _x_bvnu_1))
_w_bvnu_2 = np.hstack((_w_bvnu_2, _w_bvnu_2))
_x_bvnu_2 = np.hstack((1 - _x_bvnu_2, 1 + _x_bvnu_2))
_w_bvnu_3 = np.hstack((_w_bvnu_3, _w_bvnu_3))
_x_bvnu_3 = np.hstack((1 - _x_bvnu_3, 1 + _x_bvnu_3))


def bvnu(a, b, rho=0):
    r"""
    Evaluate bivariate cummulative standard normal distribution function

    .. math::
        \int_a^\infty \int_b^\infty \phi(x,y,\rho) dxdy

    with correlation coefficient :math:`\rho`.

    This function is based on the method described in [1].

    References
    ----------
    .. [1] Drezner, Z and G.O. Wesolowsky, (1989), On the computation of the bivariate normal inegral, Journal of Statist. Comput. Simul. 35, pp. 101-107.
    """
    global _w_bvnu_1, _x_bvnu_1, _w_bvnu_2, _x_bvnu_2, _w_bvnu_3, _x_bvnu_3
    if np.isposinf(a) or np.isposinf(b):
        p = 0
    elif np.isneginf(a):
        if np.isneginf(b):
            p = 1
        else:
            p = normcdf(-b)
    elif np.isneginf(b):
        p = normcdf(-a)
    elif rho == 0:
        p = normcdf(-a) * normcdf(-b)
    else:
        tp = 2 * np.pi
        h = a
        k = b
        hk = h * k
        bvn = 0
        if abs(rho) < 0.3:  # Gauss Legendre points and weights, n =  6
            w = _w_bvnu_1
            x = _x_bvnu_1
        elif abs(rho) < 0.75:  # Gauss Legendre points and weights, n = 12
            w = _w_bvnu_2
            x = _x_bvnu_2
        else:  # Gauss Legendre points and weights, n = 20
            w = _w_bvnu_3
            x = _x_bvnu_3
        if abs(rho) < 0.925:
            hs = (h * h + k * k) / 2
            asr = np.arcsin(rho) / 2
            sn = np.sin(asr * x)
            bvn = np.dot(np.exp((sn * hk - hs) / (1 - sn**2)), w)
            bvn = bvn * asr / tp + normcdf(-h) * normcdf(-k)
        else:
            if rho < 0:
                k = -k
                hk = -hk
            if abs(rho) < 1:
                ass = 1 - rho**2
                a = np.sqrt(ass)
                bs = (h - k) ** 2
                asr = -(bs / ass + hk) / 2
                c = (4 - hk) / 8
                d = (12 - hk) / 80
                if asr > -100:
                    bvn = (
                        a * np.exp(asr) * (1 - c * (bs - ass) * (1 - d * bs) / 3 + c * d * ass**2)
                    )
                if hk > -100:
                    b = np.sqrt(bs)
                    spp = np.sqrt(tp) * normcdf(-b / a)
                    bvn = bvn - np.exp(-hk / 2) * spp * b * (1 - c * bs * (1 - d * bs) / 3)
                a = a / 2
                xs = (a * x) ** 2
                asr = -(bs / xs + hk) / 2
                ix = asr > -100
                xs = xs[ix]
                spp = 1 + c * xs * (1 + 5 * d * xs)
                rs = np.sqrt(1 - xs)
                ep = np.exp(-(hk / 2) * xs / (1 + rs) ** 2) / rs
                bvn = (a * np.dot(np.exp(asr[ix]) * (spp - ep), w[ix]) - bvn) / tp
            if rho > 0:
                bvn = bvn + normcdf(-max(h, k))
            elif h >= k:
                bvn = -bvn
            else:
                if h < 0:
                    L = normcdf(k) - normcdf(h)
                else:
                    L = normcdf(-h) - normcdf(-k)
                bvn = L - bvn
        p = max(0, min(1, bvn))
    return p


def erf(x):
    """
    From the Handbook of Mathematical Functions, formula 7.1.26.
    """
    # save the sign of x
    sign = np.sign(x)
    x = np.abs(x)

    # constants
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    # A&S formula 7.1.26
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-np.square(x))
    return sign * y  # erf(-x) = -erf(x)


def erfc(x):
    return 1 - erf(x)


def normcdf(x):
    """
    Standard normal cumulative distribution function

    Seems to be slightly faster than scipy.stats.norm.cdf
    """
    return 0.5 * erfc(-x / np.sqrt(2))


def bvnu_vectorized(a, b, rho=0):
    r"""
    Evaluate bivariate cummulative standard normal distribution function

    .. math::
        \int_a^\infty \int_b^\infty \phi(x,y,\rho) dxdy

    with correlation coefficient :math:`\rho`.

    This function is based on the method described in [1].

    References
    ----------
    .. [1] Drezner, Z and G.O. Wesolowsky, (1989), On the computation of the bivariate normal inegral, Journal of Statist. Comput. Simul. 35, pp. 101-107.
    """
    global _w_bvnu_1, _x_bvnu_1, _w_bvnu_2, _x_bvnu_2, _w_bvnu_3, _x_bvnu_3
    a = np.asanyarray(a)
    b = np.asanyarray(b)
    assert a.ndim == b.ndim == 1
    assert len(a) == len(b)
    # If uncorrelated, return the product of the marginals
    if rho == 0:
        return normcdf(-a) * normcdf(-b)
    # If a or b is infinite set appropriate values
    p = np.full(len(a), np.nan)
    neginf_a = np.isneginf(a)
    neginf_b = np.isneginf(b)
    posinf_a = np.isposinf(a)
    posinf_b = np.isposinf(b)
    p[posinf_a | posinf_b] = 0
    p[neginf_a & neginf_b] = 1
    if np.any(neginf_a & ~neginf_b):
        p[neginf_a & ~neginf_b] = normcdf(-b[neginf_a & ~neginf_b])
    if np.any(~neginf_a & neginf_b):
        p[~neginf_a & neginf_b] = normcdf(-a[~neginf_a & neginf_b])
    # Handle the rest
    sel = ~(neginf_a | neginf_b | posinf_a | posinf_b)
    if np.any(sel):
        h = a[sel]
        k = b[sel]
        tp = 2 * np.pi
        hk = h * k
        if abs(rho) < 0.3:  # Gauss Legendre points and weights, n =  6
            w = _w_bvnu_1
            x = _x_bvnu_1
        elif abs(rho) < 0.75:  # Gauss Legendre points and weights, n = 12
            w = _w_bvnu_2
            x = _x_bvnu_2
        else:  # Gauss Legendre points and weights, n = 20
            w = _w_bvnu_3
            x = _x_bvnu_3
        if abs(rho) < 0.925:
            hs = (np.square(h) + np.square(k)) / 2
            asr = np.arcsin(rho) / 2
            sn = np.sin(asr * x)
            bvn = (np.outer(hk, sn) - hs.reshape((-1, 1))) / (1 - np.square(sn))
            bvn = np.dot(np.exp(bvn), w) * asr / tp + normcdf(-h) * normcdf(-k)
        else:
            if rho < 0:
                k = -k
                hk = -hk
            if abs(rho) < 1:
                ass = 1 - rho**2
                a = np.sqrt(ass)
                bs = np.square(h - k)
                asr = -(bs / ass + hk) / 2
                c = (4 - hk) / 8
                d = (12 - hk) / 80
                bvn = np.where(
                    asr > -100,
                    a
                    * np.exp(asr)
                    * (1 - c * (bs - ass) * (1 - d * bs) / 3 + c * d * np.square(ass)),
                    0,
                )
                cond = hk > -100
                if cond.any():
                    b = np.sqrt(bs)[cond]
                    spp = np.sqrt(tp) * normcdf(-b / a)
                    bvn[cond] += -np.exp(-hk[cond] / 2) * spp * b * (1 - c * bs * (1 - d * bs) / 3)
                a = a / 2
                xs = np.square(a * x)
                asr = -(np.outer(bs, 1 / xs) + hk.reshape((-1, 1))) / 2
                xs = np.where(asr > -100, xs, 0)
                spp = 1 + xs * c.reshape((-1, 1)) * (1 + 5 * xs * d.reshape((-1, 1)))
                rs = np.sqrt(1 - xs)
                ep = np.exp(-hk.reshape((-1, 1)) * xs / np.square(1 + rs)) / rs
                bvn = (a * np.dot(np.exp(asr) * (spp - ep), w) - bvn) / tp
            if rho > 0:
                bvn = bvn + normcdf(-np.maximum(h, k))
            else:
                cond = h >= k
                bvn = np.where(cond, -bvn, bvn)
                cond1 = ~cond & (h < 0)
                if cond1.any():
                    bvn[cond1] = normcdf(k[cond1]) - normcdf(h[cond1]) - bvn
                cond2 = ~cond & (h >= 0)
                if cond2.any():
                    bvn[cond2] = normcdf(-h[cond2]) - normcdf(-k[cond2]) - bvn
        p[sel] = np.clip(bvn, 0, 1)
    return p


def bvnl(a, b, rho=0):
    r"""
    Evaluate bivariate cummulative standard normal distribution function

    .. math::
        \int_{-\infty}^{a} \int_{\infty}^{b} \phi(x,y,\rho) dxdy

    with correlation coefficient :math:`\rho`.
    """
    a = np.asanyarray(a)
    b = np.asanyarray(b)
    if a.ndim == 0 and b.ndim == 0:
        return bvnu(-a, -b, rho)
    elif a.ndim == b.ndim == 1:
        return bvnu_vectorized(-a, -b, rho)
    else:
        raise ValueError("Bounds must be scalars or vectors")
