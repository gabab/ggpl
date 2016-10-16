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

    for height in interstoryHeights:
        
        pillar = CUBOID([px, py, height])
        beams = []
        pillars = [pillar]
        beamWidth = py / 2.0 # the first beam is half py size wider than the
                             # others so we account for this using beamWidth

        for i in range(0, len(axesDistances) - 1):
            distance = axesDistances[i]
            beamWidth += distance + py
            beams += [CUBOID([bx, beamWidth, bz]), T(2)(beamWidth)]
            pillars += [T(2)(distance + py), pillar]
            beamWidth = 0

        distance = axesDistances[-1]

        # the last beam has the same width as the first. We add beamWidth
        # to account for the case where there are two pillars.
        beams.append(CUBOID([bx, distance + py + (py / 2.0) + beamWidth, bz]))

        # last pillar
        pillars += [T(2)(distance + py), pillar]

        floors += [STRUCT(pillars), T(3)(height), STRUCT(beams), T(3)(bz)]

    return STRUCT(floors)
