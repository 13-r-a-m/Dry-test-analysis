import matplotlib.pyplot as plt
import numpy as np
from math import atan2,degrees
from scipy.fft import rfft,irfft
import math
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

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

demping = 0.30379627930520586
omega0_ansatz = 1.4631955908069594
T = 2*np.pi / omega0_ansatz / (1-2*demping**2)**.5
print(omega0_ansatz * (1-2*demping**2)**.5)
print(T)
A = -0.2
# B = 45
B = 0.9

omega1 = np.load('drytest 2910_verwerkt/omega1.npy')
omega2 = np.load('drytest 2910_verwerkt/omega2.npy')
fase1 = np.load('drytest 2910_verwerkt/fase1.npy')
fase2 = np.load('drytest 2910_verwerkt/fase2.npy')
power1 = np.load('drytest 2910_verwerkt/power1.npy')
power2 = np.load('drytest 2910_verwerkt/power2.npy')
# fase1[-1]-=5
# fase1[-2]-=3
fase1+= 180/np.pi * omega1 * A
fase2+= 180/np.pi * omega2* A

# plt.plot(omega1,power1/omega1,marker='o',linestyle='')
# plt.plot(omega2,power2/omega2,marker='o',linestyle='')
# plt.show()

def curve(omega,omega0):
    return -B*90/omega0*omega + (1-B)*np.where(omega>omega0,180*(np.arctan(2*omega*omega0*demping/(omega**2-omega0**2)))/np.pi-180,180*(np.arctan(2*omega*omega0*demping/(omega**2-omega0**2)))/np.pi)

# # dPhase = dt / T * 360 = dt * omega / (2pi) *360 = 180/pi * omega * dt
# def curve(omega,omega0):
#     return np.where(omega>omega0,180*(np.arctan(2*omega*omega0*demping/(omega**2-omega0**2)))/np.pi-180,180*(np.arctan(2*omega*omega0*demping/(omega**2-omega0**2)))/np.pi) 
fit1,cov1 = curve_fit(curve,omega1,fase1)
fit2,cov2 = curve_fit(curve,omega2,fase2)

T1 = 2*np.pi / (fit1[0]*(1-2*demping**2)**.5)
T2 = 2*np.pi / (fit2[0]*(1-2*demping**2)**.5)
print(T1,T2)

print(fit1)
print(fit2)


plt.plot(np.linspace(min(omega1),max(omega1),1000),curve(np.linspace(min(omega1),max(omega1),1000),fit1[0]),label='For $P_{SpT}=10.4 bar(g)$, $T_{res}='+'{:.2f}s$'.format(T1),color='orange')
plt.plot(omega1,fase1,linestyle='',marker='o',color='orange')
# plt.plot([fit1[0]+1/fit1[1]],[90],marker ='o',linestyle='',color='gray')
# plt.plot([fit1[0]+1/fit1[1],fit1[0]+1/fit1[1]],[0,90],linestyle='--',color='gray')

plt.plot(np.linspace(min(omega2),max(omega2),1000),curve(np.linspace(min(omega2),max(omega2),1000),fit2[0]),label='For $P_{SpT}=9.9 bar(g)$, $T_{res}='+'{:.2f}s$'.format(T2),color='green')
plt.plot(omega2,fase2,linestyle='',marker='o',color='green')
# plt.plot([fit2[0]+1/fit2[1]],[90],marker ='o',linestyle='',color='gray')
# plt.plot([fit2[0]+1/fit2[1],fit2[0]+1/fit2[1]],[0,90],linestyle='--',color='gray')

plt.plot([min(list(omega1)+list(omega2)),max(list(omega1)+list(omega2))],[0,0],linestyle='--',color='gray')

# plt.title(A)
plt.title('Resonance frequency modulation through varying SpringTank pressure')
plt.xlabel('Driving angular velocity $\omega$ in rad/s')
plt.ylabel('Phase angle $\phi$ in deg')
plt.legend()
plt.savefig('drytest 2910_verwerkt/resontiefrequentie.png')

plt.show()