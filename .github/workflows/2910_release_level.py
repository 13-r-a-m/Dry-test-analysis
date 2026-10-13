import matplotlib.pyplot as plt
import numpy as np
from math import atan2,degrees
from scipy.fft import rfft,irfft
import math
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.optimize import OptimizeWarning
import warnings
from matplotlib.widgets import Slider
from modelParams import SymphonyParams as SP


def labelLine(line,x,label=None,align=True,**kwargs):

    ax = line.axes
    xdata = line.get_xdata()
    ydata = line.get_ydata()

    if (x < xdata[0]) or (x > xdata[-1]):
        print('x label location is outside data range!')
        return

    #Find corresponding y co-ordinate and angle of the line
    ip = 1
    for i in range(len(xdata)):
        if x < xdata[i]:
            ip = i
            break

    y = ydata[ip-1] + (ydata[ip]-ydata[ip-1])*(x-xdata[ip-1])/(xdata[ip]-xdata[ip-1])

    if not label:
        label = line.get_label()

    if align:
        #Compute the slope
        dx = xdata[ip] - xdata[ip-1]
        dy = ydata[ip] - ydata[ip-1]
        ang = degrees(atan2(dy,dx))

        #Transform to screen co-ordinates
        pt = np.array([x,y]).reshape((1,2))
        trans_angle = ax.transData.transform_angles(np.array((ang,)),pt)[0]

    else:
        trans_angle = 0

    #Set a bunch of keyword arguments
    if 'color' not in kwargs:
        kwargs['color'] = line.get_color()

    if ('horizontalalignment' not in kwargs) and ('ha' not in kwargs):
        kwargs['ha'] = 'center'

    if ('verticalalignment' not in kwargs) and ('va' not in kwargs):
        kwargs['va'] = 'center'

    if 'backgroundcolor' not in kwargs:
        kwargs['backgroundcolor'] = ax.get_facecolor()

    if 'clip_on' not in kwargs:
        kwargs['clip_on'] = True

    if 'zorder' not in kwargs:
        kwargs['zorder'] = 2.5

    ax.text(x,y,label,rotation=trans_angle,**kwargs)

def labelLines(lines,align=True,xvals=None,**kwargs):

    ax = lines[0].axes
    labLines = []
    labels = []

    #Take only the lines which have labels other than the default ones
    for line in lines:
        label = line.get_label()
        if "_line" not in label:
            labLines.append(line)
            labels.append(label)

    if xvals is None:
        xmin,xmax = ax.get_xlim()
        xvals = np.linspace(xmin,xmax,len(labLines)+2)[1:-1]

    for line,x,label in zip(labLines,xvals,labels):
        labelLine(line,x,label,align,**kwargs)

tijd = np.load('drytest 2910_verwerkt/tijd.npy')
tijd = (tijd - tijd[0]) / 1000
radar = np.load('drytest 2910_verwerkt/radar.npy')
dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
snelheid = dz/dt
posencoder = np.load('drytest 2910_verwerkt/posencoder.npy')
targetencoder = np.load('drytest 2910_verwerkt/targetencoder.npy')
power = np.load('drytest 2910_verwerkt/power.npy')
stroom = np.load('drytest 2910_verwerkt/stroom.npy')
spanning = np.load('drytest 2910_verwerkt/spanning.npy')
level = np.load('drytest 2910_verwerkt/level.npy')
druk_liquid = np.load('drytest 2910_verwerkt/pspring_liquid.npy')
druk_gas = np.load('drytest 2910_verwerkt/pspring_gas.npy')
waterkolom = druk_gas - druk_liquid
Massa = SP.floaterMass



t = []
for i in range(len(tijd)):
    t.append(int(np.floor(tijd[i])))

def toIndex(tijd_waarde):
    index = t.index(tijd_waarde)
    return index


tijdsloten = [[1159,1172],
            [1926,1943],
            [2687,2700],
            [2925,2937],
            [3508,3523],
            [3686,3697],
            [5698,5705],
            [7701,7715],
            [11404,11420],
            [12452,12467],
            [13423,13437],
            [14349,14362],
            [14938,14951]]


mperiode = []
mdemping = []
mdemping_correct = []

def curve(t,a,b):
    return t*a+b

for stuk in tijdsloten:
    periode = []
    demping = []
    demping_correct = []
    
    tussenstuk = slice(toIndex(stuk[0])+30,toIndex(stuk[1])+80)
    if len(posencoder[tussenstuk]) % 2:
        tussenstuk = slice(toIndex(stuk[0]),toIndex(stuk[1])+81)
    posencoder[tussenstuk] -= posencoder[tussenstuk][-1]
    dt = (tijd[tussenstuk][-1] - tijd[tussenstuk][0]) / len(tijd[tussenstuk])
    # ref_pos = np.concatenate([posencoder[tussenstuk],np.zeros(3000)])
    # ref_tijd = np.concatenate([tijd[tussenstuk],np.linspace(tijd[tussenstuk][-1]+dt,tijd[tussenstuk][-1]+3000*dt,3000)])-tijd[tussenstuk][0]
    ref_pos = posencoder[tussenstuk]
    dz = ref_pos[1:] - ref_pos[:-1]
    ref_tijd = tijd[tussenstuk]-tijd[tussenstuk][0]
    ref_power = power[tussenstuk]
    ref_v = snelheid[tussenstuk]
    ref_level = level[tussenstuk]
    ref_waterkolom = waterkolom[tussenstuk]
    
    if max(ref_pos) + min(ref_pos) < 0:
        ref_pos *= -1

    start = np.where(dz==0)[0][0]
    saaie_slice = slice(start,None)


    [[a_level,b_level],cov] = curve_fit(curve,ref_tijd[saaie_slice],ref_level[saaie_slice])
    [[a_water,b_water],cov] = curve_fit(curve,ref_tijd[saaie_slice],ref_waterkolom[saaie_slice])

    plt.plot(ref_tijd,ref_pos,label='encoder')
    plt.plot(ref_tijd[saaie_slice],ref_level[saaie_slice],label='level')
    plt.plot(ref_tijd[saaie_slice],curve(ref_tijd[saaie_slice],a_level,b_level))
    plt.plot(ref_tijd[saaie_slice],ref_waterkolom[saaie_slice],label='dP')
    plt.plot(ref_tijd[saaie_slice],curve(ref_tijd[saaie_slice],a_water,b_water))
    plt.legend()
    plt.show()
    print(a_water*1e5/(9.81*a_level))