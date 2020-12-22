import argparse
import numpy as np
import math
import RectPatch
from RectPatch import PatchFunction, cart2sph1, sph2cart1
import ArrayFactor
from ArrayFactor import CalculateRelativePhase


def FieldSumPatchElement(element, Freq, W, L, h, Er):
    """
    Summation of field contributions from each patch element in array, at frequency freq for theta 0°-95°, phi 0°-360°.
    Element = xPos, yPos, zPos, ElementAmplitude, ElementPhaseWeight
    Returns arrayFactor[theta, phi, elementSum]
    """

    arrayFactor = np.full((360, 90), 1e-9 + 0j)

    Lambda = 3e8 / Freq

    for theta in range(90):
        for phi in range(360):                                                                                                      # For all theta/phi positions
            elementSum = 1e-9 + 0j

            xff, yff, zff = sph2cart1(999, math.radians(theta), math.radians(phi))                                                  # Find point in far field

            # find local theta/phi, calculate field contribution and add to summation for point
            xlocal = xff - element[0]
            ylocal = yff - element[1]                                                                                           # Calculate local position in cartesian
            zlocal = zff - element[2]

            r, thetaLocal, phiLocal = cart2sph1(xlocal, ylocal, zlocal)                                                         # Convert local position to spherical

            patchFunction = PatchFunction(math.degrees(thetaLocal), math.degrees(phiLocal), Freq, W, L, h, Er)            # Patch element pattern for local theta, phi

            if patchFunction != 0:                                                                                              # Sum each elements contribution
                relativePhase = CalculateRelativePhase(element, Lambda, math.radians(theta), math.radians(phi))                 # Find relative phase for current element
                elementSum += element[3] * patchFunction * math.e ** ((relativePhase + element[4]) * 1j)                        # Element contribution = Amp * e^j(Phase + Phase Weight)

            arrayFactor[phi][theta] = elementSum

    return arrayFactor
