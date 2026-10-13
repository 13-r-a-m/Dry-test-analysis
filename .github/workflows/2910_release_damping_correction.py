import matplotlib.pyplot as plt
from matplotlib import cm, colors
import numpy as np
from modelParams import SymphonyParams as SP
from scipy.optimize import curve_fit


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
p_mem = np.load('drytest 2910_verwerkt/pmem1.npy')

rpm = np.load('drytest 2910_verwerkt/rpm.npy')
Massa = SP.floaterMass

# plt.plot(tijd,stroom*spanning/10)
# plt.plot(tijd,power*100)
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


mperiode = []
mdemping = []
mcolor = []
mcolor_alt = []

for stuk in tijdsloten:
    periode = []
    demping = []
    color = []
    color_alt = []

    tussenstuk = slice(toIndex(stuk[0])+30,toIndex(stuk[1]))
    if len(posencoder[tussenstuk]) % 2:
        tussenstuk = slice(toIndex(stuk[0]),toIndex(stuk[1])+1)
    posencoder[tussenstuk] -= posencoder[tussenstuk][-1]
    dt = (tijd[tussenstuk][-1] - tijd[tussenstuk][0]) / len(tijd[tussenstuk])
    # ref_pos = np.concatenate([posencoder[tussenstuk],np.zeros(3000)])
    # ref_tijd = np.concatenate([tijd[tussenstuk],np.linspace(tijd[tussenstuk][-1]+dt,tijd[tussenstuk][-1]+3000*dt,3000)])-tijd[tussenstuk][0]
    ref_pos = posencoder[tussenstuk]
    amplitude = max(abs(ref_pos))
    ref_tijd = tijd[tussenstuk]-tijd[tussenstuk][0]
    ref_hoogte = radar[tussenstuk] - radar[tussenstuk][-1]
    ref_power = power[tussenstuk]
    ref_v = snelheid[tussenstuk]
    ref_I = stroom[tussenstuk]
    ref_rpm = rpm[tussenstuk]


    # ref_dp_turb *= amplitude /  max(abs(ref_dp_turb))
    # ref_dp_buiten *= amplitude / max(abs(ref_dp_buiten))
    # ref_I *= amplitude /  max(abs(ref_I))
    # ref_rpm *= amplitude /  max(abs(ref_rpm))

    if max(ref_pos) + min(ref_pos) < 0:
        ref_pos *= -1

    index = [i for i,val in enumerate(ref_pos) if val == max(ref_pos)][0]
    zoeken = -1
    jndex = 1
    if index:
        indices = [index]
    else:
        indices = []

    while jndex != 0:
        nieuwe_hoogte = max(zoeken*ref_pos[index:])
        jndex = [j for j,val in enumerate(ref_pos[index:]) if zoeken*val == nieuwe_hoogte][0]
        if jndex:
            indices.append(index+jndex)

        index+=jndex
        zoeken *= -1

    # plt.plot(ref_tijd,ref_pos,label='Turbine position [m]')
    # plt.plot(ref_tijd,ref_hoogte,label='Radar [m]')
    # plt.plot(ref_tijd,ref_I,label='Current [A]')
    # plt.plot(ref_tijd,ref_rpm,label= '$\omega / \omega _{max}$ [ ]')
    # plt.plot(ref_tijd[indices],ref_pos[indices],linestyle='',marker='o')
    # plt.grid()
    # plt.title('Example of a release')
    # plt.xlabel('Time [s]')
    # plt.legend()
    # plt.show()

    i0 = indices[0]
    t0 = ref_tijd[i0]
    z0 = ref_pos[i0]
    
    for i in range(len(indices)-1):
        i1 = indices[i+1]
        t1 = ref_tijd[i1]
        z1 = ref_pos[i1]
        T = (t1 - t0) * 2
        D = -z0/z1
        delta = 2*np.log(D)
        D = delta / ((2*np.pi)**2+delta**2)**.5
        if periode:
            gem_periode = sum(periode) / len(periode)
            if gem_periode * .9<T<gem_periode*1.1 and D<.4:

                v = max(max(ref_rpm[i0:i1]),max(-ref_rpm[i0:i1]))

                periode.append(T)
                demping.append(D)
                color.append(p_mem[tussenstuk][-1])
                color_alt.append(v)
        elif D<.4:

            v = max(max(ref_rpm[i0:i1]),max(-ref_rpm[i0:i1]))
            print(v)
            periode.append(T)
            demping.append(D)
            color.append(p_mem[tussenstuk][-1])
            color_alt.append(v)

        t0 = t1
        z0 = z1
        i0 = i1
    
    mperiode.append(periode)
    mdemping.append(demping)
    mcolor.append(color)
    mcolor_alt.append(color_alt)


# mcolor = mcolor_alt
maxcolor = 0
mincolor = 100
for i in range(len(mcolor)):
    if mcolor[i]:
        if max(mcolor[i])>maxcolor:
            maxcolor = max(mcolor[i])
        if min(mcolor[i])<mincolor:
            mincolor = min(mcolor[i])
cmap = cm.get_cmap('plasma')
# norm = colors.Normalize(0,maxcolor)
norm = colors.Normalize(mincolor,maxcolor)



fig,ax=plt.subplots()
for i in range(len(mperiode)):
    ax.plot(np.arange(len(mperiode[i]))+1.5,mperiode[i],color='grey')
    for j in range(len(mperiode[i])):
        if mperiode[i][j]:
            ax.plot(j+1.5,mperiode[i][j],color=cmap(norm(mcolor[i][j])),marker='o',markersize=5)
fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap),ax=ax,label='Max rpm between two extrema')
ax.set_title('Periods measured between two extrema during release')
ax.set_xticks(range(1,5))
ax.set_xlabel('n-th extremum')
ax.set_ylabel('Period $T \ [s]$')
plt.show()

fig,ax=plt.subplots()
for i in range(len(mdemping)):
    ax.plot(np.arange(len(mdemping[i]))+1.5,mdemping[i],color='grey')
    for j in range(len(mdemping[i])):
        if mdemping[i][j]:
            ax.plot(j+1.5,mdemping[i][j],color=cmap(norm(mcolor[i][j])),marker='o',markersize=5)
fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap),ax=ax,label='Max rpm between two extrema')
ax.set_title('Damping measured between two extrema during release')
ax.set_xticks(range(1,5))
ax.set_xlabel('n-th extremum')
ax.set_ylabel('Damping $\zeta \ [kg/s]$')
plt.show()


gem_periode = np.concatenate(mperiode)
gem_periode = sum(gem_periode) / len(gem_periode)
print(gem_periode)

gem_demping = np.concatenate(mdemping)
gem_demping = sum(gem_demping) / len(gem_demping)
print(gem_demping)

print('w0={}'.format(2*np.pi/gem_periode/(1-gem_demping**2)**.5))



for i in range(len(mperiode)):
    for j in range(len(mperiode[i])):
        plt.plot(mcolor[i][j],mperiode[i][j],marker='o',markersize=5,color='r')
plt.yticks(np.linspace(3.6,5.6,6))
plt.grid()
plt.xlabel('Maximum rpm between two extrema [rpm]')
plt.ylabel('Period derived from time between two extrema [s]')

plt.show()


for i in range(len(mdemping)):
    for j in range(len(mdemping[i])):
        plt.plot(mcolor[i][j],mdemping[i][j],marker='o',markersize=5,color='g')
plt.grid()
plt.xlabel('Maximum turbine rpm between two extrema [rpm]')
plt.ylabel('Damping $\zeta \ [kg/s]$')
plt.show()