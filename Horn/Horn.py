import numpy as np
import math
import ArrayFactor
from ArrayFactor import CalculateRelativePhase
from math import cos, sin, sqrt, atan2, acos

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

def FieldSumHorn(element, Freq):
    """
    Summation of field contributions from each horn element in array, at frequency freq for theta 0°-95°, phi 0°-360°.
    Horn pattern estimate using cos q(theta) function.
    Element = xPos, yPos, zPos, ElementAmplitude, ElementPhaseWeight
    Returns arrayFactor[theta, phi, elementSum]
    """
    arrayFactor = np.full((360, 90), 1e-9 + 0j)

    Lambda = 3e8 / Freq

    for theta in range(90):
        for phi in range(360):                                                                                                      # For all theta/phi positions
            elementSum = 1e-9 + 0j

            xff, yff, zff = sph2cart1(999, math.radians(theta), math.radians(phi))                                                  # Find point in far field

            if theta > 90:
                hornFunction = 0                                                                                                # Assume no radiation behind horn for simplification
            else:
                xlocal = xff - element[0]                                                                                       # Calculate local position in cartesian
                ylocal = yff - element[1]
                zlocal = zff - element[2]

                r, thetaLocal, phiLocal = cart2sph1(xlocal, ylocal, zlocal)                                                     # Convert local position to spherical

                hornFunction = math.cos(thetaLocal) ** 28                                                                       # Horn q function, q = 28

            if hornFunction != 0:                                                                                               # Sum each elements contribution
                relativePhase = CalculateRelativePhase(element, Lambda, math.radians(theta), math.radians(phi))                 # Find relative phase for current element
                elementSum += element[3] * hornFunction * math.e ** ((relativePhase + element[4]) * 1j)                         # Element contribution = Amp * e^j(Phase + Phase Weight)

            arrayFactor[phi][theta] = elementSum.real

    return arrayFactor
