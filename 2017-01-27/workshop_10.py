import math
from pyplasm import *
from larlib import *

# utility functions

"""
    Wrapper to COLOR with RGBA 0-255 scale

    Args:
        r:  the value of the red channel. An
            integer between 0 and 255.
        b:  the value of the blue channel. An
            integer between 0 and 255.
        g:  the value of the green channel. An
            integer between 0 and 255.
        a:  the value of the alpha channel. A
            float between 0 and 1.
            Default value: 1

    Returns
        The COLOR function with the desired color
"""
rgba = lambda r, g, b, a=1: COLOR([r / 255.0, g / 255.0, b /255.0, a])

"""
    Easy texture application

    Args:
        pol: the HPC model to which apply the texture
        txt: the texture to apply (path to an image file). If txt is None,
             or gives a false boolean value, then no texture is applied
    Returns:
        An HPC model with the desired texture applied, or the HPC model
        passed as input if no texture is specified
"""
apply_texture = lambda pol, txt: TEXTURE(txt)(pol) if txt else pol

def getStepParameters(radius, z):
    """
    Processes input parameters

    Args:
        x: area size on the x axis
        x: area size on the y axis
        x: area size on the z axis

    Returns:
        stepDim: tuple containing step dimension (x, y, z)
        rotationAngle: angle to witch rotate every step
        internalRadius: radius of the internal (void) circle. Could be 0
      """
    # steps dimension for good practice
    STEP_SIZE = (0.4, 0.8, 0.16)

    radius = radius / 2.0
    stepY = radius if STEP_SIZE[1] > radius else STEP_SIZE[1]
    internalRadius = radius - stepY

    rotationAngle = ASIN(STEP_SIZE[0] / stepY)

    return ((STEP_SIZE[0], stepY, STEP_SIZE[2]),
            rotationAngle,
            internalRadius)

def ggpl_spiral_stairs(dx, dy, dz):
    """
    Returns an HPC value describing a set of spiral stairs contained
    in an area defined by input parameters.

    Args:
        x: area size on the x axis
        x: area size on the y axis
        x: area size on the z axis

    Returns:
        area: an HPC value describing a set of stairs contained in a
              boxed area defined by input parameters
    """
    stepDim, angle, radius = getStepParameters(min(dx, dy), dz)
    stepX, stepY, stepZ = stepDim

    stepsNumber = int(dz / stepZ)

    rise = CUBOID([1.3 * stepX, stepY, stepZ])
    step = STRUCT([T(2)(radius), rise, T(3)(stepZ)])

    rotation = 0
    steps = []

    # create stairs
    for i in range (0, stepsNumber + 1):
        steps += [R([1, 2])(rotation)(step), T(3)(stepZ)]
        rotation += angle

    # uncomment to make a central column
    # column = CYLINDER([radius, dz])(1000)
    # return STRUCT([column] + steps)

    return STRUCT(steps)

def addNeg(l, x):
    """
        Negates the positive number x and adds it to the list l.
        If the last element of l is negative, then adds -x to it,
        otherwise appends -x to l.

        Args:
            x:  the number to negate and append
            l:  the list to append

        Returns:
            N/A
    """
    if l != [] and l[-1] < 0:
        l[-1] -= x
    else:
        l.append(-x)


def glassStruct(X, Y, Z, occupancy, (glassColor, structColor)):
    """
        Creates a glass structure described by the input args.

        Args:
            X:         float list of lateral quotes (X-axis)
            Y:         float list of lateral quotes (Y-axis)
            Z:         float list of lateral quotes (Z-axis).
                       Only the first two values are used:
                       The first value for the glass depth,
                       the second value for the struct depth
            occupancy: a list of integer lists representing
                       the incidence matrix of X on Y.
                       If occupancy[i][j] is 1, then the struct
                       is present, else there is glass
            glassColor: glass color
            structColor: struct color
        Returns
            An HPC value representing the desired structure
    """

    def aux(dx, dy, dz):
        """
            glassStruct auxiliary function. Creates the glass
            structure and scales it by the parameters
            Args:
                dx: scaling value (X-axis)
                dy: scaling value (Y-axis)
                dz: scaling value (Z-axis)
            Returns
                An HPC value representing the desired structure,
                scaled accordingly
        """
        prodX = lambda *args: reduce(lambda x, y: PROD([x, y]), args)
        struct = []
        glass = []
        for iY in range(0, len(Y)):
            structV = []
            glassV = []
            for iX in range(0, len(X)):
                value = X[iX]
                if occupancy[iY][iX] == 1:
                    structV.append(value)
                    addNeg(glassV, value)
                else:
                    addNeg(structV, value)
                    glassV.append(value)

            t = T([2])(Y[iY])
            if len(structV) > 1:
                struct.append(prodX(QUOTE(structV), QUOTE([Y[iY]]), QUOTE([Z[1]])))

            if len(glassV) > 1:
                glass.append(prodX(QUOTE(glassV), QUOTE([Y[iY]]), QUOTE([Z[0]])))

            struct.append(t)
            glass.append(t)

        final_struct = STRUCT(
            [
                T(3)(Z[1] / 2.0),
                rgba(*glassColor)(STRUCT(glass)),
                T(3)(-(Z[1] / 2.0)),
                rgba(*structColor)(STRUCT(struct))
            ])

        return STRUCT([S([1, 2, 3])([dx, dy, dz]), final_struct])
    return aux

