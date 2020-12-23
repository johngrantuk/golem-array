import numpy as np
import math

def ArrayFactor(ElementArray, Freq):
    """
    Summation of field contributions from each element in array, at frequency freq at theta 0°-95°, phi 0°-360°.
    Element = xPos, yPos, zPos, ElementAmplitude, ElementPhaseWeight
    Returns arrayFactor[theta, phi, elementSum]
    """

    arrayFactor = np.ones((360, 90))

    Lambda = 3e8 / Freq

    for theta in range(90):
        for phi in range(360):                                                                                                      # For all theta/phi positions
            elementSum = 1e-9 + 0j

            for element in ElementArray:                                                                                            # Summation of each elements contribution at theta/phi position.
                relativePhase = CalculateRelativePhase(element, Lambda, math.radians(theta), math.radians(phi))                     # Find relative phase for current element
                elementSum += element[3] * math.e ** ((relativePhase + element[4]) * 1j)                                            # Element contribution = Amp * e^j(Phase + Phase Weight)

            arrayFactor[phi][theta] = abs(elementSum)
            #arrayFactor[phi][theta] = elementSum.real

    return arrayFactor


def CalculateRelativePhase(Element, Lambda, theta, phi):
    """
    Incident wave treated as plane wave. Phase at element is referred to phase of plane wave at origin.
    Element = xPos, yPos, zPos, ElementAmplitude, ElementPhaseWeight
    theta & phi in radians
    See Eqn 3.1 @ https://theses.lib.vt.edu/theses/available/etd-04262000-15330030/unrestricted/ch3.pdf
    """
    phaseConstant = (2 * math.pi / Lambda)

    xVector = Element[0] * math.sin(theta) * math.cos(phi)
    yVector = Element[1] * math.sin(theta) * math.sin(phi)
    zVector = Element[2] * math.cos(theta)

    phaseOfIncidentWaveAtElement = phaseConstant * (xVector + yVector + zVector)

    return phaseOfIncidentWaveAtElement
