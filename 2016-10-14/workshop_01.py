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

    sections = []

    for distance in axesDistances:
        beamGroup = []
        structureHeight = bz  #to account for last beam

        for height in interstoryHeights:
            structureHeight += height
            beam = CUBOID([bx, distance, bz])
            beamGroup += [T(3)(height), beam]

        beams = STRUCT(beamGroup)
        pillar = CUBOID([px, py, structureHeight])
        sections += [pillar, T(2)(py), beams, T(2)(distance)]

    # last pillar
    pillar = CUBOID([px, py, structureHeight])
    sections.append(pillar)

    return STRUCT(sections)