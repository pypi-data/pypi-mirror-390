"""
This module contains basic control blocks implementations
"""

# pyximport is needed to compile dynamically
import typhoon.utils.environment as tytest_env

if tytest_env.is_run_from_source():
    import pyximport

    pyximport.install()

from .. import __version__  # noqa: F401
from . import impl as _impl  # noqa: E402


def integrator(
    input,  # noqa: A002
    initial_value,
    limit_output=False,
    max_limit=None,
    min_limit=None,
):
    """
    Integrates provided input signal. It is implemented by using Backward Euler method.

    Parameters
    ----------
    input: pandas.Series with timedelta index values
        Input signal to be integrated.
    initial_value: int, float
        Initial value of the integrated output signal
    limit_output: bool
        If set to True, limits the output signal. In this case, parameters max_limit and min_limit have to be specified.
    max_limit: int, float
        If limit_output argument is specified, this value limits the output from the upper side. Otherwise, it doesn't
        take effect.
    min_limit: int, float
        If limit_output argument is specified, this value limits the output from the lower side. Otherwise, it doesn't
        take effect.

    Returns
    -------
    result: pandas.Series

    Examples
    --------

    Simple test for the integrator with a constant input

    >>> from typhoon.test.signals.control import integrator
    >>> from typhoon.test.signals import pandas_sine, assert_is_ramp
    >>>
    >>> def test_integrator():
    >>>     const, initial_value = 1, 0
    >>>     input_sig = pandas_sine(Ts=1e-4)
    >>>     input_sig[:] = const
    >>>     output_sig = integrator(input_sig, initial_value=initial_value)
    >>>     assert_is_ramp(output_sig, slope=const, tol=1e-4, initial_value=initial_value)
    """
    return _impl.integrator(input, initial_value, limit_output, max_limit, min_limit)


def signal_frequency_SOGI_pll(
    input,  # noqa: A002
    initial_amp,
    frequency,
    initial_angle=0,
    max_freq_var=10,
    pll_filter_params=None,
):
    """
    Measures the frequency of the signal using a SOGI PLL algorithm.

    Parameters
    ----------
    input: pandas.Series with timedelta index values
        Input signal to be measured.
    initial_amp: int, float
        Initial value of the signal amplitude
    frequency: int, float
        Value of frequency to be achieved
    initial_angle: int, float
        Initial value of the signal phase
    max_freq_var: int, float
        Frequency (in ``Hz``) used to saturate the PI Controller
    pll_filter_params: Nonetype, dict
        This dictionary contains the projected gain of the PLL and the cutoff frequency of the filters.
        If those values are not defined, the ``Default`` values will be used
        The dict keys that can be set are:

        * **"sogi_gain"** (int, float. Default: ``0.4``) - SOGI Algorithm Gain
        * **"kp_pll"** (int, float. Default: ``4.81e3``) - PLL controller proportional gain
        * **"ki_pll"** (int, float. Default: ``1.84e4``) - PLL controller integral gain
        * **"kd_pll"** (int, float. Default: ``-5.19``) - PLL controller derivative gain
        * **"lp_cut_off_filter_d"** (int, float. Default: ``20``) - Cut-off frequency (in ``Hz``) of the output filters of ``d`` coordinate
        * **"lp_cut_off_filter_w"** (int, float. Default: ``100``) - Cut-off frequency (in ``Hz``) of the output filters of angular frequency (``w``)
        * **"lp_cut_off_filter_f"** (int, float. Default: ``10``) - Cut-off frequency (in ``Hz``) of the output filters of frequency

    Returns
    -------
    result: pandas.Dataframe
        The Dataframe contains dq coordinates (``d`` and ``q``), the frequency measured (``f``), the angle (``wt``),
        and the sinusoidal output (``sin_wt``).

    Examples
    --------
    >>> from typhoon.test.signals.control import signal_frequency_SOGI_pll
    >>> from typhoon.test.signals import pandas_sine, assert_is_constant
    >>>
    >>> amp = 311
    >>> freq_initial = 55
    >>> freq = 60
    >>>
    >>> signal = pandas_sine(amp, freq, 100/freq, 0)
    >>>
    >>> df = signal_frequency_SOGI_pll(signal, amp, freq_initial)

    You can set ``None``, one, or all parameters of the PLL project:

    >>> df = signal_frequency_SOGI_pll(signal, amp, freq_initial, pll_filter_params={"lp_cut_off_filter_f": 15})

    The data are available in each column of the dataframe ``df``:

    >>> frequency = df["f"]
    >>> d_coordinate = df["d"]
    >>> q_coordinate = df["q"]
    >>> wt = df["wt"]  # Angle
    >>> sin_wt = df["sin_wt"]  # sine of angle (sin(angle))

    If desired, ``assert_is_constant`` can be included in the test procedure as follows:

    >>> def test_pll():
    >>>     # ...
    >>>
    >>>     ref_value = freq
    >>>
    >>>     tol = .5
    >>>     tol_t = 250e-3
    >>>
    >>>     assert_is_constant(df["f"], (ref_value - tol, ref_value + tol), during=(tol_t, df.index[-1]), strictness=tol)

    See Also
    --------
    typhoon.test.signals.control.integrator
    """
    return _impl.frequency_meas_SOGI_pll(
        input,
        initial_amp,
        frequency,
        angle_init=initial_angle,
        delta_Hz_max=max_freq_var,
        pll_filter_params=pll_filter_params,
    )
