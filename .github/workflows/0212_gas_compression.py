import matplotlib.pyplot as plt
import numpy as np
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


tijd = np.load('drytest 0212_verwerkt/tijd.npy')
radar = np.load('drytest 0212_verwerkt/radar.npy')
# pfloater = np.load('drytest 0212_verwerkt/pfloater.npy')
pspring = np.load('drytest 0212_verwerkt/pspring_gas.npy') +1
# pmem = np.load('drytest 0212_verwerkt/pmem1.npy')
temp = np.load('drytest 0212_verwerkt/tempspring.npy') +273.15

p_ref = np.linspace(8,10,1000)
T_ref = (9/p_ref)**.4*280



dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
v = dz/dt
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
v = 1000*(np.array([0]+list(v))+np.array(list(v)+[0])) / 2

snel = [i for i,val in enumerate(v) if abs(val)>.01]
traag = []
for index in range(len(snel)-1):
    if snel[index+1] - snel[index] > 4:
        traag = np.concatenate([traag,range(snel[index]+1,snel[index+1])])


snel  = [i for i,val in enumerate(tijd) if i not in traag]
tijd = tijd[snel]
radar = radar[snel]
pspring = pspring[snel]
temp = temp[snel]

# for i in range(len(temp)-1):
#     dtemp = temp[i+1] - temp[i]
    


delen = 3
deellengte = round(len(tijd)/delen)



for delay in range(50):
    delay*=20
    tijdstap = 200
    stap = int(np.ceil(delay/tijdstap))
    a = (delay % tijdstap) / tijdstap
    if not a:
        stap +=1
    print(stap)
    print(a)
    b = 1 - a

    # pmem_verwerkt = np.concatenate([pmem,np.zeros(stap)])
    # pmem_verwerkt = b * pmem_verwerkt[stap-1:len(pmem_verwerkt)-stap] + a * pmem_verwerkt[stap:len(pmem_verwerkt)-stap+1]
    pspring_verwerkt = np.concatenate([pspring,np.zeros(stap)])
    pspring_verwerkt = b * pspring_verwerkt[stap-1:len(pspring_verwerkt)-stap] + a * pspring_verwerkt[stap:len(pspring_verwerkt)-stap+1]




    # for deel in range(delen):
    deel = 0
    slice_deel = slice(deel*deellengte,(deel+1)*deellengte-1)
    # slice_deel = slice(-1)
    tijd_deel = tijd[slice_deel]
    radar_deel = radar[slice_deel]
    pspring_deel = pspring_verwerkt[slice_deel]
    temp_deel = temp[slice_deel]
    fig,ax = plt.subplots()
    lines = colored_line(pspring_deel,temp_deel, tijd_deel, ax, linewidth=2, cmap="viridis")
    plt.plot(p_ref,T_ref)
    ax.set_xlim(.9*min(pspring_deel),1.1*max(pspring_deel))
    ax.set_ylim(.9*min(temp_deel),1.1*max(temp_deel))
    ax.set_title('Course of pressure with {}ms delay'.format(delay))
    ax.set_xlabel('Springtankdruk [bar(a)]')
    ax.set_ylabel('Temperatuur [K]')
    plt.show()

    # fig.savefig('drytest 0212_verwerkt/druk-positie'+str(delay)+'.png')
    
    # plt.cla()


    # plt.plot(radar,pfloater,linestyle='',marker='o',markersize=1)
    # plt.plot(radar,pmem,linestyle='',marker='o',markersize=1)
    # plt.title('Floater tank volume fit')
    # plt.xlabel('Floater position [$m$]')
    # plt.ylabel('Floater tank pressure [$bar(g)$]')
    # plt.show()