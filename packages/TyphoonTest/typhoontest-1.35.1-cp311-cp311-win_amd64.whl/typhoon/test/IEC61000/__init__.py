"""This package contains measurement functions according to the IEC 61000 standard."""

import pandas
import typhoon.test.IEC61000.flickmeter as _impl_flickmeter
import typhoon.test.IEC61000.impl as _impl
import typhoon.test.IEC61000.power_quantities as _impl_power_quantities
import typhoon.test.IEC61000.power_quantities_3ph as _impl_power_quantities_three_phase

from .. import __version__  # noqa: F401


def rms(samples, nominal_grid_freq, reference_split=None):
    """Measures the root-mean-square (RMS) value for input samples according to the IEC 61000-4-30 standard.

    Parameters
    ----------
    samples: pandas.DataFrame or pandas.Series
        Samples from the signals in which RMS values should be measured, organized in columns.

    nominal_grid_freq: float
        This method is applied only to grids with a nominal frequency of 50.0 Hz or 60.0 Hz in accordance with the
        IEC 61000-4-30 standard.

    reference_split: list
        Optional and None by default. List of the indices to split the sample in windows. If ``None``, the samples
        will be split according to the zero-crossings of the voltage signal.

    Returns
    -------
    rms_values: pandas.DataFrame
        The RMS values for each signal.

    Raises
    ------
    ValueError: When the ``nominal_grid_freq`` is different from 50 Hz or 60 Hz

    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> from typhoon.test.IEC61000 import rms
    >>> grid_freq = 60
    >>> signal = pandas_sine(frequency=grid_freq)
    >>> rms_signal = rms(signal, grid_freq)

    See Also
    --------
    typhoon.test.IEC61000.flickermeter
    typhoon.test.IEC61000.harmonic_content
    typhoon.test.IEC61000.frequency
    """
    return _impl.rms(samples, nominal_grid_freq, reference_split)


def frequency(samples: pandas.DataFrame):
    """This method calculates the frequency of the grid voltage. The frequency reading is obtained every 10 seconds in
    accordance with IEC 61000-4-30. This method is applied only to grids with a nominal frequency of 50.0 Hz or 60.0 Hz
    in accordance with the IEC 61000-4-30 standard.

    Parameters
    ----------
    samples: pandas.DataFrame
        The sample voltages of the signals that want to measure the frequency.

    Returns
    -------
    freq: pandas.DataFrame
        The grid frequency in each window.

    Raises
    ------
    ValueError: When the capture time calculated is smaller than 10 seconds.

    Examples
    --------
    >>> from typhoon.test.signals import pandas_3ph_sine, pandas_sine
    >>> from typhoon.test.IEC61000 import frequency
    >>> signal = pandas_sine(duration=10.1, Ts=10/100000)  # signal needs to be 10s or bigger
    >>> freqs = frequency(sample)

    See Also
    --------
    typhoon.test.IEC61000.rms
    typhoon.test.IEC61000.harmonic_content
    """
    return _impl.frequency(samples)


