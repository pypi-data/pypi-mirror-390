import pandas

from .. import __version__  # noqa: F401
from . import impl as _impl


def abc_to_alphabetagamma(signals, method="Amplitude invariant", alignment="alpha"):
    """Calculates abc to alpha-beta-gamma transformation, also known as Clarke's transformation.

    If the input signals are symmetrical, the result represents its projection in alpha-beta stationary reference
    frame, while the gamma component equals to zero. There are three methods of this transformation, which can be chosen
    by setting the 'method' argument to appropriate value:

    * |  Amplitude invariant - with this method, amplitudes of the input signals are preserved. It is implemented by following equations:
      |  ``alpha = 2/3 * (a * cos(-theta) + b * cos(2*pi/3 - theta)  + c * cos(4*pi/3 - theta))``
      |  ``beta = 2/3 * (a * sin(-theta) + b * sin(2*pi/3 - theta) + c * sin(4*pi/3 - theta))``
      |  ``gamma = 1/3 * ( a + b + c)``
    * | Uniform - Clarke's original. The calculation of alpha and beta is the same as before, but gamma axis is not
      | squashed, so its output is the same as the zero sequence obtained from the symmetrical components trasformation:
      |  ``alpha = 2/3 * (a * cos(-theta) + b * cos(2*pi/3 - theta)  + c * cos(4*pi/3 - theta))``
      |  ``beta = 2/3 * (a * sin(-theta) + b * sin(2*pi/3 - theta) + c * sin(4*pi/3 - theta))``
      |  ``gamma = sqrt(2)/3 * (a + b + c)``

    * |  Power invariant - this transformation preserves the power of the new equivalent, two phase system. Because of that, amplitudes of the signals are sqrt(3/2) times bigger then the original signals a,b,c. The equations for this method are:
      |  ``alpha = sqrt(2/3) * (a * cos(-theta) + b * cos(2*pi/3 - theta)  + c * cos(4*pi/3 - theta))``
      |  ``beta = sqrt(2/3) * (a * sin(-theta) + b * sin(2*pi/3 - theta) + c * sin(4*pi/3 - theta))``
      |  ``gamma = 1/sqrt(3) * ( a + b + c)``

        parameter theta is defined by function argument alignment: if it is set to alpha, theta angle is zero;
        otherwise, it is -pi/2

    Parameters
    ----------
    signals : pandas.DataFrame
        Dataframe with three columns, one for every signal of the three-phase abc input.
    method : string
        The chosen method of the transformation. It can have one of the following values: "Amplitude invariant',
        'Uniform' or 'Power invariant'.
    alignment: string
        Defines axis of the alpha-beta reference frame which is aligned with a-axis of the original reference frame.
        Valid values are "alpha" and "beta".

    Returns
    -------
    pandas.DataFrame:
        DataFrame containing three output signals. Labels for output signals are alpha, beta and gamma, respectively.

    Examples
    --------
    >>> from typhoon.test.signals import pandas_3ph_sine
    >>> from typhoon.test.transformations import abc_to_alphabetagamma
    >>> abc_frame = pandas_3ph_sine(frequency=50)
    >>> alpha_beta_frame = abc_to_alphabetagamma(abc_frame, method="Amplitude invariant")
    >>> alpha = alpha_beta_frame["alpha"]
    >>> beta = alpha_beta_frame["beta"]
    >>> gamma = alpha_beta_frame["gamma"]


    See Also
    --------
    typhoon.test.transformations.alphabetagamma_to_abc
    typhoon.test.transformations.abc_to_dq0
    typhoon.test.transformations.abc_to_symmetrical_components
    """
    return _impl.abc_to_alphabetagamma(signals, method, alignment)


