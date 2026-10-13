import matplotlib.pyplot as plt
import numpy as np
from math import atan2,degrees
from scipy.fft import rfft,irfft
import math
from scipy.optimize import curve_fit


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
pturbmem = np.load('drytest 2910_verwerkt/pturbmem.npy')
pturbspring = np.load('drytest 2910_verwerkt/pturbspring.npy')
pspring_gas = np.load('drytest 2910_verwerkt/pspring_gas.npy')
pfloater = np.load('drytest 2910_verwerkt/pfloater.npy')

# plt.plot(tijd,pturbmem-pturbspring,linestyle='',marker='o',markersize=1)
# # plt.plot(tijd,radar,linestyle='',marker='o',markersize=1)
# plt.show()
dz = radar[1:] - radar[:-1]
# plt.plot(tijd,radar,linestyle='',marker='o',markersize=1)
kleinecheck = np.where(abs(dz)<.01,1,0)
kleinecheck = kleinecheck[:-10]*kleinecheck[1:-9]*kleinecheck[2:-8]*kleinecheck[3:-7]*kleinecheck[4:-6]*kleinecheck[5:-5]*kleinecheck[6:-4]*kleinecheck[7:-3]*kleinecheck[8:-2]*kleinecheck[9:-1]*kleinecheck[10:]
kleinecheck = 1 - kleinecheck
begin = []
eind = []
for i in range(len(kleinecheck)-1):
    if kleinecheck[i+1] - kleinecheck[i] == 1:
        begin.append(i+1)
    if kleinecheck[i+1] - kleinecheck[i] == -1:
        if begin:
            if i - begin[-1] < 500:
                begin.pop(-1)
            else:
                eind.append(i)
# plt.plot(tijd[:-11],kleinecheck,linestyle='',marker='o',markersize=1)
# plt.show()
dp = pturbmem - pturbspring
for i in range(len(begin)):
    maxdp = max(abs(dp[slice(begin[i],eind[i])]))
    while maxdp > 4:
        element = list(np.where(abs(dp[slice(begin[i],eind[i]+10)])==maxdp,1,0)).index(1)
        if element > (eind[i] - begin[i])/2:
            eind[i] = begin[i] + element - 2
        else:
            begin[i] = begin[i] + element + 1
        maxdp = max(abs(dp[slice(begin[i],eind[i])]))
        if begin[i] > eind[i]:
            begin.pop(i)
            eind.pop(i)
            maxdp = 0

periode1 = []
fase1 = []
periode2 = []
fase2 = []

for i in range(len(begin)):
    gebied = slice(begin[i],eind[i]+10)
    hoogte = radar[gebied]
    dp = pturbmem[gebied]-pturbspring[gebied]

    freqs = list(abs(rfft(hoogte)))[1:]
    freq = freqs.index(max(freqs))
    if freq:
        freq /= (tijd[gebied][-1]-tijd[gebied][0])
        periode = 1/ freq
        if periode <15:
            # plt.plot(range(len(freqs)),freqs)
            # plt.plot([freq,freq],[0,freqs[freq]])
            # plt.show()
            # verschuifsels = 40*int(math.floor(periode*2*len(tijd[gebied]) / (tijd[gebied][-1]-tijd[gebied][0])))
            verschuifsels = 10000
            max_producth = 0
            max_phaseh = 0
            max_productp = 0
            max_phasep = 0
            for phase in range(verschuifsels):
                sinus = np.sin(2*np.pi*(tijd[gebied] / periode + phase/verschuifsels))
                if sum(hoogte*sinus) > max_producth:
                    max_phaseh = phase
                if sum(dp*sinus) > max_productp:
                    max_phasep = phase

            max_phase = (max_phaseh-max_phasep)/verschuifsels*360
            gem_float = sum(pfloater[gebied])/len(pfloater[gebied])
            gem_st = sum(pspring_gas[gebied])/len(pspring_gas[gebied])
            titel = 'floaterdruk '+str(round(gem_float,2))+ ' barg, periode '+str(round(periode,1))+' s, fasehoek '+str(round(max_phase,1))+' deg' 
            plt.title(titel)
            plt.plot(tijd[gebied],dp,label = 'dp')
            plt.plot(tijd[gebied],hoogte,label = 'hoogte')
            plt.legend()
            plt.savefig('drytest 2910_verwerkt/'+titel+'.png')
            plt.clf()

            if gem_float <.12:
                periode1.append(periode)
                fase1.append(max_phase)
            else:
                periode2.append(periode)
                fase2.append(max_phase)



fase2.pop(6)
periode2.pop(6)

opschroeven = [i for i,n in enumerate(periode1) if n>4.5 and fase1[i]<50]
for i,n in enumerate(fase1):
    if i in opschroeven:
        fase1[i]+=180
opschroeven = [i for i,n in enumerate(periode2) if n>4.5 and fase2[i]<50]
for i,n in enumerate(fase2):
    if i in opschroeven:
        fase2[i]+=180

def curve(x,a,b):
    return 360*np.arctan(b*(x-a))/np.pi
fit1,cov1 = curve_fit(curve,periode1,fase1)
fit2,cov2 = curve_fit(curve,periode2,fase2)

plt.plot(np.linspace(min(periode1),max(periode1),1000),curve(np.linspace(min(periode1),max(periode1),1000),fit1[0],fit1[1]),label='For $P_{SpT}=10.4 bar(g)$, $T_{res}='+str(round(fit1[0],2))+'s$',color='orange')
plt.plot(periode1,fase1,linestyle='',marker='o',color='orange')
plt.plot([fit1[0]],[0],marker ='o',linestyle='',color='gray')

plt.plot(np.linspace(min(periode2),max(periode2),1000),curve(np.linspace(min(periode2),max(periode2),1000),fit2[0],fit2[1]),label='For $P_{SpT}=9.9 bar(g)$, $T_{res}='+'{:.2f}'.format(round(fit2[0],2))+'s$',color='green')
plt.plot(periode2,fase2,linestyle='',marker='o',color='green')
plt.plot([fit2[0]],[0],marker ='o',linestyle='',color='gray')

plt.plot([min(periode1+periode2),max(periode1+periode2)],[0,0],linestyle='--',color='gray')

plt.title('Resonance frequency modulation through varying SpringTank pressure')
plt.xlabel('Driving period in s')
plt.ylabel('Phase angle in deg')
plt.legend()
plt.show()