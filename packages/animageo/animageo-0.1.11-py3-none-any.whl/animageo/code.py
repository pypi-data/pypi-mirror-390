from typing import overload, List, Any
import numpy as np

#----------------------------------------------------------------

def interpolate(start, end, alpha):
    return (1-alpha)*start + alpha*end
def a_to_cpx(a):
    return complex(*a)
def cpx_to_a(cpx):
    return np.array((cpx.real, cpx.imag))
def vector_perp_rot(vec):
    return np.array((vec[1], -vec[0]))
def get_direction(alpha = None):
    return cpx_to_a(np.exp((alpha if alpha is not None else np.random.random()) * 1j))
def square_norm(x):
    return np.dot(x,x)
def rotate_vec(vec, alpha):
    return cpx_to_a(np.exp(alpha*1j) * a_to_cpx(vec))

#----------------------------------------------------------------

class Measure:
    def __init__(self, x, dim = 0):
        self.x = x
        self.dim = dim

class AngleSize:
    def __init__(self, x):
        self.value = x

class Boolean:
    def __init__(self, b):
        self.b = b

class Point:
    def __init__(self, a):
        self.a = np.array(a, dtype = float)

        self.style = {}
        self.style['r'] = 2.5
        #self.style['fill'] = 'black'
        self.style['show_label'] = False
        self.style['offset'] = [0.5, 0]
        self.style['z_index'] = 50

class Line:
    def __init__(self, n, c):
        self.n = np.array(n)
        self.c = c

        assert((self.n != 0).any())

        norm = np.linalg.norm(n)
        if not np.isclose(norm, 1):
            self.n /= norm
            self.c /= norm
        self.v = vector_perp_rot(self.n)

        self.style = {}
        #self.style['stroke'] = 'black'
        #self.style['stroke_width'] = 2

        self.style['z_index'] = 4

class Segment(Line):
    def __init__(self, p1, p2): # [x,y] in Line([a,b],c) <=> xa + yb == c
        assert((p1 != p2).any())
        normal_vec = vector_perp_rot(p1 - p2)
        c = np.dot(p1, normal_vec)
        super().__init__(normal_vec, c)
        
        self.end_points = np.array([p1, p2])
        self.length = np.linalg.norm(p1 - p2)

        self.style['z_index'] = 5

class Ray(Line):
    def __init__(self, start_point, vec):
        normal_vec = -vector_perp_rot(vec)
        c = np.dot(start_point, normal_vec)
        super().__init__(normal_vec, c)
        self.start_point = start_point

class Angle:
    def __init__(self, p, v1, v2):
        self.p = p
        self.angle = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0]) #np.angle(a_to_cpx(v2) / a_to_cpx(v1))

        if self.angle < 0:
            self.angle += 2*np.pi
        #    self.angle = -self.angle
        #    v1,v2 = v2,v1

        self.start_angle = np.angle(a_to_cpx(v1))
        self.end_angle = self.start_angle + self.angle
        self.v1 = v1
        self.v2 = v2
        max_r = min(np.linalg.norm(v1), np.linalg.norm(v2))*0.65
        if self.angle > 0.01:
            self.r = min(max_r, 0.8 / self.angle**0.25)
        else:
            self.r = min(max_r, 0.8 / 0.01**0.25)
    
        self.style = {}
        #self.style['stroke'] = 'black'
        #self.style['stroke_width'] = 1.5
        #self.style['fill'] = 'white'
        #self.style['fill'] = 'transparent'
        self.style['fill_opacity'] = 1
        self.style['lines'] = 1
        self.style['r_offset'] = 0
        #self.style['label_r_offset'] = 0.45

        self.style['z_index'] = 3

class Polygon:
    def __init__(self, points):
        self.points = np.array(points, dtype = float)
        
        self.style = {}
        #self.style['stroke'] = 'black'
        #self.style['stroke_width'] = 2
        self.style['stroke_opacity'] = 0

        self.style['z_index'] = 0.0

class Circle:
    def __init__(self, center, r):
        assert(r > 0)
        self.c = np.array(center)
        self.r = r
        self.r_squared = self.r**2
        
        self.style = {}
        #self.style['stroke'] = 'black'
        #self.style['stroke_width'] = 2
        #self.style['fill'] = 'transparent'
        self.style['fill_opacity'] = 0

        self.style['z_index'] = 4