def alphabetagamma_to_abc(signals, method="Amplitude invariant", alignment="alpha"):
    """Calculates alpha-beta-gamma to abc transformation, also known as Clarke's inverse transformation.

    This transformation projects the two stationary (alpha-beta) axis onto the three-phase axis.
    It has the same three forms as abc to alpha-beta-gamma transformation:

    * |  Amplitude invariant:
      |  ``a = alpha * cos(-theta) + beta * sin(-theta) + gamma``
      |  ``b = alpha * cos(2*pi/3 - theta) + beta * sin(2*pi/3 - theta) + gamma``
      |  ``c = alpha * cos(4*pi/3 - theta) + beta * sin(4*pi/3 - theta) + gamma``
    * |  Uniform - Clarke's original:
      |  ``a = alpha * cos(-theta) + beta * sin(-theta) + 1/sqrt(2) * gamma``
      |  ``b = alpha * cos(2*pi/3 - theta) + beta * sin(2*pi/3 - theta) + 1/sqrt(2) * gamma``
      |  ``c = alpha * cos(4*pi/3 - theta) + beta * sin(4*pi/3 - theta) + 1/sqrt(2) * gamma``
    * |  Power invariant:
      |  ``a = sqrt(2/3) * (alpha * cos(-theta) + beta * sin(-theta) + 1/sqrt(2) * gamma)``
      |  ``b = sqrt(2/3) * (alpha * cos(2*pi/3 - theta) + beta * sin(2*pi/3 - theta) + 1/sqrt(2) * gamma)``
      |  ``c = sqrt(2/3) * (alpha * cos(4*pi/3 - theta) + beta * sin(4*pi/3 - theta) + 1/sqrt(2) * gamma)``

        parameter theta is defined by function argument alignment: if it is set to alpha, theta angle is zero;
        otherwise, it is -pi/2

    Parameters
    ----------
    signals: pandas.DataFrame
        DataFrame with three columns, one for alpha, beta and gamma signal.
    method : string
        The string for selecting the one of three possible methods: "Amplitude invariant', 'Uniform', 'Power invariant'
    alignment : string
        Defines axis of the alpha-beta reference frame which is aligned with a-axis of the original reference frame.
        Valid values are "alpha" and "beta".

    Returns
    -------
    pandas.DataFrame:
        DataFrame containing three columns - one for each output signal. The labels for selection of the signals are a,
        b and c, respectively

    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> from typhoon.test.transformations import alphabetagamma_to_abc
    >>> import pandas as pd
    >>> alpha = pandas_sine() # sine with amplitude 1 and phase 0
    >>> beta = pandas_sine(phase=-90) # sine with amplitude 1 and phase -90
    >>> gamma = pandas_sine(amplitude=0) # constant with zeros
    >>> alpha_beta_frame = pd.DataFrame(data={"alpha":alpha, "beta":beta, "gamma":gamma}, index=alpha.index)
    >>> abc_frame = alphabetagamma_to_abc(alpha_beta_frame, method="Amplitude invariant")
    >>> a = abc_frame["a"]
    >>> b = abc_frame["b"]
    >>> c = abc_frame["c"]


    See Also
    --------
    typhoon.test.transformations.abc_to_alphabetagamma
    typhoon.test.transformations.alphabetagamma_to_dq0
    """
    return _impl.alphabetagamma_to_abc(signals, method, alignment)


def alphabetagamma_to_dq0(signals, theta, alignment="d"):
    """Implements the alpha-beta-gamma to dq0 transformation, also known as Clarke to Park angle transform.

    The Clarke to Park Angle Transform block converts the alpha, beta, and zero components in a stationary reference
    frame to direct, quadrature, and zero components in a rotating reference frame. For balanced three-phase systems,
    zero component is equal to zero. There are two possible forms, as alpha-axis of stationary reference frame can be
    aligned with q- or d-axis of the rotating reference frame. These methods are implemented by following equations:

    * |  alpha-axis and d-axis are aligned:
      |  ``d = cos(theta) * alpha + sin(theta) * b``
      |  ``q = -sin(theta) * alpha + cos(theta) * b``
      |  ``zero = gamma``
    * | alpha-axis and q-axis are aligned:
      |  ``d = sin(theta) * a - cos(theta) * b``
      |  ``q = cos(theta) * a + sin(theta) * b``
      |  ``zero = gamma``

        Variable theta represents the angle between two reference frames; it is measured between alpha-axis of
        alpha-beta reference frame, and the axis from d-q reference frame which is initially aligned with alpha.

    Parameters
    ----------
    signals: pandas.DataFrame
        DataFrame with three columns, one for alpha, beta and gamma signal.
    theta : pandas.Series
        The angle in time between the two reference frames; it is measured between alpha-axis of alpha-beta reference
        frame, and the axis from d-q reference frame which is initially aligned with alpha.
    alignment : string
        It has two valid values: 'd' or 'q'. That is the way to chose which axis in rotating reference frame is
        initially aligned with alpha-axis from stationary reference frame.

    Returns
    -------
    pandas.DataFrame:
        DataFrame with three columns, one for every output signal. The labels to select columns are d, q and zero,
        respectively.

    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> from typhoon.test.transformations import alphabetagamma_to_dq0
    >>> from scipy.signal import sawtooth
    >>> import numpy as np
    >>> import pandas as pd
    >>> alpha = pandas_sine(frequency=50) # sine with amplitude 1 and phase 0
    >>> beta = pandas_sine(frequency=50, phase=-90) # sine with amplitude 1 and phase -90
    >>> gamma = pandas_sine(frequency=50, amplitude=0) # constant with zeros

    >>> # create pandas.Series which represents dq reference frame angle
    >>> t = np.arange(0, 1, 1e-4) # time axis for the angle
    >>> index = pd.TimedeltaIndex(t, unit='s')
    >>> angle = sawtooth(2 * np.pi * 50 * t) # create sawtooth signal from -1 to 1
    >>> angle = (angle + 1) * np.pi # make sawtooth go from 0 to 2pi
    >>> theta = pd.Series(data=angle, index=index)

    >>> alpha_beta_frame = pd.DataFrame(data={"alpha":alpha, "beta":beta, "gamma":gamma}, index=alpha.index)
    >>> dq0_frame = alphabetagamma_to_dq0(alpha_beta_frame, theta, alignment='q')
    >>> d = dq0_frame["d"]
    >>> q = dq0_frame["q"]
    >>> zero = dq0_frame["zero"]

    See Also
    --------
    typhoon.test.transformations.alphabetagamma_to_abc
    typhoon.test.transformations.dq0_to_alphabetagamma
    """
    return _impl.alphabetagamma_to_dq0(signals, theta, alignment)


