from modelParams import SymphonyParams as SP
from modelParams import GeneralParams as GP
from modelParams import ControlParams as CP
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import interpolate
import csv

tijd = np.load('drytest 0212_verwerkt/tijd.npy')
tijd = (tijd-tijd[0]) / 1000
deel = slice(round(11820/max(tijd)*len(tijd)),round(12350/max(tijd)*len(tijd)))
tijd = tijd[deel]
radar = np.load('drytest 0212_verwerkt/radar.npy')[deel]
pfloater = np.load('drytest 0212_verwerkt/pfloater.npy')[deel] + 1
pspring_gas = np.load('drytest 0212_verwerkt/pspring_gas.npy')[deel]+1


i = [i for i,val in enumerate(radar) if abs(val)<0.02]
gem_p_float = pfloater[i]
gem_p_float = gem_p_float[round(len(gem_p_float)/2)]
gem_p_spring = pspring_gas[i]
gem_p_spring = gem_p_spring[round(len(gem_p_spring)/2)]

profiel = SP.profileDiam
z,dz = np.linspace(-2,2,4001,retstep=True)
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
V_gas = integrate.cumulative_trapezoid(dVdz_per_z,z)
V_gas_inter = interpolate.PchipInterpolator(np.linspace(z[0]+dz/2,z[-1]-dz/2,len(V_gas)),V_gas)
V_gas = V_gas_inter(z) - V_gas_inter(0) +1.7/2  #+ SP.fillLevel * SP.Vtank


# ------------------------------------------------------------------------
# zwaartekracht
zwaartekracht = - GP.g * (SP.floaterMass) * np.ones(len(z))
plt.plot(z,zwaartekracht/1e5,label='zwaartekracht')

# ----------------------------------------------------------------------------
# Kracht door buitendruk, als je alle krachten sommeert hou je minus de kracht op de core en half het membraan over
Fcore = -GP.Patm*((np.pi/4)*SP.membrameInnerDiam**2)
Fmembrane = -GP.Patm*(np.pi/8)*(SP.profileDiam**2-SP.membrameInnerDiam**2)
Buitendruk = Fcore + Fmembrane

plt.plot(z,Buitendruk/1e5,label='buitendruk')

# ----------------------------------------------------------------------------
# Kracht door gasdruk van het bovendeel
opp_floater = np.pi/4 * SP.floaterInnerDiamUp**2 - np.pi/8 *(SP.floaterInnerDiamUp**2-SP.membrameInnerDiam**2)


opp_deksel = np.pi/4*SP.floaterOuterDiamUp**2
opp_core = np.pi/4*SP.membrameInnerDiam**2

V_floater = np.linspace(8.890227055149078,17.585877561495522,4001)

P_floater = gem_p_float * (V_floater[2000]/V_floater)**(7/5)
F_floater = P_floater*opp_floater*1e5

plt.plot(z,F_floater/1e5,label='FT')


# ----------------------------------------------------------------------------
# Kracht door gasdruk van de tank
opp_spring = np.pi/4*((profiel-.034)**2-(SP.floaterInnerDiamUp-.034)**2)
P_spring = gem_p_spring * (V_gas[2000]/V_gas)**(7/5)
F_spring = P_spring*opp_spring*1e5 / 2 / 1.045


plt.plot(z,F_spring/1e5,label='membraan / SpT')

# ----------------------------------------------------------------------------
# Resultante kracht
F_res_per_z = zwaartekracht + Buitendruk + F_floater + F_spring
plt.plot(z,F_res_per_z/1e5,label='resultant')


plt.plot([-2,2],[0,0],'--', color='gray')
plt.xlabel('positie [m]')
plt.ylabel('kracht [100kN]')
plt.title('statisch krachtverloop')
plt.legend()
plt.show()


h_oud = 0
stappen = 500
dt = .02
V = V_profiel[2000]
F_z = zwaartekracht[0]
v_oud=0
h=0
a_vloeistof = []
a_hysterese = []
a_turb = []
a_ft = []
a_spt = []
a_g = []
a_bui = []
for stap in range(stappen):
    rpm = 400*np.cos(stap*dt*2*np.pi/4)
    index = round((h+2)*1000)
    dh = h - h_oud
    v = dh/dt
    dv = v - v_oud
    a_vloeistof.append(dv/dt)
    # F_res = SP.floaterMass * a
    # F_turb = F_res - F_res_per_z[index]
    # dP = 2*F_turb / opp_spring[index] / 1e5
    dP_opgebouwd = 5.49/600*rpm 
    F_turb = dP_opgebouwd * opp_spring[index]*1e5/2
    a_turb.append(-F_turb/SP.floaterMass)
    a_hysterese.append(np.sign(v)*1500/SP.floaterMass)
    a_ft.append(F_floater[index]/SP.floaterMass)
    a_spt.append(F_spring[index]/SP.floaterMass)
    a_bui.append(Buitendruk[index]/SP.floaterMass)
    a_g.append(zwaartekracht[index]/SP.floaterMass)
    dV = rpm/60*dt*0.0106
    V+=dV
    h_oud = h
    h = interpolate.interp1d(V_profiel,z)(V)
    v_oud = v

a_vloeistof = np.array(a_vloeistof[4:-16])
a_g = np.array(a_g[4:-16])
a_bui = np.array(a_bui[4:-16])
a_hysterese = np.array(a_hysterese[4:-16])
a_turb = np.array(a_turb[16:-4])
a_ft = np.array(a_ft[16:-4])
a_spt = np.array(a_spt[16:-4])

a_krachtenbalans = a_turb+a_hysterese+a_bui+a_g+a_ft+a_spt
tijd = np.arange(stappen-20)*dt
teken = np.where(np.sign(a_vloeistof)==np.sign(a_krachtenbalans),0,1)
plt.plot(tijd,teken)
plt.plot(tijd,a_vloeistof,marker='o',markersize=1,label='versnelling door onsamendrukbare vloeistof')
plt.plot(tijd,a_g,marker='o',markersize=1,label='versnelling door zwaartekracht')
plt.plot(tijd,a_bui,marker='o',markersize=1,label='versnelling door buitendruk')
plt.plot(tijd,a_ft,marker='o',markersize=1,label='versnelling door samendrukken gas floater tank')
plt.plot(tijd,a_spt,marker='o',markersize=1,label='versnelling door samendrukken gas spring tank')
plt.plot(tijd,a_turb,marker='o',markersize=1,label='versnelling door drukopbouw over turbine')



data = np.array([a_vloeistof,a_g,a_hysterese,a_bui,a_ft,a_spt,a_turb]).transpose()
fieldnames = ['gepompte vloeistof','zwaartekracht','hysterese','buitendruk','floater tank gasdruk','spring tank gasdruk','drukval turbine']

with open('simulatie tijdsdomein.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    writer.writerows(data)



plt.plot(tijd,a_krachtenbalans,marker='o',markersize=1,label='versnelling door momentembehoud en gasdruk')
plt.legend()
plt.xlabel('tijd[$s$]')
plt.ylabel('versnelling[$ms^{-2}$]')
plt.title('versnelling')
plt.show()