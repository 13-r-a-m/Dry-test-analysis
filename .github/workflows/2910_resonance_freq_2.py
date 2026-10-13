import matplotlib.pyplot as plt
import numpy as np
from math import atan2,degrees
from scipy.fft import rfft,irfft
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

tijd = np.load('drytest 2910_verwerkt/tijd.npy')
tijd = (tijd - tijd[0]) / 1000
radar = np.load('drytest 2910_verwerkt/radar.npy')
radar = np.delete(np.concatenate([[0,0],radar]),[-1,-2])
pturbmem = np.load('drytest 2910_verwerkt/pturbmem.npy')
pturbspring = np.load('drytest 2910_verwerkt/pturbspring.npy')
pspring_gas = np.load('drytest 2910_verwerkt/pspring_gas.npy')
pfloater = np.load('drytest 2910_verwerkt/pfloater.npy')

# plt.plot(tijd,pturbmem-pturbspring,linestyle='',marker='o',markersize=1)
# # plt.plot(tijd,radar,linestyle='',marker='o',markersize=1)
# plt.show()
dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
v = dz/dt
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
v = (np.array([0]+list(v))+np.array(list(v)+[0])) / 2
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

dp = pturbspring - pturbmem
# for i in range(len(begin)):
#     maxdp = max(abs(dp[slice(begin[i],eind[i])]))
#     while maxdp > 3.5:
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

periode1 = []
fase1 = []
periode2 = []
fase2 = []

for i in range(len(begin)):
    if (eind[i]-begin[i])%2:
        eind[i]-=1
    gebied = slice(begin[i],eind[i]+10)
    snelheid = v[gebied]
    dp = pturbspring[gebied] - pturbmem[gebied]
    fourier = rfft(dp)
    fourier[0] = 0
    trap = np.where(np.linspace(0,len(tijd)/(2*(tijd[-1]-tijd[0])),int(len(dp)/2+1))<.5,1,0)
    dp = irfft(fourier*trap)
    # dp -= sum(dp)/len(dp)
    for i in range(len(dp)-51):
        venster = dp[i:i+52].copy()
        maximum = 0
        for j in range(len(venster)):
            if venster[j] < 0:
                venster[j]*=-1
            if venster[j]>maximum:
                maximum = venster[j]
        if not i:
            dp[:i+25+1]/=maximum
        elif i==len(dp)-52:
            dp[i+25:]/=maximum
        else:
            dp[i+25]/=maximum

    for i in range(len(snelheid)-51):
        venster = snelheid[i:i+52].copy()
        maximum = 0
        for j in range(len(venster)):
            if venster[j] < 0:
                venster[j]*=-1
            if venster[j]>maximum:
                maximum = venster[j]
        if not i:
            snelheid[:i+25+1]/=maximum
        elif i==len(snelheid)-52:
            snelheid[i+25:]/=maximum
        else:
            snelheid[i+25]/=maximum
    
    tijd_extra = np.linspace(tijd[gebied][0],tijd[gebied][-1],(len(tijd[gebied])-1)*10)
    dp_extra = np.array(interp1d(tijd[gebied],dp)(tijd_extra))
    snelheid_extra = np.array(interp1d(tijd[gebied],snelheid)(tijd_extra))
    factor = 1
    freqs = list(abs(rfft(snelheid_extra,n=factor*len(snelheid_extra))))[1:]
    freq = freqs.index(max(freqs))
    if freq:
        Deltat = (tijd_extra[-1]-tijd_extra[0])*factor
        freq_onder = (freq -2)/Deltat
        freq_boven = (freq +2)/Deltat
        periode = Deltat / freq
        if periode <15:
            
            freqs = np.linspace(freq_onder,freq_boven,50)
            phase_0 = 0
            phase_eind = 359
            for zoeksels in range(4):
                max_productp = 0
                for phase in np.linspace(phase_0,phase_eind,360):
                    for freq in range(len(freqs)):
                        periode = 1/freqs[freq]
                        sinus = np.sin(2*np.pi*(tijd_extra / periode + phase/360))
                        productp = sum(dp_extra*sinus)
                        if productp > max_productp:
                            max_productp = productp
                            max_phasep = phase
                            max_periodep = periode
                i_0_nieuw = max_phasep - (phase_eind-phase_0) / 360
                i_eind_nieuw = max_phasep + (phase_eind-phase_0) / 360

            phase_0 = 0
            phase_eind = 359
            for zoeksels in range(3):
                max_productv = 0
                for phase in np.linspace(phase_0,phase_eind,360):
                    for freq in range(len(freqs)):
                        periode = 1/freqs[freq]
                        sinus = np.sin(2*np.pi*(tijd_extra / periode + phase/360))
                        productv = sum(snelheid_extra*sinus)
                        if productv > max_productv:
                            max_productv = productv
                            max_phasev = phase
                            max_periodev = periode
                i_0_nieuw = max_phasev - (phase_eind-phase_0) / 360
                i_eind_nieuw = max_phasev + (phase_eind-phase_0) / 360

            periode = round(max_periodep,1)
            if periode != round(max_periodev,1):
                print('help!')

            sinusp = np.sin(2*np.pi*(tijd_extra / max_periodep + max_phasep/360))
            sinusv = np.sin(2*np.pi*(tijd_extra / max_periodev + max_phasev/360))

            max_phase = max_phasev-max_phasep

            if len(tijd_extra) > 1001:
                midden = slice(round(len(tijd_extra) / 2)-500,round(len(tijd_extra) / 2)+501)
                plt.plot(tijd_extra[midden],sinusp[midden])
                plt.plot(tijd_extra[midden],sinusv[midden])
                plt.plot(tijd_extra[midden],dp_extra[midden],label = 'dp',marker='o',markersize=1,linestyle='')
                plt.plot(tijd_extra[midden],snelheid_extra[midden],label = 'snelheid',marker='o',markersize=1,linestyle='')
            else:
                plt.plot(tijd_extra,sinusp)
                plt.plot(tijd_extra,sinusv)
                plt.plot(tijd_extra,dp_extra,label = 'dp',marker='o',markersize=1,linestyle='')
                plt.plot(tijd_extra,snelheid_extra,label = 'snelheid',marker='o',markersize=1,linestyle='')

            gem_float = sum(pfloater[gebied])/len(pfloater[gebied])
            gem_st = sum(pspring_gas[gebied])/len(pspring_gas[gebied])
            titel = 'periode '+str(round(max_periodep,1))+' s, floaterdruk '+str(round(gem_float,2))+' barg, fasehoek '+str(round(max_phase,1))+' deg' 
            
            plt.title(titel)
            plt.legend()
            plt.savefig('drytest 2910_verwerkt/'+titel+'.png')
            plt.clf()
            # plt.show()

            if gem_float <.12:
                periode1.append(max_periodep)
                fase1.append((max_phase+720)%360)
                print((max_phase+720)%360,periode,1)
            else:
                periode2.append(max_periodep)
                fase2.append((max_phase+720)%360)
                print((max_phase+720)%360,periode,2)



