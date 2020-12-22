import PatchArray
from PatchArray import FieldSumPatchElement
import numpy as np

print("STARTING")
elementField = np.empty((1, 360, 90))
element = np.genfromtxt('element.csv', delimiter=',')
physics = np.genfromtxt('physics.csv', delimiter=',')
elementField[0] = FieldSumPatchElement(element, physics[0], physics[1], physics[2], physics[3], physics[4])
np.savetxt('patchresult.csv', elementField[0], delimiter=',')
print("DONE")
