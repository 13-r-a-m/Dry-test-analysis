import matplotlib.pyplot as plt
import numpy as np
from modelParams import SymphonyParams as SP
import warnings
from matplotlib.collections import LineCollection
import csv
from scipy.optimize import curve_fit
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


tijd = np.load('drytest 0212_verwerkt/tijd.npy')

# deel = slice(int(round(len(tijd)*0.)),int(round(len(tijd)*0.36)))


tijd = (tijd-tijd[0]) / 1000

deel = slice(round(11820/max(tijd)*len(tijd)),round(12450/max(tijd)*len(tijd)))
tijd = tijd[deel]-tijd[deel][0]
level = np.load('drytest 0212_verwerkt/level.npy')[deel]

level -=sum(level)/len(level)
freqs = rfft(level)
plt.plot(np.arange(len(freqs))/(tijd[-1]-tijd[0]),abs(freqs))
plt.show()

deel2 = slice(round(125/max(tijd)*len(tijd)),round(145/max(tijd)*len(tijd)))
# deel2 = slice(0,-1)
tijd = tijd[deel2] - tijd[deel2][0]
level = level[deel2]
# helft = slice(0,round(len(tijd)/3))
radar = np.load('drytest 0212_verwerkt/radar.npy')[deel][deel2]
pfloater = np.load('drytest 0212_verwerkt/pfloater.npy')[deel][deel2]
pmem = np.load('drytest 0212_verwerkt/pmem1.npy')[deel][deel2]
encoder = np.load('drytest 0212_verwerkt/encoder.npy')[deel][deel2]            # %65530
pturb_spring = np.load('drytest 0212_verwerkt/pturbspring.npy')[deel][deel2]
pturb_mem = np.load('drytest 0212_verwerkt/pturbmem.npy')[deel][deel2]+.1-.005
pspring_gas = np.load('drytest 0212_verwerkt/pspring_gas.npy')[deel][deel2]
rpm = np.load('drytest 0212_verwerkt/rpm.npy')[deel][deel2]
power = np.load('drytest 0212_verwerkt/power.npy')[deel][deel2]
stroom = np.load('drytest 0212_verwerkt/stroom1.npy')[deel][deel2]*100
spanning = np.load('drytest 0212_verwerkt/spanning.npy')[deel][deel2]

dt = tijd[1:] - tijd[:-1]
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
dpdt = pmem[1:] - pmem[:-1]
dpdt = (np.array([0]+list(dpdt))+np.array(list(dpdt)+[0]))/2/dt
# dpdt = dpdt/dt
# dpdt = np.array(list(dpdt)+[0])/dt
v = radar[1:] - radar[:-1]
v = (np.array([0]+list(v))+np.array(list(v)+[0]))/2/dt
v = v/dt
# tijd_verschoven = tijd[:-1]+dt/2

# pmem_rescaled = pmem-sum(pmem)/len(pmem)

# def curve(X,a,b):
#     x1,x2 = X
#     return a*x1+b*x2
# x1 = pmem_rescaled
# x2 = dpdt
# X = (x1,x2)
# fit,cov = curve_fit(curve,X,radar,[.8,-.1])
# [a,b] = fit
# print(fit)


# # plt.plot(tijd,a*pmem_rescaled,label='pmem')
# # plt.plot(tijd,b*dpdt,label='dptdt')
# plt.plot(tijd,a*pmem_rescaled+b*dpdt,label='combo')
# plt.plot(tijd,radar,label='radar')
# plt.legend()
# plt.show()


# # plt.plot(tijd,(level - sum(level)/len(level))*25,label='level')
# plt.plot(tijd,radar)
# plt.plot(tijd,rpm/300,label='rpm')
# plt.plot(tijd_verschoven,-v*2,label='v')
# # plt.plot(tijd,rpm/300+v*2)
# # plt.plot(tijd,pspring_gas-sum(pspring_gas)/len(pspring_gas),label='druk')
# plt.legend()
# plt.show()


dlevel = level[1:]-level[:-1]
# # dlevel = np.array(list(dlevel)+[0])
# # dlevel = np.array(list(dlevel)[1:]+[0,0])
# # dlevel = np.array(list(dlevel)[2:]+[0,0,0])
dlevel = (np.array([0]+list(dlevel))+np.array(list(dlevel)+[0]))/2
# dlevel = np.array(list(dlevel)[2:]+[0,0])


