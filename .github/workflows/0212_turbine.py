import matplotlib.pyplot as plt
import numpy as np
from modelParams import SymphonyParams as SP
from modelParams import GeneralParams as GP
import warnings
from matplotlib.collections import LineCollection
import seaborn as sns
from scipy.fft import rfft,irfft



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


tijd = np.load('drytest 20251202_verwerkt/tijd.npy')
deel = slice(int(round(len(tijd)*0.)),int(round(len(tijd)*0.36)))

tijd = (tijd[deel] - tijd[deel][0]) / 1000
radar = np.load('drytest 20251202_verwerkt/radar.npy')[deel]
pfloater = np.load('drytest 20251202_verwerkt/pfloater.npy')[deel]
pmem = np.load('drytest 20251202_verwerkt/pmem1.npy')[deel]
encoder = np.load('drytest 20251202_verwerkt/encoder.npy')[deel]            # %65530
pturb_spring = np.load('drytest 20251202_verwerkt/pturbspring.npy')[deel]
pturb_mem = np.load('drytest 20251202_verwerkt/pturbmem.npy')[deel]
pspring_gas = np.load('drytest 20251202_verwerkt/pspring_gas.npy')[deel]
rpm = np.load('drytest 20251202_verwerkt/rpm.npy')[deel]


plt.plot(tijd,rpm)
plt.show()

freqs = rfft(rpm)
plt.plot(np.arange(int(np.ceil(len(tijd)/2)))/(tijd[-1]-tijd[0]),abs(freqs))
plt.show()


dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
v = 1000*dz/dt


profieldiam = SP.profileDiam
# offset = np.pi/4*(profieldiam[2000]-profieldiam) + 0.06
z = np.linspace(0,4,4001)#+offset
drukval = pturb_mem - pturb_spring + 0.089

# rpm = encoder[1:] - encoder[:-1]
# zaag_af = np.where(rpm>3e4,-65530,0)
# zaag_op = np.where(rpm<-3e4,65530,0)
# rpm += zaag_af + zaag_op
# rpm *= 60/.2/ 65530
# rpm = (np.array([0]+list(rpm))+np.array(list(rpm)+[0]))/2
drpm = rpm[1:] - rpm[:-1]
drpm = (np.array([0]+list(drpm))+np.array(list(drpm)+[0]))/2





i = [i for i,val in enumerate(rpm) if val!=0.]
rpm = rpm[i]
drukval = drukval[i]
drpm = drpm[i]
v=v[i]
plt.plot(rpm,drukval,linestyle='',marker='o',markersize=1)
plt.show()
# dz = dz[i]

# i = [i for i,val in enumerate(drpm) if abs(val)>5]
# rpm = rpm[i]
# drukval = drukval[i]

pmem -= .6  #ongeveer .6bar waterkolom
pfloater += 1
radar += 2

verlies = -drukval*rpm*1e5*10.6/1e3/60
up = [i for i,val in enumerate(drukval) if val > 0]
down = [i for i,val in enumerate(drukval) if val < 0]
drukval = np.concatenate([drukval[up],-drukval[down]])
verlies = np.concatenate([verlies[up],verlies[down]])
fit = np.polyfit(drukval,verlies/drukval,2)



up = [i for i,val in enumerate(verlies) if val>0]
down = [i for i,val in enumerate(verlies) if val<0]
verlies_dubbelgevouwen = np.concatenate([verlies[up],-verlies[down]])
drukval_dubbelgevouwen = np.concatenate([drukval[up],drukval[down]])
plt.plot(drukval,verlies,linestyle='',marker='o',markersize=2)
plt.title('Turbine loss')
# plt.legend()
plt.ylabel('Power loss [W]')
plt.xlabel('Pressure drop over the turbine [bar]')
plt.show()


lek = drukval*np.poly1d([-49.92674769,349.01214219,28.82145074])(drukval)
# lek = drukval*np.poly1d(fit)(drukval)
verlies -= lek

up = [i for i,val in enumerate(verlies) if val>0]
down = [i for i,val in enumerate(verlies) if val<0]
verlies_dubbelgevouwen = np.concatenate([verlies[up],-verlies[down]])
drukval_dubbelgevouwen = np.concatenate([drukval[up],drukval[down]])