def dq0_to_alphabetagamma(signals, theta, alignment="d"):
    """Implements dq0 to alpha-beta-gamma angle transform, also known as Park to Clarke angle transform.

    Converts the direct, quadrature and zero component from the rotating reference frame into the alpha, beta and gamma
    component in the stationary reference frame. If the system is balanced, zero component in the rotating, as well as
    gamma component in stationary reference frame is equal to zero. The d- or q-axis alignment can also be chosen
    according to the :func:`typhoon.test.transformations.alphabetagamma_to_dq0` function:

    * |  d-axis alignment: d-axis is aligned with alpha-axis. The following equation perform this transformation:
      |  ``alpha = cos(theta) * d - sin(theta) * q``
      |  ``beta = sin(theta) * d + cos(theta) * q``
    * |  q-axis alignment: q-axis is aligned with alpha-axis. The equations look like this:
      |  ``alpha = sin(theta) * d + cos(theta) * q``
      |  ``beta = -cos(theta) * d + sin(theta) * q``

    Parameters
    ----------
    signals : pandas.DataFrame
        DataFrame with three columns, with each one representing direct, quadrature and zero component in rotating
        reference frame.
    theta : pandas.Series
        the signal in time which represents the angle between two reference frames
    alignment : string
        Selects the alignment between the reference frames. It can be 'd' or 'q'

    Returns
    -------
    pandas.DataFrame:
        DataFrame with three columns, one for every output signal. The labels to select columns are alpha, beta and
        gamma, respectively.

    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> from typhoon.test.transformations import dq0_to_alphabetagamma
    >>> import numpy as np
    >>> import pandas as pd
    >>> t = np.linspace(0, 1, 10000)
    >>> index = pd.TimedeltaIndex(t, unit='s')
    >>> d = pd.Series(data=np.ones(10000), index=index) # constant signal with value 1
    >>> q = pd.Series(data=np.zeros(10000), index=index) # constant signal with value 0
    >>> zero = pd.Series(data=np.zeros(10000), index=index) # constant signal with value 0
    >>> dq0_dataframe = pd.DataFrame(data={'d': d, 'q': q, 'zero': zero}, index=index)

    >>> # create pandas.Series which represents dq reference frame angle
    >>> t = np.arange(0, 1, 1e-4) # time axis for the angle
    >>> index = pd.TimedeltaIndex(t, unit='s')
    >>> angle = sawtooth(2 * np.pi * 50 * t) # create sawtooth signal from -1 to 1
    >>> angle = (angle + 1) * np.pi # make sawtooth go from 0 to 2pi
    >>> theta = pd.Series(data=angle, index=index)

    >>> alpha_beta_frame = dq0_to_alphabetagamma(dq0_dataframe, theta, alignment='q')
    >>> alpha = alpha_beta_frame['alpha']
    >>> beta = alpha_beta_frame['beta']
    >>> gamma = alpha_beta_frame['gamma']

    See Also
    --------
    typhoon.test.transformations.alphabetagamma_to_dq0
    typhoon.test.transformations.dq0_to_abc
    typhoon.test.transformations.dq0_to_alphabetagamma
    """
    return _impl.dq0_to_alphabetagamma(signals, theta, alignment)