class Arc(Circle):
    def __init__(self, center, r, angles):
        super().__init__(center, r)
        self.angles = [a % (2*np.pi) for a in angles]
        if self.angles[0] > self.angles[1]:
            self.angles[1] += 2*np.pi

        self.style['z_index'] = 5

class CircleSector(Circle):
    def __init__(self, center, r, angles):
        super().__init__(center, r)
        self.angles = [a % (2*np.pi) for a in angles]
        if self.angles[0] > self.angles[1]:
            self.angles[1] += 2*np.pi

        self.style['z_index'] = 5

class Vector:
    def __init__(self, end_points):
        self.end_points = np.array(end_points)
        self.v = self.end_points[1] - self.end_points[0]
        self.style = {}

        self.style['z_index'] = 5

#----------------------------------------------------------------

def Assign(p: Point) -> Point: pass

@overload
def AngleSize(a: Angle) -> AngleSize: pass
@overload
def AngleSize(x: float) -> AngleSize: pass
@overload
def AngleSize(p1: Point, p2: Point, p3: Point) -> AngleSize: pass

@overload
def Angle(p1: Point, p2: Point, p3: Point) -> Angle: pass

@overload
def AngularBisector(l1: Line, l2: Line) -> list: pass
@overload
def AngularBisector(p1: Point, p2: Point, p3: Point) -> Line: pass
@overload
def AngularBisector(l1: Segment, l2: Segment) -> list: pass

@overload
def Arc(circle: Circle, p1: Point, p2: Point) -> Arc: pass

@overload
def CircumcircleArc(p1: Point, p2: Point, p3: Point) -> Arc: pass
@overload
def CircleArc(p1: Point, p2: Point, p3: Point) -> Arc: pass
@overload
def CircumcircleSector(p1: Point, p2: Point, p3: Point) -> CircleSector: pass
@overload
def CircleSector(p1: Point, p2: Point, p3: Point) -> CircleSector: pass
@overload
def CircleSector(p1: Point, p2: Point, ang: AngleSize) -> CircleSector: pass
@overload
def CircleSector(p1: Point, p2: Point, value: float) -> CircleSector: pass

@overload
def AreCollinear(p1: Point, p2: Point, p3: Point) -> Boolean: pass
@overload
def AreConcurrent(l1: Line, l2: Line, l3: Line) -> Boolean: pass
@overload
def AreConcurrent(o1: Any, o2: Any, o3: Any) -> Boolean: pass
@overload
def AreConcyclic(p1: Point, p2: Point, p3: Point, p4: Point) -> Boolean: pass
@overload
def AreCongruent(a1: Angle, a2: Angle) -> Boolean: pass
@overload
def AreComplementary_aa(a1: Angle, a2: Angle) -> Boolean: pass
@overload
def AreCongruent(s1: Segment, s2: Segment) -> Boolean: pass
@overload
def AreEqual(m1: Measure, m2: Measure) -> Boolean: pass
@overload
def AreEqual(m: Measure, i: float) -> Boolean: pass
@overload
def AreEqual(p1: Point, p2: Point) -> Boolean: pass
@overload
def AreParallel(l1: Line, l2: Line) -> Boolean: pass
@overload
def AreParallel(l: Line, s: Segment) -> Boolean: pass
@overload
def AreParallel(r1: Ray, r2: Ray) -> Boolean: pass
@overload
def AreParallel(s: Segment, l: Line) -> Boolean: pass
@overload
def AreParallel(s1: Segment, s2: Segment) -> Boolean: pass
@overload
def ArePerpendicular(l1: Line, l2: Line) -> Boolean: pass
@overload
def ArePerpendicular(l: Line, r: Ray) -> Boolean: pass
@overload
def ArePerpendicular(r: Ray, l: Line) -> Boolean: pass
@overload
def ArePerpendicular(s: Segment, l: Line) -> Boolean: pass
@overload
def ArePerpendicular(l: Line, s: Segment) -> Boolean: pass
@overload
def ArePerpendicular(s1: Segment, s2: Segment) -> Boolean: pass

