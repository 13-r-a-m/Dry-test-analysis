import matplotlib.pyplot as plt
import numpy as np
from modelParams import SymphonyParams as SP
from modelParams import GeneralParams as GP
import warnings
from matplotlib.collections import LineCollection
from scipy.optimize import curve_fit
import sys

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


vertraging = 6
tijdspanne = 10

tijd = np.load('drytest 20251202_verwerkt/tijd.npy')
deel = slice(int(round(len(tijd)*0.14)),int(round(len(tijd)*0.36)))

tijd = tijd[deel]
radar = np.load('drytest 20251202_verwerkt/radar.npy')[deel]
pfloater = np.load('drytest 20251202_verwerkt/pfloater.npy')[deel]
pmem = np.load('drytest 20251202_verwerkt/pmem1.npy')[deel]
encoder = np.load('drytest 20251202_verwerkt/encoder.npy')[deel]            # %65530
pturb_spring = np.load('drytest 20251202_verwerkt/pturbspring.npy')[deel]
pturb_mem = np.load('drytest 20251202_verwerkt/pturbmem.npy')[deel]
pspring_gas = np.load('drytest 20251202_verwerkt/pspring_gas.npy')[deel]
rpm = np.load('drytest 20251202_verwerkt/rpm.npy')[deel]
stroom = np.load('drytest 20251202_verwerkt/stroom1.npy')[deel]*1e2
stroom_alt = np.load('drytest 20251202_verwerkt/stroom2.npy')[deel]*1e2
spanning = np.load('drytest 20251202_verwerkt/spanning.npy')[deel]
level = np.load('drytest 20251202_verwerkt/level.npy')[deel]
power = np.load('drytest 20251202_verwerkt/power.npy')[deel]*1e5

# inductance_ds = .48e-3
# resistance_ds = .06
# voltage_ds = 253 / 3**.5
# current_ds = 102.9
# power_ds = 43865 / 3
# rpm_ds = 400

# impedance_R = power_ds / current_ds**2
# impedance_I = rpm_ds / 60 * 2*np.pi * 24 * inductance_ds
# impedance_ds = (impedance_R**2+impedance_I**2)**.5
# impedance_ds2 = voltage_ds / current_ds


torque = np.where(stroom_alt>2)[0]
# torque = np.sort(np.concatenate([np.where(stroom>.2)[0],np.where(stroom<-.2)[0]]))
stroom_alt = stroom_alt[torque]
stroom = stroom[torque]
tijd = tijd[torque]
spanning = spanning[torque] / 3 **.5
power = power[torque] / 3
rpm = rpm[torque]
impedance_im = rpm /60 *2* np.pi * 24 *.48e-3

impedance_re = power / stroom_alt**2
# weerstandsfilter = np.where(abs(weerstand))
# weerstandsfilter = np.sort(np.concatenate([np.where(weerstand_alt>.2)[0],np.where(weerstand_alt<-.2)[0]]))

plt.plot(tijd,abs(impedance_re),label="Re")
plt.plot(tijd,np.ones(len(impedance_re))*sum(abs(impedance_re))/len(impedance_re),label="Re - gem")
plt.plot(tijd,abs(impedance_im),label="Im")
# plt.plot(tijd,np.ones(len(impedance_im))*sum(impedance_im)/len(impedance_im),label="Im - gem")
plt.plot(tijd,(impedance_im**2+impedance_re**2)**.5,label="impedance - sum")
plt.plot(tijd,np.ones(len(tijd))*sum((impedance_im**2+impedance_re**2)**.5)/len(tijd),label="sum - gem")
plt.plot(tijd,spanning/stroom_alt,label="impedance - measured")
plt.plot(tijd,np.ones(len(tijd))*sum(spanning/stroom_alt)/len(tijd),label="measured - gem")
plt.legend()
plt.show()


power*=3
power_gem = sum(power)/len(power)
loss_gem = sum(0.06*3*stroom**2)/len(tijd)
plt.plot(range(len(tijd)),power,label="Power input")
plt.plot(range(len(tijd)),0.06*3*stroom**2,label="Ohmic loss")
plt.plot(range(len(tijd)),np.ones(len(tijd))*power_gem,label="Avg. {}W - 100%".format(round(power_gem)))
plt.plot(range(len(tijd)),np.ones(len(tijd))*loss_gem,label="Avg. {}W - {}%".format(round(loss_gem),round(100*loss_gem/power_gem)))
plt.legend()
plt.show()