def abc_to_dq0(signals, theta, method="Amplitude invariant", alignment="d"):
    """Implements abc_to_dq0 transformation, also known as Park transformation.

    Converts signals from the abc reference frame into the dq rotating reference frame.
    This function is a cascaded combination of the :func:`typhoon.test.transformations.abc_to_alphabetagamma` and
    :func:`typhoon.test.transformations.alphabetagamma_to_dq0` transformations. This enables choice between one of the
    three methods for transformation into the stationary alpha-beta reference frame, and also one of the two possible
    alignments between the alpha-beta and dq reference frame.

    Parameters
    ----------
    signals : pandas.DataFrame
        Dataframe with three columns, one for every signal of the three-phase abc input.
    theta : pandas.Series
        The signal in time which represents the angle between stationary and rotating reference frame. It is the angle
        between a-axis from abc frame, and axis which is chosen as initially aligned axis from dq frame(d or q).
    method : string
        The argument which enables choice of the method for the abc to alpha-beta part of the transformation. It can be
        'Amplitude invariant', 'Uniform' or 'Power invariant'
    alignment : string
        The argument which enables the choice of the alignment between the stationary and rotating reference frame; It
        can be set to 'd' or 'q', and the appropriate axis will be aligned with a-axis from the abc frame.

    Returns
    -------
    pandas.DataFrame:
        DataFrame with three columns, one for every output signal. The labels to select columns are d, q and zero,
        respectively.

    Examples
    --------
    >>> from typhoon.test.signals import pandas_3ph_sine
    >>> from typhoon.test.transformations import abc_to_dq0
    >>> abc_frame = pandas_3ph_sine(frequency=50) # input a, b, c signals - balanced three-phase

    >>> # create pandas.Series which represents dq reference frame angle
    >>> t = np.arange(0, 1, 1e-4) # time axis for the angle
    >>> index = pd.TimedeltaIndex(t, unit='s')
    >>> angle = sawtooth(2 * np.pi * 50 * t) # create sawtooth signal from -1 to 1
    >>> angle = (angle + 1) * np.pi # make sawtooth go from 0 to 2pi
    >>> theta = pd.Series(data=angle, index=index)

    >>> dq0_frame = abc_to_dq0(abc_frame, theta, method='Amplitude invariant', alignment='q')
    >>> d = dq0_frame['d']
    >>> q = dq0_frame['q']
    >>> zero = dq0_frame['zero']


    See Also
    --------
    typhoon.test.transformations.dq0_to_abc
    typhoon.test.transformations.abc_to_alphabetagamma
    typhoon.test.transformations.alphabetagamma_to_dq0
    typhoon.test.transformations.abc_to_symmetrical_components
    """
    return _impl.abc_to_dq0(signals, theta, method, alignment)


