import numpy as np
from scipy.fft import rfft, irfft
from os import walk

for path, bestandsnamen, bestanden in walk('drytest 20251202'):
    for bestandsnaam in bestanden:
        bestand = open('drytest 20251202/'+bestandsnaam)
        firstline = 0
        lines= len(bestand.readlines()) - 9
        if lines % 2 == 1:
            lines -= 1
        bestand = open('drytest 20251202/'+bestandsnaam)

        for line in bestand:
            gehakt = line.split(',')

            if not firstline:
                datasheet = np.zeros(shape=(len(gehakt),lines))
                labels = gehakt

            elif firstline <= lines:
                if not 'undefined' in gehakt:
                    for index in range(len(labels)):
                        datasheet[index][firstline-1] = float(gehakt[index])
            firstline += 1


        if 'tijd' not in locals():
            # starttijd = datasheet[0][0]
            # datasheet[0] = (datasheet[0] - starttijd) / 1000
            tijd = datasheet[0]
            stroom1 = datasheet[2]
            stroom2 = datasheet[3]
            encoder = datasheet[5]
            power = datasheet[7]
            spanning = datasheet[8]
            rpm = datasheet[9]
            pspring_gas = datasheet[10]
            pspring_liquid = datasheet[11]
            pfloater = datasheet[13]
            pturbspring = datasheet[14]
            pturbmem = datasheet[15]
            pmem1 = datasheet[16]
            pmem2 = datasheet[17]
            level = (datasheet[18] -200) / 1000
            radar = datasheet[19]
            tempgenerator = datasheet[20]
            tempkoeling = datasheet[21]
            tempspring = datasheet[22]
        else:
            tijd = np.concatenate([tijd,datasheet[0]])
            stroom1 = np.concatenate([stroom1,datasheet[2]])                #CTOAC active current
            stroom2 = np.concatenate([stroom1,datasheet[3]])                #CTOCA current amplitude
            encoder = np.concatenate([encoder,datasheet[5]])                #CTOEP
            power = np.concatenate([power,datasheet[7]])                    #CTOOP
            spanning = np.concatenate([spanning,datasheet[8]])              #CTOOV
            # tijd = np.concatenate([tijd,(datasheet[0]-starttijd)/1000])
            # fourier = rfft(datasheet[20])
            # trap = np.where(np.linspace(0,len(tijd)/(2*(tijd[-1]-tijd[0])),int(len(datasheet[0])/2+1))<.15,1,0)
            # datasheet[20] = irfft(fourier*trap)
            rpm = np.concatenate([rpm,datasheet[9]])
            pspring_gas = np.concatenate([pspring_gas,datasheet[10]])       #pt01
            pspring_liquid = np.concatenate([pspring_liquid,datasheet[11]]) #pt05
            pfloater = np.concatenate([pfloater,datasheet[13]])             #pt08
            pturbspring = np.concatenate([pturbspring,datasheet[14]])       #pt09
            pturbmem = np.concatenate([pturbmem,datasheet[15]])             #pt10
            pmem1 = np.concatenate([pmem1,datasheet[16]])                   #pt11
            pmem2 = np.concatenate([pmem2,datasheet[17]])                   #pt12
            level = np.concatenate([level,(datasheet[18] -200) / 1000])     #sl01
            radar = np.concatenate([radar,datasheet[19]])                   #so01
            tempgenerator = np.concatenate([tempgenerator,datasheet[20]])   #st01
            tempkoeling = np.concatenate([tempkoeling,datasheet[21]])       #st02
            tempspring = np.concatenate([tempspring,datasheet[22]])         #st06

print(len(tijd))
tijd = list(tijd)
tijd_kopie = tijd.copy()
vorige_tijd = -max(tijd)
nieuwe_tijd = []
nieuwe_radar = []
nieuwe_pfloater = []
nieuwe_pturbspring = []
nieuwe_pturbmem = []
nieuwe_pspring_gas = []
nieuwe_pmem1 = []
nieuwe_pmem2 = []
nieuwe_level = []
nieuwe_encoder = []
nieuwe_tempspring = []
nieuwe_rpm = []
nieuwe_stroom1 = []
nieuwe_stroom2 = []
nieuwe_power = []
nieuwe_spanning = []

for i in range(len(tijd)):
    volgende_tijd = min(tijd_kopie)
    volgende_index = tijd.index(volgende_tijd)
    if vorige_tijd != volgende_tijd:
        nieuwe_tijd.append(volgende_tijd)
        nieuwe_radar.append(radar[volgende_index])
        nieuwe_pfloater.append(pfloater[volgende_index])
        nieuwe_pturbmem.append(pturbmem[volgende_index])
        nieuwe_pturbspring.append(pturbspring[volgende_index])
        nieuwe_pspring_gas.append(pspring_gas[volgende_index])
        nieuwe_pmem1.append(pmem1[volgende_index])
        nieuwe_pmem2.append(pmem2[volgende_index])
        nieuwe_level.append(level[volgende_index])
        nieuwe_encoder.append(encoder[volgende_index])
        nieuwe_tempspring.append(tempspring[volgende_index])
        nieuwe_rpm.append(rpm[volgende_index])
        nieuwe_stroom1.append(stroom1[volgende_index])
        nieuwe_stroom2.append(stroom2[volgende_index])
        nieuwe_power.append(power[volgende_index])
        nieuwe_spanning.append(spanning[volgende_index])
    vorige_tijd = volgende_tijd
    tijd_kopie.remove(vorige_tijd)
tijd = np.array(nieuwe_tijd)
radar = np.array(nieuwe_radar)
pfloater = np.array(nieuwe_pfloater)
pturbmem = np.array(nieuwe_pturbmem)
pturbspring = np.array(nieuwe_pturbspring)
pspring_gas = np.array(nieuwe_pspring_gas)
pmem1 = np.array(nieuwe_pmem1)
pmem2 = np.array(nieuwe_pmem2)
level = np.array(nieuwe_level)
encoder = np.array(nieuwe_encoder)
tempspring = np.array(nieuwe_tempspring)
rpm = np.array(nieuwe_rpm)
stroom1 = np.array(nieuwe_stroom1)
stroom2 = np.array(nieuwe_stroom2)
power = np.array(nieuwe_power)
spanning = np.array(nieuwe_spanning)

print(len(tijd))
np.save('drytest 20251202_verwerkt/tijd.npy',tijd)
np.save('drytest 20251202_verwerkt/radar.npy',radar)
np.save('drytest 20251202_verwerkt/pfloater.npy',pfloater)
np.save('drytest 20251202_verwerkt/pturbmem.npy',pturbmem)
np.save('drytest 20251202_verwerkt/pturbspring.npy',pturbspring)
np.save('drytest 20251202_verwerkt/pspring_gas.npy',pspring_gas)
np.save('drytest 20251202_verwerkt/pmem1.npy',pmem1)
np.save('drytest 20251202_verwerkt/pmem2.npy',pmem2)
np.save('drytest 20251202_verwerkt/level.npy',level)
np.save('drytest 20251202_verwerkt/encoder.npy',encoder)
np.save('drytest 20251202_verwerkt/tempspring.npy',tempspring)
np.save('drytest 20251202_verwerkt/rpm.npy',rpm)
np.save('drytest 20251202_verwerkt/stroom1.npy',stroom1)
np.save('drytest 20251202_verwerkt/stroom2.npy',stroom2)
np.save('drytest 20251202_verwerkt/power.npy',power)
np.save('drytest 20251202_verwerkt/spanning.npy',spanning)