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
Massa = SP.floaterMass
plt.plot(tijd,posencoder,linestyle='',marker='o',markersize=1)
# plt.plot(tijd,targetencoder,linestyle='',marker='o',markersize=1)
plt.show()

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

periode = []
demping = []
demping_correct = []
fig = plt.figure()

for stuk in tijdsloten:
    
    tussenstuk = slice(toIndex(stuk[0])+30,toIndex(stuk[1]))
    if len(posencoder[tussenstuk]) % 2:
        tussenstuk = slice(toIndex(stuk[0]),toIndex(stuk[1])+1)
    posencoder[tussenstuk] -= posencoder[tussenstuk][-1]
    dt = (tijd[tussenstuk][-1] - tijd[tussenstuk][0]) / len(tijd[tussenstuk])
    # ref_pos = np.concatenate([posencoder[tussenstuk],np.zeros(3000)])
    # ref_tijd = np.concatenate([tijd[tussenstuk],np.linspace(tijd[tussenstuk][-1]+dt,tijd[tussenstuk][-1]+3000*dt,3000)])-tijd[tussenstuk][0]
    ref_pos = posencoder[tussenstuk]
    ref_tijd = tijd[tussenstuk]-tijd[tussenstuk][0]
    ref_power = power[tussenstuk]
    ref_v = snelheid[tussenstuk]
    
    frequentie = rfft(ref_pos)
    frequentiebereik = np.linspace(0,.5/dt,len(frequentie))
    
    frequentie = abs(frequentie[1:])
    frequentiebereik = frequentiebereik[1:]
    
    T_p = 1 / frequentiebereik[list(frequentie).index(max(frequentie))]
    minT_p =  1 / frequentiebereik[list(frequentie).index(max(frequentie))+1]
    maxT_p =  1 / frequentiebereik[list(frequentie).index(max(frequentie))-1]

    # print(minT_p,T_p,maxT_p)
    if max(ref_pos) + min(ref_pos) > 0:
        i = list(ref_pos).index(max(ref_pos))
        phi = 2*np.pi*(ref_tijd[0] - ref_tijd[i])/T_p - np.pi/2
    else:
        i = list(ref_pos).index(min(ref_pos))
        phi = 2*np.pi*(ref_tijd[0] - ref_tijd[i])/T_p - np.pi/2

    A_gok = ref_pos[i]/np.exp(-2*(ref_tijd[i]-ref_tijd[0])/T_p)/np.sin(2*np.pi/T_p * ref_tijd[i]+phi)
    omega_gok = 2*np.pi/T_p

    if max(ref_pos) == max(abs(ref_pos)):
        ref_pos *= -1

    index = [i for i,val in enumerate(ref_pos) if val == max(ref_pos)][0]

    zoeken = -1
    jndex = 1
    if index:
        indices = [index]
        eerste = True
    else:
        indices = []
        eerste = False
    while jndex != 0:
        jndex = [j for j,val in enumerate(ref_pos[index:]) if zoeken*val == max(zoeken*ref_pos[index:])][0]
        if jndex:
            hap = slice(index,index+jndex)

            if tijd[index+jndex]!= tijd[index] and ref_pos[index+jndex] != 0. and -ref_pos[index]/ref_pos[index+jndex]<1:
                T = (tijd[index+jndex]-tijd[index])*2
                d = -ref_pos[index]/ref_pos[index+jndex]
                periode.append(T)
                demping.append(d)
                v2 = sum(ref_v[hap]**2) / len(ref_v[hap])
                p = sum(ref_power[hap]) / len(ref_power[hap])
                print(T,d,v2,p)
                demping_correct.append(d + p / (Massa*4*np.pi/T/(1-d**2)**.5) / v2)
                indices.append(index+jndex)
            index+=jndex
            zoeken *= -1


    # if not eerste:
    #     periode.pop(0)
    #     demping.pop(0)
    #     demping_correct.pop(0)


    # if len(periode)>4:
    #     periode.pop(0)
    #     demping.pop(0)
    #     demping_correct.pop(0)
    # print(periode)
    # if len(periode) >= 3:
    #     mperiode.append(periode[:-2])
    #     mdemping.append(demping[:-2])
    #     mdemping_correct.append(demping_correct[:-2])
    # if periode:
    #     mperiode.append(periode[0])
    #     mdemping.append(demping[0])
    #     mdemping_correct.append(demping_correct[0])



    def demp_func(t,A,omega,zeta,phi):
        return A*np.exp(-zeta*t)*np.sin(omega*t+phi)
    
    with warnings.catch_warnings():
        warnings.simplefilter("error", OptimizeWarning)
        try:
            [A,omega,zeta,phi], cov = curve_fit(demp_func,ref_tijd,ref_pos,p0=[A_gok,omega_gok,.4,0],bounds=((-3,.5*omega_gok,0,-np.pi),(3,2*omega_gok,10,np.pi)))
            
            ax = fig.add_subplot(111)
            fig.subplots_adjust(bottom=0.35)
            [line] = ax.plot(ref_tijd, demp_func(ref_tijd,A,omega,zeta,phi))

            ax.set_xlim([0, ref_tijd[-1]])
            ax.set_ylim([min(ref_pos)*1.1, max(ref_pos)*1.1])

            A_slider_ax  = fig.add_axes([0.1, 0.1, 0.65, 0.03])
            A_slider = Slider(A_slider_ax, '$A$', -3, 3, valinit=A)

            omega_slider_ax  = fig.add_axes([0.1, 0.15, 0.65, 0.03])
            omega_slider = Slider(omega_slider_ax, '$\omega$', .1*omega, 2*omega, valinit=omega)

            zeta_slider_ax = fig.add_axes([0.1, 0.2, 0.65, 0.03])
            zeta_slider = Slider(zeta_slider_ax, '$\zeta$', 0., 1/2**.5, valinit=zeta)

            phi_slider_ax  = fig.add_axes([0.1, 0.25, 0.65, 0.03])
            phi_slider = Slider(phi_slider_ax, '$\phi$', -np.pi,np.pi, valinit=phi)

            def sliders_on_changed(val):
                line.set_ydata(demp_func(ref_tijd,A_slider.val,omega_slider.val,zeta_slider.val,phi_slider.val))
                fig.canvas.draw_idle()
            A_slider.on_changed(sliders_on_changed)
            omega_slider.on_changed(sliders_on_changed)
            zeta_slider.on_changed(sliders_on_changed)
            phi_slider.on_changed(sliders_on_changed)



            plt.title(2*np.pi/omega)
            ax.plot(ref_tijd,ref_pos)
            for index in indices:
                ax.plot([ref_tijd[index],ref_tijd[index]],[0,ref_pos[index]],linestyle='--')

            # plt.plot(ref_tijd,demp_func(ref_tijd,A,omega,zeta,phi))
            plt.savefig('drytest 2910_verwerkt/dode slinger {}.png'.format(2*np.pi/omega))
            plt.clf()
        except OptimizeWarning:
            print('deze is pooped')