@overload
def Area(*points: Point) -> Measure: pass
@overload
def Area_P(polygon: Polygon) -> Measure: pass

@overload
def Circle(circle: Circle) -> Point: pass
@overload
def Circle(center: Point, passing_point: Point) -> Circle: pass
@overload
def Circle(p1: Point, p2: Point, p3: Point) -> Circle: pass
@overload
def Circle(p: Point, m: Measure) -> Circle: pass
@overload
def Circle(p: Point, i: float) -> Circle: pass
@overload
def Circle(p: Point, s: Segment) -> Circle: pass
@overload
def ContainedBy(point: Point, by_circle: Circle) -> Boolean: pass
@overload
def ContainedBy(point: Point, by_line: Line) -> Boolean: pass

@overload
def Distance(p1: Point, p2: Point) -> Measure: pass

@overload
def Equality(a1: Angle, a2: Angle) -> Boolean: pass
@overload
def Equality(m1: Measure, m2: Measure) -> Boolean: pass
@overload
def Equality(m: Measure, s: Segment) -> Boolean: pass
@overload
def Equality(m: Measure, i: float) -> Boolean: pass
@overload
def Equality(p1: Point, p2: Point) -> Boolean: pass
@overload
def Equality(polygon: Polygon, m: Measure) -> Boolean: pass
@overload
def Equality(poly1: Polygon, poly2: Polygon) -> Boolean: pass
@overload
def Equality(s: Segment, m: Measure) -> Boolean: pass
@overload
def Equality(s1: Segment, s2: Segment) -> Boolean: pass
@overload
def Equality(seg: Segment, a: float) -> Boolean: pass

@overload
def Intersect(line1: Line, line2: Line) -> Point: pass
@overload
def Intersect(line: Line, circle: Circle) -> list[Point]: pass
@overload
def Intersect(line: Line, circle: Circle, index: int) -> Any: pass
@overload
def Intersect(circle1: Circle, circle2: Circle) -> Any: pass
@overload
def Intersect(circle1: Circle, circle2: Circle, index: int) -> Any: pass
@overload
def Intersect(circle: Circle, line: Line) -> Any: pass
@overload
def Intersect(circle: Circle, line: Line, index: int) -> Any: pass
@overload
def Intersect(circle: Circle, ray: Ray) -> Any: pass
@overload
def Intersect(circle: Circle, ray: Ray, index: int) -> Any: pass
@overload
def Intersect(arc: Arc, line: Line) -> list: pass
@overload
def Intersect(line: Line, arc: Arc) -> list: pass
@overload
def Intersect(arc: Arc, line: Line, index: int) -> Any: pass
@overload
def Intersect(line: Line, arc: Arc, index: int) -> Any: pass
@overload
def Intersect(sector: CircleSector, line: Line) -> list: pass
@overload
def Intersect(line: Line, sector: CircleSector) -> list: pass
@overload
def Intersect(sector: CircleSector, line: Line, index: int) -> Any: pass
@overload
def Intersect(line: Line, sector: CircleSector, index: int) -> Any: pass
@overload
def Intersect(circle: Circle, segment: Segment) -> list: pass
@overload
def Intersect(circle: Circle, segment: Segment, index: int) -> Any: pass
@overload
def Intersect(ray: Ray, circle: Circle) -> list: pass
@overload
def Intersect(ray: Ray, circle: Circle, index: int) -> Any: pass
@overload
def Intersect(segment: Segment, circle: Circle) -> list: pass
@overload
def Intersect(segment: Segment, circle: Circle, index: int) -> Any: pass
@overload
def Intersect(line: Line, ray: Ray) -> Point: pass
@overload
def Intersect(line: Line, segment: Segment) -> Point: pass
@overload
def Intersect(ray: Ray, line: Line) -> Point: pass
@overload
def Intersect(r1: Ray, r2: Ray) -> Point: pass
@overload
def Intersect(ray: Ray, segment: Segment) -> Point: pass
@overload
def Intersect(segment: Segment, line: Line) -> Point: pass
@overload
def Intersect(segment: Segment, ray: Ray) -> Point: pass
@overload
def Intersect(s1: Segment, s2: Segment) -> Point: pass

