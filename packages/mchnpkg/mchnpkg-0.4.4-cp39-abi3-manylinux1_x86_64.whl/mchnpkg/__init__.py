from mchnpkg._core import hello_from_bin

from mchnpkg.model import LinearRegression


from .model import LinearRegression
__all__ = ["LinearRegression"]

from .model.regression import CauchyRegression

__all__ = ["CauchyRegression"]

from .model.cauchy_statsmodels import CauchyMLE, fit_cauchy_mle
__all__ += ["CauchyMLE", "fit_cauchy_mle"]




def hello() -> str:
    return hello_from_bin()
