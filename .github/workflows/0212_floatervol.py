import matplotlib.pyplot as plt
import numpy as np
from math import atan2,degrees
from scipy.fft import rfft, irfft
from os import walk
from scipy.optimize import curve_fit
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

tijd = np.load('drytest 0212_verwerkt/tijd.npy')
radar = np.load('drytest 0212_verwerkt/radar.npy')
pfloater = np.load('drytest 0212_verwerkt/pfloater.npy')

# dz = radar[1:] - radar[:-1]
# kleinecheck = np.where(abs(dz)<.01,1,0)
# kleinecheck = kleinecheck[:-10]*kleinecheck[1:-9]*kleinecheck[2:-8]*kleinecheck[3:-7]*kleinecheck[4:-6]*kleinecheck[5:-5]*kleinecheck[6:-4]*kleinecheck[7:-3]*kleinecheck[8:-2]*kleinecheck[9:-1]*kleinecheck[10:]
# kleinecheck = 1 - kleinecheck
# begin = []
# eind = []
# for i in range(len(kleinecheck)-1):
#     if kleinecheck[i+1] - kleinecheck[i] == 1:
#         begin.append(i+1)
#     if kleinecheck[i+1] - kleinecheck[i] == -1:
#         if begin:
#             if i - begin[-1] < 500:
#                 begin.pop(-1)
#             else:
#                 eind.append(i)

# dp = pturbmem - pturbspring
# for i in range(len(begin)):
#     maxdp = max(abs(dp[slice(begin[i],eind[i])]))
#     while maxdp > 4:
#         element = list(np.where(abs(dp[slice(begin[i],eind[i]+10)])==maxdp,1,0)).index(1)
#         if element > (eind[i] - begin[i])/2:
#             eind[i] = begin[i] + element - 2
#         else:
#             begin[i] = begin[i] + element + 1
#         maxdp = max(abs(dp[slice(begin[i],eind[i])]))
#         if begin[i] > eind[i]:
#             begin.pop(i)
#             eind.pop(i)
#             maxdp = 0

dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
v = dz/dt
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
v = (np.array([0]+list(v))+np.array(list(v)+[0])) / 2
# def curve(x,a,b,c):
#     return a -b*x[0]+c*x[1]
# fit,cov = curve_fit(curve,[radar,dz],pfloater)
# print(fit)
# plt.plot(radar,pfloater-fit[2]*dz,linestyle='',marker='o',markersize=1)
# plt.plot(np.linspace(min(radar),max(radar),1000),fit[0]-fit[1]*np.linspace(min(radar),max(radar),1000))
# plt.show()
pfloater = np.array(pfloater)
dzabs = abs(dz)
filter1 = np.where(dzabs<.005,1,0)
filter1 = np.concatenate((filter1[-2:], filter1[:-2]))*np.concatenate((filter1[-1:], filter1[:-1])) * filter1 * np.concatenate((filter1[1:], filter1[:1]))*np.concatenate((filter1[2:], filter1[:2]))
filter2 = np.where(pfloater==.0,0,1)
filter3 = np.where(pfloater<0,0,1)
filter4 = np.where(pfloater>1,0,1)

# filter3 = np.where(radar<-1.6,0,1)
# filter4 = np.where(radar>-1,0,1)
filter = filter1*filter2*filter3*filter4

zeros = [i for i, val in enumerate(filter) if val == 0]
pfloater_fil = np.array([val for i, val in enumerate(pfloater) if i not in zeros])
radar_fil = np.array([val for i, val in enumerate(radar) if i not in zeros])

# dz_fil = np.array([val for i, val in enumerate(dz) if i not in zeros])

pfloater_fil += 1
radar_fil += 2

bewegen = [i for i,val in enumerate(radar_fil) if val>.66]


# opp = np.pi/4 * SP.floaterInnerDiamUp**2 - np.pi/8 *(SP.floaterInnerDiamUp**2-SP.membrameInnerDiam**2)
oppervlak_floater = np.pi/4*SP.floaterInnerDiamUp**2
oppervlak_core = np.pi/4*SP.membrameInnerDiam**2
V0 = 0.8 + oppervlak_floater * 1.83 + 1.88 + (oppervlak_floater - oppervlak_core) * 2.51
print(V0)


def curve(x,NRT,opp):
    return NRT / (V0+opp*x)
[NRT,opp],cov = curve_fit(curve,radar_fil[bewegen],pfloater_fil[bewegen])
print(cov)
print(V0+4*opp,NRT)
plt.plot(radar_fil,pfloater_fil-1,linestyle='',marker='o',markersize=1)
plt.plot(np.linspace(min(radar_fil),max(radar_fil),1000),NRT / (V0+opp*np.linspace(min(radar_fil),max(radar_fil),1000))-1)
plt.title('Floater tank volume fit')
plt.xlabel('Floater position [$m$]')
plt.ylabel('Floater tank pressure [$bar(g)$]')
plt.show()


print(opp)