import matplotlib.pyplot as plt
import numpy as np
from modelParams import SymphonyParams as SP
from modelParams import GeneralParams as GP
import warnings
from matplotlib.collections import LineCollection
from scipy.optimize import curve_fit

def colored_line(x, y, c, ax, **lc_kwargs):
    """
    Plot a line with a color specified along the line by a third value.

    It does this by creating a collection of line segments. Each line segment is
    made up of two straight lines each connecting the current (x, y) point to the
    midpoints of the lines connecting the current point with its two neighbors.
    This creates a smooth line with no gaps between the line segments.

    Parameters
    ----------
    x, y : array-like
        The horizontal and vertical coordinates of the data points.
    c : array-like
        The color values, which should be the same size as x and y.
    ax : Axes
        Axis object on which to plot the colored line.
    **lc_kwargs
        Any additional arguments to pass to matplotlib.collections.LineCollection
        constructor. This should not include the array keyword argument because
        that is set to the color argument. If provided, it will be overridden.

    Returns
    -------
    matplotlib.collections.LineCollection
        The generated line collection representing the colored line.
    """
    if "array" in lc_kwargs:
        warnings.warn('The provided "array" keyword argument will be overridden')

    # Default the capstyle to butt so that the line segments smoothly line up
    default_kwargs = {"capstyle": "butt"}
    default_kwargs.update(lc_kwargs)

    # Compute the midpoints of the line segments. Include the first and last points
    # twice so we don't need any special syntax later to handle them.
    x = np.asarray(x)
    y = np.asarray(y)
    x_midpts = np.hstack((x[0], 0.5 * (x[1:] + x[:-1]), x[-1]))
    y_midpts = np.hstack((y[0], 0.5 * (y[1:] + y[:-1]), y[-1]))

    # Determine the start, middle, and end coordinate pair of each line segment.
    # Use the reshape to add an extra dimension so each pair of points is in its
    # own list. Then concatenate them to create:
    # [
    #   [(x1_start, y1_start), (x1_mid, y1_mid), (x1_end, y1_end)],
    #   [(x2_start, y2_start), (x2_mid, y2_mid), (x2_end, y2_end)],
    #   ...
    # ]
    coord_start = np.column_stack((x_midpts[:-1], y_midpts[:-1]))[:, np.newaxis, :]
    coord_mid = np.column_stack((x, y))[:, np.newaxis, :]
    coord_end = np.column_stack((x_midpts[1:], y_midpts[1:]))[:, np.newaxis, :]
    segments = np.concatenate((coord_start, coord_mid, coord_end), axis=1)

    lc = LineCollection(segments, **default_kwargs)
    lc.set_array(c)  # set the colors of each segment

    return ax.add_collection(lc)


vertraging = 6
tijdspanne = 10

tijd = np.load('drytest 0212_verwerkt/tijd.npy')
deel = slice(int(round(len(tijd)*0.14)),int(round(len(tijd)*0.36)))
tijd = tijd[deel]

rpm = np.load('drytest 0212_verwerkt/rpm.npy')[deel]
filter_move = [i for i,val in enumerate(rpm) if abs(val) > 40]
plt.plot(tijd,np.where(abs(rpm)>40,1,0))
plt.show()
rpm = rpm[filter_move]
tijd = tijd[filter_move]


radar = np.load('drytest 0212_verwerkt/radar.npy')[deel][filter_move]
pfloater = np.load('drytest 0212_verwerkt/pfloater.npy')[deel][filter_move]
pmem = np.load('drytest 0212_verwerkt/pmem1.npy')[deel][filter_move]
encoder = np.load('drytest 0212_verwerkt/encoder.npy')[deel][filter_move]            # %65530
pturb_spring = np.load('drytest 0212_verwerkt/pturbspring.npy')[deel][filter_move]
pturb_mem = np.load('drytest 0212_verwerkt/pturbmem.npy')[deel][filter_move]
pspring_gas = np.load('drytest 0212_verwerkt/pspring_gas.npy')[deel][filter_move]
stroom = np.load('drytest 0212_verwerkt/stroom1.npy')[deel][filter_move]*100
level = np.load('drytest 0212_verwerkt/level.npy')[deel][filter_move]


level-= sum(level)/len(level)

dlevel = (level[1:]-level[:-1])/(tijd[1:] - tijd[:-1])
dpmem = (pmem[1:]-pmem[:-1])/(tijd[1:] - tijd[:-1])
plt.plot(rpm,pturb_mem-pturb_spring)
plt.show()


# plt.plot(tijd,radar*3, marker='o',markersize=2,label='radar')
plt.plot(tijd,pturb_mem, marker='o',markersize=2,label='druk turbine - membraan')
plt.plot(tijd,-rpm/400,marker='o',markersize=2,label='rpm')
plt.plot(tijd,pmem,marker='o',markersize=2,label='druk membraan')
plt.plot(tijd,level*25,marker='o',markersize=2,label='level')


plt.xlabel('tijd in s')
plt.ylabel('druk in bar(g)')
plt.legend()
plt.show()