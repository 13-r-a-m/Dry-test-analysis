import matplotlib.pyplot as plt
import numpy as np
from modelParams import SymphonyParams as SP
import warnings
from matplotlib.collections import LineCollection
from scipy.optimize import minimize
profiel = SP.profileDiam

tijd = np.load('drytest 20251202_verwerkt/tijd.npy')
tijd = (tijd-tijd[0]) / 1000
deel = slice(round(11820/max(tijd)*len(tijd)),round(12350/max(tijd)*len(tijd)))
tijd = tijd[deel]
radar = np.load('drytest 20251202_verwerkt/radar.npy')[deel] + 2
pfloater = np.load('drytest 20251202_verwerkt/pfloater.npy')[deel] + 1
pmem = np.load('drytest 20251202_verwerkt/pmem1.npy')[deel]
encoder = np.load('drytest 20251202_verwerkt/encoder.npy')[deel]            # %65535
pturb_spring = np.load('drytest 20251202_verwerkt/pturbspring.npy')[deel]   
pturb_mem = np.load('drytest 20251202_verwerkt/pturbmem.npy')[deel]+.1-.005 
pspring_gas = np.load('drytest 20251202_verwerkt/pspring_gas.npy')[deel]
temp_spring = np.load('drytest 20251202_verwerkt/tempspring.npy')[deel] + 273.15
rpm = np.load('drytest 20251202_verwerkt/rpm.npy')[deel]
level = np.load('drytest 20251202_verwerkt/level.npy')[deel]
power = np.load('drytest 20251202_verwerkt/power.npy')[deel]
def toIndex(hoogte):
    return int(round(hoogte*1000))

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

plt.plot(tijd,pmem,label='membrane')
plt.plot(tijd,pturb_mem,label='turbine - membrane')
plt.plot(tijd,pturb_spring,label='turbine - SpT')
plt.plot(tijd,pspring_gas,label='SpT')
plt.xlabel('Time [s]')
plt.ylabel('Pressure at sensor [bar(g)]')
plt.grid()
plt.legend()
plt.show()



z,dz = np.linspace(-2,2,4001,retstep=True)
snelheid = np.gradient(radar,tijd)
bewegend = [i for i,val in enumerate(snelheid) if abs(val)>.4]
aansnijspot = z + np.pi/4*(profiel[2000]-profiel)
dz_aansnij = aansnijspot[1:] - aansnijspot[:-1]
dz_aansnij = (np.array([dz_aansnij[0]]+list(dz_aansnij))+np.array(list(dz_aansnij)+[dz_aansnij[-1]]))/2
V_cumulatief = 0
V_profiel = []
for hoogte in range(len(profiel)):
    dV = np.pi/8*((profiel[hoogte]-0.034)**2-(1.6826-0.034)**2)*dz_aansnij[hoogte]
    V_cumulatief += dV
    V_profiel.append(V_cumulatief)
dVdz_per_z = np.gradient(V_profiel,z)
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
pfloater = np.concatenate([pfloater[2:],[pfloater[-1],pfloater[-1]]])
opp_floater = 2.173912626586611
oppervlak_deksel = np.pi/4*SP.floaterInnerDiamUp**2
oppervlak_core = np.pi/4*SP.membrameInnerDiam**2
V0 = 0.8 + oppervlak_deksel * 1.83 + 1.88 + (oppervlak_deksel - oppervlak_core) * 2.51
V_floater = V0 + radar*opp_floater
radar_gem = sum(radar) / len(radar)
p_floater_gem = sum(pfloater) / len(pfloater)
# V_floater_gem = sum(V_floater) / len(V_floater)
V_floater_gem = V0 + radar_gem*opp_floater
NRT = p_floater_gem * V_floater_gem**(1.12)
V_floater = (NRT / pfloater)**(1/1.12)
hoogte_floater = (V_floater - V0)/opp_floater

fit_floater = np.polyfit(hoogte_floater,radar,7)
hoogte_floater = np.polyval(fit_floater,hoogte_floater)

