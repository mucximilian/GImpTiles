'''
Created on Jun 5, 2015

@author: mucx
'''

from __future__ import division

from geometry import LineSimple, LineString

import math
import random

class SketchRenderer(object):
    '''
    classdocs
    '''

    def __init__(self, seed):
        '''
        Constructor
        '''
        self.seed = seed
           
    def displace_points_handy(self, line, r):
        """
        Does what the Handy renderer is supposed to do (according to paper).
        
        :param line: Tuple of two coordinate pairs determining the line points.
        """
        
        point_a = self.displace_point(line[0], r)
        point_b = self.displace_point(line[1], r)
        point_m = self.displace_point_orthogonal(line, r)
        point_n = self.displace_point_orthogonal_area(line, r)
        
        line_sketch = [point_a, point_m, point_n, point_b]
        
        return line_sketch
    
    def displace_point(self, point, r, method = "square"):
        """
        Displaces a point, r defines the radius within which the point 
        coordinates are randomly perturbed (with a uniform random deviate).
        
        Note: The random seed should be set outside of the function.
        
        :param point: Tuple of x and y coordinates.
        """
        
        # random.seed(r * self.seed)
        
        coords_new = None
        
        if (method == "circle"):
            
            angle = random.random() * 360
            distance = random.random() * r
            
            x = point[0] + (math.cos(math.radians(angle)) * distance)
            y = point[1] + (math.sin(math.radians(angle)) * distance)
            
            coords_new = (x,y)
            
        elif(method == "square"):
            
            d_x = random.uniform(-r, r)
            d_y = random.uniform(-r, r)
            
            x = d_x + point[0]
            y = d_y + point[1]
            
            coords_new = (x,y)
        
        return coords_new
    
    def displace_point_orthogonal(self, line, r):
        """
        Displaces a point, r defines the radius within which the point 
        coordinates are randomly perturbed (with a uniform random deviate)
        """
        
        m = self.calculate_point_at_line_pos(line, 0.5)
        
        print m
        
        # TO DO:
        # Calculate point that is within r on a orthogonal line through m 
        
        x = 0
        y = 0
        
        return [x,y]
    
    def displace_point_orthogonal_area(self, line, r):
        """
        Displaces a point, r defines the radius within which the point 
        coordinates are randomly perturbed (with a uniform random deviate)
        """
        
        n = line.calculate_point_at_line_pos(0.75)
        
        print n
        
        # TO DO:
        # Calculate point that is within r and orthogonal to a 10 % section of
        # the line around n
        
        x = 0
        y = 0
        
        return [x,y]
    
    def displace_line(self, line, r):
        """
        Displaces the two end points of a line. If the specified radius is
        larger than the line length, the points are displaced by half of the
        original line length.
        """
        
        line = LineSimple(line)
        
        a = line.coords[0]
        b = line.coords[1]
        
        length = line.length()
        
        if (length <= r):
            r =  length/2               
                
        random.seed(length + self.seed)
        point1 = self.displace_point(a, r, method = "circle")
        point2 = self.displace_point(b, r, method = "circle")
        
        line_new = LineSimple([point1, point2])
        
        return line_new
    
    def polygon_disjoin(self, polygon, angle_disjoin = 135.0):
        """
        Disjoins polygon linestrings into segments at vertices where the angle 
        between the lines from the vertex to the vertex behind and the vertex 
        to the vertex ahead exceeds a given threshold. Returns the calculated
        line segments as an array.
        
        :param polygon: Input geometry, array of lines (arrays of coordinates)
        :param angle_disjoin: Threshold angle for disjoin in degree.
        """
        
        def get_three_point_angle(points):
            """
            Calculates the angle between the lines from a vertex to the vertex 
            behind and the vertex to the vertex ahead.
            
            :param points: Coordinate array, containing three points 
            (vertex behind, vertex, vertex ahead)
            """
            
            p0 = points[0] # point_behind
            p1 = points[1] # point_center
            p2 = points[2] # point_ahead
            
            a = (p1[0] - p0[0])**2 + (p1[1] - p0[1])**2
            b = (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2
            c = (p2[0] - p0[0])**2 + (p2[1] - p0[1])**2
            
            angle = math.acos((a + b - c) / math.sqrt(4 * a * b)) * 180/math.pi
        
            return angle
        
        outline_segments = []
        
        for line in polygon:
            
            print line
            print "###"
            
            segment = []
            segment.append(line[0])
            
            for i in range(1, len(line) -1):
                
                points = []
                
                points.append(line[i - 1])
                points.append(line[i])
                points.append(line[i + 1])
                
                angle = self.get_three_point_angle(points)
                
                # Continue segment
                if (angle >= angle_disjoin):
                    segment.append(line[i])
                    
                # Finish segment and create new one
                else:
                    segment.append(line[i])                    
                    outline_segments.append(segment)
                    
                    segment = []
                    segment.append(line[i])
                
            segment.append(line[0])                    
            outline_segments.append(segment)
            
        return outline_segments
    
    def get_random_control_point(self, line, d):
        """
        Computes a random point that is on the straight line between P0 and P1 
        and the distance d away from P0 and P1. The distance is capped at half 
        of the line length.
        
        :param line: Tuple of two coordinate pairs determining the line points.
        """
        
        line = LineSimple(line)
                
        line_length_half = line.length()/2
        
        cp = None
        
        if d >= line_length_half:   
        
            point = self.get_point_shifted(line.coords, line_length_half)
            cp = self.displace_point(point, line_length_half)
            
        else:

            point1 = self.get_point_shifted(line.coords, d)            
            point2 = self.get_point_shifted((line.coords[1], line.coords[0]), d)
            
            point = self.get_random_point_on_line((point1, point2))
            cp = self.displace_point(point, d)
                    
        return cp
    
    def get_point_shifted(self, line, d):
        """
        Computes the point that is on the straight line between P0 and P1 and
        the distance d away from P0.
        
        :param line: Tuple of two coordinate pairs determining the line points.
        """ 
        
        line = LineSimple(line)
        
        line_vector = line.vector()        
        length = line.length()
        
        shift = tuple((d / length) * x for x in line_vector)
                
        point_shifted = tuple(sum(t) for t in zip(line.coords[0], shift))
        
        return point_shifted
    
    def jitter_line_new(self, line, d_rel = 10.0, d_abs = None, method = "simple"):
        
        def jitter_line_simple(line, d_abs, d_rel, method):
            
            line = LineSimple(line)
            length = line.length()
            
            d = None        
            if d_abs is not None:
                # Avoiding greater displacement than the length of the line
                if d_abs >= length:
                    d= d_abs/2
                else:
                    d = d_abs
            else:
                d = length / d_rel
            
            # Adding additional points to the line if line is longer than 2d
            parts = int(math.floor(length / (2 *d))) -1
            if parts > 0 and len(line.coords) == 2:

                print parts
                print d
                print length
                print line.coords
     
                line.coords = self.add_points_to_line(
                    line.coords, parts, "equal_uniform"
                )            
                self.jitter_line_string(line.coords, d, method)
                
            else:                
                
                linepoints = []
            
                if method == "displace":
                    
                    a = line.coords[0]
                    b = line.coords[1]
                    
                    a = self.displace_point(a, d, "circle")
                    linepoints.append(a)
                    
                    b = self.displace_point(b, d, "circle")
                    linepoints.append(b)                
                    
                elif method == "bezier":
                    
                    a = line.coords[0]
                    b = line.coords[1]
                    
                    linepoints.append(a)
                                    
                    cp1 = self.get_random_control_point((a, b), d)            
                    cp2 = self.get_random_control_point((b, a), d)
                        
                    linepoints.append(cp1)
                    linepoints.append(cp2)                    
                    
                    linepoints.append(b)
                
                elif method == "displace_bezier":
                    
                    a = line.coords[0]
                    b = line.coords[1]
                    
                    a = self.displace_point(line.coords[0], d, "circle")
                    b = self.displace_point(line.coords[1], d, "circle")
                    
                    linepoints.append(a)
                                    
                    cp1 = self.get_random_control_point((a, b), d)            
                    cp2 = self.get_random_control_point((b, a), d)
                        
                    linepoints.append(cp1)
                    linepoints.append(cp2)                    
                    
                    linepoints.append(b)
                    
                return linepoints
        
        def jitter_line_string(line, d_abs, d_rel, method):
            
            linepoints = []
            
            for i in range(0, len(line), 2):
                
                a = line[i]
                b = line[i + 1]
                
                linepoints += jitter_line_simple([a, b], d_abs, d_rel, method)
                
            return linepoints
        
        ########################################################################
        
        linepoints = []
        
        # Input line is a simple line
        if len(line) == 2:            
            linepoints = jitter_line_simple(line, d_abs, d_rel, method)                
         
        # Input line is a line string   
        else:
            linepoints = jitter_line_string(line, d_abs, d_rel, method)
            
        return linepoints
    
    def jitter_line(self, line, d_rel = 10.0, d_abs = None, method = "simple"):
        """
        Calculates random control points for a jittered line. The minumum 
        distance d of a random point to the corresponding end point can either
        be relative to the line lenght or a absolute value. Absolute values
        are capped at half of the line length between two points in the 
        'get_random_control_point' function.
         
       :param line: Tuple of two coordinate pairs determining the line points.
       :param d_rel: The relative offset of the jitter, used by default.
       :param d_abs: The relative offset of the jitter.
       :param method: 'simple': points are displaced, 'bezier: points are 
       displaced and line is smoothed using random control points.
        """
        
        # TO DO:
        # - Avoid overlapping controlpoints --> smoother line
        # - Control points on opposite sides of the line --> smoother line
        
        line = LineString(line)
        length = line.length()
        
        # Setting d_rel if d_abs is not defined:
        d = None        
        if d_abs is not None:
            # Avoiding a greater displacement than  the length of the line
            if d_abs >= length:
                d= d_abs/2
            else:
                d = d_abs
        else:
            d = length / d_rel
            
        # Adding additional points to the line if line is longer than 2d
        if length > 2 * d and len(line.coords) == 2:
            parts = int(math.floor(length / (2 *d)))
 
            line.coords = self.add_points_to_line(
                line.coords, parts, "equal_uniform"
            )
              
        random.seed(length * self.seed)
        
        line_jittered = []
        
        if method == "simple":
            
            point = self.displace_point(line.coords[0], d, "circle")
            line_jittered.append(point)
            
            for i in range(1, len(line.coords) -1):
                
                point = self.displace_point(line.coords[i], d, "circle")
                line_jittered.append(point)
            
            point = self.displace_point(line.coords[-1], d, "circle")
            line_jittered.append(point)                
            
        elif method == "bezier":
        
            controlpoints = []
            point = self.displace_point(line.coords[0], d, "circle")
            controlpoints.append(point)
            
            for i in range(1, len(line.coords) -1):
                
                point_behind = line.coords[i - 1]
                point = line.coords[i]
                point_ahead = line.coords[i + 1]
                                
                # TO DO: Do d checking here!!
                            
                cp1 = self.get_random_control_point((point, point_behind), d)            
                cp2 = self.get_random_control_point((point, point_ahead), d)
                
                controlpoints.append(cp1)
                controlpoints.append(cp2)
                
            point = self.displace_point(line.coords[-1], d, "circle")
            controlpoints.append(point)
            
            line_jittered = line.get_curve(controlpoints)
            
        return line_jittered  
    
    def jitter_line_bezier_test_one(self, line):
        """
        Creates a jittered line as described here:
        
        http://stackoverflow.com/a/6373008/3854098 
        http://jsfiddle.net/GfGVE/9/
        
        :param line: Tuple of two coordinate pairs determining the line points.
        """
        
        line = LineSimple(line)
        
        random.seed(line.length() * self.seed)
        
        curve = []
        curve.append(line.coords[0])
        
        for i in range(0, len(line.coords) -1):
            
            p0_x = line.coords[i][0]
            p0_y = line.coords[i][1]
            p1_x = line.coords[i+1][0]
            p1_y = line.coords[i+1][1]

            diff_y = p1_y - p0_y;
            
            # so the y value can go positive or negative from the typical   
            neg = random.random() - 0.5; 
                
            cp1 = (
                -neg + p0_x + ((random.random() - 0.5) * diff_y / 8),
                p0_y + 0.3 * diff_y
            )
            cp2 = (
                -neg + p0_x + ((random.random() - 0.5) * diff_y / 8),
                p0_y + 0.6 * diff_y
            )
            p = (p1_x, p1_y)
            
            curve.append(cp1)
            curve.append(cp2)
            curve.append(p)
            
        return curve
    
    def jitter_handrawn_raphael(self, line, segments, wobble):
        """
        Creates a jittered line as described here:
        
        https://github.com/jhund/raphael.handdrawn.js/blob/master/raphael.handdrawn.js
        
        :param line: Tuple of two coordinate pairs determining the line points.
        """
        
        def randomizeNormal(range_in = 1.0, mean = 0.0):
            range1 = range_in / 9;
            rand = math.cos(2 * math.pi * random.random()) * math.sqrt(-2 * math.log(random.random()))
            
            return round((rand * range1) + mean)
        
        def randomizeUniform (range_in = 100, mean = 0.0):
            rand = random.random() * range_in;
            return round((rand - (range_in / 2)) + mean);
        
        x = line[0][0]
        y = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        
        points = ['M ' + str(x) + ' ' + str(y)]
    
        for i in range(1, segments +1):
            
            segmentStartX = x + (x2-x) * (i-1) / segments
            segmentStartY = y + (y2-y) * (i-1) / segments
            segmentEndX = x + (x2-x) * i/segments
            segmentEndY = y + (y2-y) * i/segments
        
            midX1 = int(round(segmentStartX + (segmentStartX - segmentEndX) * -0.3 + randomizeUniform(wobble)))
            midX2 = int(round(segmentStartX + (segmentStartX - segmentEndX) * -0.7 + randomizeUniform(wobble)))
            midY1 = int(round(segmentStartY + (segmentStartY - segmentEndY) * -0.3 + randomizeUniform(wobble)))
            midY2 = int(round(segmentStartY + (segmentStartY - segmentEndY) * -0.7 + randomizeUniform(wobble)))
        
            points.append(
              'C ' + str(midX1) + ' ' + str(midY1) + ' ' + str(midX2) + ' ' + str(midY2) + ' ' + str(segmentEndX) + ' ' + str(segmentEndY)
            );
            
        return ' '.join(points);
                
            
    def add_points_to_line(self, line, n = 1, method = "equal"):
        """
        Adds a specified number of points to a line between two points using
        the selected method. Returns a new line.
        
        :param line: Tuple of two coordinate pairs determining the line points.
        """
        
        line = LineSimple(line)
        length = line.length()
        
        a = min(line.coords) # Get point with smaller x value as point a
        b = max(line.coords)
            
        points_on_line = []
        
        # Distribute points equally
        if method == "equal":
            
            for i in range(0, n + 1):
            
                d = (length / (n + 1)) * i
            
                point = self.get_point_shifted((a, b), d)                
                points_on_line.append(point)
        
        # Distribute points randomly  
        elif (method == "uniform" or
            method == "equal_uniform" or
            method == "equal_normlike"):            
        
            random.seed(length * self.seed)
        
            # - just random
            if method == "uniform":
        
                for _ in range(0, n):
                    
                    d = length * random.random()
            
                    point = self.get_point_shifted((a, b), d)                
                    points_on_line.append(point)        
            
            # - randomly within equal segments        
            elif method == "equal_uniform":
                
                # Computing the start and end points of the equal segments
                segment_points = [a]
                for i in range(0, n - 1):
                    d_part = (length / (n + 1)) * (i + 1)
                    point = self.get_point_shifted((a, b), d_part)
                    segment_points.append(point)
                segment_points.append(b)
                
                # Now random points between the segments are added               
                for i in range(0, len(segment_points) - 1):                   
                    points_on_line.append(
                        self.get_random_point_on_line(
                            (segment_points[i], segment_points[i + 1])
                        )
                    )
            
            # Distribute points normal distribution like on segment 
            elif method == "equal_normlike":
                print "'equal_normlike' not yet implemented"
            
        # Inserting new points in the original line
        line_new = [a]
        line_new += sorted(points_on_line)
        line_new += [b]
        
        return line_new
    
    def get_random_point_on_line(self, line):
        """
        Computes the point that is on the straight line between P0 and P1 and
        the distance d away from.
        
        :param line: Tuple of two coordinate pairs determining the line points.
        """ 
        
        line = LineSimple(line)
        
        d = line.length()
        d_rand = random.random() * d
        
        point = self.get_point_shifted(line.coords, d_rand)
        
        return point
        
    
class HandyRenderer(SketchRenderer):
    '''
    This class is a customized and simplified copy of the HandyRenderer.java 
    class which contains the geometry processing logic of the Handy Processing 
    library developed by Jo Wood.
    
    http://www.gicentre.net/software/#/handy/
    '''

    def __init__(self, seed, roughness = 1.0, bowing = 1.0):
        '''
        Constructor
        '''
        super(HandyRenderer, self).__init__(seed)
        
        self.bowing = bowing
        self.roughness = roughness
    
    def line(self, line, max_offset):
        """
        Clone of the function:
        
        void line(float x1, float y1, float x2, float y2, float maxOffset)
        """
        
        line = LineSimple(line)
        
        x1 = line.coords[0][0]
        y1 = line.coords[0][1]
        x2 = line.coords[1][0]
        y2 = line.coords[1][1]

        # Ensure random perturbation is no more than 10% of line length.
        lenSq = (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)
        offset = max_offset

        if (max_offset * max_offset * 100 > lenSq):
            offset = math.sqrt(lenSq)/10.0

        half_offset = offset/2
        
        random.seed(line.length() * self.seed)
        
        divergePoint = 0.2 + random.random() * 0.2

        # This is the midpoint displacement value to give slightly bowed lines.
        midDispX = self.bowing * max_offset * (y2-y1) / 200.0
        midDispY = self.bowing * max_offset * (x1-x2) / 200.0

        midDispX = self.get_offset(-midDispX, midDispX)
        midDispY = self.get_offset(-midDispY, midDispY)

        # Calculating line 1           
        line1 = self.get_displaced_linepoints(x1, y1, x2, y2, 
                                              midDispX, midDispY, 
                                              divergePoint, offset)
        
        # Calculating line 2
        line2 = self.get_displaced_linepoints(x1, y1, x2, y2, 
                                              midDispX, midDispY, 
                                              divergePoint, half_offset)
                    
        return [line1, line2]
        
    def get_offset(self, minVal, maxVal):
        """
        Clone of the function:
        
        float getOffset(float minVal, float maxVal)
        
        Should be called only from the 'line' function for secure random seed.
        """
             
        offset = self.roughness * (random.random() * (maxVal - minVal) + minVal)
             
        return offset
    
    def get_displaced_linepoints(self, x_a, y_a, x_b, y_b, 
                     midDispX, midDispY, divergePoint, offset):
        """
        This is part of the line function in the original Java code and was put
        separately for readability reasons.
        """
        
        x0 = x_a + self.get_offset(-offset, offset)
        y0 = y_a + self.get_offset(-offset, offset)
        p0 = [x0, y0]
        
        x1 = midDispX + x_a + (x_b-x_a) * divergePoint + self.get_offset(-offset, offset)
        y1 = midDispY + y_a + (y_b-y_a) * divergePoint + self.get_offset(-offset, offset)
        p1 = [x1, y1]
        
        x2 = midDispX + x_a + 2 * (x_b-x_a) * divergePoint + self.get_offset(-offset, offset)
        y2 = midDispY + y_a + 2 * (y_b-y_a) * divergePoint + self.get_offset(-offset, offset)
        p2 = [x2, y2] 
        
        x3 = + x_b + self.get_offset(-offset, offset)
        y3 = + y_b + self.get_offset(-offset, offset)
        p3 = [x3, y3]
        
        # Note:
        # self.get_offset(...) cannot be substituted to a variable as the
        # random function inside it needs to be called each time
        
        line = [p0, p1, p2, p3]
        
        return line