from modelParams import SymphonyParams as SP
from modelParams import GeneralParams as GP
from modelParams import ControlParams as CP
import numpy as np
import matplotlib.pyplot as plt
import warnings
from matplotlib.collections import LineCollection



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
tijd = (tijd-tijd[0]) / 1000
deel = slice(round(11820/max(tijd)*len(tijd)),round(12350/max(tijd)*len(tijd)))
tijd = tijd[deel]
radar = np.load('drytest 0212_verwerkt/radar.npy')[deel]
pfloater = np.load('drytest 0212_verwerkt/pfloater.npy')[deel] + 1
pspring_gas = np.load('drytest 0212_verwerkt/pspring_gas.npy')[deel]+1
pturb_spring = np.load('drytest 0212_verwerkt/pturbspring.npy')[deel]
pturb_mem = np.load('drytest 0212_verwerkt/pturbmem.npy')[deel]
stroom = np.load('drytest 0212_verwerkt/stroom1.npy')[deel]*4
rpm = np.load('drytest 0212_verwerkt/rpm.npy')[deel]
pmem = np.load('drytest 0212_verwerkt/pmem1.npy')[deel]


pspring_gas -= sum(pspring_gas) / len(pspring_gas)
pmem-= sum(pmem) / len(pmem)
dp_far = pspring_gas - pmem
pturb_mem -= sum(pturb_mem)/ len(pturb_mem)
pturb_spring -= sum(pturb_spring) / len(pturb_spring)
dp_close = pturb_spring - pturb_mem



# plt.plot(tijd,pturb_mem,label='mem')
# plt.plot(tijd,pturb_spring,label='spring')
plt.plot(tijd,radar,label='radar')
# plt.plot(tijd,stroom,label='stroom')
plt.plot(tijd,pspring_gas,label='spring')
plt.plot(tijd,pmem,label='mem')
plt.plot(tijd,rpm/300,label='rpm')
plt.plot([tijd[0],tijd[-1]],[0,0],linestyle='--')
plt.legend()
plt.show()



dt = tijd[1:] - tijd[:-1]
# dt = (np.array([dt[0]]+list(dt))+np.array(list(dt)+[dt[-1]])) / 2
dt = np.array([dt[0]]+list(dt))

dp = pspring_gas[1:] - pspring_gas[:-1]
# dp = (np.array([dp[0]]+list(dp))+np.array(list(dp)+[dp[-1]])) / 2
dp = np.array([dp[0]]+list(dp))

dpdt = dp/dt

alpha = rpm[1:] - rpm[:-1]
# alpha = (np.array([alpha[0]]+list(alpha))+np.array(list(alpha)+[alpha[-1]])) / 2
alpha = np.array([alpha[0]]+list(alpha))

alpha = alpha / dt

dz = radar[1:] - radar[:-1]
dz = np.array([radar[0]]+list(dz))

v = dz/dt

# dpdt += alpha/2000

fig,ax = plt.subplots()
lines = colored_line(rpm,dpdt,dp_close, ax, linewidth=2, cmap="viridis")
fig.colorbar(lines)
ax.set_xlim(1.1*min(rpm),1.1*max(rpm))
ax.set_ylim(1.1*min(dpdt),1.1*max(dpdt))
ax.set_xlabel('rpm')
ax.set_ylabel('dpdt')
plt.show()






# i = [i for i,val in enumerate(radar) if abs(val)<0.02]
# gem_p_float = np.sort(pfloater[i])
# gem_p_float = gem_p_float[round(len(gem_p_float)/2)]
# gem_p_spring = np.sort(pspring_gas[i])
# gem_p_spring = gem_p_spring[round(len(gem_p_spring)/2)]