filter_floater = [i for i,val in enumerate(hoogte_floater-radar) if val>-.3 and val<.2]

print('Radar vs floater tank pressure')
cov_floater = np.cov(radar,hoogte_floater)
print(cov_floater[0,1])

fig,ax = plt.subplots()
lines = colored_line(radar,hoogte_floater, snelheid, ax, linewidth=2, cmap="viridis")
fig.colorbar(lines,label='velocity [m/s]')
ax.set_title('Radar vs floater tank pressure')
ax.set_xlabel('Position derived from radar sensor [m]')
ax.set_ylabel('Position derived from FT pressure sensor [m]')
ax.set_xlim(.9*min(radar),1.1*max(radar))
ax.set_ylim(.9*min(hoogte_floater),1.1*max(hoogte_floater))
plt.show()
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
rpm_verschoven_0 = np.concatenate([rpm[1:],[rpm[0]]])
rpm_verschoven_1 = rpm
rpm_verschoven_2 = np.concatenate([[rpm[0]],rpm[:-1]])

a=0
# for b in range(11):
# for a in range(21):
if a<11:
    rpm_verschoven = a/10*rpm_verschoven_1 + (1-a/10)*rpm_verschoven_0
else:
    rpm_verschoven = (a-10)/10*rpm_verschoven_2 + (1-(a-10)/10)*rpm_verschoven_1
rpm_integraal = []
for toerental in rpm_verschoven:
    if rpm_integraal:
        rpm_integraal.append(rpm_integraal[-1]-toerental)
    else:
        rpm_integraal.append(-toerental)

lowpass = np.polyfit(range(len(rpm_integraal)),rpm_integraal,4)
rpm_integraal -=np.polyval(lowpass,range(len(rpm_integraal)))

dVdz = []
for hoogte in radar:
    dVdz.append(dVdz_per_z[toIndex(hoogte)])
dVdz = np.array(dVdz)

rpm_integraal = radar[0] + rpm_integraal * 0.2 / 60 * 10.6/1e3 / dVdz

omhoog = [i for i,val in enumerate(snelheid) if val > 0.3]
omlaag = [i for i,val in enumerate(snelheid) if val < -0.3]
hysterese = np.zeros(len(rpm_integraal))
hysterese[omhoog] = -1
hysterese[omlaag] = 1
i0 = 0
for i in range(len(rpm_integraal)-1):
    if hysterese[i] == 0 and hysterese[i+1]!=0:
        hysterese[i0:i] = np.linspace(hysterese[i0],hysterese[i+1],i-i0)
    if hysterese[i] !=0 and hysterese[i+1] == 0:
        i0 = i
rpm_integraal += .12*hysterese


fit_rpm = np.polyfit(rpm_integraal,radar,3)
hoogte_rpm = np.polyval(fit_rpm,rpm_integraal)

print('Radar vs encoder')
cov_rpm = np.cov(radar,hoogte_rpm)
print(cov_rpm[0,1])

# hoogte_rpm = rpm_integraal

fig,ax = plt.subplots()
lines = colored_line(radar,hoogte_rpm, snelheid, ax, linewidth=2, cmap="viridis")
fig.colorbar(lines,label='velocity [m/s]')
# ax.set_title(b)
ax.set_title('Radar vs encoder')
ax.set_xlabel('Position derived from radar sensor [m]')
ax.set_ylabel('Position derived from turbine encoder [m]')
ax.set_xlim(.9*min(radar),1.1*max(radar))
ax.set_ylim(.9*min(hoogte_rpm),1.1*max(hoogte_rpm))
plt.show()
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
radar_level = radar
filter_level = [i for i,val in enumerate(level) if val < 0.965]
level = level[filter_level]
radar_level = radar[filter_level]
snelheid_level = np.gradient(radar_level,tijd[filter_level])


i = [i for i,val in enumerate(radar_level) if abs(val-2)<0.003]
level0 = sum(level[i]) / len(level[i])
V_profiel_level = V_profiel[2000] - level + level0
hoogte_level = np.interp(V_profiel_level,V_profiel,2+z)

