import matplotlib.pyplot as plt
import numpy as np
from math import atan2,degrees
from modelParams import SymphonyParams as SP
from modelParams import GeneralParams as GP

def labelLine(line,x,label=None,align=True,**kwargs):

    ax = line.axes
    xdata = line.get_xdata()
    ydata = line.get_ydata()

    if (x < xdata[0]) or (x > xdata[-1]):
        print('x label location is outside data range!')
        return

    #Find corresponding y co-ordinate and angle of the line
    ip = 1
    for i in range(len(xdata)):
        if x < xdata[i]:
            ip = i
            break

    y = ydata[ip-1] + (ydata[ip]-ydata[ip-1])*(x-xdata[ip-1])/(xdata[ip]-xdata[ip-1])

    if not label:
        label = line.get_label()

    if align:
        #Compute the slope
        dx = xdata[ip] - xdata[ip-1]
        dy = ydata[ip] - ydata[ip-1]
        ang = degrees(atan2(dy,dx))

        #Transform to screen co-ordinates
        pt = np.array([x,y]).reshape((1,2))
        trans_angle = ax.transData.transform_angles(np.array((ang,)),pt)[0]

    else:
        trans_angle = 0

    #Set a bunch of keyword arguments
    if 'color' not in kwargs:
        kwargs['color'] = line.get_color()

    if ('horizontalalignment' not in kwargs) and ('ha' not in kwargs):
        kwargs['ha'] = 'center'

    if ('verticalalignment' not in kwargs) and ('va' not in kwargs):
        kwargs['va'] = 'center'

    if 'backgroundcolor' not in kwargs:
        kwargs['backgroundcolor'] = ax.get_facecolor()

    if 'clip_on' not in kwargs:
        kwargs['clip_on'] = True

    if 'zorder' not in kwargs:
        kwargs['zorder'] = 2.5

    ax.text(x,y,label,rotation=trans_angle,**kwargs)

def labelLines(lines,align=True,xvals=None,**kwargs):

    ax = lines[0].axes
    labLines = []
    labels = []

    #Take only the lines which have labels other than the default ones
    for line in lines:
        label = line.get_label()
        if "_line" not in label:
            labLines.append(line)
            labels.append(label)

    if xvals is None:
        xmin,xmax = ax.get_xlim()
        xvals = np.linspace(xmin,xmax,len(labLines)+2)[1:-1]

    for line,x,label in zip(labLines,xvals,labels):
        labelLine(line,x,label,align,**kwargs)

z = np.linspace(-2,2,4001)
# a = 0.46136336632294683


# profiel = SP.profileDiam                            # profiel[0]^=z[0]
profiel = 1.85+0.032*(np.arctan(20*(z+1.7))+np.arctan(20*(z-1.7)))*2/np.pi
plt.plot(profiel,z)
plt.show()

offset = np.pi/4*(profiel[2000]-profiel)+ 0.025
dz_offset = (z+offset)[1:]-(z+offset)[:-1]
dz_offset = (np.array([0]+list(dz_offset))+np.array(list(dz_offset)+[0])) / 2

# ------------------------------------------------------------------------
# Hydrostatische kracht

ztop = SP.clearance + SP.lstpp + SP.maxstroke/2 - z;                        # distance between water surface and pressure point [m]
zbotmem = SP.clearance + SP.h_Ltfbm + SP.maxstroke/2  - (z+offset)/2;       # distance between water surface and bottom membrane[m]
zbotfloat = SP.clearance + SP.heightfloater + SP.maxstroke/2 - z;           # distance between water surface and bottom of the floater [m]
zflens = SP.clearance + SP.flenshoogte + SP.maxstroke / 2 - z

Atop = np.pi/4*SP.floaterOuterDiamUp**2                                     # Cumulatief: outer up
Aflens = np.pi/4*(SP.floaterOuterDiamDown**2 - SP.floaterOuterDiamUp**2)    # Cumulatief: outer down
Abottomfloater = np.pi/4*(SP.floaterOuterDiamDown**2 - profiel[-1]**2)      # Cumulatief: core + mem + profieldeel exposed
Abottommem = np.pi/4*(profiel**2-SP.floaterInnerDiamDown**2)                # Cumulatief: core + profieldeel exposed

Fhstop = -(GP.Patm + GP.rho*GP.g*ztop)*Atop
FhsFlens = -(GP.Patm + GP.rho*GP.g*zflens) * Aflens
Fhsbottomfloater = (GP.Patm + GP.rho*GP.g*zbotfloat) * Abottomfloater
Fhsbottommembrame = (GP.Patm + GP.rho*GP.g*zbotmem)* Abottommem / 2

hydrostatisch = Fhstop + Fhsbottommembrame + Fhsbottomfloater + FhsFlens

Fhsprofiel = np.zeros(len(z))
for etha in range(len(z)-1):
    if not etha:
        dA = 0
    else:
        dA = np.pi/4*(profiel[-etha-1]**2-profiel[-etha-2]**2)                  # Cumulatief: Core
    P = GP.Patm + GP.rho*GP.g*zbotmem[-etha-1]
    Fhsprofiel[-etha-2] = P*dA + Fhsprofiel[-etha-1]+np.pi/4*(profiel[-1]**2 - profiel[-etha-1]**2)*GP.rho*GP.g*dz_offset[-etha-1]

hydrostatisch += Fhsprofiel


# ------------------------------------------------------------------------
# zwaartekracht
zwaartekracht = - GP.g * SP.floaterMass


# ----------------------------------------------------------------------------
# Kracht door gasdruk van het bovendeel
opp = np.pi/8 * (SP.floaterInnerDiamUp**2 +SP.membrameInnerDiam**2)
oppervlak_floater = np.pi/4*SP.floaterOuterDiamUp**2
oppervlak_core = np.pi/4*SP.membrameInnerDiam**2
V0 = 0.8 + oppervlak_floater * 3.83 + 1.88 + (oppervlak_floater - oppervlak_core) * 1.51
V1 = V0+z*opp

oppervlak_m = np.pi / 4 * ((profiel-.034)**2 - (SP.floaterInnerDiamUp-.034)**2 )
F_gasdruk_tank_midden = 13.5e5 *oppervlak_m[2000]/2

P_midden = (-hydrostatisch[2000] - zwaartekracht - F_gasdruk_tank_midden) / opp

druk = P_midden * (V0/V1)
F_gasdruk_boven = druk * opp

# ----------------------------------------------------------------------------
# Gasdruk van de tank
F_gasdruk_tank = -hydrostatisch -zwaartekracht -F_gasdruk_boven
druk = 2*F_gasdruk_tank / oppervlak_m

plt.plot(z,hydrostatisch)
plt.plot(z,len(z)*[zwaartekracht])
plt.plot(z,F_gasdruk_boven)
plt.plot(z,F_gasdruk_tank)
plt.show()

plt.title(P_midden/1e5)
plt.plot(z,druk/1e5)
plt.show()