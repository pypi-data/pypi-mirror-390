# Fast evaluation of multivariate normal distributions

This package provides a fast way to evaluate the pdf and cdf of a standardized multivariate normal distribution. Currently, it only contains code for the bivariate normal distribution.

The implementation in this package is based on the following references:

1. Drezner, Zvi, and George O. Wesolowsky. "On the computation of the bivariate normal integral." Journal of Statistical Computation and Simulation 35.1-2 (1990): 101-107.
2. Genz, Alan, and Frank Bretz. "Computation of multivariate normal and t probabilities." Lecture Notes in Statistics 195 (2009)

Simply put, the method comes down to an interpolation specifically tailored to the multivariate normal distribution.
Although it is an approximation, the method is near to exact and fast.
The implementation in Scipy is based on the same methodology, see [here](https://github.com/scipy/scipy/blob/v1.13.0/scipy/stats/mvndst.f) and [here](https://github.com/scipy/scipy/blob/v1.13.0/scipy/stats/_qmvnt.py.

With scalar input, the speed is comparable to the Scipy implementation.
The Scipy implemantation, however, is slow for vector valued input. This packages containes a vectorized implementation which is signficantly faster albeit still slower than a native C implementation such as the one in the [approxcdf](https://github.com/david-cortes/approxcdf) package.
The advantage of this package is that it is pure Python and does not require any (build) dependencies.

Rough findings for speed improvements compared to the Scipy implementation.
| Module | Correlation | Speed improvement single | Speed improvement vectorized
| --- | --- | --- | --- |
| fastnorm | abs < 0.925 | >1000 x faster than Scipy | 10 x faster than Scipy|
| approxcdf | abs < 0.925 | >1000 x faster than Scipy| 10 x faster than Scipy|
| fastnorm | abs > 0.925 | >1000 x faster than Scipy| 3 x faster than Scipy|
| approxcdf | abs > 0.925 | >1000 x faster than Scipy| 10 x faster than Scipy|

These finds are based on an average of 100 runs and can be reproduced by running the `example.py` script.

## Basic example

```python
import fastnorm as fn
correl = 0.5

x=[1,1]
fn.bivar_norm_pdf(x, correl)
fn.bivar_norm_cdf(x, correl)

x=[[1,1],[2,2]]
fn.bivar_norm_pdf(x, correl)
fn.bivar_norm_cdf(x, correl)
```

## Installation

To install from PyPI:

```bash
pip install fastnorm
```

To install the latest development version from github:

```bash
pip install git+https://github.com/mvds314/fastnorm.git
```

## Development

For development purposes, clone the repo:

```bash
git clone https://github.com/mvds314/fastnorm.git
```

Then navigate to the folder containing `setup.py` and run

```bash
pip install -e .
```

to install the package in edit mode.

Run unittests with `pytest`.

## Roadmap

- Add support for the trivariate and quadrivariate normal distribution.
- Add support for the higher dimensional normal distribution.
- Maybe extend to the multivariate t-distribution.

## Related software

- [approxcdf](https://github.com/david-cortes/approxcdf)
- [Matlab implementations](https://www.math.wsu.edu/faculty/genz/software/software.html)
