# Licensed under a 3-clause BSD style license - see LICENSE.rst
from gammapy.modeling import Fit, Parameter
from gammapy.stats.utils import sigma_to_ts

__all__ = ["select_nested_models"]


class TestStatisticNested:
    """Compute the test statistic (TS) between two nested hypothesis.
    The null hypothesis is the minimal one, for which a set of parameters
    are frozen to given values. The model is updated to the alternative hypothesis
    if there is a significant improvement (larger than the given threshold).

    Parameters
    ----------
    parameters : `~gammapy.modeling.Parameters` or list of `~gammapy.modeling.Parameter`
        List of parameters frozen for the null hypothesis but free for the test hypothesis.
    null_values : list of float or `~gammapy.modeling.Parameters`
        Values of the parameters frozen for the null hypothesis.
        If a `Parameters` object or a list of `Parameters` is given
        the null hypothesis follows the values of these parameters,
        so this tests linked parameters versus unliked.
    n_sigma : float
        Threshold in number of sigma to switch from the null hypothesis
        to the alternative one. Default is 2.
        The TS is converted to sigma assuming that the Wilk's theorem is verified.
    n_free_parameters : int
        Number of free parameters to consider between the two hypothesis
        in order to estimate the `ts_threshold` from the `n_sigma` threshold.
        Default is len(parameters).
    fit : `Fit`
        Fit instance specifying the backend and fit options.
    """

    __test__ = False

    def __init__(
        self, parameters, null_values, n_sigma=2, n_free_parameters=None, fit=None
    ):
        self.parameters = parameters
        self.null_values = null_values
        self.n_sigma = n_sigma

        if n_free_parameters is None:
            n_free_parameters = len(parameters)
        self.n_free_parameters = n_free_parameters

        if fit is None:
            fit = Fit()
            minuit_opts = {"tol": 0.1, "strategy": 1}
            fit.backend = "minuit"
            fit.optimize_opts = minuit_opts
        self.fit = fit

    @property
    def ts_threshold(self):
        """Threshold value in TS corresponding to `n_sigma`.
        This assumes that the TS follows a chi squared distribution
        with a number of degree of freedom equal to `n_free_parameters`.
        """
        return sigma_to_ts(self.n_sigma, self.n_free_parameters)

    def run(self, datasets):
        """Perform the alternative hypothesis testing

        Parameters
        ----------
        datasets : `~gammapy.datasets.Datasets`
            Datasets

        Returns
        -------
        result : dict
            Dict with the TS of the best fit value compared to the null hypothesis
            and fit results for the two hypotheses. Entries are:

                * "ts" : fit statistic difference with null hypothesis
                * "fit_results" : results for the best fit
                * "fit_results_null" : fit results for the null hypothesis
        """

        for p in self.parameters:
            p.frozen = False
        fit_results = self.fit.run(datasets)
        object_cache = [p.__dict__ for p in datasets.models.parameters]
        prev_pars = [p.value for p in datasets.models.parameters]
        stat = datasets.stat_sum()

        for p, val in zip(self.parameters, self.null_values):
            if isinstance(val, Parameter):
                p.__dict__ = val.__dict__
            else:
                p.value = val
                p.frozen = True
        fit_results_null = self.fit.run(datasets)
        stat_null = datasets.stat_sum()

        ts = stat_null - stat
        if ts > self.ts_threshold:
            # restore default model if prefered againt null hypothesis
            for p in self.parameters:
                p.frozen = False
            for kp, p in enumerate(datasets.models.parameters):
                p.__dict__ = object_cache[kp]
                p.value = prev_pars[kp]
        return dict(
            ts=ts,
            fit_results=fit_results,
            fit_results_null=fit_results_null,
        )


def select_nested_models(
    datasets, parameters, null_values, n_sigma=2, n_free_parameters=None, fit=None
):
    """Compute the test statistic (TS) between two nested hypothesis .
    The null hypothesis is the minimal one, for which a set of parameters
    are frozen to given values. The model is updated to the alternative hypothesis
    if there is a significant improvement (larger than the given threshold).

    Parameters
    ----------
    datasets : `~gammapy.datasets.Datasets`
        Datasets
    parameters : `~gammapy.modeling.Parameters` or list of `~gammapy.modeling.Parameter`
        List of parameters frozen for the null hypothesis but free for the test hypothesis.
    null_values : list of float or `~gammapy.modeling.Parameters`
        Values of the parameters frozen for the null hypothesis.
        If a `Parameters` object or a list of `Parameters` is given
        the null hypothesis follows the values of these parameters,
        so this tests linked parameters versus unliked.
    n_sigma : float
        Threshold in number of sigma to switch from the null hypothesis
        to the alternative one. Default is 2.
        The TS is converted to sigma assuming that the Wilk's theorem is verified.
    n_free_parameters : int
        Number of free parameters to consider between the two hypothesis
        in order to estimate the `ts_threshold` from the `n_sigma` threshold.
        Default is len(parameters).
    fit : `Fit`
        Fit instance specifying the backend and fit options.

    Returns
    -------
    result : dict
        Dict with the TS of the best fit value compared to the null hypothesis
        and fit results for the two hypotheses. Entries are:

            * "ts" : fit statistic difference with null hypothesis
            * "fit_results" : results for the best fit
            * "fit_results_null" : fit results for the null hypothesis
    """
    test = TestStatisticNested(parameters, null_values, n_sigma, n_free_parameters, fit)
    return test.run(datasets)
