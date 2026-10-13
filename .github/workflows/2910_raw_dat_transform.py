import numpy as np
from scipy.fft import rfft, irfft
from os import walk

for path, bestandsnamen, bestanden in walk('drytest 2910'):
    for bestandsnaam in bestanden:
        bestand = open('drytest 2910/'+bestandsnaam)
        firstline = 0
        lines= len(bestand.readlines()) - 9
        if lines % 2 == 1:
            lines -= 1
        bestand = open('drytest 2910/'+bestandsnaam)

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
            stroom = datasheet[2]
            power = datasheet[7]
            spanning = datasheet[8]
            rpm = datasheet[9]
            fourier = rfft(datasheet[20])
            trap = np.where(np.linspace(0,len(tijd)/(2*(tijd[-1]-tijd[0])),int(len(datasheet[0])/2+1))<.2,1,0)
            datasheet[20] = irfft(fourier*trap)
            pspring_gas = datasheet[12]
            pspring_liquid = datasheet[16]
            pfloater = datasheet[19]
            pturbspring = datasheet[20]
            pturbmem = datasheet[21]
            pmem1 = datasheet[22]
            pmem2 = datasheet[23]
            targetencoder = datasheet[24] / 1e6
            posencoder = datasheet[25] / 1e6
            acc1 = datasheet[26]
            acc2 = datasheet[27]
            acc3 = datasheet[28]
            level = (datasheet[29] -200) / 1000
            radar = datasheet[32]
            tempgenerator = datasheet[33]
            tempkoeling = datasheet[34]
            tempspring = datasheet[37]
        else:
            tijd = np.concatenate([tijd,datasheet[0]])
            stroom = np.concatenate([stroom,datasheet[2]])
            power = np.concatenate([power,datasheet[7]])
            spanning = np.concatenate([spanning,datasheet[8]])
            rpm = np.concatenate([rpm,datasheet[9]])
            # tijd = np.concatenate([tijd,(datasheet[0]-starttijd)/1000])
            # fourier = rfft(datasheet[20])
            # trap = np.where(np.linspace(0,len(tijd)/(2*(tijd[-1]-tijd[0])),int(len(datasheet[0])/2+1))<.15,1,0)
            # datasheet[20] = irfft(fourier*trap)
            pspring_gas = np.concatenate([pspring_gas,datasheet[12]])
            pspring_liquid = np.concatenate([pspring_liquid,datasheet[16]])
            pfloater = np.concatenate([pfloater,datasheet[19]])
            pturbspring = np.concatenate([pturbspring,datasheet[20]])
            pturbmem = np.concatenate([pturbmem,datasheet[21]])
            pmem1 = np.concatenate([pmem1,datasheet[22]])
            pmem2 = np.concatenate([pmem2,datasheet[23]])
            targetencoder = np.concatenate([targetencoder,datasheet[24] / 1e6])
            posencoder = np.concatenate([posencoder,datasheet[25] / 1e6])
            acc1 = np.concatenate([acc1,datasheet[26]])
            acc2 = np.concatenate([acc2,datasheet[27]])
            acc3 = np.concatenate([acc3,datasheet[28]])
            level = np.concatenate([level,(datasheet[29] -200) / 1000])
            radar = np.concatenate([radar,datasheet[32]])
            tempgenerator = np.concatenate([tempgenerator,datasheet[33]])
            tempkoeling = np.concatenate([tempkoeling,datasheet[34]])
            tempspring = np.concatenate([tempspring,datasheet[37]])

print(len(tijd))
tijd = list(tijd)
tijd_kopie = tijd.copy()
vorige_tijd = -max(tijd)
nieuwe_tijd = []
nieuwe_stroom = []
nieuwe_power = []
nieuwe_spanning = []
nieuwe_radar = []
nieuwe_pfloater = []
nieuwe_pturbspring = []
nieuwe_pturbmem = []
nieuwe_pspring_liquid = []
nieuwe_pspring_gas = []
nieuwe_pmem1 = []
nieuwe_pmem2 = []
nieuwe_level = []
nieuwe_targetencoder = []
nieuwe_posencoder = []
nieuwe_rpm = []

for i in range(len(tijd)):
    volgende_tijd = min(tijd_kopie)
    volgende_index = tijd.index(volgende_tijd)
    if vorige_tijd != volgende_tijd:
        nieuwe_tijd.append(volgende_tijd)
        nieuwe_stroom.append(stroom[volgende_index])
        nieuwe_power.append(power[volgende_index])
        nieuwe_spanning.append(spanning[volgende_index])
        nieuwe_radar.append(radar[volgende_index])
        nieuwe_pfloater.append(pfloater[volgende_index])
        nieuwe_pturbmem.append(pturbmem[volgende_index])
        nieuwe_pturbspring.append(pturbspring[volgende_index])
        nieuwe_pspring_liquid.append(pspring_liquid[volgende_index])
        nieuwe_pspring_gas.append(pspring_gas[volgende_index])
        nieuwe_pmem1.append(pmem1[volgende_index])
        nieuwe_pmem2.append(pmem2[volgende_index])
        nieuwe_level.append(level[volgende_index])
        nieuwe_targetencoder.append(targetencoder[volgende_index])
        nieuwe_posencoder.append(posencoder[volgende_index])
        nieuwe_rpm.append(rpm[volgende_index])
    vorige_tijd = volgende_tijd
    tijd_kopie.remove(vorige_tijd)
tijd = np.array(nieuwe_tijd)
stroom = np.array(nieuwe_stroom)
power = np.array(nieuwe_power)
spanning = np.array(nieuwe_spanning)
radar = np.array(nieuwe_radar)
pfloater = np.array(nieuwe_pfloater)
pturbmem = np.array(nieuwe_pturbmem)
pturbspring = np.array(nieuwe_pturbspring)
pspring_liquid = np.array(nieuwe_pspring_liquid)
pspring_gas = np.array(nieuwe_pspring_gas)
pmem1 = np.array(nieuwe_pmem1)
pmem2 = np.array(nieuwe_pmem2)
level = np.array(nieuwe_level)
targetencoder = np.array(nieuwe_targetencoder)
posencoder = np.array(nieuwe_posencoder)
rpm = np.array(nieuwe_rpm)

print(len(tijd))
np.save('drytest 2910_verwerkt/tijd.npy',tijd)
np.save('drytest 2910_verwerkt/stroom.npy',stroom)
np.save('drytest 2910_verwerkt/power.npy',power)
np.save('drytest 2910_verwerkt/spanning.npy',spanning)
np.save('drytest 2910_verwerkt/radar.npy',radar)
np.save('drytest 2910_verwerkt/pfloater.npy',pfloater)
np.save('drytest 2910_verwerkt/pturbmem.npy',pturbmem)
np.save('drytest 2910_verwerkt/pturbspring.npy',pturbspring)
np.save('drytest 2910_verwerkt/pspring_liquid.npy',pspring_liquid)
np.save('drytest 2910_verwerkt/pspring_gas.npy',pspring_gas)
np.save('drytest 2910_verwerkt/pmem1.npy',pmem1)
np.save('drytest 2910_verwerkt/pmem2.npy',pmem2)
np.save('drytest 2910_verwerkt/level.npy',level)
np.save('drytest 2910_verwerkt/targetencoder.npy',targetencoder)
np.save('drytest 2910_verwerkt/posencoder.npy',posencoder)
np.save('drytest 2910_verwerkt/rpm.npy',rpm)