import numpy as np
from scipy.fft import rfft, irfft
from os import walk

for path, bestandsnamen, bestanden in walk('drytest 0607'):
    for bestandsnaam in bestanden:
        bestand = open('drytest 0607/'+bestandsnaam)
        firstline = 0
        lines= len(bestand.readlines()) - 9
        if lines % 2 == 1:
            lines -= 1
        bestand = open('drytest 0607/'+bestandsnaam)

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
            tijd = datasheet[0]
            stroom = datasheet[2]           #CTOAC
            power = datasheet[7]            #CTOOP
            spanning = datasheet[8]         #CTOOV
            rpm = datasheet[9]              #CTOSF
            # fourier = rfft(datasheet[20])
            # trap = np.where(np.linspace(0,len(tijd)/(2*(tijd[-1]-tijd[0])),int(len(datasheet[0])/2+1))<.2,1,0)
            # datasheet[20] = irfft(fourier*trap)
            pspring_liquid = datasheet[11]  #PT_01
            pspring_gas = datasheet[12]     #PT_05
            pmem_onder = datasheet[13]      #PT_07
            pfloater = datasheet[14]        #PT_08
            pturbspring = datasheet[15]     #PT_09
            pturbmem = datasheet[16]        #PT_10
            pmem = datasheet[17]            #PT_11
            pmem_midden = datasheet[19]     #PT_14
            pmem_boven = datasheet[20]      #PT_15
            level = datasheet[21]           #SL_01
            radar = datasheet[22]           #SO_01
            tempgenerator = datasheet[23]   #ST_01
            tempkoeling = datasheet[24]     #ST_02
            tempspring = datasheet[25]      #ST_06
            tempfloater = datasheet[26]     #ST_07

        else:
            tijd = np.concatenate([tijd,datasheet[0]])
            stroom = np.concatenate([stroom,datasheet[2]])              #CTOAC
            power = np.concatenate([power,datasheet[7]])                #CTOOP
            spanning = np.concatenate([spanning,datasheet[8]])          #CTOOV
            rpm = np.concatenate([rpm,datasheet[9]])                    #CTOSF
            pspring_liquid = np.concatenate([pspring_liquid,datasheet[11]])     #PT_01
            pspring_gas = np.concatenate([pspring_gas,datasheet[12]])           #PT_05
            pmem_onder = np.concatenate([pmem_onder,datasheet[13]])             #PT_07
            pfloater = np.concatenate([pfloater,datasheet[14]])                 #PT_08
            pturbspring = np.concatenate([pturbspring,datasheet[15]])           #PT_09
            pturbmem = np.concatenate([pturbmem,datasheet[16]])                 #PT_10
            pmem = np.concatenate([pmem,datasheet[17]])                         #PT_11
            pmem_midden = np.concatenate([pmem_midden,datasheet[19]])           #PT_14
            pmem_boven = np.concatenate([pmem_boven,datasheet[20]])             #PT_15
            level = np.concatenate([level,datasheet[21]])                       #SL_01
            radar = np.concatenate([radar,datasheet[22]])                       #SO_01
            tempgenerator = np.concatenate([tempgenerator,datasheet[23]])       #ST_01
            tempkoeling = np.concatenate([tempkoeling,datasheet[24]])           #ST_02
            tempspring = np.concatenate([tempspring,datasheet[25]])             #ST_06
            tempfloater = np.concatenate([tempfloater,datasheet[26]])           #ST_07

print(len(tijd))
tijd = list(tijd)
tijd_kopie = tijd.copy()
vorige_tijd = -max(tijd)

nieuwe_tijd = []
nieuwe_stroom = []
nieuwe_power = []
nieuwe_spanning = []
nieuwe_rpm = []
nieuwe_pspring_liquid = []
nieuwe_pspring_gas = []
nieuwe_pmem_onder = []
nieuwe_pfloater = []
nieuwe_pturbspring = []
nieuwe_pturbmem = []
nieuwe_pmem = []
nieuwe_pmem_midden = []
nieuwe_pmem_boven = []
nieuwe_level = []
nieuwe_radar = []
nieuwe_tempgenerator = []
nieuwe_tempkoeling = []
nieuwe_tempspring = []
nieuwe_tempfloater = []