def dq0_to_abc(signals, theta, method="Amplitude invariant", alignment="d"):
    """Implements the dq0_to_abc transformation, also known as inverse Park transformation.

    Converts the direct, quadrature, and zero components from the dq rotating reference frame to the components of the
    three-phase system in abc reference frame. This function is a cascaded combination of
    :func:`typhoon.test.transformations.dq0_to_alphabetagamma`, which converts rotation into the alpha-beta stationary
    reference frame, and :func:`typhoon.test.transformations.alphabetagamma_to_abc`, which gives the result in the abc
    frame. One of the two possible alignments can be chosen in the first step, and one of three
    possible methods can be chosen in the second step of the transformation.

    Parameters
    ----------
    signals : pandas.DataFrame
        The signals in the dq reference frame. They represent direct, quadrature and zero component. For the balanced
        system zero component is equal to zero.
    theta : pandas.Series
        The signal in time which represents the angle between stationary and rotating reference frame. It is the angle
        between a-axis from abc frame, and axis which is chosen as initially aligned axis from dq frame(d or q).
    method : string
        Enables the choice of the method for the first step of the transformation - conversion to
        alpha-beta reference frame. It can be 'Amplitude invariant', 'Uniform', or 'Power invariant'. Another value will
        raise exception.
    alignment : string
        Enables the choice of the alignment between two reference frames - rotating and stationary. It can be set to 'd'
        or 'q'. Another value will raise exception.

    Returns
    -------
    pandas.DataFrame:
        DataFrame containing three columns - one for each output signal. The labels to select the columns are a,
        b and c, respectively

    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> from typhoon.test.transformations import dq0_to_abc
    >>> import numpy as np
    >>> import pandas as pd
    >>> t = np.linspace(0, 1, 10000)
    >>> index = pd.TimedeltaIndex(t, unit='s')
    >>> d = pd.Series(data=np.ones(10000), index=index) # constant signal with value 1
    >>> q = pd.Series(data=np.zeros(10000), index=index) # constant signal with value 0
    >>> zero = pd.Series(data=np.zeros(10000), index=index) # constant signal with value 0
    >>> dq0_frame = pd.DataFrame(data={'d': d, 'q': q, 'zero': zero}, index=index)

    >>> # create pandas.Series which represents dq reference frame angle
    >>> t = np.arange(0, 1, 1e-4) # time axis for the angle
    >>> index = pd.TimedeltaIndex(t, unit='s')
    >>> angle = sawtooth(2 * np.pi * 50 * t) # create sawtooth signal from -1 to 1
    >>> angle = (angle + 1) * np.pi # make sawtooth go from 0 to 2pi
    >>> theta = pd.Series(data=angle, index=index)

    >>> abc_frame = dq0_to_abc(dq0_frame, theta, method="Amplitude invariant", alignment='q')
    >>> a = abc_frame['a']
    >>> b = abc_frame['b']
    >>> c = abc_frame['c']

    See Also
    --------
    typhoon.test.transformations.abc_to_dq0
    typhoon.test.transformations.dq0_to_alphabetagamma
    typhoon.test.transformations.alphabetagamma_to_abc
    """
    return _impl.dq0_to_abc(signals, theta, method, alignment)