leeg = [i for i,n in enumerate(fase1) if n==.0]
for i in leeg[::-1]:
    periode1.pop(i)
    fase1.pop(i)
leeg = [i for i,n in enumerate(fase2) if n==.0]
for i in leeg[::-1]:
    periode2.pop(i)
    fase2.pop(i)


# for i,n in enumerate(fase1):
#     if n<0:
#         fase1[i]+=180
# for i,n in enumerate(fase2):
#     if n<0:
#         fase2[i]+=180

omega1 = 2*np.pi/np.array(periode1)
omega2 = 2*np.pi/np.array(periode2)
# demping = 0.32652889908204114

# def curve(omega,omega0,demping):
#     return 180*np.arctan(2*omega*omega0*demping/(omega**2-omega0**2))/np.pi
# fit1,cov1 = curve_fit(curve,omega1,fase1)
# fit2,cov2 = curve_fit(curve,omega2,fase2)

# plt.plot(np.linspace(min(omega1),max(omega1),1000),curve(np.linspace(min(omega1),max(omega1),1000),fit1[0],fit1[1]),label='For $P_{SpT}=10.4 bar(g)$, $T_{res}='+str(round(fit1[0],2))+'s$',color='orange')
plt.plot(omega1,fase1,linestyle='',marker='o',color='orange')

# plt.plot(np.linspace(min(omega2),max(omega2),1000),curve(np.linspace(min(omega2),max(omega2),1000),fit2[0],fit2[1]),label='For $P_{SpT}=9.9 bar(g)$, $T_{res}='+'{:.2f}'.format(round(fit2[0],2))+'s$',color='green')
plt.plot(omega2,fase2,linestyle='',marker='o',color='green')

plt.plot([min(list(omega1)+list(omega2)),max(list(omega1)+list(omega2))],[0,0],linestyle='--',color='gray')

plt.title('Resonance frequency modulation through varying SpringTank pressure')
plt.xlabel('Driving angular velocity $\omega$ in rad/s')
plt.ylabel('Phase angle $\phi$ in deg')
plt.legend()
plt.show()