def flickermeter(
    samples,
    reference_voltage,
    reference_frequency,
    nominal_voltage,
    nominal_frequency,
    returns="all_parameters",
):
    """This is a digital flickermeter based on 61000-4-30 standard. Is used for evaluating flicker severity and
    calculating the d parameters in relation to steady state conditions. This method is applied only to grids with a
    nominal frequency of 50.0 Hz or 60.0 Hz.

    Parameters
    ----------
    samples: pandas.DataFrame or pandas.Series
        Voltage samples captured from simulation.

    reference_voltage: float
        Voltage value used to determine the parameters of the weighting filter block that simulates the frequency
        response of the human ocular system to sinusoidal voltage fluctuations of a coiled filament gas-filled lamp.
        This value can be 230.0 V or 120.0 V.

    reference_frequency: float
        Frequency value used to determine the parameters of the weighting filter block that simulates the frequency
        response of the human ocular system to sinusoidal voltage fluctuations of a coiled filament gas-filled lamp.
        This value can be 60.0 Hz or 50.0 Hz.

    nominal_voltage: float
        Nominal voltage of the grid to be measured. This value can be 100.0 V, 120.0 V, 220.0 V or 230.0 V.

    nominal_frequency: float
        Nominal frequency of the grid to be measured. This value can be 60.0 Hz or 50.0 Hz.

    returns: str
        Describes which parameters the function should return, considering the metrics calculated on the
        flickermeter project (IEC 61000-4-15). This parameter accepts the following arguments:
            - ``"d_parameters"`` - Return the values ``(dc, d_max, t_max)``.
            - ``"Pinst"`` - Return the ``Pinst`` values.
            - ``"Pst"`` - Return the ``Pst`` values.
            - ``"Plt"`` - Return the ``Plt`` values.
            - ``"all_parameters"`` - Return the ``(Pst, Plt, dc, d_max, t_max)`` values.

    Returns
    -------
    Pst: numpy.array
        Known as the ``Short-Term Flicker Severity``, which measures the severity based on an observation period (10 min).
        This is derived from the time-at-level statistics obtained from the level classifier in block 5 of the
        flickermeter.
    Plt: numpy.array
        The long-term flicker severity (Plt), shall be derived from the Short-Term Severity values (Pst).
        The Plt value is calculated over a 2-hour period measurement. This time frame is recommended for power quality
        measurements according to IEC 61000-4-30, and for measurements in accordance with IECs 61000-3-3 and 61000-3-11.
    dc: float
        The highest absolute value of all steady state voltage change observations during an
        observation period.
    d_max: float
        The highest absolute voltage change observed during an observation period.
    t_max: float
        Maximum time duration during the observation period in which the voltage deviation exceeds the dc limit.
    Pinst: numpy.array
        The output of block 4 represents the instantaneous flicker sensation (Pinst).

    Raises
    ------
    ValueError: When the parameters passed for the function are different from what is specified in the documentation.

    ValueError: When the capture time calculated from the timedelta index is smaller than 7800 seconds (2h10min) using
        ``returns="all_parameters"`` or ``returns="Plt"``.

    ValueError: When the capture time calculated from the timedelta index is smaller than 1200 seconds (20min) using
        ``returns="Pst"``.

    ValueError: When the capture time calculated from the timedelta index is smaller than 10 seconds using
        ``returns="d_parameters"``.

    Note
    ----
    The initial 2 seconds of the analyzed signal are not considered when using ``returns="d_parameters"``.

    Examples
    --------
    >>> import numpy as np
    >>> import scipy.signal as sig
    >>> from typhoon.test.IEC61000 import flickermeter
    >>>
    >>> # Parameters of the signal
    >>> duration = 10
    >>> sample_rate = 1000
    >>> rms_voltage = 230
    >>> frequency = 60
    >>>
    >>> # Signal and modulation signal
    >>> time = np.linspace(0, duration, sample_rate * duration)
    >>> fundamental_voltage = rms_voltage * np.sqrt(2) * np.sin(2 * np.pi * frequency * time)
    >>>
    >>> frequency_modulation, amplitude_modulation = 0.500, 0.597
    >>>
    >>> modulation = (amplitude_modulation / 2 / 100) * sig.square(2 * np.pi * frequency_modulation * time) + 1
    >>>
    >>> # pandas.Series of the ``voltages_sample = fundamental_voltage * modulation`` signals
    >>> time_index = pd.to_timedelta(time, "s")
    >>> voltage_samples = pd.Series(fundamental_voltage * modulation, index=time_index)
    >>> dc, d_max, Tmax = flickermeter(voltage_samples, rms_voltage, frequency, rms_voltage, frequency, 'd_parameters')

    See Also
    --------
    typhoon.test.IEC61000.rms
    """
    return _impl_flickmeter.flickermeter(
        samples,
        reference_voltage,
        reference_frequency,
        nominal_voltage,
        nominal_frequency,
        returns,
    )


