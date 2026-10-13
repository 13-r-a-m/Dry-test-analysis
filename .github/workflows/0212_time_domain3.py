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

m = 1e4
kz = m/2
ku = 100000*kz
z_bereik = np.linspace(-2,2,4001)
u_bereik = np.linspace(-1,1,2001)
dt = .001
terug_in_de_tijd = .2

h = 0
z = 0
u = 0
v_h = 0
v_z = 0
v_u = 0
hlijst = []
zlijst = []
ulijst = []
ddotz_lijst = list(round(terug_in_de_tijd/dt)*[0])


stappen = round(100/dt)
for stap in range(stappen):
    Fext = m*np.sin(stap*2*np.pi*dt/4)
    F_z = - kz* z
    F_u = - ku*u**5
    ddotz = (Fext+F_z-3000*v_z*abs(v_z))/m
    ddotu = (F_u-Fext-3000*v_u*abs(v_u))/m-ddotz_lijst[-round(terug_in_de_tijd/dt)]
    ddoth = ddotz+ddotu
    v_z += ddotz*dt
    v_u += ddotu*dt
    v_h += ddoth*dt
    z += v_z*dt
    u += v_u*dt
    h += v_h*dt

    hlijst.append(h)
    ulijst.append(u)
    zlijst.append(z)
    ddotz_lijst.append(ddotz)


plt.plot(np.arange(stappen)*dt,zlijst,marker='o',markersize=1,label = 'Algemene uitwijking')
plt.plot(np.arange(stappen)*dt,ulijst,marker='o',markersize=1,label = 'Extra uitwijking membraanvervorming')
plt.plot(np.arange(stappen)*dt,hlijst,marker='o',markersize=1,label = 'Totale uitwijking')
plt.xlabel('tijd in s')
plt.ylabel('uitwijking in m')
plt.legend()
plt.show()