def ggpl_window(X, Y, Z, occupancy):
    """
        Creates a window described by the input args.

        Args:
            X:         float list of lateral quotes (X-axis)
            Y:         float list of lateral quotes (Y-axis)
            Z:         float list of lateral quotes (Z-axis).
                       Only the first two values are used:
                       The first value for the glass depth,
                       the second value for the struct depth
            occupancy: a list of integer lists representing
                       the incidence matrix of X on Y.
                       If occupancy[i][j] is 1, then the struct
                       is present, else there is glass
        Returns
            An HPC value representing a window
    """
    return glassStruct(X, Y, Z, occupancy, ((182, 208, 249), (255, 255, 255)))

def ggpl_door(X, Y, Z, occupancy):
    """
        Creates a door described by the input args.

        Args:
            X:         float list of lateral quotes (X-axis)
            Y:         float list of lateral quotes (Y-axis)
            Z:         float list of lateral quotes (Z-axis).
                       Only the first two values are used:
                       The first value for the glass depth,
                       the second value for the struct depth
            occupancy: a list of integer lists representing
                       the incidence matrix of X on Y.
                       If occupancy[i][j] is 1, then the struct
                       is present, else there is glass
        Returns
            An HPC value representing a door
    """
    return glassStruct(X, Y, Z, occupancy, ((182, 208, 249), (0, 0, 0)))


def make_base(filename):
    """
    Creates an HPC from a .lines file

    Args:
        filename: the path of the .lines file
    Returns
        an HPC value created from the .lines file, scaled accordingly

    """
    p = []
    with open(filename) as f:
        for line in f.read().splitlines():
            values = map(lambda x: float(x), line.split(','))
            p.append(POLYLINE([[values[1], values[0]], [values[3], values[2]]]))

    return S([1, 2, 3])([0.015, 0.015, 0.015])(SOLIDIFY(STRUCT(p)))


def make_walls(filename, height):
    """
    Creates an HPC value representing walls from a .lines file

    Args:
        filename: the path of the .lines file
        height:   the desired height of the walls
    Returns
        an HPC value representing walls created from the .lines file
    """
    return OFFSET([0,0, height])(make_base(filename))


def make_floor(filename, height, texture):
    """
    Creates an HPC value representing a floor from a .lines file

    Args:
        filename: the path of the .lines file
        height:   the desired height of the floor
        texture:  the texture to apply to the HPC
    Returns
        an HPC value representing floors created from the .lines file
    """
    return apply_texture((OFFSET([0, 0, height])(make_base(filename))), texture)

def pairList(inputList):
    """
    Given a list L as input, returns a new list formed by couples of consecutive
    elements of L

    Example:
        input:  [e1, e2, e3, ... , eK]
        output: [[e1, e2], [e2, e3], ..., [eK - 1, eK], [eK, e1]]

    Args:
        inputList: the list to process

    Returns:
        outputList: a new list formed by couples of consecutive elements
                    of the input list
    """

    inputLen = len(inputList)
    outputList = []

    for i in range(0, inputLen - 1):
        outputList.append([inputList[i], inputList[i + 1]])

    if (inputLen > 0):
        outputList.append([inputList[inputLen - 1], inputList[0]])

    return outputList