# fig,ax = plt.subplots()
# lines = colored_line(dlevel[helft],rpm[helft], level[helft], ax, linewidth=2, cmap="viridis")
# fig.colorbar(lines)
# ax.set_xlim(1.1*min(dlevel),1.1*max(dlevel))
# ax.set_ylim(1.1*min(rpm),1.1*max(rpm))
# ax.set_title('Lek / luchthappen turbine')
# ax.set_xlabel('Verandering level per tijdstap m)')
# ax.set_ylabel('rpm')
# plt.show()


alpha = rpm[1:]-rpm[:-1]
alpha = np.array([alpha[0]]+list(alpha)) / 2 / dt / 60 * 2*np.pi


# def curve(X,a,b):
#     x1,x2 = X
#     return a*x1+b*1000*x2
# x1 = alpha
# x2 = rpm
# X = (x1,x2)
# fit,cov = curve_fit(curve,X,stroom,[1,0])
# [a,b] = fit
# print(fit)
# fig,ax = plt.subplots()
# lines = colored_line(stroom,a*alpha+b*1000*rpm, level, ax, linewidth=2, cmap="viridis")
# fig.colorbar(lines)
# ax.set_xlim(1.1*min(stroom),1.1*max(stroom))
# ax.set_ylim(2*min(alpha),2*max(alpha))
# # ax.set_ylim(-.1,.1)
# ax.set_title('Draaimoment?')
# ax.set_xlabel('stroom $[A]$')
# ax.set_ylabel('hoekversnelling $[rad/s^2]$')
# plt.show()

dP = pturb_spring-pturb_mem
stroom_geschaald = stroom - dP * 16.2059052 - rpm/40
def func(A,C):
    return C * A
fit = curve_fit(func,stroom_geschaald,alpha)[0]
print(fit)
fig,ax = plt.subplots()
lines = colored_line(stroom_geschaald,alpha, rpm, ax, linewidth=2, cmap="viridis")
plt.plot(np.linspace(min(stroom_geschaald),max(stroom_geschaald),1000),fit*np.linspace(min(stroom_geschaald),max(stroom_geschaald),1000))
fig.colorbar(lines)
ax.set_xlim(1.1*min(stroom_geschaald),1.1*max(stroom_geschaald))
ax.set_ylim(1.1*min(alpha),1.1*max(alpha))
ax.set_title('Draaimoment?')
ax.set_xlabel('stroom $[A]$')
ax.set_ylabel('hoekversnelling $[rad/s^2]$')
plt.show()



profieldiam = SP.profileDiam

def Oppervlak(z):
    index = round(z*1000)
    opp = np.pi/4*((profieldiam[index]-.034)**2-(SP.floaterInnerDiamUp-.034)**2)/2
    return opp

opp = []
for h in radar:
    opp.append(Oppervlak(h+2))
opp = np.array(opp)
F_totaal = -dP*opp*1e5

snelheid = np.gradient(radar,tijd)
versnelling = np.gradient(snelheid,tijd)
mass = SP.floaterMass
F_vaste_massa = mass*versnelling    # massa in en uit membraan wordt genegeerd: ~400kg / 2 * 2m/s^2 max=0.4kN<<F_vaste_massa
dP_massakracht = F_vaste_massa / 1e5 / opp

opp_floater = np.pi/4 * SP.floaterInnerDiamUp**2 - np.pi/8 *(SP.floaterInnerDiamUp**2-SP.membrameInnerDiam**2)
dP_floater = (pfloater+1)*opp_floater / opp - 1



# plt.plot(tijd,F_vaste_massa,label='vaste mass')
# plt.plot(tijd,F_totaal,label='excitatie')
# plt.legend()
# plt.show()

level-= sum(level)/len(level)
plt.plot(tijd,radar*2.5, marker='o',markersize=2,label='Radar $[4*10^{-1} m]$')
# plt.plot(tijd,dP_massakracht , marker='o',markersize=2,label='massakracht omgezet in druk')
plt.plot(tijd,pturb_mem-sum(pturb_mem)/len(pturb_mem), marker='o',markersize=2,label='Pressure turbine-membrane $[bar]$')
# plt.plot(tijd,pturb_spring-7, marker='o',markersize=2,label='druk turbine - spring tank')
# plt.plot(tijd,pturb_spring-pturb_mem,marker='o',markersize=2,label='druk over turbine')
# plt.plot(tijd,pspring_gas-7,marker='o',markersize=2,label='druk sping tank gas')
plt.plot(tijd,-rpm/400,marker='o',markersize=2,label='Turbine $\omega \ [4*10^2 rpm]$')
plt.plot(tijd,pmem-sum(pmem)/len(pmem),marker='o',markersize=2,label='Pressure membrane $[bar]$')
plt.plot(tijd,level*25,marker='o',markersize=2,label='Spring tank level $[4*10^{-2} m]$')

