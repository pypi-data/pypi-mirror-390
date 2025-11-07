import abc
from typing import Generic, ParamSpec, TypeVar, overload

from bayesline.api._src._utils import docstrings_from_sync
from bayesline.api._src.equity.report.accessor import (
    AsyncTypedReportAccessorApi,
    TypedReportAccessorApi,
)
from bayesline.api._src.equity.report.factor_model import (
    AsyncFactorModelReportApi,
    FactorModelReportApi,
    FactorModelReportSettings,
)
from bayesline.api._src.equity.report.settings import (
    ReportSettings,
)
from bayesline.api._src.equity.report.universe import (
    AsyncUniverseCountReportApi,
    UniverseCountReportApi,
    UniverseCountReportSettings,
)

T = TypeVar("T", bound=TypedReportAccessorApi, covariant=True)
AT = TypeVar("AT", bound=AsyncTypedReportAccessorApi, covariant=True)
S = TypeVar("S", bound=ReportSettings)
P = ParamSpec("P")


class ReportApi(abc.ABC, Generic[P, T, S]):
    """
    A base interface for report APIs.

    It is meant to be extended by several more concrete interfaces which
    narrow down the set of possible args and kwargs to a more specific set,
    e.g. for the subset of possible reports that require a start and end date.
    """

    @property
    @abc.abstractmethod
    def settings(self) -> S:
        """
        The settings used to create this report.

        Returns
        -------
        S
            The settings used to create this report.
        """

    @abc.abstractmethod
    def calculate(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Triggers the calculation of the report and returns an accessor API.

        Parameters
        ----------
        *args: P.args
            The arguments to the report calculation.
        **kwargs: P.kwargs
            The keyword arguments to the report calculation.

        Returns
        -------
        T
            The accessor API for the report result.
        """


@docstrings_from_sync
class AsyncReportApi(abc.ABC, Generic[P, AT, S]):

    @abc.abstractmethod
    async def calculate(  # noqa: D102
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AT: ...

    @property
    @abc.abstractmethod
    def settings(self) -> S: ...  # noqa: D102


class ReportLoaderApi(abc.ABC):
    """The main interface for loading different types of reports."""

    @overload
    def load(self, settings: UniverseCountReportSettings) -> UniverseCountReportApi: ...

    @overload
    def load(self, settings: FactorModelReportSettings) -> FactorModelReportApi: ...

    @abc.abstractmethod
    def load(self, settings: S) -> ReportApi[..., TypedReportAccessorApi, S]:
        """
        Load a report using the specified settings.

        Parameters
        ----------
        settings: S
            The settings to use to load the report.

        Returns
        -------
        ReportApi[..., TypedReportAccessorApi, S]
            The loaded report API.
        """


@docstrings_from_sync
class AsyncReportLoaderApi(abc.ABC):

    @overload
    async def load(  # noqa: D102
        self, settings: UniverseCountReportSettings
    ) -> AsyncUniverseCountReportApi: ...

    @overload
    async def load(  # noqa: D102
        self, settings: FactorModelReportSettings
    ) -> AsyncFactorModelReportApi: ...

    @abc.abstractmethod
    async def load(  # noqa: D102
        self, settings: S
    ) -> AsyncReportApi[..., AsyncTypedReportAccessorApi, S]: ...