# dz = radar[1:] - radar[:-1]
# dt = tijd[1:] - tijd[:-1]
# v = dz/dt
# dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
# dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
# v = (np.array([0]+list(v))+np.array(list(v)+[0])) / 2

# totaalperiode = [0,0,0]
# lenperiode = [0,0,0]
# somperiode = 0
print(periode)
for i in range(len(periode)):
    plt.plot(i,periode[i],marker='o',markersize=5)
    # for j in range(len(mperiode[i])):
    # j=0
    # somperiode += mperiode[i]
    # totaalperiode[j]+=mperiode[i][j]
    # lenperiode[j]+=1
    # somperiode +=mperiode[i][j]

gem_periode = sum(periode) / len(periode)

# plt.plot(range(len(mperiode)),np.array(somperiode)/np.array(teller),linewidth=3)
# plt.plot(range(len(mperiode)),mperiode,linestyle='',marker='o',markersize=3)
plt.plot(range(len(periode)),[gem_periode]*len(periode))
plt.show()


demping = demping_correct
# print(demping)
for i in range(len(demping)):
    delta = 2*np.log(demping[i])
    demping[i] = delta / ((2*np.pi)**2+delta**2)**.5
for i in range(len(demping)):
    plt.plot(i,-demping[i],marker='o',markersize=5)
    # for j in range(len(mzeta[i])):
    #     totaaldemping[j]+=mzeta[i][j]
    #     lendemping[j]+=1
    #     somdemp += mzeta[i][j]
    #     teller += 1
plt.plot(range(len(demping)),[sum(demping)/len(demping)]*len(demping),linewidth=3)
plt.show()
gem_demping = sum(demping) / len(demping)




# totaaldemping = np.zeros(len(mperiode))
# lendemping = np.zeros(len(mperiode))
# mzeta = mdemping.copy()
# somdemp = 0
# teller = 0

# for i in range(len(mzeta)):
#     for j in range(len(mzeta[i])):

#         delta = 2*np.log(mdemping[i][j])
#         mzeta[i][j] = delta / ((2*np.pi)**2+delta**2)**.5
# for i in range(len(mzeta)):

#     plt.plot(range(len(mzeta[i])),mzeta[i],marker='o',markersize=5)
#     for j in range(len(mzeta[i])):
#         totaaldemping[j]+=mzeta[i][j]
#         lendemping[j]+=1
#         somdemp += mzeta[i][j]
#         teller += 1
# plt.plot([0,1,2],np.array(totaaldemping)/np.array(lendemping),linewidth=3)
# plt.show()
# gem_demping = somdemp / teller

omega0 = 2*np.pi/gem_periode/(1-gem_demping**2)**.5
print(omega0)
print(gem_demping)

print(demping_correct)