print('Radar vs spring tank level')
cov_level = np.cov(radar_level,hoogte_level)
print(cov_level[0,1])

fig,ax = plt.subplots()
lines = colored_line(radar_level,hoogte_level, snelheid_level, ax, linewidth=2, cmap="viridis")
fig.colorbar(lines,label='velocity [m/s]')
ax.set_title('Radar vs spring tank level')
ax.set_xlabel('Position derived from radar sensor [m]')
ax.set_ylabel('Position derived from SpT level sensor [m]')
ax.set_xlim(.9*min(radar_level),1.1*max(radar_level))
ax.set_ylim(.9*min(hoogte_level),1.1*max(hoogte_level))
plt.show()
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
# pmem = np.concatenate([[pmem[0],pmem[0]],pmem[:-2]])

pmem = pmem[bewegend]
snelheid_mem = snelheid[bewegend]
radar_mem = radar[bewegend]

omhoog = [i for i,val in enumerate(snelheid_mem) if val > 0.3]
omlaag = [i for i,val in enumerate(snelheid_mem) if val < -0.3]
pmem[omhoog]-=.4
pmem[omlaag]+=.4

# hysterese = np.zeros(len(pmem))
# hysterese[omhoog] = -1
# hysterese[omlaag] = 1
# i0 = 0
# for i in range(len(pmem)-1):
#     if hysterese[i] == 0 and hysterese[i+1]!=0:
#         hysterese[i0:i] = np.linspace(hysterese[i0],hysterese[i+1],i-i0)
#     if hysterese[i] !=0 and hysterese[i+1] == 0:
#         i0 = i
# # pmem += 0.3*hysterese




fit_pmem = np.polyfit(pmem,radar_mem,7)
hoogte_mem = np.polyval(fit_pmem,pmem)

print('Radar vs membrane pressure')
cov_pmem = np.cov(radar_mem,pmem)
print(cov_pmem[0,1])

fig,ax = plt.subplots()
lines = colored_line(radar_mem,pmem, snelheid_mem, ax, linewidth=2, cmap="viridis")
fig.colorbar(lines,label='velocity [m/s]')
ax.set_title('Radar vs membrane pressure')
ax.set_xlabel('Position derived from radar sensor [m]')
ax.set_ylabel('Position derived from membrane pressure sensor [m]')
ax.set_xlim(.9*min(radar_mem),1.1*max(radar_mem))
ax.set_ylim(.9*min(pmem),1.1*max(pmem))
plt.show()
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
pspring_gas = np.concatenate([[pspring_gas[0]],pspring_gas[:-1]])

omhoog = [i for i,val in enumerate(snelheid) if val > 0.3]
omlaag = [i for i,val in enumerate(snelheid) if val < -0.3]
hysterese = np.zeros(len(pspring_gas))
hysterese[omhoog] = -1
hysterese[omlaag] = 1
i0 = 0
for i in range(len(pmem)-1):
    if hysterese[i] == 0 and hysterese[i+1]!=0:
        hysterese[i0:i] = np.linspace(hysterese[i0],hysterese[i+1],i-i0)
    if hysterese[i] !=0 and hysterese[i+1] == 0:
        i0 = i
pspring_gas -= 0.12*hysterese
pspring_gas/= temp_spring

fit_pspring = np.polyfit(pspring_gas,radar,7)
hoogte_spring = np.polyval(fit_pspring,pspring_gas)

cov_spring = np.cov(radar,hoogte_spring)
print('Radar vs spring tank pressure')
print(cov_spring[0,1])

fig,ax = plt.subplots()
lines = colored_line(radar,hoogte_spring, snelheid, ax, linewidth=2, cmap="viridis")
fig.colorbar(lines,label='velocity [m/s]')
ax.set_title('Radar vs spring tank pressure')
ax.set_xlabel('Position derived from radar sensor [m]')
ax.set_ylabel('Position derived from SpT pressure sensor [m]')
ax.set_xlim(.9*min(radar),1.1*max(radar))
ax.set_ylim(.9*min(hoogte_spring),1.1*max(hoogte_spring))
plt.show()
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------