sys.exit()

# rpm = np.concatenate([[0,0,0,0,0,0],rpm[:-6]])

drukval = pturb_mem - pturb_spring + 0.089
drukval = -drukval

# rpm = encoder[1:] - encoder[:-1]
# zaag_af = np.where(rpm>6e4,-65530,0)
# zaag_op = np.where(rpm<-6e4,65530,0)
# rpm += zaag_af + zaag_op
# rpm *= 60/.2/ 65530
# rpm = (np.array([0]+list(rpm))+np.array(list(rpm)+[0]))/2



# geendruk = [i for i,val in enumerate(rpm) if val==0.]
# plt.plot(drukval[geendruk],range(len(drukval[geendruk])))
# plt.show()

pmem -= .6  #ongeveer .6bar waterkolom
pfloater += 1
radar += 2

dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2

profieldiam = SP.profileDiam
# offset = np.pi/4*(profieldiam[2000]-profieldiam) + 0.06
z = np.linspace(0,4,4001)#+offset


filterplus = np.where(dz>.01,1,0)
filtermin = np.where(dz<-.01,1,0)

pmem_plus = []
pturb_mplus = []
pturb_splus = []
pfloat_plus = []
pspring_plus = []
tijd_plus = []
radar_plus = []
rpm_plus = []
drukval_plus = []
stroom_plus = []
level_plus = []
pmem_min = []
pturb_mmin = []
pturb_smin = []
pfloat_min = []
pspring_min = []
tijd_min = []
radar_min = []
rpm_min = []
drukval_min = []
stroom_min = []
level_min = []
j=0
k=0

for i in range(len(filterplus)):
    if filterplus[i] == 1 and j+tijdspanne<i:
        pmem_plus.append(pmem[i-tijdspanne-vertraging:i-vertraging])
        pfloat_plus.append(pfloater[i-tijdspanne-vertraging:i-vertraging])
        pspring_plus.append(pspring_gas[i-tijdspanne-vertraging:i-vertraging])
        pturb_mplus.append(pturb_mem[i-tijdspanne-vertraging:i-vertraging])
        pturb_splus.append(pturb_spring[i-tijdspanne-vertraging:i-vertraging])
        tijd_plus.append(tijd[i-tijdspanne-vertraging:i-vertraging])
        radar_plus.append(radar[i-tijdspanne-vertraging:i-vertraging])
        rpm_plus.append(rpm[i-tijdspanne-vertraging:i-vertraging])
        drukval_plus.append(drukval[i-tijdspanne-vertraging:i-vertraging])
        stroom_plus.append(stroom[i-tijdspanne-vertraging:i-vertraging])
        level_plus.append(level[i-tijdspanne-vertraging:i-vertraging])
        j = i
    if filtermin[i] == 1 and k+tijdspanne<i:
        pmem_min.append(pmem[i-tijdspanne-vertraging:i-vertraging])
        pturb_mmin.append(pturb_mem[i-tijdspanne-vertraging:i-vertraging])
        pturb_smin.append(pturb_spring[i-tijdspanne-vertraging:i-vertraging])
        pfloat_min.append(pfloater[i-tijdspanne-vertraging:i-vertraging])
        pspring_min.append(pspring_gas[i-tijdspanne-vertraging:i-vertraging])
        tijd_min.append(tijd[i-tijdspanne-vertraging:i-vertraging])
        radar_min.append(radar[i-tijdspanne-vertraging:i-vertraging])
        rpm_min.append(rpm[i-tijdspanne-vertraging:i-vertraging])
        drukval_min.append(drukval[i-tijdspanne-vertraging:i-vertraging])
        stroom_min.append(stroom[i-tijdspanne-vertraging:i-vertraging])
        level_min.append(level[i-tijdspanne-vertraging:i-vertraging])
        k = i


pmem_plus.pop(6)
pturb_splus.pop(6)
pturb_mplus.pop(6)
pfloat_plus.pop(6)
pspring_plus.pop(6)
radar_plus.pop(6)
rpm_plus.pop(6)
drukval_plus.pop(6)
stroom_plus.pop(6)
level_plus.pop(6)

radar_uiteinde = [radar_plus[6]]
pmem_uiteinde = [pmem_plus[6]]
pturb_muiteinde = [pturb_mplus[6]]
pturb_suiteinde = [pturb_splus[6]]
pspring_uiteinde = [pspring_plus[6]]
pfloat_uiteinde = [pfloat_plus[6]]
rpm_uiteinde = [rpm_plus[6]]
drukval_uiteinde = [drukval_plus[6]]
stroom_uiteinde = [stroom_plus[6]]
level_uiteinde = [level_plus[6]]

