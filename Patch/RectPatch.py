""" Functions dealing with rectangular patch antenna."""
import math
import numpy as np
from math import cos, sin, sqrt, atan2, acos

def PatchFunction(thetaInDeg, phiInDeg, Freq, W, L, h, Er):
    """
    Taken from Design_patchr
    Calculates total E-field pattern for patch as a function of theta and phi
    Patch is assumed to be resonating in the (TMx 010) mode.
    E-field is parallel to x-axis
    W......Width of patch (m)
    L......Length of patch (m)
    h......Substrate thickness (m)
    Er.....Dielectric constant of substrate
    Refrence C.A. Balanis 2nd Edition Page 745
    """
    lamba = 3e8 / Freq

    theta_in = math.radians(thetaInDeg)
    phi_in = math.radians(phiInDeg)

    ko = 2 * math.pi / lamba

    xff, yff, zff = sph2cart1(999, theta_in, phi_in)                            # Rotate coords 90 deg about x-axis to match array_utils coord system with coord system used in the model.
    xffd = zff
    yffd = xff
    zffd = yff
    r, thp, php = cart2sph1(xffd, yffd, zffd)
    phi = php
    theta = thp

    if theta == 0:
        theta = 1e-9                                                              # Trap potential division by zero warning

    if phi == 0:
        phi = 1e-9

    Ereff = ((Er + 1) / 2) + ((Er - 1) / 2) * (1 + 12 * (h / W)) ** -0.5        # Calculate effictive dielectric constant for microstrip line of width W on dielectric material of constant Er

    F1 = (Ereff + 0.3) * (W / h + 0.264)                                        # Calculate increase length dL of patch length L due to fringing fields at each end, giving total effective length Leff = L + 2*dL
    F2 = (Ereff - 0.258) * (W / h + 0.8)
    dL = h * 0.412 * (F1 / F2)

    Leff = L + 2 * dL

    Weff = W                                                                    # Calculate effective width Weff for patch, uses standard Er value.
    heff = h * sqrt(Er)

    # Patch pattern function of theta and phi, note the theta and phi for the function are defined differently to theta_in and phi_in
    Numtr2 = sin(ko * heff * cos(phi) / 2)
    Demtr2 = (ko * heff * cos(phi)) / 2
    Fphi = (Numtr2 / Demtr2) * cos((ko * Leff / 2) * sin(phi))

    Numtr1 = sin((ko * heff / 2) * sin(theta))
    Demtr1 = ((ko * heff / 2) * sin(theta))
    Numtr1a = sin((ko * Weff / 2) * cos(theta))
    Demtr1a = ((ko * Weff / 2) * cos(theta))
    Ftheta = ((Numtr1 * Numtr1a) / (Demtr1 * Demtr1a)) * sin(theta)

    # Due to groundplane, function is only valid for theta values :   0 < theta < 90   for all phi
    # Modify pattern for theta values close to 90 to give smooth roll-off, standard model truncates H-plane at theta=90.
    # PatEdgeSF has value=1 except at theta close to 90 where it drops (proportional to 1/x^2) to 0

    rolloff_factor = 0.5                                                       # 1=sharp, 0=softer
    theta_in_deg = theta_in * 180 / math.pi                                          # theta_in in Deg
    F1 = 1 / (((rolloff_factor * (abs(theta_in_deg) - 90)) ** 2) + 0.001)       # intermediate calc
    PatEdgeSF = 1 / (F1 + 1)                                                    # Pattern scaling factor

    UNF = 1.0006                                                                # Unity normalisation factor for element pattern

    if theta_in <= math.pi / 2:
        Etot = Ftheta * Fphi * PatEdgeSF * UNF                                   # Total pattern by pattern multiplication
    else:
        Etot = 0

    return Etot


def sph2cart1(r, th, phi):
  x = r * cos(phi) * sin(th)
  y = r * sin(phi) * sin(th)
  z = r * cos(th)

  return x, y, z


