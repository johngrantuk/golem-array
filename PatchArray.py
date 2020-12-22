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


def GenerateElementArray(X_Patches, Y_Patches, patchSpace):
    noPatches = X_Patches * Y_Patches
    ElementArray = np.empty((noPatches, 5))
    if(Y_Patches == 1):
        # TO DO X = 1
        min = -1.0 * ((X_Patches/2 - 1) + 0.5) * patchSpace
        for xNo in range(X_Patches):
            ElementArray[xNo] = [min, 0, 0, 1, 0]
            min += patchSpace
    else:
        patchCount = 0
        minY = -1.0 * ((Y_Patches/2 - 1) + 0.5) * patchSpace
        for y in range(Y_Patches):
            minX = -1.0 * ((X_Patches/2 - 1) + 0.5) * patchSpace
            for x in range(X_Patches):
                ElementArray[patchCount] = [minX, minY, 0, 1, 0]
                minX += patchSpace
                patchCount += 1
            minY += patchSpace

    return ElementArray

"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Design Your Own Antenna Array - Powered By Golem')
    parser.add_argument('--freq', type=float, help='Frequency of operation', default=14e9)
    parser.add_argument('--width', type=float, help='Width Of Patch', default=10.7e-3)
    parser.add_argument('--length', type=float, help='Length Of Patch', default=10.7e-3)
    parser.add_argument('--h', type=float, help='Height of Patch', default=3e-3)
    parser.add_argument('--Er', type=float, help='Permittivity', default=2.5)
    parser.add_argument('--xpatches', type=int, help='Number of X Patches', default=10)
    parser.add_argument('--ypatches', type=int, help='Number of Y Patches', default=1)
    parser.add_argument('--patchSpace', type=float, help='Space Between Patches', default=0.06)

    args = parser.parse_args()
    freq = args.freq
    W = args.width
    L = args.length
    h = args.h
    Er = args.Er
    X_Patches = args.xpatches
    Y_Patches = args.ypatches
    patchSpace = args.patchSpace

    ElementArray = GenerateElementArray(X_Patches, Y_Patches, patchSpace)

    noPatches = len(ElementArray)
    elementField = np.empty((noPatches, 360, 90))

    for patchNo in range(noPatches):
        elementField[patchNo] = FieldSumPatchElement(ElementArray[patchNo], freq, W, L, h, Er)
        # TODO - This will be saved from worker
        np.savetxt('./plotFiles/patch' + str(patchNo) + '.csv', elementField[patchNo], delimiter=',')

    generatePlots(noPatches)
"""