pmem_plus.pop(6)
pturb_mplus.pop(6)
pturb_splus.pop(6)
pfloat_plus.pop(6)
pspring_plus.pop(6)
radar_plus.pop(6)
rpm_plus.pop(6)
drukval_plus.pop(6)
stroom_plus.pop(6)
level_plus.pop(6)

radar_uiteinde.append(radar_min[0])
pmem_uiteinde.append(pmem_min[0])
pturb_muiteinde.append(pturb_mmin[0])
pturb_suiteinde.append(pturb_smin[0])
pspring_uiteinde.append(pspring_min[0])
pfloat_uiteinde.append(pfloat_min[0])
rpm_uiteinde.append(rpm_min[0])
drukval_uiteinde.append(drukval_min[0])
stroom_uiteinde.append(stroom_min[0])
level_uiteinde.append(level_min[0])

pmem_min.pop(0)
pturb_mmin.pop(0)
pturb_smin.pop(0)
pfloat_min.pop(0)
pspring_min.pop(0)
radar_min.pop(0)
rpm_min.pop(0)
drukval_min.pop(0)
stroom_min.pop(0)
level_min.pop(0)



dP = np.zeros(8)
radar_dP = np.zeros(8)
A = np.zeros(8)

dP[0] = sum(pmem_plus[0])/len(pmem_plus[0]) - (sum(pmem_min[6])+sum(pmem_min[5]))/(len(pmem_min[6])+len(pmem_min[5]))
radar_dP[0] = (sum(radar_plus[0])+sum(radar_min[6])+sum(radar_min[5]))/(len(radar_plus[0])+len(radar_min[6])+len(radar_min[5]))
index = [i for i,val in enumerate(z) if val > radar_dP[0]][0]
a = (radar_dP[0] - z[index]) / (z[index-1]-z[index])

A[0] = a*profieldiam[index-1]+(1-a)*profieldiam[index]

dP[1] = sum(pmem_plus[1])/len(pmem_plus[1]) - sum(pmem_min[4])/len(pmem_min[4])
radar_dP[1] = (sum(radar_plus[1])+sum(radar_min[4])) / (len(radar_plus[1])+len(radar_min[4]))
index = [i for i,val in enumerate(z) if val > radar_dP[1]][0]
a = (radar_dP[1] - z[index]) / (z[index-1]-z[index])

A[1] = a*profieldiam[index-1]+(1-a)*profieldiam[index]

dP[2] = sum(pmem_plus[2])/len(pmem_plus[2]) - sum(pmem_min[3])/len(pmem_min[3])
radar_dP[2] = (sum(radar_plus[2])+sum(radar_min[3])) / (len(radar_plus[2])+len(radar_min[3]))
index = [i for i,val in enumerate(z) if val > radar_dP[2]][0]
a = (radar_dP[2] - z[index]) / (z[index-1]-z[index])

A[2] = a*profieldiam[index-1]+(1-a)*profieldiam[index]

dP[3] = sum(pmem_plus[3])/len(pmem_plus[3]) - sum(pmem_min[2])/len(pmem_min[2])
radar_dP[3] = (sum(radar_plus[3])+sum(radar_min[2])) / (len(radar_plus[3])+len(radar_min[2]))
index = [i for i,val in enumerate(z) if val > radar_dP[3]][0]
a = (radar_dP[3] - z[index]) / (z[index-1]-z[index])

A[3] = a*profieldiam[index-1]+(1-a)*profieldiam[index]

dP[4] = sum(pmem_plus[4])/len(pmem_plus[4]) - sum(pmem_min[1])/len(pmem_min[1])
radar_dP[4] = (sum(radar_plus[4])+sum(radar_min[1])) / (len(radar_plus[4])+len(radar_min[1]))
index = [i for i,val in enumerate(z) if val > radar_dP[4]][0]
a = (radar_dP[4] - z[index]) / (z[index-1]-z[index])

A[4] = a*profieldiam[index-1]+(1-a)*profieldiam[index]

