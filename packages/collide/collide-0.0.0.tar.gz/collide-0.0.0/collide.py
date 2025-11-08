import math

class Group:
    def __init__(self, points=None):
        self.points = points if points is not None else []
    
    def add_point(self, x, y):
        """添加单个点到坐标列表"""
        self.points.append((x, y))
    
    def get_points(self):
        """返回所有坐标点"""
        return self.points
    
    def clear_points(self):
        """清空坐标列表"""
        self.points = []
    
    def create_shape(self, shape_type, *args):
        """创建不同类型的图形坐标点
        支持的形状类型: rectangle, circle, triangle, polygon
        """
        self.clear_points()
        if shape_type == 'rectangle':
            if len(args) != 4:
                raise ValueError("矩形需要x, y, width, height四个参数")
            x, y, width, height = args
            self.add_point(x, y)
            self.add_point(x + width, y)
            self.add_point(x + width, y + height)
            self.add_point(x, y + height)
        elif shape_type == 'circle':
            if len(args) != 4:
                raise ValueError("圆形需要x, y, radius, num_vertices四个参数")
            x, y, radius, num_vertices = args
            for i in range(num_vertices):
                angle = 2 * math.pi * i / num_vertices
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
                self.add_point(px, py)
        elif shape_type == 'triangle':
            if len(args) != 6:
                raise ValueError("三角形需要x1, y1, x2, y2, x3, y3六个参数")
            x1, y1, x2, y2, x3, y3 = args
            self.add_point(x1, y1)
            self.add_point(x2, y2)
            self.add_point(x3, y3)
        elif shape_type == 'polygon':
            if len(args) < 6 or len(args) % 2 != 0:
                raise ValueError("多边形需要至少3个顶点（6个参数），且参数数量为偶数")
            for i in range(0, len(args), 2):
                x = args[i]
                y = args[i + 1]
                self.add_point(x, y)
        else:
            raise ValueError(f"不支持的形状类型: {shape_type}")

class Collide:
    @staticmethod
    def is_colliding_with(group1, group2):
        """使用分离轴定理检测两个Group实例是否碰撞"""
        points1 = group1.get_points()
        points2 = group2.get_points()
        if not points1 or not points2:
            return False
        
        polygons = [points1, points2]
        for i in range(2):
            polygon = polygons[i]
            for j in range(len(polygon)):
                p1 = polygon[j]
                p2 = polygon[(j+1) % len(polygon)]
                edge = (p2[0] - p1[0], p2[1] - p1[1])
                normal = (-edge[1], edge[0])  # 计算法向量
                min1, max1 = Collide._project_polygon(polygon, normal)
                min2, max2 = Collide._project_polygon(polygons[1-i], normal)
                if not Collide._overlap(min1, max1, min2, max2):
                    return False
        return True
    
    @staticmethod
    def contains_point(group, point):
        """判断点是否在Group实例表示的图形内（包含边界检测）"""
        points = group.get_points()
        if not points:
            return False
        
        x, y = point
        inside = False
        n = len(points)
        for i in range(n):
            j = (i + 1) % n
            xi, yi = points[i]
            xj, yj = points[j]
            
            if Collide._is_point_on_segment(point, (xi, yi), (xj, yj)):
                return True
            
            if ((yi > y) != (yj > y)):
                x_intersect = ((y - yi) * (xj - xi)) / (yj - yi + 1e-8) + xi
                if x < x_intersect:
                    inside = not inside
        return inside
    
    @staticmethod
    def get_bounding_box(group):
        """返回Group实例表示的图形的边界框(min_x, min_y, max_x, max_y)"""
        points = group.get_points()
        if not points:
            return (0, 0, 0, 0)
        xs, ys = zip(*points)
        return (min(xs), min(ys), max(xs), max(ys))
    
    @staticmethod
    def get_collision_points(group1, group2):
        """计算两个Group实例表示的图形的所有碰撞点"""
        points1 = group1.get_points()
        points2 = group2.get_points()
        collision_points = []
        if not points1 or not points2:
            return collision_points
        
        edges1 = Collide._get_edges(points1)
        edges2 = Collide._get_edges(points2)
        
        for edge1 in edges1:
            a1, a2 = edge1
            for edge2 in edges2:
                b1, b2 = edge2
                intersect = Collide._segment_intersect(a1, a2, b1, b2)
                if intersect:
                    collision_points.append(intersect)
        return collision_points
    
    @staticmethod
    def contains_shape(outer_group, inner_group):
        """判断outer_group是否完全包含inner_group"""
        inner_points = inner_group.get_points()
        if not inner_points:
            return True
        for point in inner_points:
            if not Collide.contains_point(outer_group, point):
                return False
        return True
    
    @staticmethod
    def _is_point_on_segment(p, a, b):
        """判断点p是否在线段ab上"""
        px, py = p
        ax, ay = a
        bx, by = b
        cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
        if abs(cross) > 1e-8:
            return False
        min_x = min(ax, bx) - 1e-8
        max_x = max(ax, bx) + 1e-8
        min_y = min(ay, by) - 1e-8
        max_y = max(ay, by) + 1e-8
        return (min_x <= px <= max_x) and (min_y <= py <= max_y)
    
    @staticmethod
    def _project_polygon(polygon, axis):
        """将多边形投影到给定轴上，返回投影的最小值和最大值"""
        min_proj = float('inf')
        max_proj = -float('inf')
        for point in polygon:
            proj = point[0] * axis[0] + point[1] * axis[1]
            if proj < min_proj:
                min_proj = proj
            if proj > max_proj:
                max_proj = proj
        return min_proj, max_proj
    
    @staticmethod
    def _overlap(min1, max1, min2, max2):
        """检查两个投影区间是否重叠"""
        return not (max1 < min2 - 1e-8 or max2 < min1 - 1e-8)
    
    @staticmethod
    def _get_edges(points):
        """获取多边形的所有边（线段）"""
        edges = []
        n = len(points)
        for i in range(n):
            p1 = points[i]
            p2 = points[(i+1) % n]
            edges.append((p1, p2))
        return edges
    
    @staticmethod
    def _segment_intersect(a1, a2, b1, b2):
        """判断两条线段是否相交，并返回交点坐标"""
        def ccw(A, B, C):
            return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
        
        A, B, C, D = a1, a2, b1, b2
        if ccw(A,B,C) != ccw(A,B,D) and ccw(C,D,A) != ccw(C,D,B):
            x1, y1 = A
            x2, y2 = B
            x3, y3 = C
            x4, y4 = D
            
            denom = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
            if denom == 0:
                return None
                
            t_num = (x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)
            t = t_num / denom
            u_num = -((x1 - x2)*(y1 - y3) - (y1 - y2)*(x1 - x3))
            u = u_num / denom
            
            if -1e-8 <= t <= 1+1e-8 and -1e-8 <= u <= 1+1e-8:
                x = x1 + t*(x2 - x1)
                y = y1 + t*(y2 - y1)
                return (round(x, 8), round(y, 8))
        return None