def abc_to_symmetrical_components(
        signals: pandas.DataFrame,
        method: str="Fortescue",
        output: str="Complex",
        mag_in_rms: bool = True,
        angle_in_degrees: bool = True,
    ):
    """Implements the Symmetrical transformation, also known as Fortescue transform.

    The Symmetrical transformation splits the unbalanced 3-phases signals into three
    balanced signal with the zero, positive and negative sequences.

    This function allows input of sine or complex sine values. For **sine** signals (not complex values),
    such as the three-phase generated by :func:`typhoon.test.signals.pandas_3ph_sine`, the
    `Hilbert Transform <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.hilbert.html>`_
    will be used to split the real and imaginary component of the sine function. For **complex** signals,
    the Hilbert transform is not applied, and only the symmetrical components transform is performed.

    The sequences (zero, positive, and negative) from the symmetrical components can be
    represented by complex or phasor values.

    Parameters
    ----------
    signals : pandas.DataFrame
        Signals with three columns, one for every signal of the three-phase abc input.
        Signals can be complex or sinusoidal.
    method : string
        Selects the transformation method. Allowed values are ``'Fortescue'``, or
        ``'Power invariant'``; other values will raise an exception.
        Default is ``method='Fortescue'``
    output : string
        Selects the output type. Allowed values are ``'Complex'``, or
        ``'Phasor'``; other values will raise an exception.
        If ``'Complex'`` is selected this function will return:
            - A ``pandas.DataFrame`` with **three** columns, one for each output signal.
            The labels to select the columns are ``'zero'``, ``'positive'`` and ``'negative'``,
            respectively.
        If ``'Phasor'`` is selected this function will return:
            - A ``pandas.DataFrame`` with **six** columns, one for each symmetrical component (magnitude and phase).
            The labels to select the columns are, respectively:
                - ``"zero_mag"``: **Magnitude** of **Zero** Component
                - ``"zero_phase"``: **Phase** of **Zero** Component
                - ``"pos_mag"``: **Magnitude** of **Positive** Component
                - ``"pos_phase"``: **Phase** of **Positive** Component
                - ``"neg_mag"`` : **Magnitude** of **Negative** Component
                - ``"neg_phase"``: **Phase** of **Negative** Component
        Default is ``output='Complex'``.
    mag_in_rms: bool
        If this option is ``True`` and ``output='Phasor'`` the magnitude of the symmetrical components in the
        ``pandas.DataFrame`` will be return with values in RMS.
        If this option is ``False``, amplitude values will be returned.
        Default is ``mag_in_rms=True``.
    angle_in_degrees: bool
        If this option is ``True`` and ``output='Phasor'`` the angle of the symmetrical components in the
        ``pandas.DataFrame`` will be return with values in degrees.
        If this option is ``False``, values will be returned in radians.
        Default is ``angle_in_degrees=True``.

    Returns
    -------
    pandas.DataFrame:
        DataFrame containing the symmetrical components, the columns size and label depends
        on the chosen ``'output'``.

    Examples
    --------
    In this example the instantaneous mode of the function is used.
    The three-phase sines are used as ``signals``. These are decomposed into
    complex values, using **Hilbert Transform**, which are then used to calculate
    the symmetrical components.

    >>> from typhoon.test.transformations import abc_to_symmetrical_components
    >>> from typhoon.test.signals import pandas_3ph_sine
    >>>
    >>> amplitude = 311
    >>> frequency = 50
    >>> duration = 1
    >>> Ts = 1e-4
    >>>
    >>> signals = pandas_3ph_sine(amplitude, frequency, duration, Ts)
    >>>
    >>> zpn_fortescue = abc_to_symmetrical_components(signals)  # Implicit method = "Fortescue"
    >>> zpn_power_inv = abc_to_symmetrical_components(signals, method="Power invariant")

    The ``zpn_fortescue`` and ``zpn_power_inv`` will both be
    :class:`pandas.DataFrame` with three columns of :class:`complex`:

    * ``"zero"`` with the balanced zero components,
    * ``"positive"`` with the balanced positive components,
    * ``"negative"`` with the balanced negative components

    The ``zpn_fortescue`` components are shown in the plot:

    .. image:: ../../symmetrical_components_plot.png
        :alt: Symmetrical components plot

    And to get the symmetrical components as magnitude and phase:

    >>> zpn_fortescue_phasor = abc_to_symmetrical_components(
    >>>     signals, output="Phasor"
    >>> )  # Implicit method = "Fortescue"

    The ``zpn_fortescue_phasor`` **zero** and **positive** components
    are shown in the plot:

    .. image:: ../../symmetrical_components_plot_phasor.png
        :alt: Symmetrical components plot as phasors

    See Also
    --------
    typhoon.test.transformations.abc_to_alphabetagamma
    typhoon.test.transformations.abc_to_dq0
    typhoon.test.transformations.symmetrical_components_to_abc
    """
    return _impl.abc_to_symmetrical_components(signals, method, output, mag_in_rms, angle_in_degrees)


def symmetrical_components_to_abc(signals: pandas.DataFrame, method="Fortescue"):
    """Implements the Inverse Symmetrical Transformation to abc coordinates.

    The Inverse Symmetrical transformation results in an unbalanced three-phase
    system (abc), resulting of ``"zero"``, ``"positive"`` and ``"negative"`` components.

    Parameters
    ----------
    signals : pandas.DataFrame
        Complex signals with three columns:
            - **First** column: The Zero sequence,
            - **Second** column: The Positive sequence and,
            - **Third** column: The Negative sequence.
    method : string
        Enables the choice of the inverse transformation method. Allowed values are
        'Fortescue' or 'Power invariant'; other values will raise an exception.
        Default is ``method="Fortescue"``.

    Returns
    -------
    pandas.DataFrame:
        DataFrame containing three columns - one for each output signal. The labels to select
        the columns are ``"a"``, ``"b"`` and ``"c"``, respectively.

    Examples
    --------
    Using :func:`typhoon.test.transformations.symmetrical_components_to_abc` and
    :func:`typhoon.test.signals.pandas_3ph_sine` to inverse symmetrical
    components can be used:

    >>> import numpy as np
    >>> import pandas as pd
    >>>
    >>> from typhoon.test.transformations import (
    >>>     abc_to_symmetrical_components,
    >>>     symmetrical_components_to_abc
    >>> )
    >>> from typhoon.test.signals import pandas_3ph_sine
    >>>
    >>> amplitude = 1
    >>> frequency = 50
    >>> duration = 1
    >>> Ts = 1e-4
    >>>
    >>> signals = pandas_3ph_sine(amplitude, frequency, duration)
    >>>
    >>> zpn_fortescue = abc_to_symmetrical_components(signals)  # method="fortescue"
    >>> abc_inv_zpn_fortescue = symmetrical_components_to_abc(zpn_fortescue)  # method="fortescue"
    >>>
    >>> zpn_power_invar = abc_to_symmetrical_components(signals, "Power invariant")
    >>> abc_inv_zpn_power_invar = symmetrical_components_to_abc(zpn_power_invar, "Power invariant")

    See Also
    --------
    typhoon.test.transformations.abc_to_symmetrical_components
    """
    return _impl.symmetrical_components_to_abc(signals, method)


