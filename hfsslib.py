class Point:
    def __init__(self, x=0.0, y=0.0, z=0.0, unit="mm"):
        self.x = x
        self.y = y
        self.z = z
        self.unit = unit

    def dot(self, pt):
        return self.x * pt.x + self.y * pt.y + self.z * pt.z

class Dimension:
    def __init__(self, width, height, unit="mm"):
        self.width = width
        self.height = height
        self.unit = unit

class Line:
    def __init__(self, points):
        self.points = points

    def generate(self):
        pts = ["NAME:PolylinePoints"]
        for pt in self.points:
            pts.append([
                    "NAME:PLPoint",
                    "X:="           , str(pt.x) + pt.unit,
                    "Y:="           , str(pt.y) + pt.unit,
                    "Z:="           , str(pt.z) + pt.unit
                ])
        segments = ["NAME:PolylineSegments"]
        for i in range(0, len(self.points)-1):
            segments.append(
                [
                        "NAME:PLSegment",
                        "SegmentType:="     , "Line",
                        "StartIndex:="      , i,
                        "NoOfPoints:="      , 2
                ])

        xsection = [
                "NAME:PolylineXSection",
                "XSectionType:="    , "None",
                "XSectionOrient:="  , "Auto",
                "XSectionWidth:="   , "0mm",
                "XSectionTopWidth:="    , "0mm",
                "XSectionHeight:="  , "0mm",
                "XSectionNumSegments:=" , "0",
                "XSectionBendType:="    , "Corner"
            ]

        content = ["NAME:PolylineParameters",
            "IsPolylineCovered:="   , True,
            "IsPolylineClosed:="    , False,
            pts,
            segments,
            xsection]

        return content

class Attr:
    def __init__(self, name, flags="", color="(132 132 193)", transparency=0, coord_system="Global", UDMId="", material="\"vacuum\"", solve_inside=True):
        self.name = name
        self.flags = flags
        self.color = color
        self.transparency = transparency
        self.coord_system = coord_system
        self.UDMId = UDMId
        self.material = material
        self.solve_inside = solve_inside

    def generate(self):
        return [
            "NAME:Attributes",
            "Name:="        , self.name,
            "Flags:="       , self.flags,
            "Color:="       , self.color,
            "Transparency:="    , self.transparency,
            "PartCoordinateSystem:=", self.coord_system,
            "UDMId:="       , self.UDMId,
            "MaterialValue:="   , self.material,
            "SolveInside:="     , self.solve_inside
        ]


class Polyline:
    def __init__(self, editor, line, attr):
        self.editor = editor
        self.line = line
        self.attr = attr

    def create(self):
        self.editor.CreatePolyline(self.line.generate(), self.attr.generate())
        return self

class Rectangle:
    def __init__(self, editor, params, attr):
        self.editor = editor
        self.params = params
        self.attr = attr

    class RectParams:
        def __init__(self, point, dimension, axis, is_covered=True):
            self.point = point
            self.dimension = dimension
            self.axis = axis
            self.is_covered = is_covered

        def generate(self):
            return [
                "NAME:RectangleParameters",
                "IsCovered:="       , self.is_covered,
                "XStart:="          , str(self.point.x) + self.point.unit,
                "YStart:="          , str(self.point.y) + self.point.unit,
                "ZStart:="          , str(self.point.z) + self.point.unit,
                "Width:="           , str(self.dimension.width) + self.dimension.unit,
                "Height:="          , str(self.dimension.height) + self.dimension.unit,
                "WhichAxis:="       , self.axis
            ]

    def create(self):
        self.editor.CreateRectangle(self.params.generate(), self.attr.generate())
        return self

class Sweep:
    def __init__(self, editor, params):
        self.editor = editor
        self.params = params

    class SweepParams:
        def __init__(self, name, shape, path, model_flag = "Model", draft_angle=0, draft_type="round", check_intersection=False, twist_angle=0):
            self.name = name
            self.shape = shape
            self.path = path
            self.model_flag = model_flag
            self.draft_angle = draft_angle
            self.draft_type = draft_type
            self.check_intersection = check_intersection
            self.twist_angle = twist_angle

        def generateSelection(self):
            return [
                "NAME:Selections",
                "Selections:="      , self.shape.attr.name + "," + self.path.attr.name,
                "NewPartsModelFlag:="   , self.model_flag
            ]

        def generateParams(self):
            return [
                "NAME:PathSweepParameters",
                "DraftAngle:="      , str(self.draft_angle) + "deg",
                "DraftType:="       , self.draft_type,
                "CheckFaceFaceIntersection:=", self.check_intersection,
                "TwistAngle:="      , str(self.twist_angle) + "deg"
            ]

    def create(self):
        self.editor.SweepAlongPath(self.params.generateSelection(), self.params.generateParams())
        return self

class Unite:
    def __init__(self, editor, bodies, keep_original=False):
        self.editor = editor
        self.bodies = bodies
        self.keep_original = keep_original

    def generateSelection(self):
        selection_str = ""
        for i,body in enumerate(bodies):
            if i != 0:
                selection_str += ","
            selection_str += body.attr.name

        return [
            "NAME:Selections",
            "Selections:="      , selection_str
        ]

    def generateParams(self):
        return [
            "NAME:UniteParameters",
            "KeepOriginals:="   , keep_original
        ]

    def execute(self):
        editor.Unite(self.generateSelection(), self.generateParams())
        return self


class Cylinder:
    def __init__(self, editor, params, attr):
        self.editor = editor
        self.params = params
        self.attr = attr

    class CylinderParams:
        def __init__(self, center, radius, height, axis, num_sides=0):
            self.center = center
            self.radius = radius
            self.height = height
            self.axis = axis
            self.num_sides = num_sides

        def generate(self):
            return [
                "NAME:RectangleParameters",
                "XCenter:="          , str(self.center.x) + self.center.unit,
                "YCenter:="          , str(self.center.y) + self.center.unit,
                "ZCenter:="          , str(self.center.z) + self.center.unit,
                "Radius:="           , str(self.radius) + "mm",
                "Height:="          , str(self.height) + "mm",
                "WhichAxis:="       , self.axis,
                "NumSides:="        , self.num_sides
            ]

    def create(self):
        self.editor.CreateCylinder(self.params.generate(), self.attr.generate())
        return self