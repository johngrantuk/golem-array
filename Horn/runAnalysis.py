import Horn
from Horn import FieldSumHorn
import numpy as np

print("STARTING")
elementField = np.empty((1, 360, 90))
element = np.genfromtxt('element.csv', delimiter=',')
physics = np.genfromtxt('physics.csv', delimiter=',')
elementField[0] = FieldSumHorn(element, physics[0])
np.savetxt('elementresult.csv', elementField[0], delimiter=',')
print("DONE")
