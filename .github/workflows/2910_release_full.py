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
posencoder = np.load('drytest 2910_verwerkt/posencoder.npy')
targetencoder = np.load('drytest 2910_verwerkt/targetencoder.npy')

# plt.plot(tijd,posencoder,linestyle='',marker='o',markersize=1)
# plt.plot(tijd,targetencoder,linestyle='',marker='o',markersize=1)
# plt.show()

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
    
    frequentie = rfft(ref_pos)
    frequentiebereik = np.linspace(0,.5/dt,len(frequentie))
    
    frequentie = abs(frequentie[1:])
    frequentiebereik = frequentiebereik[1:]
    
    T_p = 1 / frequentiebereik[list(frequentie).index(max(frequentie))]
    minT_p =  1 / frequentiebereik[list(frequentie).index(max(frequentie))+1]
    maxT_p =  1 / frequentiebereik[list(frequentie).index(max(frequentie))-1]

    print(minT_p,T_p,maxT_p)
    if max(ref_pos) + min(ref_pos) > 0:
        i = list(ref_pos).index(max(ref_pos))
        phi = 2*np.pi*(ref_tijd[0] - ref_tijd[i])/T_p - np.pi/2
    else:
        i = list(ref_pos).index(min(ref_pos))
        phi = 2*np.pi*(ref_tijd[0] - ref_tijd[i])/T_p - np.pi/2

    A_gok = ref_pos[i]/np.exp(-2*(ref_tijd[i]-ref_tijd[0])/T_p)/np.sin(2*np.pi/T_p * ref_tijd[i]+phi)
    omega_gok = 2*np.pi/T_p

    def demp_func(t,A,omega,demping,phi):
        return A*np.exp(-demping*omega*t)*np.sin((1-demping**2)*omega**(1/2)*t+phi)
    
    with warnings.catch_warnings():
        warnings.simplefilter("error", OptimizeWarning)
        try:
            [A,omega,demping,phi], cov = curve_fit(demp_func,ref_tijd,ref_pos,p0=[A_gok,omega_gok,.4,0],bounds=((-3,.5*omega_gok,0,-np.pi),(3,2*omega_gok,1/2**.5,np.pi)))
            
            fig = plt.figure()
            ax = fig.add_subplot(111)
            fig.subplots_adjust(bottom=0.35)
            [line] = ax.plot(ref_tijd, demp_func(ref_tijd,A,omega,demping,phi))

            ax.set_xlim([0, ref_tijd[-1]])
            ax.set_ylim([min(ref_pos)*1.1, max(ref_pos)*1.1])

            A_slider_ax  = fig.add_axes([0.1, 0.1, 0.65, 0.03])
            A_slider = Slider(A_slider_ax, '$A$', -3, 3, valinit=A)

            omega_slider_ax  = fig.add_axes([0.1, 0.15, 0.65, 0.03])
            omega_slider = Slider(omega_slider_ax, '$\omega$', .1*omega, 2*omega, valinit=omega)

            demping_slider_ax = fig.add_axes([0.1, 0.2, 0.65, 0.03])
            demping_slider = Slider(demping_slider_ax, '$\zeta$', 0., 1/2**.5, valinit=demping)

            phi_slider_ax  = fig.add_axes([0.1, 0.25, 0.65, 0.03])
            phi_slider = Slider(phi_slider_ax, '$\phi$', -np.pi,np.pi, valinit=phi)

            def sliders_on_changed(val):
                line.set_ydata(demp_func(ref_tijd,A_slider.val,omega_slider.val,demping_slider.val,phi_slider.val))
                fig.canvas.draw_idle()
            A_slider.on_changed(sliders_on_changed)
            omega_slider.on_changed(sliders_on_changed)
            demping_slider.on_changed(sliders_on_changed)
            phi_slider.on_changed(sliders_on_changed)



            # plt.title(2*np.pi/omega)
            ax.plot(ref_tijd,ref_pos)

            # plt.plot(ref_tijd,demp_func(ref_tijd,A,omega,demping,phi))
            plt.show()
        except OptimizeWarning:
            print('deze is pooped')



dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
v = dz/dt
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
v = (np.array([0]+list(v))+np.array(list(v)+[0])) / 2