plt.grid()
plt.xlabel('Time [s]')
plt.ylabel('Rescaled varation of sensor measurements')
plt.legend()
plt.show()




plt.plot(tijd,F_vaste_massa*snelheid/1000,label='vaste massa')
plt.plot(tijd,F_totaal*snelheid/1000,label='output door druk')
plt.plot(tijd,power*100,label='output door turbine')
plt.xlabel('tijd in s')
plt.ylabel('kracht in kN')
plt.legend()
plt.show()



data = np.array([tijd,radar,F_vaste_massa,pturb_mem,pturb_spring,pturb_spring-pturb_mem,stroom,spanning,pspring_gas,dP_floater,level,rpm,dP_massakracht,pmem]).transpose()
fieldnames = ['tijd [s]','radarpositie[m]','massakracht[N]','Membraandruk bij turbine [bar(g)]','Springtankdruk bij turbine [bar(g)]','Druk over turbine [bar]','stroom [A]','spanning [V]','Springtank gasdruk [bar(g)]','Floatertank druk - alsof in membraan [bar(g)]','level [m^3]','toerental [rpm]','massakracht omgezet in druk [bar]','membraandruk [bar(g)]']

with open('meting tijdsdomein.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile,delimiter='\t')
    writer.writerow(fieldnames)
    writer.writerows(data)



# dz = radar[1:] - radar[:-1]
# dt = tijd[1:] - tijd[:-1]
# dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
# dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
# v = 1000*dz/dt


# profieldiam = SP.profileDiam
# # offset = np.pi/4*(profieldiam[2000]-profieldiam) + 0.06
# z = np.linspace(0,4,4001)#+offset
# drukval = pturb_mem - pturb_spring + 0.089

# rpm = encoder[1:] - encoder[:-1]
# zaag_af = np.where(rpm>3e4,-65530,0)
# zaag_op = np.where(rpm<-3e4,65530,0)
# rpm += zaag_af + zaag_op
# rpm *= 60/.2/ 65530
# rpm = (np.array([0]+list(rpm))+np.array(list(rpm)+[0]))/2
# drpm = rpm[1:] - rpm[:-1]
# drpm = (np.array([0]+list(drpm))+np.array(list(drpm)+[0]))/2




# i = [i for i,val in enumerate(rpm) if val!=0.]
# rpm = rpm[i]
# drukval = drukval[i]
# drpm = drpm[i]
# v=v[i]
# # dz = dz[i]

# # i = [i for i,val in enumerate(drpm) if abs(val)>5]
# # rpm = rpm[i]
# # drukval = drukval[i]

# pmem -= .6  #ongeveer .6bar waterkolom
# pfloater += 1
# radar += 2

# verlies = -drukval*rpm*1e5*10.6/1e3/60
# up = [i for i,val in enumerate(drukval) if val > 0]
# down = [i for i,val in enumerate(drukval) if val < 0]
# drukval = np.concatenate([drukval[up],-drukval[down]])
# verlies = np.concatenate([verlies[up],verlies[down]])
# fit = np.polyfit(drukval,verlies/drukval,2)



# up = [i for i,val in enumerate(verlies) if val>0]
# down = [i for i,val in enumerate(verlies) if val<0]
# verlies_dubbelgevouwen = np.concatenate([verlies[up],-verlies[down]])
# drukval_dubbelgevouwen = np.concatenate([drukval[up],drukval[down]])
# plt.plot(drukval,verlies,linestyle='',marker='o',markersize=2)
# plt.title('Turbine loss')
# # plt.legend()
# plt.ylabel('Power loss [W]')
# plt.xlabel('Pressure drop over the turbine [bar]')
# plt.show()


# lek = drukval*np.poly1d([-49.92674769,349.01214219,28.82145074])(drukval)
# # lek = drukval*np.poly1d(fit)(drukval)
# verlies -= lek

# up = [i for i,val in enumerate(verlies) if val>0]
# down = [i for i,val in enumerate(verlies) if val<0]
# verlies_dubbelgevouwen = np.concatenate([verlies[up],-verlies[down]])
# drukval_dubbelgevouwen = np.concatenate([drukval[up],drukval[down]])


# a = 50
# b = a
# zestig = .6*len(verlies_dubbelgevouwen)
# for iteratie in range(100):
#     sigma = b*drukval_dubbelgevouwen**2
#     waardes = list(np.where(verlies_dubbelgevouwen<sigma,1,0)).count(1)
#     a/=2
#     if waardes>zestig:
#         b-=a
#     if waardes<zestig:
#         b+=a



# # fit = np.polyfit(drukval,lek/drukval,2)
# drukval_array = np.linspace(0.1,max(drukval),1000)


# fig, ax = plt.subplots()
# plt.plot(drukval, verlies, linestyle='',marker='o',markersize=1,label='Measured power loss minus leak and static friction')
# plt.plot(drukval_array,-b*drukval_array**2,color='purple')
# plt.plot(drukval_array,b*drukval_array**2,color='purple')
# ax.fill_between(drukval_array, -b*drukval_array**2, b*drukval_array**2, color='purple',alpha=0.2,label='$1\sigma$ quadratic noise')
# plt.ylim(-1750,1750)
# # ax.plot(x, y, 'o', color='tab:brown')


# # plt.plot(drukval,verlies,linestyle='',marker='o',markersize=2,label='Measured leak [W] for static angular turbine velocity [rpm]')
# # plt.plot(drukval_array,b*drukval_array**2,label='$\sigma$',color='orange')
# # plt.plot(drukval_array,-b*drukval_array**2,color='orange')
# plt.title('Dynamic turbine power loss')
# plt.legend()
# plt.ylabel('Dynamic power loss [W]')
# plt.xlabel('Absolute pressure drop over the turbine [bar]')
# plt.show()

# genormalizeerd = verlies / (b*drukval**2)
# i = [i for i,val in enumerate(genormalizeerd) if abs(val)<4]
# genormalizeerd = genormalizeerd[i]
# v = v[i]
# rpm = rpm[i]
# i = [i for i,val in enumerate(v) if val!=0.]
# genormalizeerd = genormalizeerd[i]
# v = v[i]
# rpm = rpm[i]

# v = np.sort(abs(v))
# rpm = np.sort(abs(rpm))
# genormalizeerd = np.sort(genormalizeerd+.151)

# # genormalizeerd = np.sort(genormalizeerd +.34)
# # pakketje = np.floor(len(genormalizeerd)/100)

# # for i in range(100):
# #     deel = slice(i*pakketje,(i+1)*pakketje)
# sigma = np.linspace(-2,3,401)


# x = np.linspace(-2, 3, 1000)
# y = 220*np.exp(-x**2 / (2*.02))
# plt.plot(x, y, 'g--', label='normal distribution')
# plt.plot(sigma,np.histogram(genormalizeerd,401,(-2,3))[0],label='normalized power loss minus leak and friction')
# # sns.histplot(genormalizeerd, kde=True, bins=40, color='purple',label='normalized power loss minus leak and friction')
# plt.legend()
# plt.title('Noise and dynamic power loss')
# plt.xlabel('$\sigma$')
# plt.ylabel('Count')
# plt.grid()
# plt.show()

# plt.plot(sigma,np.histogram(genormalizeerd,401,(-2,3))[0],label='measured power loss')
# plt.plot(sigma,220*np.exp(-sigma**2 / (2*.02)),label='noise')
# plt.plot(sigma,np.histogram(genormalizeerd,401,(-2,3))[0]-220*np.exp(-sigma**2 / (2*.02)),label='denoised power loss')
# # plt.plot(sigma[17:],np.histogram(v[17:],401,(-4,4))[0][:-17],label='snelheid')
# plt.title('Denoised dynamic power loss')
# plt.xlabel('$\sigma$')
# plt.ylabel('Count')
# plt.show()

# verschil = np.histogram(genormalizeerd,401,(-4,4))[0]-220*np.exp(-sigma**2 / (2*.02))
# v_gefilterd = v[-len(verschil):-100]
# rpm_gefilterd = rpm[-len(verschil):-100]
# genormalizeerd_gefilter = genormalizeerd[-len(verschil):-100]

# fit = np.polyfit(v_gefilterd,genormalizeerd_gefilter,1)
# v_fit = np.linspace(min(v_gefilterd),max(v_gefilterd),1000)
# verlies_dynamisch = np.poly1d(fit)(v_fit)

# plt.title('Dynamic loss')
# plt.plot(v_gefilterd,genormalizeerd_gefilter,linestyle='',marker='o',markersize=2,label='Denoised dynamic loss measurement')
# plt.plot(v_fit,verlies_dynamisch,label='P[W] = {}*v[m/s]'.format(round(fit[0])))
# plt.xlabel('Absolute velocity [m/s]')
# plt.ylabel('Dynamic turbine loss [W]')
# plt.legend()
# plt.show()