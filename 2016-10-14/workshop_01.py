from pyplasm import T, CUBOID, STRUCT

def createSpace(beamDimensions,
                pillarDimensions,
                axesDistances,
                interstoryHeights):

    """
    Return a HPC value describing a space frame in reinforced concrete.

    Args:
        beamDimensions: a tuple containing beam section dimension (x, z)
        pillarDimensions: a tuple containing pillar section dimension (x, y)
        axesDistances: a list containing distances between pillar axes
        interstoryHeights: a list containing interstory heights
    Returns:
        a HPC value describing the space frame parameterized by the arguments

    """

    bx, bz = beamDimensions
    px, py = pillarDimensions

    floors = []

    beams = None   # struct of beams
    pillars = None # struct of pillars

    for height in interstoryHeights:

        # if structures don't exists we create them
        if not beams and not pillars:
            pillar = CUBOID([px, py, height])
            beamsList = []
            pillarsList = [pillar]
            beamSize = py / 2.0 # the first beam is half py size wider than the
                                # others so we account for this

            for i in range(0, len(axesDistances) - 1):
                distance = axesDistances[i]
                beamSize += distance + py
                beamsList += [CUBOID([bx, beamSize, bz]), T(2)(beamSize)]
                pillarsList += [T(2)(distance + py), pillar]
                beamSize = 0

            # the last beam has the same width as the first
            distance = axesDistances[-1]
            beamsList.append(CUBOID([bx, distance + py + (py / 2.0), bz]))
            pillarsList += [T(2)(distance + py), pillar]

            # structures
            beams = STRUCT(beamsList)
            pillars = STRUCT(pillarsList)

        floors += [pillars, T(3)(height), beams, T(3)(bz)]

    return STRUCT(floors)