dP[5] = sum(pmem_plus[5])/len(pmem_plus[5]) - sum(pmem_min[0])/len(pmem_min[0])
radar_dP[5] = (sum(radar_plus[5])+sum(radar_min[0])) / (len(radar_plus[5])+len(radar_min[0]))
index = [i for i,val in enumerate(z) if val > radar_dP[5]][0]
a = (radar_dP[5] - z[index]) / (z[index-1]-z[index])

A[5] = a*profieldiam[index-1]+(1-a)*profieldiam[index]

dP[6] = sum(pmem_plus[6])/len(pmem_plus[6]) - sum(pmem_min[8])/len(pmem_min[8])
radar_dP[6] = (sum(radar_plus[6])+sum(radar_min[8])) / (len(radar_plus[6])+len(radar_min[8]))
index = [i for i,val in enumerate(z) if val > radar_dP[6]][0]
a = (radar_dP[6] - z[index]) / (z[index-1]-z[index])

A[6] = a*profieldiam[index-1]+(1-a)*profieldiam[index]

dP[7] = sum(pmem_plus[7])/len(pmem_plus[7]) - sum(pmem_min[7])/len(pmem_min[7])
radar_dP[7] = (sum(radar_plus[7])+sum(radar_min[7])) / (len(radar_plus[7])+len(radar_min[7]))
index = [i for i,val in enumerate(z) if val > radar_dP[7]][0]
a = (radar_dP[7] - z[index]) / (z[index-1]-z[index])

A[7] = a*profieldiam[index-1]+(1-a)*profieldiam[index]

A = np.pi/4*((A-.034)**2-(SP.floaterInnerDiamUp-.034)**2)/2

F = dP*A*1e5


pmem_plus = np.concatenate(pmem_plus,axis=None)
pturb_mplus = np.concatenate(pturb_mplus,axis=None)
pturb_splus = np.concatenate(pturb_splus,axis=None)
pfloat_plus = np.concatenate(pfloat_plus,axis=None)
pspring_plus = np.concatenate(pspring_plus,axis=None)
radar_plus = np.concatenate(radar_plus,axis=None)
rpm_plus = np.concatenate(rpm_plus,axis=None)
drukval_plus = np.concatenate(drukval_plus,axis=None)
stroom_plus = np.concatenate(stroom_plus,axis=None)
level_plus = np.concatenate(level_plus,axis=None)
pmem_min = np.concatenate(pmem_min,axis=None)
pturb_mmin = np.concatenate(pturb_mmin,axis=None)
pturb_smin = np.concatenate(pturb_smin,axis=None)
pfloat_min = np.concatenate(pfloat_min,axis=None)
pspring_min = np.concatenate(pspring_min,axis=None)
radar_min = np.concatenate(radar_min,axis=None)
rpm_min = np.concatenate(rpm_min,axis=None)
drukval_min = np.concatenate(drukval_min,axis=None)
stroom_min = np.concatenate(stroom_min,axis=None)
level_min = np.concatenate(level_min,axis=None)
pmem_uiteinde = np.concatenate(pmem_uiteinde,axis=None)
pturb_muiteinde = np.concatenate(pturb_muiteinde,axis=None)
pturb_suiteinde = np.concatenate(pturb_suiteinde,axis=None)
pfloat_uiteinde = np.concatenate(pfloat_uiteinde,axis=None)
pspring_uiteinde = np.concatenate(pspring_uiteinde,axis=None)
radar_uiteinde = np.concatenate(radar_uiteinde,axis=None)
rpm_uiteinde = np.concatenate(rpm_uiteinde,axis=None)
drukval_uiteinde = np.concatenate(drukval_uiteinde,axis=None)
stroom_uiteinde = np.concatenate(stroom_uiteinde,axis=None)
level_uiteinde = np.concatenate(level_uiteinde,axis=None)

plt.plot(radar_plus,pmem_plus,linestyle='',marker='o',markersize=2,label='upwards trajectory')
plt.plot(radar_min,pmem_min,linestyle='',marker='o',markersize=2,label='downwards trajectory')
plt.plot(radar_uiteinde,pmem_uiteinde,linestyle='',marker='o',markersize=2,label='turning points')
plt.title('Membrane pressure')
plt.ylabel('Membrane pressure [$bar(g)$]')
plt.xlabel('Radar [$m$]')
plt.legend()
plt.show()

