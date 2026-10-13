import matplotlib.pyplot as plt
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
p_turb_spt = np.load('drytest 2910_verwerkt/pturbspring.npy')
p_turb_mem = np.load('drytest 2910_verwerkt/pturbmem.npy')
p_spt = np.load('drytest 2910_verwerkt/pspring_liquid.npy')
p_mem = np.load('drytest 2910_verwerkt/pmem1.npy')
rpm = np.load('drytest 2910_verwerkt/rpm.npy')
Massa = SP.floaterMass

dp_turb = p_turb_mem - p_turb_spt
dp_buiten = p_mem - p_spt
dp_turb -= sum(dp_turb) / len(dp_turb)
dp_buiten -= sum(dp_buiten) / len(dp_buiten)

plt.plot(tijd,stroom*spanning/10)
plt.plot(tijd,power*100)
plt.show()


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
mdemping_correct = []
alle_ruis = np.array([])

fig = plt.figure()

for stuk in tijdsloten:
    periode = []
    demping = []
    demping_correct = []
    
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
    ref_power = power[tussenstuk]
    ref_v = snelheid[tussenstuk]
    ref_dp_turb = dp_turb[tussenstuk] - dp_turb[tussenstuk][-1]
    ref_dp_buiten = dp_buiten[tussenstuk] - dp_buiten[tussenstuk][-1]
    ref_I = stroom[tussenstuk]
    ref_rpm = rpm[tussenstuk]


    # ref_dp_turb *= amplitude /  max(abs(ref_dp_turb))
    # ref_dp_buiten *= amplitude / max(abs(ref_dp_buiten))
    # ref_I *= amplitude /  max(abs(ref_I))
    ref_rpm *= amplitude /  max(abs(ref_rpm))

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
    # plt.plot(ref_tijd,ref_dp_turb,label='Pressure differential close [bar]')
    # plt.plot(ref_tijd,ref_dp_buiten,label='Pressure differential far [bar]')
    # plt.plot(ref_tijd,ref_I,label='Current [A]')
    # plt.plot(ref_tijd,ref_rpm,label= '$\omega / \omega _{max}$ [ ]')
    # plt.plot(ref_tijd[indices],ref_pos[indices],linestyle='',marker='o')
    # plt.grid()
    # plt.title('Example of a release')
    # plt.xlabel('Time [s]')
    # plt.legend()
    # plt.show()


    flow = ref_dp_buiten - ref_dp_turb
    i = [i for i,val in enumerate(flow) if abs(val)<.5]
    ref_tijd_schaaf = ref_tijd[i]
    flow_schaaf = flow[i]
    rpm_schaaf = rpm[tussenstuk][i]
    norm_flow = (sum(flow_schaaf**2))**.5
    norm_rpm = (sum(rpm_schaaf**2)**.5)
    flow_schaaf /= norm_flow
    rpm_schaaf /= norm_rpm
    cov = rpm_schaaf*flow_schaaf
    # ruis = flow / norm_flow - rpm[tussenstuk] / norm_rpm
    ruis = flow_schaaf - rpm_schaaf

    plt.plot(ref_tijd,rpm[tussenstuk])
    plt.title(str(norm_flow/norm_rpm)+'  '+str(round(sum(cov),2)))
    plt.show()
    # plt.plot(ref_tijd_schaaf,flow_schaaf,label='Pressure differential')
    # plt.plot(ref_tijd_schaaf,rpm_schaaf,label= 'rpm')
    # # plt.plot(ref_tijd_schaaf,cov,label='Covariant signal')
    # plt.plot(ref_tijd_schaaf,ruis,label='Noise')
    # plt.plot(ref_tijd[indices],rpm[tussenstuk][indices],linestyle='',marker='o')
    # plt.grid()
    # plt.title('Covariance of {}'.format(round(sum(cov),2)))
    # plt.ylabel('Measurement relative to root mean squared value []')
    # plt.xlabel('Time [s]')
    # plt.legend()
    # plt.show()

    alle_ruis = np.concatenate([alle_ruis,ruis])

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

                E = sum(ref_power[i0:i1])/(i1-i0)*T/2
                V2 = sum(ref_v[i0:i1]**2)/(i1-i0)
                corr =  E /Massa / 2 / V2 / (np.pi*(1-D**2)**.5)   
                D_corr = D + corr

                periode.append(T)
                demping.append(D)
                demping_correct.append(D_corr)
        elif D<.4:

            E = sum(ref_power[i0:i1])/(i1-i0)*T/2
            V2 = sum(ref_v[i0:i1]**2)/(i1-i0)
            corr =  E /Massa / 2 / V2 / (np.pi*(1-D**2)**.5)
            D_corr = D + corr
            periode.append(T)
            demping.append(D)
            demping_correct.append(D_corr)

        t0 = t1
        z0 = z1
        i0 = i1
    
    mperiode.append(periode)
    mdemping.append(demping)
    mdemping_correct.append(demping_correct)



def gaus(X,A,sigma):
    return A/(sigma*(2*np.pi)**.5)*np.exp(-X**2/(2*sigma**2))
weights = np.ones_like(alle_ruis) * 12 / len(alle_ruis)
histogram = plt.hist(alle_ruis, weights=weights,bins=12)
hoogtes = histogram[0]
bin_edges = histogram[1]


x_hist=np.zeros(len(hoogtes)) 

for i in range(len(hoogtes)):
    x_hist[i]=(bin_edges[i+1]+bin_edges[i])/2
sigma = curve_fit(gaus,x_hist,hoogtes)[0][1]
A = curve_fit(gaus,x_hist,hoogtes)[0][0]


x_gaus = np.linspace(bin_edges[0],bin_edges[-1],1000)
y_gaus = gaus(x_gaus,A,sigma)
plt.plot(x_gaus,y_gaus,linestyle='--')
plt.title("Gaussian distributed noise with $\sigma = {}$".format(round(sigma,2)))
plt.ylabel("Probability density P")
plt.xlabel("Error $\epsilon$")
# plt.plot(x_hist,hoogtes)
plt.show()


print(sigma)

# for i in range(len(mperiode)):
#     plt.plot(range(len(mperiode[i])),mperiode[i],marker='o',markersize=5)
# plt.show()

# for i in range(len(mdemping)):
#     plt.plot(range(len(mdemping[i])),mdemping[i],marker='o',markersize=5)
# plt.show()

# for i in range(len(mdemping_correct)):
#     plt.plot(range(len(mdemping_correct[i])),mdemping_correct[i],marker='o',markersize=5)
# plt.show()


# gem_periode = np.concatenate(mperiode)
# gem_periode = sum(gem_periode) / len(gem_periode)
# print(gem_periode)

# gem_demping = np.concatenate(mdemping)
# gem_demping = sum(gem_demping) / len(gem_demping)
# print(gem_demping)

# gem_demping_corr = np.concatenate(mdemping_correct)
# gem_demping_corr = sum(gem_demping_corr) / len(gem_demping_corr)
# print(gem_demping_corr)

# print('w0={}'.format(2*np.pi/gem_periode/(1-gem_demping_corr**2)**.5))