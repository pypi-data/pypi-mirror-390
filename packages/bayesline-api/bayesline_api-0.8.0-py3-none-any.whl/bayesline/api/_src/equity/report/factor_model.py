import abc

import polars as pl

from bayesline.api._src._utils import docstrings_from_sync
from bayesline.api._src.equity.portfolioreport import (
    AsyncReportAccessorApi,
    ReportAccessorApi,
)
from bayesline.api._src.equity.report.accessor import (
    AsyncTypedReportAccessorApi,
    TypedReportAccessorApi,
)
from bayesline.api._src.equity.report.api import AsyncReportApi, ReportApi
from bayesline.api._src.equity.report.settings import ReportSettings


class FactorModelReportSettings(ReportSettings):
    """Settings for a factor model report."""

    pass


class FactorModelReportAccessor(TypedReportAccessorApi):
    """Specific accessor for a factor model report giving access to the model output."""

    @abc.abstractmethod
    def get_t_stats(self) -> pl.DataFrame:
        """
        Return the t-statistics for the factor model.

        Returns
        -------
        pl.DataFrame
            A dataframe with a `date` column and columns for each factor with their
            respective t-stats.
        """

    @abc.abstractmethod
    def get_p_values(self) -> pl.DataFrame:
        """
        Return the p-values for the factor model.

        Returns
        -------
        pl.DataFrame
            A dataframe with a `date` column and columns for each factor with their
            respective p-values.
        """

    @abc.abstractmethod
    def get_factor_returns(self) -> pl.DataFrame:
        """
        Return the factor returns for the factor model.

        Returns
        -------
        pl.DataFrame
            A dataframe with a `date` column and columns for each factor with their
            respective factor returns.
        """


class FactorModelReportApi(
    ReportApi[[], FactorModelReportAccessor, FactorModelReportSettings]
):
    """API for a factor model report."""

    @abc.abstractmethod
    def calculate(self) -> FactorModelReportAccessor:
        """
        Calculate the factor model report.

        Returns
        -------
        FactorModelReportAccessor
            The factor model report accessor.
        """


class FactorModelReportAccessorImpl(FactorModelReportAccessor):  # noqa: D101

    def __init__(self, accessor: ReportAccessorApi):
        self._accessor = accessor

    @property
    def accessor(self) -> ReportAccessorApi:  # noqa: D102
        return self._accessor

    def get_t_stats(self) -> pl.DataFrame:  # noqa: D102
        raise NotImplementedError()

    def get_p_values(self) -> pl.DataFrame:  # noqa: D102
        raise NotImplementedError()

    def get_factor_returns(self) -> pl.DataFrame:  # noqa: D102
        raise NotImplementedError()


@docstrings_from_sync
class AsyncFactorModelReportAccessor(AsyncTypedReportAccessorApi):

    @property
    @abc.abstractmethod
    def accessor(self) -> AsyncReportAccessorApi: ...  # noqa: D102

    @abc.abstractmethod
    async def get_t_stats(self) -> pl.DataFrame: ...  # noqa: D102

    @abc.abstractmethod
    async def get_p_values(self) -> pl.DataFrame: ...  # noqa: D102

    @abc.abstractmethod
    async def get_factor_returns(self) -> pl.DataFrame: ...  # noqa: D102


@docstrings_from_sync
class AsyncFactorModelReportApi(
    AsyncReportApi[[], AsyncFactorModelReportAccessor, FactorModelReportSettings]
):

    @abc.abstractmethod
    async def calculate(self) -> AsyncFactorModelReportAccessor: ...  # noqa: D102


class AsyncFactorModelReportAccessorImpl(AsyncFactorModelReportAccessor):  # noqa: D101

    def __init__(self, accessor: AsyncReportAccessorApi):
        self._accessor = accessor

    @property
    def accessor(self) -> AsyncReportAccessorApi:  # noqa: D102
        return self._accessor

    async def get_t_stats(self) -> pl.DataFrame:  # noqa: D102
        raise NotImplementedError()

    async def get_p_values(self) -> pl.DataFrame:  # noqa: D102
        raise NotImplementedError()

    async def get_factor_returns(self) -> pl.DataFrame:  # noqa: D102
        raise NotImplementedError()