plt.plot(np.concatenate([radar_plus,radar_min,radar_uiteinde]),np.concatenate([pmem_plus,pmem_min,pmem_uiteinde]),linestyle='',marker='o',markersize=2,label='membraan')
plt.plot(np.concatenate([radar_plus,radar_min,radar_uiteinde]),np.concatenate([pturb_mplus,pturb_mmin,pturb_muiteinde]),linestyle='',marker='o',markersize=2,label='turbine membraan')
plt.plot(np.concatenate([radar_plus,radar_min,radar_uiteinde]),np.concatenate([pturb_splus,pturb_smin,pturb_suiteinde]),linestyle='',marker='o',markersize=2,label='turbine spring tank')
plt.plot(np.concatenate([radar_plus,radar_min,radar_uiteinde]),np.concatenate([pspring_plus,pspring_min,pspring_uiteinde]),linestyle='',marker='o',markersize=2,label='spring tank')
plt.title('Pressures')
plt.ylabel('Pressure [$bar(g)$]')
plt.xlabel('Radar [$m$]')
plt.legend()
plt.show()


plt.plot(radar_plus,level_plus,linestyle='',marker='o',markersize=2,label='upwards trajectory')
plt.plot(radar_min,level_min,linestyle='',marker='o',markersize=2,label='downwards trajectory')
plt.plot(radar_uiteinde,level_uiteinde,linestyle='',marker='o',markersize=2,label='turning points')
plt.title('Level')
plt.ylabel('level')
plt.xlabel('Radar [$m$]')
plt.legend()
plt.show()


plt.plot(radar_plus,pfloat_plus,linestyle='',marker='o',markersize=2,label='upwards trajectory')
plt.plot(radar_min,pfloat_min,linestyle='',marker='o',markersize=2,label='downwards trajectory')
plt.plot(radar_uiteinde,pfloat_uiteinde,linestyle='',marker='o',markersize=2,label='turning points')
plt.title('Floater pressure')
plt.ylabel('Floater pressure [$bar(g)$]')
plt.xlabel('Radar [$m$]')
plt.legend()
plt.show()



plt.plot(radar_plus,rpm_plus,linestyle='',marker='o',markersize=2,label='upwards trajectory')
plt.plot(radar_min,rpm_min,linestyle='',marker='o',markersize=2,label='downwards trajectory')
plt.plot(radar_uiteinde,rpm_uiteinde,linestyle='',marker='o',markersize=2,label='turning points')
plt.xlabel('radar $[m]$')
plt.ylabel('$\omega \  [rpm]$')
plt.legend()
plt.show()

plt.plot(pmem_plus,stroom_plus,linestyle='',marker='o',markersize=2,label='upwards trajectory')
plt.plot(pmem_min,stroom_min,linestyle='',marker='o',markersize=2,label='downwards trajectory')
plt.plot(pmem_uiteinde,stroom_uiteinde,linestyle='',marker='o',markersize=2,label='turning points')
plt.xlabel('Membraandruk $[bar(g)]$')
plt.ylabel('$Stroom \  [A]$')
plt.legend()
plt.show()



plt.plot(radar_dP,F,linestyle='',marker='o',markersize=2)
plt.show()
bewaren_plus = [i for i,val in enumerate(rpm_plus) if abs(val) < 90]
bewaren_min = [i for i,val in enumerate(rpm_min) if abs(val) < 90]
bewaren_uiteinde = [i for i,val in enumerate(rpm_uiteinde) if abs(val)<90]

lek_plus = drukval_plus[bewaren_plus]*rpm_plus[bewaren_plus]*1e5*10.6/1e3/60
lek_min = drukval_min[bewaren_min]*rpm_min[bewaren_min]*1e5*10.6/1e3/60
lek_uiteinde = drukval_uiteinde[bewaren_uiteinde]*rpm_uiteinde[bewaren_uiteinde]*1e5*10.6/1e3/60

plt.plot(rpm_plus[bewaren_plus],drukval_plus[bewaren_plus],linestyle='',marker='o',markersize=2,label='upwards trajectory')
plt.plot(rpm_min[bewaren_min],drukval_min[bewaren_min],linestyle='',marker='o',markersize=2,label='downwards trajectory')
plt.plot(rpm_uiteinde[bewaren_uiteinde],drukval_uiteinde[bewaren_uiteinde],linestyle='',marker='o',markersize=2,label='turning points')
plt.plot([min(rpm_uiteinde[bewaren_uiteinde]),max(rpm_uiteinde[bewaren_uiteinde])],[0,0],linestyle='--',color='gray')
plt.ylabel('Pressure drop [bar]')
plt.xlabel('Angular turbine velocity [rpm]')
plt.title('Pressure drop for static angular turbine velocity')
plt.legend()
plt.show()


