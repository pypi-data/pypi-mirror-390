from typing import Literal, overload

import numpy as np
import numpy.typing as npt
import pandas as pd

from zfpkm.approx import approx
from zfpkm.density import bin_distribution, density, dnorm, nrd0
from zfpkm.peak_finder import find_peaks
from zfpkm.plot import zfpkm_plot
from zfpkm.types import ApproxResult, DensityResult, ZFPKMResult

__all__ = [
    "ApproxResult",
    "DensityResult",
    "ZFPKMResult",
    "approx",
    "bin_distribution",
    "density",
    "dnorm",
    "find_peaks",
    "nrd0",
    "zFPKM",
    "zfpkm_plot",
]


def _zfpkm_1d(fpkm: np.ndarray[tuple[float], float]) -> tuple[pd.Series, ZFPKMResult]: ...


def _zfpkm_2d(fpkm: np.ndarray[tuple[float, float], float]) -> tuple[np.ndarray[tuple[float, float], float], list[ZFPKMResult]]: ...


@overload
def zFPKM(fpkm: pd.DataFrame) -> tuple[pd.DataFrame, list[ZFPKMResult]]: ...


@overload
def zFPKM(fpkm: pd.Series) -> tuple[pd.Series, ZFPKMResult]: ...


@overload
def zFPKM(fpkm: np.ndarray[tuple[float], float], results_as_dict: Literal[False] = False) -> tuple[np.ndarray[tuple[float], float], ZFPKMResult]: ...


@overload
def zFPKM(
    fpkm: np.ndarray[tuple[float], float], results_as_dict: Literal[True] = True
) -> tuple[np.ndarray[tuple[float], float], dict[str, ZFPKMResult]]: ...


@overload
def zFPKM(
    fpkm: np.ndarray[tuple[float, float], float], results_as_dict: Literal[False] = False
) -> tuple[np.ndarray[tuple[float, float], float], list[ZFPKMResult]]: ...


@overload
def zFPKM(
    fpkm: np.ndarray[tuple[float, float], float], results_as_dict: Literal[True] = True
) -> tuple[np.ndarray[tuple[float, float], float], dict[str, ZFPKMResult]]: ...


def zFPKM(
    fpkm: pd.DataFrame | pd.Series | np.ndarray[tuple[float], float] | np.ndarray[tuple[float, float], float],
    results_as_dict: bool = False,
) -> tuple[
    pd.DataFrame | pd.Series | np.ndarray[tuple[float], float] | np.ndarray[tuple[float, float], float], list[ZFPKMResult] | dict[str, ZFPKMResult]
]:
    """Calculate zFPKM from raw FPKM values.

    This function will perform a zFPKM calculation, following Hart et al's (2013) paper and the zFPKM implementation at: `https://github.com/ronammar/zFPKM`

    The input dataframe should have:
        - Row names as genomic identifier (Entrez Gene ID, Ensembl Gene ID, Gene Symbol, etc.)
        - Column names as sample identifiers

    :param fpkm: raw FPKM values.
    :param results_as_dict: if true, the `ZFPKMResult` object will be returned as a dictionary where:
        - the keys are the column names (if a `pd.DataFrame` provided as input), otherwise integer values (if a `np.ndarray` provided as input)
        - the values are the `ZFPKMResult` object of the associated key

    :returns: a tuple of:
        1) The zFPKM calculation, where the index and columns are in the same order as the input dataframe
        2) A list of associated metadata, the same length as the number of input columns, containing:
            - Density calculations
            - Mean (peak) Gaussian distribution value
            - Standard deviation of the Gaussian distribution
            - The FPKM value at the Gaussian mean (peak)
    """
    with np.errstate(divide="ignore"):
        log2_fpkm: npt.NDArray[float] = np.log2(fpkm.values if isinstance(fpkm, pd.DataFrame | pd.Series) else fpkm).astype(float)

    if fpkm.ndim > 2:
        raise ValueError("Input ndarray must be 1D or 2D.")

    # if fpkm.ndim == 1:
    #     zfpkm_arr, zfpkm_results = _zfpkm_1d(log2_fpkm)
    # elif fpkm.ndim == 2:
    #     zfpkm_arr, zfpkm_results = _zfpkm_2d(log2_fpkm)
    # else:
    #     raise ValueError(f"Input ndarray must be 1D or 2D, got: {fpkm.ndim}D.")

    zfpkm_df: pd.DataFrame = pd.DataFrame(data=0.0, index=fpkm.index, columns=fpkm.columns)
    zfpkm_results: list[ZFPKMResult] = []

    for i, col in enumerate(fpkm.columns):
        log2_values: npt.NDArray[float] = log2_fpkm[:, i]
        d = density(log2_values)
        peaks: pd.DataFrame = find_peaks(d.y)
        peak_positions = d.x[peaks["peak_idx"]]

        sd = 1.0
        mu = 0.0
        fpkm_at_mu = 0.0
        if peak_positions.size > 0:
            mu = float(peak_positions.max())
            u = float(log2_values[log2_values > mu].mean())
            fpkm_at_mu = float(d.y[peaks.loc[np.argmax(peak_positions).astype(int), "peak_idx"]])
            sd = float((u - mu) * np.sqrt(np.pi / 2))
        zfpkm_df[col] = np.asarray((log2_values - mu) / sd, dtype=float)
        zfpkm_results.append(ZFPKMResult(name=col, density=d, mu=mu, sd=sd, fpkm_at_mu=fpkm_at_mu))

    if results_as_dict:
        return zfpkm_df, {r.name: r for r in zfpkm_results}
    return zfpkm_df, zfpkm_results