def rotatePoints(directions, angle):
    """
    Given a list of directions L and an angle A as input, returns a list of points
    A direction is represented with a list composed of two element ([point, quadrant]),
    where point is a list with three integers describing the point coordinates ([x, y, z]),
    while quadrant is an integer 1 and 4 that determines the rotation for the x and y axis.
    If quadrant is zero then no rotation is applied to the first two coordinates.
    Angle represents the desired rotation angle for the z axis.

    Example:
        input:   [[[1, 1, 1], 2], [[3, 5, 7], 1], [[8, 5, 5], 4]], 0
        output:

    Args:
        directions: a list of directions
        angle:      the angle of rotation in the z axis

    Returns:
       points:      a list of points

    """

    factors = ((1, 1), (-1, 1), (-1, -1), (1, -1))

    points = []

    for point, quadrant in directions:

        if quadrant < 1 or quadrant > 4:
            fX, fY = (0, 0)
        else:
            fX, fY = factors[quadrant - 1]

        points.append(
            [
                point[0] + fX * (30 * math.cos(math.pi / 4)),
                point[1] + fY * (30 * math.sin(math.pi / 4)),
                point[2] + (30 * math.sin(angle))
            ])

    return points + [points[0]]

def ggpl_create_roof(verts, cells, angle, directions):
    """
    Given a list of verts, a list of cells, an angle and a
    list of directions, returns an HPC model representing a roof

    Args:
        verts: list of verts
        cells: list of cells
        angle: rotation angle (z axis)
        directions: list of directions

    Returns:
        An HPC model representing a roof
    """

    # determine "bottom" verts
    bottomVerts = rotatePoints(directions, angle)

    # create slopes and "upper" roof polygon
    bottom = pairList(bottomVerts)
    top = pairList(verts)

    slopes = []
    for i in range(0, len(top)):
        slopes.append(MKPOL([[
                              top[i][0], top[i][1],
                              bottom[i][0], bottom[i][1]
                             ],
                             [[1, 2, 3, 4]],
                             1]))

    roof = STRUCT([MKPOL([bottomVerts, cells, 1])] + slopes + [MKPOL([verts, cells, 1])])

    return apply_texture(roof, 'txt/roof.jpg')

house = {
    'floor_1' :
    {
        'height': 3,
        'pavement':
        [
            {
                'lines_file': 'lines/f1/ext_pavement.lines',
                'texture_file': 'lines/f1/ext.lines',
                'height': 0.05
            },
            {
                'lines_file': 'lines/f1/parquet.lines',
                'texture_file': 'txt/parquet.jpg',
                'height': 0.1
            },
            {
                'lines_file': 'lines/f1/bath_floor.lines',
                'texture_file': 'txt/parquet.jpg',
                'height': 0.1
            }
        ],
        'walls':
        [
            {
                'lines_file': 'lines/f1/ext_walls.lines',
                'texture_file': None,
                'height': 3
            },
            {
                'lines_file': 'lines/f1/int_walls.lines',
                'texture_file': None,
                'height': 3
            }
        ],
        'windows_loc':
        [
            {
                'lines_file': 'lines/f1/windows.lines',
                'texture_file': None,
                'height': 3
            }
        ],
        'doors_loc':
        [
            {
                'lines_file': 'lines/f1/doors.lines',
                'texture_file': None,
                'height': 3
            }
        ]
    },
    'floor_2' :
    {
        'height': 3,
        'pavement':
        [
            {
                'lines_file': 'lines/f2/parquet.lines',
                'texture_file': 'txt/parquet.jpg',
                'height': 0.1
            },
        ],
        'walls':
        [
            {
                'lines_file': 'lines/f2/ext_walls.lines',
                'texture_file': None,
                'height': 3
            }
        ],
        'windows_loc':
        [
            {
                'lines_file': 'lines/f2/windows.lines',
                'texture_file': None,
                'height': 3
            }
        ],
        'doors_loc':
        []

    },
    'stairs':
    {
        'lines_file': 'lines/f1/stairs.lines',
        'texture_file': None,
        'height': 3
    },
    'roof':
    {}
}

def ggpl_multistorey_house(house):

    def make_hpc(floor, key, func, *args):
        items = []
        for s in floor[key]:
            items.append(func(*[s[arg] for arg in args]))

        if len(items) > 1:
            return STRUCT(items)
        return items[0]

    house_hpc = []

    for f in ('floor_1', 'floor_2'):

        # make pavement

        floor_pavement = make_hpc(house[f], 'pavement', make_floor,
                                     'lines_file', 'height', 'texture_file')

        # make walls

        floor_walls = make_hpc(house[f], 'walls', make_walls,
                                  'lines_file', 'height')

        # make windows structure

        if (house[f].get('windows_loc')):
            floor_windows = STRUCT([make_walls(house[f]['windows_loc'][0]['lines_file'], 1),
                                    T(3)(2.5),
                                    make_walls(house[f]['windows_loc'][0]['lines_file'], 0.5)])
        # make stairs


        # make roof

        house_hpc += [floor_pavement, floor_walls, floor_windows, T(3)(house[f]['height'])]

    return STRUCT(house_hpc)
