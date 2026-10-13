import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from modelParams import SymphonyParams as SP
from modelParams import GeneralParams as GP

dikte = 0.034
dikte = 0.09

tijd = np.load('drytest 20251029_verwerkt/tijd.npy')
radar = np.load('drytest 20251029_verwerkt/radar.npy')
pfloater = np.load('drytest 20251029_verwerkt/pfloater.npy')
pmem = np.load('drytest 20251029_verwerkt/pmem2.npy')

dz = radar[1:] - radar[:-1]
dt = tijd[1:] - tijd[:-1]
v = dz/dt
dz = (np.array([0]+list(dz))+np.array(list(dz)+[0]))/2
dt = (np.array([0]+list(dt))+np.array(list(dt)+[0]))/2
v = (np.array([0]+list(v))+np.array(list(v)+[0])) / 2

pfloater = np.array(pfloater)
filter1 = np.where(dz<.01,1,0)
filter1 = np.concatenate((filter1[-2:], filter1[:-2]))*np.concatenate((filter1[-1:], filter1[:-1])) * filter1 * np.concatenate((filter1[1:], filter1[:1]))*np.concatenate((filter1[2:], filter1[:2]))
filter2 = np.where(pfloater==.0,0,1)
filter3 = np.where(radar<-1.8,0,1)
# filter4 = np.where(radar>-1,0,1)
filter = filter1*filter2*filter3#*filter4

zeros = [i for i, val in enumerate(filter) if val == 0]
pfloater_fil = np.array([val for i, val in enumerate(pfloater) if i not in zeros])
pmem_fil = np.array([val for i,val in enumerate(pmem) if i not in zeros])
radar_fil = np.array([val for i, val in enumerate(radar) if i not in zeros])

pmem_fil += .7  #ongeveer .29bar waterkolom
pfloater_fil += 1.15
radar_fil += 2

opp = np.pi/4 * SP.floaterInnerDiamUp**2 - np.pi/8 *(SP.floaterInnerDiamUp**2-SP.membrameInnerDiam**2)
F_floater = opp*pfloater_fil*1e5

Buitendruk_constant = -GP.Patm*(np.pi/8)*(SP.membrameInnerDiam**2+SP.floaterInnerDiamUp**2)



zwaartekracht = - GP.g * SP.floaterMass
Fnet = - zwaartekracht - Buitendruk_constant - F_floater + np.pi/4*(SP.floaterInnerDiamUp**2 -SP.membrameInnerDiam**2)*0.225e5
opp_profiel = 2 * Fnet / (pmem_fil*1e5-radar_fil/2*9.81*1055-0.449e5 - GP.Patm)
profieldiam = SP.profileDiam

offset = np.pi/4*(profieldiam[2000]-profieldiam) + 0.06
z = np.linspace(.2,(round(max(radar_fil),3)),int(round(max(radar_fil)-.2)*1000))
z+=offset[200:200+len(z)]
# p = np.polyfit(z,np.pi/4*((profieldiam[200:200+len(z)]-dikte)**2-(SP.floaterInnerDiamUp-dikte)**2),14)

# def profiel(x,a):
#     return np.polyval(p,x)*a

opp_veel_z = np.interp(radar_fil,z,np.pi/4*((profieldiam[200:200+len(z)]-dikte)**2-(SP.floaterInnerDiamUp-dikte)**2))

def profiel2(x,a):
    return x*a

[a],cov = curve_fit(profiel2,opp_veel_z,opp_profiel)
# [a],cov = curve_fit(profiel,radar_fil,opp_profiel)
# a*=1.045

# plt.plot(z,np.pi/4*((profieldiam[::-1][200:200+len(z)]-dikte)**2-(SP.floaterInnerDiamUp-dikte)**2),label='Shape profile - as designed')
plt.plot(radar_fil,opp_profiel,marker='o',markersize=1,linestyle='',label='Measured in drytest')
plt.plot(z,np.pi/4*((profieldiam[200:200+len(z)]-dikte)**2-(SP.floaterInnerDiamUp-dikte)**2),label='As engineered')   # - as placed in floater wall')
# plt.plot(z,profiel(z,a),label='Shape profile - force transfer {}%'.format(round(a*100,1)))
plt.plot(radar_fil,a*opp_veel_z,label='Force transfer {}%'.format(round(a*100,1)))
plt.title('Shape profile function')
plt.xlabel('Radar [$m$]')
plt.ylabel('Area difference top and bottom membrane [$m^2$]')
plt.legend()
plt.show()

print(a)