def penalty(coef):
    hoogte = coef[1]*hoogte_rpm+ coef[3]*hoogte_spring 
    hoogte[filter_floater] += coef[0]*hoogte_floater[filter_floater]
    hoogte[filter_level] += coef[2]*hoogte_level
    return sum(abs(radar - hoogte))
coefs = minimize(penalty,[1,1,1,1],bounds=((0,None),(0,None),(0,None),(0,None)))
print(coefs.x)
def som_nemen(coef):
    hoogte = coef[1]*hoogte_rpm + coef[3]*hoogte_spring 
    hoogte[filter_floater] += coef[0]*hoogte_floater[filter_floater]
    hoogte[filter_level] += coef[2]*hoogte_level
    return hoogte

hoogte = som_nemen(coefs.x)

print('som')
cov_som = np.cov(radar,hoogte)
print(cov_som[0,1])

fig,ax = plt.subplots()
lines = colored_line(radar,hoogte,snelheid, ax, linewidth=2, cmap="viridis")
fig.colorbar(lines,label='velocity [m/s]')
ax.set_title('Radar vs combination of sensors')
ax.set_xlabel('Position derived from radar sensor [m]')
ax.set_ylabel('Position derived from sensor selection [m]')
ax.set_xlim(.9*min(radar),1.1*max(radar))
ax.set_ylim(.9*min(hoogte),1.1*max(hoogte))
plt.show()




metingen = [radar,hoogte_rpm,hoogte_spring,hoogte_floater,hoogte_level,hoogte]
afstandentabel = np.zeros((6,6))
for i in range(6):
    for j in range(6):
        print(i,j)
        if i != j:
            if (i==3 and j!=4) or (j==3 and i!=4):
                verschil = metingen[i][filter_floater]-metingen[j][filter_floater]
                verschil /= len(filter_floater)
                afstandentabel[i,j] = sum(verschil**2)
            elif i==4 and j != 3:
                verschil = metingen[i]-metingen[j][filter_level]
                verschil /= len(filter_level)
                afstandentabel[i,j] = sum(verschil**2)
            elif j==4 and i != 3:
                verschil = metingen[i][filter_level]-metingen[j]
                verschil /= len(filter_level)
                afstandentabel[i,j] = sum(verschil**2)
            elif i==3 and j==4:
                filter_3 = [val for i,val in enumerate(filter_level) if val in filter_floater]
                filter_4 = [i for i,val in enumerate(filter_level) if val in filter_floater]
                verschil = metingen[i][filter_3]-metingen[j][filter_4]
                verschil /= len(filter_3)
                afstandentabel[i,j] = sum(verschil**2)
            elif i==4 and j==3:
                filter_3 = [val for i,val in enumerate(filter_level) if val in filter_floater]
                filter_4 = [i for i,val in enumerate(filter_level) if val in filter_floater]
                verschil = metingen[i][filter_4]-metingen[j][filter_3]
                verschil /= len(filter_4)
                afstandentabel[i,j] = sum(verschil**2)
            else:
                verschil = metingen[i]-metingen[j]
                verschil /= len(metingen[i])
                afstandentabel[i,j] = sum(verschil**2)

print(afstandentabel)
fig,ax=plt.subplots()
P = ax.imshow(afstandentabel,origin='lower',cmap='Blues',aspect='auto',norm='linear')
ax.set_yticks([0,1,2,3,4,5])
ax.set_yticklabels(['$Radar$','$RPM$','$P_{SpT}$','$P_{FT}$','$Level_{SpT}$','$combination$'])
ax.set_xticks([0,1,2,3,4,5])
ax.set_xticklabels(['$Radar$','$RPM$','$P_{SpT}$','$P_{FT}$','$Level_{SpT}$','$combination$'])
cb = fig.colorbar(P)
cb.set_label('Rms []')
ax.set_title('Root mean square between measurements')
plt.show()