for i in range(len(tijd)):
    volgende_tijd = min(tijd_kopie)
    volgende_index = tijd.index(volgende_tijd)
    if vorige_tijd != volgende_tijd:
        nieuwe_tijd.append(volgende_tijd)
        nieuwe_stroom.append(stroom[volgende_index])
        nieuwe_power.append(power[volgende_index])
        nieuwe_spanning.append(spanning[volgende_index])
        nieuwe_rpm.append(rpm[volgende_index])
        nieuwe_pspring_liquid.append(pspring_liquid[volgende_index])
        nieuwe_pspring_gas.append(pspring_gas[volgende_index])
        nieuwe_pmem_onder.append(pmem_onder[volgende_index])
        nieuwe_pfloater.append(pfloater[volgende_index])
        nieuwe_pturbspring.append(pturbspring[volgende_index])
        nieuwe_pturbmem.append(pturbmem[volgende_index])
        nieuwe_pmem.append(pmem[volgende_index])
        nieuwe_pmem_midden.append(pmem_midden[volgende_index])
        nieuwe_pmem_boven.append(pmem_boven[volgende_index])
        nieuwe_level.append(level[volgende_index])
        nieuwe_radar.append(radar[volgende_index])
        nieuwe_tempgenerator.append(tempgenerator[volgende_index])
        nieuwe_tempkoeling.append(tempkoeling[volgende_index])
        nieuwe_tempspring.append(tempspring[volgende_index])
        nieuwe_tempfloater.append(tempfloater[volgende_index])

    vorige_tijd = volgende_tijd
    tijd_kopie.remove(vorige_tijd)

tijd = np.array(nieuwe_tijd)
stroom = np.array(nieuwe_stroom)
power = np.array(nieuwe_power)
spanning = np.array(nieuwe_spanning)
rpm = np.array(nieuwe_rpm)
pspring_liquid = np.array(nieuwe_pspring_liquid)
pspring_gas = np.array(nieuwe_pspring_gas)
pmem_onder = np.array(nieuwe_pmem_onder)
pfloater = np.array(nieuwe_pfloater)
pturbspring = np.array(nieuwe_pturbspring)
pturbmem = np.array(nieuwe_pturbmem)
pmem = np.array(nieuwe_pmem)
pmem_midden = np.array(nieuwe_pmem_midden)
pmem_boven = np.array(nieuwe_pmem_boven)
level = np.array(nieuwe_level)
radar = np.array(nieuwe_radar)
tempgenerator = np.array(nieuwe_tempgenerator)
tempkoeling = np.array(nieuwe_tempkoeling)
tempspring = np.array(nieuwe_tempspring)
tempfloater = np.array(nieuwe_tempfloater)

tijd -= tijd[1]
tijd /= 1000

np.save('drytest 0607_verwerkt/tijd.npy',tijd[1:])
np.save('drytest 0607_verwerkt/stroom.npy',stroom[1:])
np.save('drytest 0607_verwerkt/power.npy',power[1:])
np.save('drytest 0607_verwerkt/spanning.npy',spanning[1:])
np.save('drytest 0607_verwerkt/rpm.npy',rpm[1:])
np.save('drytest 0607_verwerkt/pspring_liquid.npy',pspring_liquid[1:])
np.save('drytest 0607_verwerkt/pspring_gas.npy',pspring_gas[1:])
np.save('drytest 0607_verwerkt/pmem_onder.npy',pmem_onder[1:])
np.save('drytest 0607_verwerkt/pfloater.npy',pfloater[1:])
np.save('drytest 0607_verwerkt/pturbspring.npy',pturbspring[1:])
np.save('drytest 0607_verwerkt/pturbmem.npy',pturbmem[1:])
np.save('drytest 0607_verwerkt/pmem.npy',pmem[1:])
np.save('drytest 0607_verwerkt/pmem_midden.npy',pmem_midden[1:])
np.save('drytest 0607_verwerkt/pmem_boven.npy',pmem_boven[1:])
np.save('drytest 0607_verwerkt/level.npy',level[1:])
np.save('drytest 0607_verwerkt/radar.npy',radar[1:])
np.save('drytest 0607_verwerkt/tempgenerator.npy',tempgenerator[1:])
np.save('drytest 0607_verwerkt/tempkoeling.npy',tempkoeling[1:])
np.save('drytest 0607_verwerkt/tempspring.npy',tempspring[1:])
np.save('drytest 0607_verwerkt/tempfloater.npy',tempfloater[1:])