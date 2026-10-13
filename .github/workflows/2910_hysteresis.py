import matplotlib.pyplot as plt
import numpy as np
from modelParams import SymphonyParams as SP
from modelParams import GeneralParams as GP
import warnings
from matplotlib.collections import LineCollection

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


tijd = np.load('drytest 2910_verwerkt/tijd.npy')
radar = np.load('drytest 2910_verwerkt/radar.npy')
pfloater = np.load('drytest 2910_verwerkt/pfloater.npy')
pmem = np.load('drytest 2910_verwerkt/pmem2.npy')

dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2

pfloater = np.array(pfloater)
filter1 = np.where(dz<.001,1,0)
filter1 = np.concatenate((filter1[-7:], filter1[:-7]))*np.concatenate((filter1[-6:], filter1[:-6]))*np.concatenate((filter1[-5:], filter1[:-5]))*np.concatenate((filter1[-4:], filter1[:-4]))*np.concatenate((filter1[-3:], filter1[:-3]))*np.concatenate((filter1[-2:], filter1[:-2]))*np.concatenate((filter1[-1:], filter1[:-1])) * filter1 * np.concatenate((filter1[1:], filter1[:1]))*np.concatenate((filter1[2:], filter1[:2]))*np.concatenate((filter1[3:], filter1[:3]))*np.concatenate((filter1[4:], filter1[:4]))*np.concatenate((filter1[5:], filter1[:5]))*np.concatenate((filter1[6:], filter1[:6]))*np.concatenate((filter1[7:], filter1[:7]))
filter1 = np.concatenate((filter1[-7:], filter1[:-7]))*np.concatenate((filter1[-6:], filter1[:-6]))*np.concatenate((filter1[-5:], filter1[:-5]))*np.concatenate((filter1[-4:], filter1[:-4]))*np.concatenate((filter1[-3:], filter1[:-3]))*np.concatenate((filter1[-2:], filter1[:-2]))*np.concatenate((filter1[-1:], filter1[:-1])) * filter1 * np.concatenate((filter1[1:], filter1[:1]))*np.concatenate((filter1[2:], filter1[:2]))*np.concatenate((filter1[3:], filter1[:3]))*np.concatenate((filter1[4:], filter1[:4]))*np.concatenate((filter1[5:], filter1[:5]))*np.concatenate((filter1[6:], filter1[:6]))*np.concatenate((filter1[7:], filter1[:7]))

filter2 = np.where(pfloater==.0,0,1)
filter3 = np.where(radar<-1,0,1)
# filter4 = np.where(radar<-.9,0,1)
filter = filter1*filter2*filter3

zeros = [i for i, val in enumerate(filter) if val == 0]
pfloater_fil = np.array([val for i, val in enumerate(pfloater) if i not in zeros])
pmem_fil = np.array([val for i,val in enumerate(pmem) if i not in zeros])
radar_fil = np.array([val for i, val in enumerate(radar) if i not in zeros])
pmem_fil += .4  #ongeveer .6bar waterkolom
pfloater_fil += 1
radar_fil += 2
print(len(radar_fil))


opp = np.pi/4 * SP.floaterInnerDiamUp**2 - np.pi/8 *(SP.floaterInnerDiamUp**2-SP.membrameInnerDiam**2)
F_floater = opp*pfloater_fil*1e5

Buitendruk_constant = -GP.Patm*(np.pi/8)*(SP.membrameInnerDiam**2+SP.floaterInnerDiamUp**2)



zwaartekracht = - GP.g * SP.floaterMass
Fnet = - zwaartekracht - Buitendruk_constant - F_floater

deel = 101
begin = int(np.floor(len(radar_fil)/deel))
z = np.linspace(min(radar_fil[begin:]),max(radar_fil[begin:]),1000)


Fnet /= 1000

onder = 35*z+32.85
boven = 35*z+38.63
gem = (onder+boven) / 2
onder -= gem
boven -= gem
Fnet -= (35*radar_fil+35.765)


plt.plot(radar_fil[begin:],Fnet[begin:],marker='o',markersize=1,linestyle='')
plt.plot(z,onder,linestyle='--',color='purple')
plt.plot(z,onder+.5,linestyle='--',color='purple')
plt.plot(z,onder+2.5,linestyle='--',color='purple')
plt.plot(z,boven-1.1,linestyle='--',color='gray')
plt.plot(z,boven+.9,linestyle='--',color='gray')
plt.title('Hysteresis - dynamic measurement')
plt.ylabel('Drag force from hysteresis[$kN$]')
plt.xlabel('Radar [$m$]')
plt.show()