def harmonic_content(
    samples: pandas.DataFrame,
    nominal_grid_freq: float,
    max_harmonic_order: int,
    interharm: bool = False,
    reference_split=None,
):
    """This method measures harmonics, interharmonics, and total harmonic distortion according to IEC
    61000-4-7. The measurements are valid up to the 180th (50 Hz) or 150th (60 Hz) harmonic order.

    Parameters
    ----------
    samples: pandas.DataFrame
        Samples captured from simulation. The grid voltage is used for synchronization and detecting zero-crossings.
        According to the IEC 61000-4-30 standard the calculation window length is determined by the grid frequency.
        The voltage is also used to calculate harmonics, interharmonics, and total harmonic distortion.

    nominal_grid_freq: float
        According to the IEC 61000-4-7 standard, this method is applied only in grids with a nominal frequency of
        50.0 Hz or 60.0 Hz.

    max_harmonic_order: int
        The order of the highest harmonic that is taken into account.

    interharm: bool
        If True, returns the rms values of the harmonics and interharmonics.
        If False, returns the rms values of the harmonics only.

    reference_split: list, optional
        List of indices to split the sample in windows. If None, the samples will be split according to the zero-crossings
        of the voltage signal.

    Returns
    -------
    THD: numpy.array
        Ratio of the r.m.s. value of the sum of all the harmonic components up to a specific
    order to the r.m.s. voltage of the fundamental component, measured per window.
    rms_values: numpy.array
        RMS of a spectral components (harmonics and interharmonics).
    freq: numpy.array
        Frequency measured at each measurement window.

    Raises
    ------
    ValueError: When the ``nominal_grid_freq`` is different from 50 Hz or 60 Hz


    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> from typhoon.test.IEC61000 import harmonic_content
    >>>
    >>> frequency = 60
    >>> max_harmonic_order = 33
    >>> enable_interharmonics = False
    >>> samples = pandas_sine(frequency=frequency)
    >>>
    >>> THD, rms_components, measure_frequency = harmonic_content(samples, frequency, max_harmonic_order, enable_interharmonics)
    """
    return _impl.harmonic_content(
        samples, nominal_grid_freq, max_harmonic_order, interharm, reference_split
    )


def power_quantities(
    voltage_samples: pandas.Series,
    current_samples: pandas.Series,
    nominal_grid_freq: float,
    reference_split=None,
):
    """This method measures power quantities in single-phase systems under non-sinusoidal conditions (general case)
    according to IEC 61000-1-7. This method is applied only in grids with a nominal frequency of 50.0 Hz or 60.0 Hz.

    Parameters
    ----------
    voltage_samples: pandas.DataFrame
        Samples of voltage data captured from simulation.

    current_samples: pandas.DataFrame
        Samples of current data captured from simulation.

    nominal_grid_freq: float
        Nominal frequency of the grid (in Hz).

    reference_split: list, optional
        List of indices to split the sample in windows. If None, the samples will be split according to the
        zero-crossings of the voltage signal.

    Returns
    -------
    df_measurements: pandas.DataFrame
        With the follow columns:

        - **Active power**: Active power calculated over the entire signal.
        - **Apparent power**: Apparent power calculated over the entire signal.
        - **Non-active power**: Non-active power (reactive power + distortion power) calculated over the entire signal.
        - **Power factor**: Power factor calculated over the entire signal.
        - **Fundamental active power**: Active power calculated over the fundamental frequency component.
        - **Fundamental apparent power**: Apparent power calculated over the fundamental frequency component.
        - **Reactive power**: Reactive power calculated over the fundamental frequency component.
        - **Fundamental power factor**: Power factor calculated over the fundamental frequency component.
        - **Distortion active power**: Active power due to harmonic distortion.
        - **Non-fundamental power factor**: Power factor calculated over the non-fundamental frequency components.
        - **Non-fundamental apparent power**: Apparent power calculated over the non-fundamental frequency components.
        - **Distortion reactive power**: Reactive power due to harmonic distortion.

    Raises
    ------
    ValueError: When the ``nominal_grid_freq`` is different from 50 Hz or 60 Hz

    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> from typhoon.test.IEC61000 import power_quantities
    >>>
    >>> frequency = 50
    >>> voltage_samples = pandas_sine(phase=0, frequency=frequency)
    >>> current_samples = pandas_sine(phase=90, frequency=frequency)
    >>>
    >>> df_measurements = power_quantities(voltage_samples, current_samples, frequency)

    You can type ``df_measurements.columns`` to check the name of each one.
    Or you can use ``df_measurements.iloc[:, i]`` where ``i`` is the column number desired.
    To select each one of the columns in a **pandas.Series**:

    >>> active_power = df_measurements['Active power']
    >>> apparent_power = df_measurements['Apparent power']
    >>> non_active_power = df_measurements['Non-active power']
    >>> power_factor = df_measurements['Power factor']
    >>> fundamental_active_power = df_measurements['Fundamental active power']
    >>> fundamental_apparent_power = df_measurements['Fundamental apparent power']
    >>> reactive_power = df_measurements['Reactive power']
    >>> fundamental_power_factor = df_measurements['Fundamental power factor']
    >>> distortion_active_power = df_measurements['Distortion active power']
    >>> non_fundamental_power_factor = df_measurements['Non-fundamental power factor']
    >>> non_fundamental_apparent_power = df_measurements['Non-fundamental apparent power']
    >>> distortion_reactive_power = df_measurements['Distortion reactive power']

    See Also
    --------
    typhoon.test.IEC61000.power_quantities_three_phase
    """
    return _impl_power_quantities.power_quantities(
        voltage_samples, current_samples, nominal_grid_freq, reference_split
    )


