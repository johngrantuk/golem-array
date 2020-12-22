import numpy as np
import matplotlib.pyplot as plt
from RectPatch import sph2cart1
import math

def generatePlots(noElements, freq):
    """
    Generates plots using csv files of each element.
    """
    elementField = np.empty((noElements, 360, 90))
    fsp = np.full((360, 90), 1e-9 + 0j)

    # Generate list of element fields from saved files
    for elementNo in range(noElements):
        elementField[elementNo] = np.genfromtxt('./results/elementresult' + str(elementNo) + '.csv', delimiter=',')

    print(elementField[0])
    for theta in range(90):
        for phi in range(360):
            elementSum = 1e-9 + 0j
            for elementNo in range(noElements):
                elementSum += elementField[elementNo][phi][theta]

            fsp[phi][theta] = elementSum.real

    SurfacePlot_dB(20 * np.log10(abs(fsp)), freq, 0, 0, 0, 0)
    Xtheta = np.linspace(0, 90, 90)
    plt.plot(Xtheta, 20 * np.log10(abs(fsp[90, :])), label="H-plane (Phi=90°)")                          # Log = 20 * log10(E-field)
    plt.plot(Xtheta, 20 * np.log10(abs(fsp[0, :])), label="E-plane (Phi=0°)")
    plt.ylabel('Array Pattern (dB)')
    plt.xlabel('Theta (degs)')                                                                                  # Plot formatting
    plt.legend()
    plt.show()

def PatchEHPlanePlot(Freq, W, L, h, Er, isLog=True):
    """
    Plot 2D plots showing E-field for E-plane (phi = 0°) and the H-plane (phi = 90°).
    """

    fields = GetPatchFields(0, 360, 0, 90, Freq, W, L, h, Er)                                                   # Calculate the field at each phi, theta

    Xtheta = np.linspace(0, 90, 90)                                                                             # Theta range array used for plotting

    if isLog:                                                                                                   # Can plot the log scale or normal
        plt.plot(Xtheta, 20 * np.log10(abs(fields[90, :])), label="H-plane (Phi=90°)")                          # Log = 20 * log10(E-field)
        plt.plot(Xtheta, 20 * np.log10(abs(fields[0, :])), label="E-plane (Phi=0°)")
        plt.ylabel('E-Field (dB)')
    else:
        plt.plot(Xtheta, fields[90, :], label="H-plane (Phi=90°)")
        plt.plot(Xtheta, fields[0, :], label="E-plane (Phi=0°)")
        plt.ylabel('E-Field')

    plt.xlabel('Theta (degs)')                                                                                  # Plot formatting
    plt.title("Patch: \nW=" + str(W) + " \nL=" + str(L) +  "\nEr=" + str(Er) + " h=" + str(h) + " \n@" + str(Freq) + "Hz")
    plt.ylim(-40)
    plt.xlim((0, 90))

    start, end = plt.xlim()
    plt.xticks(np.arange(start, end, 5))
    plt.grid(b=True, which='major')
    plt.legend()
    plt.show()                                                                                                  # Show plot

    return fields                                                                                               # Return the calculated fields


def SurfacePlot(Fields, Freq, W, L, h, Er):
    """Plots 3D surface plot over given theta/phi range in Fields by calculating cartesian coordinate equivalent of spherical form."""

    print("Processing SurfacePlot...")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    phiSize = Fields.shape[0]                                                                                   # Finds the phi & theta range
    thetaSize = Fields.shape[1]

    X = np.ones((phiSize, thetaSize))                                                                           # Prepare arrays to hold the cartesian coordinate data.
    Y = np.ones((phiSize, thetaSize))
    Z = np.ones((phiSize, thetaSize))

    for phi in range(phiSize):                                                                                  # Iterate over all phi/theta range
        for theta in range(thetaSize):
            e = Fields[phi][theta]

            xe, ye, ze = sph2cart1(e, math.radians(theta), math.radians(phi))                                   # Calculate cartesian coordinates

            X[phi, theta] = xe                                                                                  # Store cartesian coordinates
            Y[phi, theta] = ye
            Z[phi, theta] = ze

    ax.plot_surface(X, Y, Z, color='b')                                                                         # Plot surface
    plt.ylabel('Y')
    plt.xlabel('X')
    #ax.set_zlim(0,40)                                                                                          # Plot formatting
    plt.title("Patch: \nW=" + str(W) + " \nL=" + str(L) +  "\nEr=" + str(Er) + " h=" + str(h) + " \n@" + str(Freq) + "Hz")
    plt.show()


def SurfacePlot_dB(Fields, Freq, W, L, h, Er):
    """Plots 3D surface plot (in dB) over given theta/phi range in Fields by calculating cartesian coordinate equivalent of spherical form."""

    print("Processing SurfacePlot...")

    minField = np.min(Fields)
    maxField = np.max(Fields)
    print(minField)
    print(maxField)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    phiSize = Fields.shape[0]                                                                                   # Finds the phi & theta range
    thetaSize = Fields.shape[1]

    X = np.ones((phiSize, thetaSize))                                                                           # Prepare arrays to hold the cartesian coordinate data.
    Y = np.ones((phiSize, thetaSize))
    Z = np.ones((phiSize, thetaSize))

    for phi in range(phiSize):                                                                                  # Iterate over all phi/theta range
        for theta in range(thetaSize):
            e = Fields[phi][theta] - minField

            xe, ye, ze = sph2cart1(e, math.radians(theta), math.radians(phi))                                   # Calculate cartesian coordinates

            X[phi, theta] = xe                                                                                  # Store cartesian coordinates
            Y[phi, theta] = ye
            Z[phi, theta] = ze

    ax.grid(False)
    ax.axis('off')
    dist = np.sqrt(X**2 + Y**2 + Z**2)
    dist_max = np.max(dist)
    axes_length = 1.2
    ax.plot([0, axes_length*dist_max], [0, 0], [0, 0], color = 'black')
    ax.plot([0, 0], [0, axes_length*dist_max], [0, 0], color = 'black')
    ax.plot([0, 0], [0, 0], [0, axes_length*dist_max], color = 'black')
    ax.text(axes_length*dist_max, 0, 0, 'x')
    ax.text(0, axes_length*dist_max, 0, 'y')
    ax.text(0, 0, axes_length*dist_max, 'z')

    surf = ax.plot_surface(X, Y, Z, cmap='jet', vmin=0, vmax=(maxField-minField), linewidth=0, antialiased=False)                                                                         # Plot surface
    plt.ylabel('Y')
    plt.xlabel('X')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])                                                                                          # Plot formatting
    #plt.title("Patch: \nW=" + str(W) + " \nL=" + str(L) +  "\nEr=" + str(Er) + " h=" + str(h) + " \n@" + str(Freq) + "Hz")
    myTicks = np.linspace(0,maxField - minField, 10)
    myTicksPrint = np.round(myTicks + minField,2)
    cbar = fig.colorbar(surf, ticks=myTicks, shrink=0.8)
    cbar.ax.set_yticklabels(myTicksPrint)
    plt.show()