def cart2sph1(x, y, z):
  r = sqrt(x**2 + y**2 + z**2) + 1e-15
  th = acos(z / r)
  phi = atan2(y, x)

  return r, th, phi


def GetPatchFields(PhiStart, PhiStop, ThetaStart, ThetaStop, Freq, W, L, h, Er):
    """"
    Calculates the E-field for range of thetaStart-thetaStop and phiStart-phiStop
    Returning a numpy array of form - fields[phiDeg][thetaDeg] = eField
    W......Width of patch (m)
    L......Length of patch (m)
    h......Substrate thickness (m)
    Er.....Dielectric constant of substrate
    """
    fields = np.ones((PhiStop, ThetaStop))                                      # Create initial array to hold e-fields for each position

    for phiDeg in range(PhiStart, PhiStop):
            for thetaDeg in range(ThetaStart, ThetaStop):                       # Iterate over all Phi/Theta combinations
                eField = PatchFunction(thetaDeg, phiDeg, Freq, W, L, h, Er)     # Calculate the field for current Phi, Theta
                fields[phiDeg][thetaDeg] = eField                               # Update array with e-field

    return fields





def DesignPatch(Er, h, Freq):
    """
    Returns the patch_config parameters for standard lambda/2 rectangular microstrip patch. Patch length L and width W are calculated and returned together with supplied parameters Er and h.
    Returned values are in the same format as the global patchr_config variable, so can be assigned directly. The patchr_config variable is of the following form [Er,W,L,h].
    Usage: patchr_config=design_patchr(Er,h,Freq)
    Er.....Relative dielectric constant
    h......Substrate thickness (m)
    Freq...Frequency (Hz)
    e.g. patchr_config=design_patchr(3.43,0.7e-3,2e9)
    """
    Eo = 8.854185e-12

    lambd = 3e8 / Freq
    lambdag = lambd / sqrt(Er)

    W = (3e8 / (2 * Freq)) * sqrt(2 / (Er + 1))

    Ereff = ((Er + 1) / 2) + ((Er - 1) / 2) * (1 + 12 * (h / W)) ** -0.5                              # Calculate effictive dielectric constant for microstrip line of width W on dielectric material of constant Er

    F1 = (Ereff + 0.3) * (W / h + 0.264)                                                 # Calculate increase length dL of patch length L due to fringing fields at each end, giving actual length L = Lambda/2 - 2*dL
    F2 = (Ereff - 0.258) * (W / h + 0.8)
    dL = h * 0.412 * (F1 / F2)

    lambdag = lambd / sqrt(Ereff)
    L = (lambdag / 2) - 2 * dL

    print('Rectangular Microstrip Patch Design')
    print("Frequency: " + str(Freq))
    print("Dielec Const, Er : " + str(Er))
    print("Patch Width,  W: " + str(W) + "m")
    print("Patch Length,  L: " + str(L) + "m")
    print("Patch Height,  h: " + str(h) + "m")

    return W, L, h, Er

if __name__ == "__main__":
    """Some example patches with various thickness & Er."""
    print("Patch.py")

    freq = 14e9
    Er = 3.66                                                           # RO4350B

    h = 0.101e-3
    W, L, h, Er = DesignPatch(Er, h, freq)
    fields = PatchEHPlanePlot(freq, W, L, h, Er)
    #np.savetxt('fields.csv', fields, delimiter=',')
    SurfacePlot(fields, freq, W, L, h, Er)

    h = 1.524e-3
    W, L, h, Er = DesignPatch(Er, h, freq)                              # RO4350B
    fields = PatchEHPlanePlot(freq, W, L, h, Er)
    SurfacePlot(fields, freq, W, L, h, Er)

    fields = PatchEHPlanePlot(freq, 10.7e-3, 10.47e-3, 3e-3, 2.5)                # Random
    SurfacePlot(fields, freq, W, L, h, Er)
