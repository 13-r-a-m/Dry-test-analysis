import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

tijd = np.load("drytest 20260706_verwerkt/tijd.npy")
radar = np.load("drytest 20260706_verwerkt/radar.npy")
druk_ft = np.load("drytest 20260706_verwerkt/pmem_boven.npy")
druk_ft_onder = np.load("drytest 20260706_verwerkt/pmem_onder.npy")
druk_ft_midden = np.load("drytest 20260706_verwerkt/pmem_midden.npy")
druk_ft_og = np.load("drytest 20260706_verwerkt/pfloater.npy")
druk_mem = np.load("drytest 20260706_verwerkt/pmem.npy")
druk_spt_gas = np.load("drytest 20260706_verwerkt\pspring_gas.npy")
druk_spt_lq = np.load("drytest 20260706_verwerkt/pspring_liquid.npy")
level = np.load("drytest 20260706_verwerkt/level.npy")
temp_spt = np.load("drytest 20260706_verwerkt/tempspring.npy")
temp_ft = np.load("drytest 20260706_verwerkt/tempfloater.npy")
rpm = np.load("drytest 20260706_verwerkt/rpm.npy")

plt.plot(tijd,rpm)
plt.show()
radar[14712:30908] -=.2
dz = np.gradient(radar)
slinger = slice(24500,27000)

dichtdrukradar = np.where(druk_ft - druk_ft_midden < -0.05)

plt.plot(tijd,druk_ft - druk_ft_midden,label='differentiaaldruk [bar]')
plt.plot(tijd[dichtdrukradar],radar[dichtdrukradar],linestyle='',marker='o',markersize=1,c='r',label='radar [m] waar dP<-0.05')
# plt.plot(tijd,druk_ft,label='PT_15')
# plt.plot(tijd,druk_ft_midden,label='PT_14')
# # plt.plot(tijd,druk_ft_onder,label='PT_07')
# plt.plot(tijd,druk_ft_og,label='PT_08')
# # plt.plot(tijd,druk_mem,label='PT_11')
# plt.plot(tijd,radar,label='radar')
plt.xlabel("tijd [s]")
plt.title('Verschil tussen PT_14 en PT_15')
plt.legend()
plt.show()


tijd = np.concatenate([tijd[:24500],tijd[27000:]])
radar = np.concatenate([radar[:24500],radar[27000:]])
druk_ft = np.concatenate([druk_ft[:24500],druk_ft[27000:]])
druk_ft_midden = np.concatenate([druk_ft_midden[:24500],druk_ft_midden[27000:]])
druk_ft_onder = np.concatenate([druk_ft_onder[:24500],druk_ft_onder[27000:]])
druk_ft_og = np.concatenate([druk_ft_og[:24500],druk_ft_og[27000:]])
druk_mem = np.concatenate([druk_mem[:24500],druk_mem[27000:]])
druk_spt_gas = np.concatenate([druk_spt_gas[:24500],druk_spt_gas[27000:]])
druk_spt_lq = np.concatenate([druk_spt_lq[:24500],druk_spt_lq[27000:]])
level = np.concatenate([level[:24500],level[27000:]])
temp_spt = np.concatenate([temp_spt[:24500],temp_spt[27000:]])
temp_ft = np.concatenate([temp_ft[:24500],temp_ft[27000:]])

avg_time = 30
temp_ft_avg = np.zeros(len(temp_ft))
druk_ft_avg = np.zeros(len(druk_ft))
startsum_t = 0
startsum_p = 0
for i in range(avg_time):
    temp_ft_avg[avg_time:] += temp_ft[i:-avg_time+i]
    druk_ft_avg[avg_time:] += druk_ft[i:-avg_time+i]
    startsum_t += temp_ft[i]
    startsum_p += druk_ft[i]
    temp_ft_avg[i] = startsum_t/(i+1)
    druk_ft_avg[i] = startsum_p/(i+1)
temp_ft_avg[avg_time:] /= avg_time
druk_ft_avg[avg_time:] /= avg_time

# avg_time  = 10
# dz_avg = np.zeros(len(dz))
# startsum_z = 0
# for i in range(avg_time):
#     dz_avg[avg_time:] += dz[i:-avg_time+i]**2
#     startsum_z += dz[i]**2
#     dz_avg[i] = startsum_z**.5 / (i+1)
# dz_avg[avg_time:] = dz_avg[avg_time:]**.5
# dz_avg[avg_time:] /= avg_time

z0 = sum(radar[:500])/500
P0 = sum(druk_ft[:500])/500
T0 = sum(temp_ft[:500])/500
V0 = (z0+2)/4 * (17.59-9.89) + 9.89
NR = V0*P0/(T0+273.15)

def Vapor_pressure(temp):
    return 0.61078*np.exp(17.27*temp / (temp+237.3)) / 100

P_vapor = Vapor_pressure(temp_ft_avg)
NnR = V0*(P0-Vapor_pressure(T0))/(T0+273.15)

def volumecheck_gas(druk,minvol,maxvol):
    return (NR*(temp_ft_avg+273.15)/druk-minvol)/(maxvol-minvol)*4
def volumecheck_condens(druk,minvol,maxvol):
    return (NnR*(temp_ft_avg+273.15)/(druk-P_vapor)-minvol)/(maxvol-minvol)*4

[V_min_gas,V_max_gas] = curve_fit(volumecheck_gas,druk_ft_avg,radar+2,[9.89,17.59])[0]
[V_min_condens,V_max_condens] = curve_fit(volumecheck_condens,druk_ft_avg,radar+2,[9.89,17.59])[0]
print(V_min_gas,V_max_gas)
print(V_min_condens,V_max_condens)

plt.plot(range(len(tijd)),radar+2)
plt.plot(range(len(tijd)),(NR*(temp_ft_avg+273.15)/druk_ft_avg-V_min_gas)/(V_max_gas-V_min_gas)*4,label='geen condens')
plt.plot(range(len(tijd)),(NnR*(temp_ft_avg+273.15)/(druk_ft_avg-P_vapor)-V_min_condens)/(V_max_condens-V_min_condens)*4,label='condens')
plt.legend()
plt.show()


# waterkolom = druk_spt_gas - druk_spt_lq
# h = waterkolom * 10**5 / 1026 / 9.81+2.25
# def curve(druk, A,B):
#     return A-B*(temp_spt+273.15)/druk

# [V_0,NR] = curve_fit(curve,druk_spt_gas,level/1000)[0]

# plt.plot(tijd,level/1000,linestyle='',marker='o',markersize=1)
# # plt.plot(tijd,druk_float,linestyle='',marker='o',markersize=1)
# # plt.plot(tijd,h,linestyle='',marker='o',markersize=1)
# plt.plot(tijd,V_0 - NR*(temp_spt+273.15)/druk_spt_gas,linestyle='',marker='o',markersize=1)
# # plt.plot(tijd,druk_spt_lq,linestyle='',marker='o',markersize=1)
# # plt.plot(tijd,temp,linestyle='',marker='o',markersize=1)

# plt.show()