def power_quantities_three_phase(
    voltages_samples: pandas.DataFrame,
    currents_samples: pandas.DataFrame,
    nominal_grid_freq: float,
    line_voltage: bool = True,
    reference_split=None,
):
    """This method measures power quantities in Three-phase systems under non-sinusoidal conditions (general case)
    according to IEEE Std 1459-2010. This method is applied only in grids with a nominal frequency of 50.0 Hz or
    60.0 Hz.

    Parameters
    ----------
    voltages_samples: pandas.DataFrame
        Voltage points vector.
    currents_samples: pandas.DataFrame
        Current points vector.
    nominal_grid_freq: float
        Nominal frequency of the voltage signal; 50 Hz or 60 Hz.
    line_voltage: bool
        Type of voltage; line-to-line or line-to-neutral voltage.
    reference_split: list, optional
        List of indices to split the sample in windows. If None, the samples will be split according to the zero-crossings
        of the voltage signal.

    Returns
    -------
    df_measurements: pandas.DataFrame
        With the follow columns:

        - **Active power**: The measured active power of the input data in W.
        - **Fundamental active power**: The measured active power in W only considering the fundamental component of the input data.
        - **Non-fundamental active power**: The measured active power in W subtracting the fundamental component of the input data.
        - **Effective voltage**: The measured effective voltage of the input data in V.
        - **Fundamental effective voltage**: The measured effective voltage in V considering the fundamental component of the input data.
        - **Non-fundamental effective voltage**: The measured effective voltage in V subtracting the fundamental component of the input data.
        - **Effective current**: The measured effective current of the input data in A.
        - **Fundamental effective current**: The measured effective current in A considering the fundamental component of the input data.
        - **Non-fundamental effective current**: The measured effective current in A subtracting the fundamental component of the input data.
        - **Effective apparent power**: The measured apparent power of the input data in VA.
        - **Fundamental effective apparent power**: The measured apparent power in VA only considering the fundamental component of the input data.
        - **Non-fundamental effective apparent power**: The measured apparent power in VA subtracting the fundamental component of the input data.
        - **Harmonic apparent power**: Evaluates the amount of VA caused by harmonic distortion.
        - **Non-active power**: The measured non active power of the input data in VAr.
        - **Current distortion power**: The apparent power caused by current distortion in relation to the fundamental voltage component.
        - **Voltage distortion power**: The apparent power caused by voltage distortion in relation to the fundamental current component.
        - **Power factor**: The measured power factor of the input data.
        - **Harmonic pollution factor**: This power factor quantifies the overall amount of harmonic pollution delivered or absorbed by a load.
        - **Fundamental positive active power**: The measured active power in W considering only the fundamental component of the positive-sequence of the input data.
        - **Fundamental positive reactive power**: The measured reactive power in VAr only considering the fundamental component of the positive-sequence of the input data.
        - **Fundamental positive apparent power**: The measured apparent power in VA only considering the fundamental component of the positive-sequence of the input data.
        - **Fundamental unbalanced power**: Evaluates the amount of VA caused by an unbalanced system.
        - **Fundamental positive power factor**: The measured power factor only considering the fundamental component of the positive-sequence of the input data.
        - **Load unbalance**: The estimated load unbalance between the phases, considering the fundamental active and reactive power and the THD measured on the system.
        - **Harmonic distortion power**: The measured non active power in VAr considering the harmonic components of the input data.

    Examples
    --------
    >>> from typhoon.test.signals import pandas_3ph_sine
    >>> from typhoon.test.IEC61000 import power_quantities_three_phase
    >>>
    >>> frequency = 60.0
    >>> line_to_line_voltage = True
    >>> voltage_samples = pandas_3ph_sine(phase=0, frequency=frequency)
    >>> current_samples = pandas_3ph_sine(phase=90, frequency=frequency)
    >>>
    >>> df_measurements = power_quantities_three_phase(voltage_samples, current_samples, frequency, line_to_line_voltage)

    You can type ``df_measurements.columns`` to check the name of each one.
    Or you can use ``df_measurements.iloc[:, i]`` where ``i`` is the column number desired.
    To select each one of the columns in a **pandas.Series**:

    >>> active_power = df_measurements['Active power']
    >>> fundamental_active_power = df_measurements['Fundamental active power']
    >>> nonfundamental_active_power = df_measurements['Non-fundamental active power']
    >>> effective_voltage = df_measurements['Effective voltage']
    >>> fundamental_effective_voltage = df_measurements['Fundamental effective voltage']
    >>> nonfundamental_effective_voltage = df_measurements['Non-fundamental effective voltage']
    >>> effective_current = df_measurements['Effective current']
    >>> fundamental_effective_current = df_measurements['Fundamental effective current']
    >>> nonfundamental_effective_current = df_measurements['Non-fundamental effective current']
    >>> effective_apparent_power = df_measurements['Effective apparent power']
    >>> fundamental_effective_apparent_power = df_measurements['Fundamental effective apparent power']
    >>> nonfundamental_effective_apparent_power = df_measurements['Non-fundamental effective apparent power']
    >>> harmonic_apparent_power = df_measurements['Harmonic apparent power']
    >>> non_active_power = df_measurements['Non-active power']
    >>> current_distortion_power = df_measurements['Current distortion power']
    >>> voltage_distortion_power = df_measurements['Voltage distortion power']
    >>> power_factor = df_measurements['Power factor']
    >>> harmonic_pollution_factor = df_measurements['Harmonic pollution factor']
    >>> fundamental_positive_active_power = df_measurements['Fundamental positive active power']
    >>> fundamental_positive_reactive_power = df_measurements['Fundamental positive reactive power']
    >>> fundamental_positive_apparent_power = df_measurements['Fundamental positive apparent power']
    >>> fundamental_unbalanced_power = df_measurements['Fundamental unbalanced power']
    >>> fundamental_positive_power_factor = df_measurements['Fundamental positive power factor']
    >>> load_unbalance = df_measurements['Load unbalance']
    >>> harmonic_distortion_power = df_measurements['Harmonic distortion power']

    Raises
    ------
    ValueError: When the ``nominal_grid_freq`` is different from 50 Hz or 60 Hz

    See Also
    --------
    typhoon.test.IEC61000.power_quantities
    """
    return _impl_power_quantities_three_phase.power_quantities_three_phase(
        voltages_samples,
        currents_samples,
        nominal_grid_freq,
        line_voltage,
        reference_split,
    )