@overload
def LineBisector(p1: Point, p2: Point) -> Line: pass
@overload
def LineBisector(segment: Segment) -> Line: pass

@overload
def Line(point: Point, line: Line) -> Line: pass
@overload
def Line(p1: Point, p2: Point) -> Line: pass
@overload
def Line(pt: Point, vec: Vector) -> Line: pass
@overload
def Line(point: Point, ray: Ray) -> Line: pass
@overload
def Line(point: Point, segment: Segment) -> Line: pass
@overload
def Line(segment: Segment) -> Line: pass

@overload
def Midpoint(p1: Point, p2: Point) -> Point: pass
@overload
def Midpoint(segment: Segment) -> Point: pass

@overload
def Mirror(circle: Circle, by_circle: Circle) -> Any: pass
@overload
def Mirror(circle: Circle, by_line: Line) -> Circle: pass
@overload
def Mirror(circle: Circle, by_point: Point) -> Circle: pass
@overload
def Mirror(line: Line, by_line: Line) -> Line: pass
@overload
def Mirror(line: Line, by_segment: Segment) -> Line: pass
@overload
def Mirror(line: Line, by_point: Point) -> Line: pass
@overload
def Mirror(point: Point, by_circle: Circle) -> Point: pass
@overload
def Mirror(point: Point, by_line: Line) -> Point: pass
@overload
def Mirror(point: Point, by_point: Point) -> Point: pass
@overload
def Mirror(point: Point, by_segment: Segment) -> Point: pass

@overload
def OrthogonalLine(point: Point, line: Line) -> Line: pass
@overload
def OrthogonalLine(point: Point, ray: Ray) -> Line: pass
@overload
def OrthogonalLine(point: Point, segment: Segment) -> Line: pass

@overload
def Point() -> Point: pass
@overload
def Point(x: float, y: float) -> Point: pass
@overload
def Point(circle: Circle) -> Point: pass
@overload
def Point(line: Line) -> Point: pass
@overload
def Point(segment: Segment) -> Point: pass

@overload
def Polar(point: Point, circle: Circle) -> Line: pass

@overload
def Polygon(p1: Point, p2: Point, n: int) -> list: pass
@overload
def Polygon(*points: Point) -> list: pass

@overload
def Prove(x: Boolean) -> Boolean: pass

@overload
def Radius(circle: Circle) -> Measure: pass
@overload
def Center(circle: Circle) -> Point: pass

@overload
def Ray(p1: Point, p2: Point) -> Ray: pass

@overload
def Rotate(point: Point, angle: Angle, by_point: Point) -> Point: pass
@overload
def Rotate(point: Point, angle_size: AngleSize, by_point: Point) -> Point: pass
@overload
def Rotate(point: Point, angle_value: float, by_point: Point) -> Point: pass
@overload
def Rotate(vec: Vector, angle_size: AngleSize, by_point: Point) -> Vector: pass

@overload
def Segment(p1: Point, p2: Point) -> Segment: pass
@overload
def Segment(p: Point, vec: Vector) -> Segment: pass

@overload
def Semicircle(p1: Point, p2: Point) -> Arc: pass

@overload
def Tangent(point: Point, circle: Circle) -> Any: pass
@overload
def Tangent(point: Point, circle: Circle, index: int) -> Any: pass

@overload
def Touches(c1: Circle, c2: Circle) -> Boolean: pass
@overload
def Touches(line: Line, circle: Circle) -> Boolean: pass
@overload
def Touches(circle: Circle, line: Line) -> Boolean: pass

@overload
def Translate(point: Point, vector: Vector) -> Point: pass
@overload
def Translate(segment: Segment, vector: Vector) -> Segment: pass
@overload
def Translate(circle: Circle, vector: Vector) -> Circle: pass

@overload
def Vector(p1: Point, p2: Point) -> Vector: pass
@overload
def Vector(p1: Point) -> Vector: pass
@overload
def Vector(x: float, y: float) -> Vector: pass
@overload
def Vector(vec: Vector, mod: float) -> Vector: pass

#--------------------------------------------------------