drukval = np.concatenate([drukval_plus[bewaren_plus],drukval_min[bewaren_min],drukval_uiteinde[bewaren_uiteinde]],axis=None)
lek = np.concatenate([lek_plus,lek_min,lek_uiteinde],axis=None)
radar = np.concatenate([radar_plus,radar_min,radar_uiteinde],axis=None)



up = [i for i,val in enumerate(drukval) if val > 0]
down = [i for i,val in enumerate(drukval) if val < 0]


def func2(P,eerste,tweede,derde):
    return eerste * P + tweede * P**2 + derde * P**3

fit_up = curve_fit(func2,drukval[up],lek[up])[0]
drukval_array_up = np.linspace(0,max(drukval),1000)

plt.plot(drukval_array_up,func2(drukval_array_up,fit_up[0],fit_up[1],fit_up[2]),label='$Leak={:.1f}dP+{:.1f}dP^2{:.1f}dP^3$'.format(fit_up[0],fit_up[1],fit_up[2]))

fit_down = curve_fit(func2,drukval[down],lek[down])[0]
drukval_array_down = np.linspace(min(drukval),0,1000)
plt.plot(drukval_array_down,func2(drukval_array_down,fit_down[0],fit_down[1],fit_down[2]),label='$Leak={:.1f}dP+{:.1f}dP^2+{:.1f}dP^3$'.format(fit_down[0],fit_down[1],fit_down[2]))


plt.plot(drukval,lek,linestyle='',marker='o',markersize=2,label='Measured leak [W] for static angular turbine velocity [rpm]')
plt.plot([min(drukval),max(drukval)],[0,0],linestyle='--',color='gray')
plt.plot([0,0],[0,max(lek)],linestyle='--',color='gray')
plt.title('Turbine leak')
plt.legend()
plt.ylabel('Power loss through leak [W]')
plt.xlabel('Pressure drop over the turbine [bar]')
plt.show()

radar = np.concatenate([radar[up],radar[down]],axis=None)
drukval = np.concatenate([drukval[up],-drukval[down]])
lek = np.concatenate([lek[up],lek[down]])
fit = curve_fit(func2,drukval,lek)[0]
print(fit)
fit_oud = [285.6903,77.5147]
drukval_array = np.linspace(0,max(drukval),1000)
plt.plot(drukval_array,func2(drukval_array,fit[0],fit[1],fit[2]),label='Leak$={:.1f}dP+{:.1f}dP^2{:.1f}dP^3$'.format(fit[0],fit[1],fit[2]))
plt.plot(drukval_array,drukval_array*np.poly1d(fit_oud)(drukval_array),label='Old measurement - Leak$={:.1f}dP^2+{:.1f}dP$'.format(fit_oud[0],fit_oud[1]))
plt.plot(drukval,lek,linestyle='',marker='o',markersize=2,label='Measured leak [W] for static angular turbine velocity [rpm]')
plt.title('Turbine leak - absolute pressure drop')
plt.legend()
plt.ylabel('Power loss through leak [W]')
plt.xlabel('Absolute pressure drop over the turbine [bar]')
plt.show()


stroom = np.concatenate([stroom_min,stroom_plus,stroom_uiteinde])
rpm = np.concatenate([rpm_min,rpm_plus,rpm_uiteinde])
drukval = np.concatenate([drukval_min,drukval_plus,drukval_uiteinde])

up = [i for i,val in enumerate(stroom) if val>0]
down = [i for i,val in enumerate(stroom) if val<0]
stroom = np.concatenate([stroom[up],-stroom[down]])
rpm = np.concatenate([rpm[up],-rpm[down]])
drukval = np.concatenate([drukval[up],-drukval[down]])

def func(dP,C):
    return C * dP
fit = curve_fit(func,drukval,stroom)[0]
print(fit)
plt.plot(np.linspace(min(drukval),max(drukval),1000),fit*np.linspace(min(drukval),max(drukval),1000))
# plt.plot(np.linspace(min(drukval),max(drukval),1000),np.linspace(min(drukval),max(drukval),1000)*np.poly1d(fit)(np.linspace(min(drukval),max(drukval),1000)))
plt.plot(drukval,stroom,marker='o',linestyle='',markersize=2)
plt.xlabel('$Drukval dP [bar]$')
plt.ylabel('$Stroom [A]$')
plt.show()