def complete_symmetrical_components(V0, V1, V2):
    """Calculates three three-phase "abc" sets from symmetrical components.

    Parameters
    ----------
    V0 : same type as input
        Zero-sequence component of phase "a".
    V1 : same type as input
        Positive-sequence component of phase "a".
    V2 : same type as input
        Negative-sequence component of phase "a".

    Returns
    -------
    V0abc, V1abc, V2abc : Phasors3ph tuple
        "abc" phasor set of zero-component, positive-component and negative-component respectively.

    Examples
    --------
    >>> Va = Phasor(mag=5, angle=53)
    >>> Vb = Phasor(mag=7, angle=-164)
    >>> Vc = Phasor(mag=7, angle=105)
    >>> V0, V1, V2 = symmetrical_components(Va, Vb, Vc)
    >>> [[Va0, Vb0, Vc0], [Va1, Vb1, Vc1], [Va2, Vb2, Vc2]] = complete_symmetrical_components(V0, V1, V2)

    See Also
    --------
    typhoon.test.transformations.symmetrical_components
    typhoon.test.transformations.inv_symmetrical_components
    """
    return _impl.complete_symmetrical_components(V0, V1, V2)


def symmetrical_components(Va, Vb, Vc):
    """Calculates symmetrical values abc phasors.

    Parameters
    ----------
    Va : complex or phasor
        Phase "a" component.
    Vb : complex or phasor
        Phase "b" component.
    Vc : complex or phasor
        Phase "c" component.

    Returns
    -------
    V0 : same type as input
        Zero-sequence component of phase "a".
    V1 : same type as input
        Positive-sequence component of phase "a".
    V2 : same type as input
        Negative-sequence component of phase "a".

    Examples
    --------
    >>> from typhoon.types.phasors import Phasor
    >>> from typhoon.test.transformations import symmetrical_components

    >>> Va = Phasor(mag=5, angle=53)
    >>> Vb = Phasor(mag=7, angle=-164)
    >>> Vc = Phasor(mag=7, angle=105)
    >>> V0, V1, V2 = symmetrical_components(Va, Vb, Vc)

    See Also
    --------
    typhoon.test.transformations.inv_symmetrical_components
    typhoon.test.transformations.complete_symmetrical_components
    """
    return _impl.symmetrical_components(Va, Vb, Vc)


def inv_symmetrical_components(V0, V1, V2):
    """Calculates the a, b and c phasors from symmetrical components.

    Parameters
    ----------
    V0 : complex or Phasor
        Zero-sequence component of phase "a".
    V1 : complex or Phasor
        Positive-sequence component of phase "a".
    V2 : complex or Phasor
        Negative-sequence component of phase "a".

    Returns
    -------
    Va : same type as input
        Phase "a" component.
    Vb : same type as input
        Phase "b" component.
    Vc : same type as input
        Phase "c" component.

    Examples
    --------
    >>> from typhoon.types.phasors import Phasor
    >>> from typhoon.test.transformations import inv_symmetrical_components

    >>> Va = Phasor(mag=5, angle=53)
    >>> Vb = Phasor(mag=7, angle=-164)
    >>> Vc = Phasor(mag=7, angle=105)
    >>> V0, V1, V2 = symmetrical_components(Va, Vb, Vc)

    >>> Va_round, Vb_round, Vc_round = inv_symmetrical_components(V0, V1, V2)
    >>> assert Va_round == Va
    >>> assert Vb_round == Vb
    >>> assert Vc_round == Vc

    See Also
    --------
    typhoon.test.transformations.symmetrical_components
    typhoon.test.transformations.complete_symmetrical_components
    """
    return _impl.inv_symmetrical_components(V0, V1, V2)