@overload
def Abs(a: float) -> float: pass
@overload
def Abs(m: Measure) -> Measure: pass

@overload
def Value(ang_size: AngleSize) -> float: pass

@overload
def USub(a: float) -> float: pass
@overload
def USub(vector: Vector) -> Vector: pass
@overload
def USub(angle: Angle) -> AngleSize: pass
@overload
def USub(anglesize: AngleSize) -> AngleSize: pass
@overload
def USub(m: Measure) -> Measure: pass

@overload
def Sub(a: float, b: float) -> float: pass
@overload
def Sub(a1: AngleSize, a2: AngleSize) -> AngleSize: pass
@overload
def Sub(a: Angle, A: AngleSize) -> AngleSize: pass
@overload
def Sub(A: AngleSize, a: Angle) -> AngleSize: pass
@overload
def Sub(v1: Vector, v2: Vector) -> Vector: pass
@overload
def Sub(point: Point, vector: Vector) -> Point: pass
@overload
def Sub(p1: Point, p2: Point) -> Vector: pass
@overload
def Sub(m1: Measure, m2: Measure) -> Measure: pass
@overload
def Sub(m: Measure, s: Segment) -> Measure: pass
@overload
def Sub(s: Segment, m: Measure) -> Measure: pass
@overload
def Sub(s1: Segment, s2: Segment) -> Measure: pass

@overload
def Pow(a: float, b: float) -> float: pass
@overload
def Pow(m: Measure, i: float) -> Measure: pass
@overload
def Pow(s: Segment, i: float) -> Measure: pass

@overload
def Mult(m: Measure, b: float) -> float: pass
@overload
def Mult(a: float, m: Measure) -> float: pass
@overload
def Mult(a: float, b: float) -> float: pass
@overload
def Mult(vector: Vector, a: float) -> Vector: pass
@overload
def Mult(a: float, vector: Vector) -> Vector: pass
@overload
def Mult(m1: Measure, m2: Measure) -> Measure: pass
@overload
def Mult(m: Measure, s: Segment) -> Measure: pass
@overload
def Mult(m: Measure, f: float) -> Measure: pass
@overload
def Mult(s: Segment, m: Measure) -> Measure: pass
@overload
def Mult(s1: Segment, s2: Segment) -> Measure: pass
@overload
def Mult(f: float, m: Measure) -> Measure: pass
@overload
def Mult(f1: float, f2: float) -> Measure: pass
@overload
def Mult(i: float, angle_size: AngleSize) -> AngleSize: pass
@overload
def Mult(a: AngleSize, i: float) -> AngleSize: pass
@overload
def Mult(i: float, s: Segment) -> Measure: pass

@overload
def Div(a: float, b: float) -> float: pass
@overload
def Div(angle_size: AngleSize, i: float) -> AngleSize: pass
@overload
def Div(m1: Measure, m2: Measure) -> Measure: pass
@overload
def Div(m: Measure, s: Segment) -> Measure: pass
@overload
def Div(m: Measure, i: float) -> Measure: pass
@overload
def Div(s: Segment, m: Measure) -> Measure: pass
@overload
def Div(s1: Segment, s2: Segment) -> Measure: pass
@overload
def Div(s: Segment, i: float) -> Measure: pass
@overload
def Div(vector: Vector, a: float) -> Vector: pass

@overload
def Add(a: float, b: float) -> float: pass
@overload
def Add(v1: Vector, v2: Vector) -> Vector: pass
@overload
def Add(point: Point, vector: Vector) -> Point: pass
@overload
def Add(vector: Vector, point: Point) -> Point: pass
@overload
def Add(m1: Measure, m2: Measure) -> Measure: pass
@overload
def Add(m: Measure, s: Segment) -> Measure: pass
@overload
def Add(m: Measure, i: float) -> Measure: pass
@overload
def Add(s1: Segment, s2: Segment) -> Measure: pass

#--------------------------------------------------------

@overload
def Cos(x: float) -> float: pass
@overload
def Sin(x: float) -> float: pass
@overload
def Tan(x: float) -> float: pass
@overload
def Ctan(x: float) -> float: pass
@overload
def Sqrt(x: float) -> float: pass