a = 50
b = a
zestig = .6*len(verlies_dubbelgevouwen)
for iteratie in range(100):
    sigma = b*drukval_dubbelgevouwen**2
    waardes = list(np.where(verlies_dubbelgevouwen<sigma,1,0)).count(1)
    a/=2
    if waardes>zestig:
        b-=a
    if waardes<zestig:
        b+=a



# fit = np.polyfit(drukval,lek/drukval,2)
drukval_array = np.linspace(0.1,max(drukval),1000)


fig, ax = plt.subplots()
plt.plot(drukval, verlies, linestyle='',marker='o',markersize=1,label='Measured power loss minus leak and static friction')
plt.plot(drukval_array,-b*drukval_array**2,color='purple')
plt.plot(drukval_array,b*drukval_array**2,color='purple')
ax.fill_between(drukval_array, -b*drukval_array**2, b*drukval_array**2, color='purple',alpha=0.2,label='$1\sigma$ quadratic noise')
plt.ylim(-1750,1750)
# ax.plot(x, y, 'o', color='tab:brown')


# plt.plot(drukval,verlies,linestyle='',marker='o',markersize=2,label='Measured leak [W] for static angular turbine velocity [rpm]')
# plt.plot(drukval_array,b*drukval_array**2,label='$\sigma$',color='orange')
# plt.plot(drukval_array,-b*drukval_array**2,color='orange')
plt.title('Dynamic turbine power loss')
plt.legend()
plt.ylabel('Dynamic power loss [W]')
plt.xlabel('Absolute pressure drop over the turbine [bar]')
plt.show()

genormalizeerd = verlies / (b*drukval**2)
i = [i for i,val in enumerate(genormalizeerd) if abs(val)<4]
genormalizeerd = genormalizeerd[i]
v = v[i]
rpm = rpm[i]
i = [i for i,val in enumerate(v) if val!=0.]
genormalizeerd = genormalizeerd[i]
v = v[i]
rpm = rpm[i]

v = np.sort(abs(v))
rpm = np.sort(abs(rpm))
genormalizeerd = np.sort(genormalizeerd+.151)

# genormalizeerd = np.sort(genormalizeerd +.34)
# pakketje = np.floor(len(genormalizeerd)/100)

# for i in range(100):
#     deel = slice(i*pakketje,(i+1)*pakketje)
sigma = np.linspace(-2,3,401)


x = np.linspace(-2, 3, 1000)
y = 220*np.exp(-x**2 / (2*.02))
plt.plot(x, y, 'g--', label='normal distribution')
plt.plot(sigma,np.histogram(genormalizeerd,401,(-2,3))[0],label='normalized power loss minus leak and friction')
# sns.histplot(genormalizeerd, kde=True, bins=40, color='purple',label='normalized power loss minus leak and friction')
plt.legend()
plt.title('Noise and dynamic power loss')
plt.xlabel('$\sigma$')
plt.ylabel('Count')
plt.grid()
plt.show()

plt.plot(sigma,np.histogram(genormalizeerd,401,(-2,3))[0],label='measured power loss')
plt.plot(sigma,220*np.exp(-sigma**2 / (2*.02)),label='noise')
plt.plot(sigma,np.histogram(genormalizeerd,401,(-2,3))[0]-220*np.exp(-sigma**2 / (2*.02)),label='denoised power loss')
# plt.plot(sigma[17:],np.histogram(v[17:],401,(-4,4))[0][:-17],label='snelheid')
plt.title('Denoised dynamic power loss')
plt.xlabel('$\sigma$')
plt.ylabel('Count')
plt.show()

verschil = np.histogram(genormalizeerd,401,(-4,4))[0]-220*np.exp(-sigma**2 / (2*.02))
v_gefilterd = v[-len(verschil):-100]
rpm_gefilterd = rpm[-len(verschil):-100]
genormalizeerd_gefilter = genormalizeerd[-len(verschil):-100]

fit = np.polyfit(v_gefilterd,genormalizeerd_gefilter,1)
v_fit = np.linspace(min(v_gefilterd),max(v_gefilterd),1000)
verlies_dynamisch = np.poly1d(fit)(v_fit)

plt.title('Dynamic loss')
plt.plot(v_gefilterd,genormalizeerd_gefilter,linestyle='',marker='o',markersize=2,label='Denoised dynamic loss measurement')
plt.plot(v_fit,verlies_dynamisch,label='P[W] = {}*v[m/s]'.format(round(fit[0])))
plt.xlabel('Absolute velocity [m/s]')
plt.ylabel('Dynamic turbine loss [W]')
plt.legend()
plt.show()