# profiel = SP.profileDiam
# z,dz = np.linspace(-2,2,4001,retstep=True)
# aansnijspot = z + np.pi/4*(profiel[2000]-profiel)
# dz_aansnij = aansnijspot[1:] - aansnijspot[:-1]
# dz_aansnij = (np.array([dz_aansnij[0]]+list(dz_aansnij))+np.array(list(dz_aansnij)+[dz_aansnij[-1]]))/2
# V_cumulatief = 0
# V_profiel = []
# for hoogte in range(len(profiel)):
#     dV = np.pi/8*((profiel[hoogte]-0.034)**2-(1.6826-0.034)**2)*dz_aansnij[hoogte]
#     V_cumulatief += dV
#     V_profiel.append(V_cumulatief)
# dVdz_per_z = np.gradient(V_profiel,z)
# V_gas = integrate.cumulative_trapezoid(dVdz_per_z,z)
# V_gas_inter = interpolate.PchipInterpolator(np.linspace(z[0]+dz/2,z[-1]-dz/2,len(V_gas)),V_gas)
# V_gas = V_gas_inter(z) - V_gas_inter(0) +1.7/2  #+ SP.fillLevel * SP.Vtank


# # ------------------------------------------------------------------------
# # zwaartekracht
# zwaartekracht = - GP.g * (SP.floaterMass) * np.ones(len(z))

# # ----------------------------------------------------------------------------
# # Kracht door buitendruk, als je alle krachten sommeert hou je minus de kracht op de core en half het membraan over
# Fcore = -GP.Patm*((np.pi/4)*SP.membrameInnerDiam**2)
# Fmembrane = -GP.Patm*(np.pi/8)*(SP.profileDiam**2-SP.membrameInnerDiam**2)
# Buitendruk = Fcore + Fmembrane


# # ----------------------------------------------------------------------------
# # Kracht door gasdruk van het bovendeel
# opp_floater = np.pi/4 * SP.floaterInnerDiamUp**2 - np.pi/8 *(SP.floaterInnerDiamUp**2-SP.membrameInnerDiam**2)


# opp_deksel = np.pi/4*SP.floaterOuterDiamUp**2
# opp_core = np.pi/4*SP.membrameInnerDiam**2

# V_floater = np.linspace(8.890227055149078,17.585877561495522,4001)

# P_floater = gem_p_float * (V_floater[2000]/V_floater)**(7/5)
# F_floater = P_floater*opp_floater*1e5



# # ----------------------------------------------------------------------------
# # Kracht door gasdruk van de tank
# opp_spring = np.pi/4*((profiel-.034)**2-(SP.floaterInnerDiamUp-.034)**2)
# P_spring = gem_p_spring * (V_gas[2000]/V_gas)**(7/5)
# F_spring = P_spring*opp_spring*1e5 / 2 / 1.045



# # ----------------------------------------------------------------------------
# # Resultante kracht
# F_vast_per_z = zwaartekracht + Buitendruk + F_floater


# stappen = np.arange(1000)
# dt = .02
# rpm = 400*np.cos(stappen*dt*2*np.pi/4)
# h=0
# a=0
# flow_oud = 0
# V = V_profiel[2000]
# lek = 0

# for stap in stappen:
#     omega = rpm[stap]
#     for iteratie in range(10):
#         flow = omega / 60 *dt *0.0106 - lek
#         V += flow
#         h = interpolate.interp1d(V_profiel,z)(V)
#         druk_spring = interpolate.interp1d(z,P_spring)(h)



# h_oud = 0
# F_z = zwaartekracht[0]
# v_oud=0
# a_vloeistof = []
# a_hysterese = []
# a_turb = []
# a_ft = []
# a_spt = []
# a_g = []
# a_bui = []
# for stap in stappen:
#     index = round((h+2)*1000)
#     dh = h - h_oud
#     v = dh/dt
#     dv = v - v_oud
#     a_vloeistof.append(dv/dt)
#     # F_res = SP.floaterMass * a
#     # F_turb = F_res - F_res_per_z[index]
#     # dP = 2*F_turb / opp_spring[index] / 1e5
#     dP_opgebouwd = 5.49/600*rpm 
#     F_turb = dP_opgebouwd * opp_spring[index]*1e5/2
#     a_turb.append(-F_turb/SP.floaterMass)
#     a_hysterese.append(np.sign(v)*1500/SP.floaterMass)
#     a_ft.append(F_floater[index]/SP.floaterMass)
#     a_spt.append(F_spring[index]/SP.floaterMass)
#     a_bui.append(Buitendruk[index]/SP.floaterMass)
#     a_g.append(zwaartekracht[index]/SP.floaterMass)
#     dV = rpm/60*dt*0.0106
#     V+=dV
#     h_oud = h
#     h = interpolate.interp1d(V_profiel,z)(V)
#     v_oud = v