def sym_comp_voltage_unbalance(
    samples: pandas.DataFrame, nominal_grid_freq: float, reference_split: list = None
):
    """Measures the Symmetrical components and Voltage Unbalance according to IEEE Std 1159-2019.

    Parameters
    ----------
    samples: pandas.DataFrame
        The samples of the signals in which to measure the symmetrical component, organized in columns.

    nominal_grid_freq: float
        According to the IEC 61000-4-30 standard, this method is applied only in grids with nominal frequency of 50.0 Hz
        or 60.0 Hz.

    reference_split: list, optional
        List of indices to split the sample in windows. If None, the samples will be split according to the
        zero-crossings of the voltage signal.

    Returns
    -------
    ZeroPosNeg_seq_per_window_df: pandas.DataFrame
        The magnitude of the zero sequence component, magnitude of the positive sequence component, and magnitude of the
        negative sequence component per window.

    voltage_unbalance_df: pandas.DataFrame
        The ratio of the magnitude of the negative sequence component to the magnitude of the positive sequence
        component, expressed as a percentage.

    Raises
    ------
    ValueError: When the ``nominal_grid_freq`` is different from 50 Hz or 60 Hz

    Examples
    --------
    >>> from typhoon.test.signals import pandas_3ph_sine
    >>> from typhoon.test.IEC61000 import sym_comp_voltage_unbalance
    >>>
    >>> frequency = 60
    >>> voltage_samples = pandas_3ph_sine(frequency=frequency)
    >>>
    >>> ZeroPosNeg_seq_per_window_df, voltage_unbalance_df = sym_comp_voltage_unbalance(voltage_samples, frequency)
    """
    return _impl.sym_comp_voltage_unbalance(samples, nominal_grid_freq, reference_split)
