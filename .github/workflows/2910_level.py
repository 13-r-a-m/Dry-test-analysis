import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from modelParams import SymphonyParams as SP
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
pmem = np.load('drytest 2910_verwerkt/pmem1.npy')
level = np.load('drytest 2910_verwerkt/level.npy')

dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
v = dz/dt
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
v = (np.array([0]+list(v))+np.array(list(v)+[0])) / 2


pfloater = np.array(pfloater)
# filter1 = np.where(dz<.01,1,0)
# filter1 = np.concatenate((filter1[-2:], filter1[:-2]))*np.concatenate((filter1[-1:], filter1[:-1])) * filter1 * np.concatenate((filter1[1:], filter1[:1]))*np.concatenate((filter1[2:], filter1[:2]))
filter2 = np.where(pfloater==.0,0,1)
filter3 = np.where(radar<-1.8,0,1)
# filter4 = np.where(radar>-1,0,1)
filter = filter2*filter3#*filter4

zeros = [i for i, val in enumerate(filter) if val == 0]
# pfloater_fil = np.array([val for i, val in enumerate(pfloater) if i not in zeros])
pmem_fil = np.array([val for i,val in enumerate(pmem) if i not in zeros])
radar_fil = np.array([val for i, val in enumerate(radar) if i not in zeros])
level_fil = np.array([val for i ,val in enumerate(level) if i not in zeros])


pmem_fil += .4  #ongeveer .6bar waterkolom
# pfloater_fil += 1
radar_fil += 2

# opp = np.pi/4 * SP.floaterInnerDiamUp**2 - np.pi/8 *(SP.floaterInnerDiamUp**2-SP.membrameInnerDiam**2)
# F_floater = opp*pfloater_fil*1e5

# Buitendruk_constant = -GP.Patm*(np.pi/8)*(SP.membrameInnerDiam**2+SP.floaterInnerDiamUp**2)



# zwaartekracht = - GP.g * SP.floaterMass
# Fnet = - zwaartekracht - Buitendruk_constant - F_floater
# opp_profiel = Fnet / (pmem_fil*1e5 - GP.Patm/2)
profieldiam = SP.profileDiam[::-1]


offset = np.pi/4*(profieldiam[2000]-profieldiam)+0.025
z = np.linspace(1,(round(max(radar_fil),3)),int(round(max(radar_fil)-.2)*1000))
z+=offset[1000:1000+len(z)]

dz = z[1:] - z[:-1]
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
diameter = profieldiam[1000:1000+len(z)]

offset = .034
V_profiel = []
V_cumulatief = 0
for hoogte in range(len(z)):
    dV = np.pi/4*((diameter[hoogte]-offset)**2-SP.floaterInnerDiamUp**2)*dz[hoogte]
    V_cumulatief += dV
    V_profiel.append(V_cumulatief)


V_profiel = (np.array(V_profiel[2:])+np.array(V_profiel[1:-1])) / 2
z  = z[1:-1]
dz = dz[1:-1]
diameter = diameter[1:-1]

p = np.polyfit(z,V_profiel,10)

def profiel(x,b):
    return b - np.polyval(p,x)

# Waardes met filter 1!!!!!
# deel1 = slice(int(np.floor(len(radar_fil)/9)))
# deel2 = slice(int(np.floor(len(radar_fil)/9)),int(np.floor(.85*len(radar_fil)/2)))
# deel3 = slice(int(np.floor(1.1*len(radar_fil)/2)),-603)

# Waardes zonder filter 1!!!
deel1 = slice(int(np.floor(len(radar_fil)/10)))
deel2 = slice(int(np.floor(len(radar_fil)/9)),int(np.floor(1.1*len(radar_fil)/2)))
deel3 = slice(int(np.floor(1.2*len(radar_fil)/2)),-603)

[b1],cov1 = curve_fit(profiel,radar_fil[deel1],level_fil[deel1])
plt.plot(radar_fil[deel1],level_fil[deel1],marker='o',markersize=1,linestyle='',label='level 1')
plt.plot(z,profiel(z,b1),label='verticale {} offset, cov {}'.format(round(b1,3),round(cov1[0][0],10)))
[b2],cov2 = curve_fit(profiel,radar_fil[deel2],level_fil[deel2])
plt.plot(radar_fil[deel2],level_fil[deel2],marker='o',markersize=1,linestyle='',label='level 2')
plt.plot(z,profiel(z,b2),label='verticale {} offset, cov {}'.format(round(b2,3),round(cov2[0][0],10)))
[b3],cov3 = curve_fit(profiel,radar_fil[deel3],level_fil[deel3])
plt.plot(radar_fil[deel3],level_fil[deel3],marker='o',markersize=1,linestyle='',label='level 3')
plt.plot(z,profiel(z,b3),label='verticale {} offset, cov {}'.format(round(b3,3),round(cov3[0][0],10)))

plt.title(offset)
plt.xlabel('radar [$m$]')
plt.ylabel('level in SpT [$m^3$]')
plt.legend()

plt.show()