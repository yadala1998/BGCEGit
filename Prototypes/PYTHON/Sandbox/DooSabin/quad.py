__author__ = 'benjamin'
import numpy as np

class Quad:
    # _quadlist and _vertexlist have to be of type np.array!
    def __init__(self, _id, _vertices, _vertexlist):

        self.quad_id = _id
        self.vertices = _vertices
#        self.vertex_ids = _quadlist[_id]
        self.vertex_ids = np.array([self.vertices[i].getId() for i in range(len(self.vertices))])
        self.centroid = self.compute_centroid(_vertexlist)
       # self.is_plane = self.compute_plane(_vertexlist)
       # self.normal = self.compute_normal(_vertexlist)
       # self.vertices_plane = self.compute_plane_corner_points(_vertexlist)
       # self.ortho_basis_AB, \
       # self.basis_BAD, \
       # self.ortho_basis_CB, \
       # self.basis_BCD = \
       #     self.compute_basis(_vertexlist)# [edge_AB;edge_orthogonal;normal]

       # self.neighbors = self.find_neighbors(_quadlist)
        #self.basis, self.basis_inv = self.get_basis()

    def compute_centroid(self, _vertexlist):
       # import numpy as np
      #  return np.mean(_vertexlist[self.vertex_ids],0) #CHANGED!!!!
        return np.mean([self.vertices[i].coordinates for i in range(len(self.vertices))], 0)

    def compute_plane(self, _vertexlist):
        import numpy as np

        A=_vertexlist[self.vertex_ids[0]]
        B=_vertexlist[self.vertex_ids[1]]
        C=_vertexlist[self.vertex_ids[2]]
        D=_vertexlist[self.vertex_ids[3]]

        AB=B-A
        AC=C-A
        AD=D-A

        Q=np.array([AB,AC,AD])

        return abs(np.linalg.det(Q))<10**-14

    def compute_normal(self, _vertexlist):
        import numpy as np

        if self.is_plane:
            vertex1 = _vertexlist[self.vertex_ids[1]]
            vertex2 = _vertexlist[self.vertex_ids[2]]
            vertex3 = _vertexlist[self.vertex_ids[3]]

            edge12 = vertex2-vertex1
            edge13 = vertex3-vertex1

            normal = np.cross(edge12,edge13)
            normal /= np.linalg.norm(normal)

        else:
            #find least squares fit plane
            lsq_matrix = _vertexlist[self.vertex_ids] - self.centroid
            u, s, v = np.linalg.svd(lsq_matrix)
            idx = np.where(np.min(abs(s)) == abs(s))[0][0]

            normal = v[idx, :]
            normal /= np.linalg.norm(normal)

        return normal

    def compute_basis(self, _vertexlist):
        import numpy as np

        vertexA = self.vertices_plane[0,:]
        vertexB = self.vertices_plane[1,:]
        vertexC = self.vertices_plane[2,:]
        vertexD = self.vertices_plane[3,:]
        edgeAB = vertexB - vertexA
        edgeAD = vertexD - vertexA
        edgeCB = vertexB - vertexC
        edgeCD = vertexD - vertexC

        basis_BAD = np.array([self.normal, edgeAB, edgeAD])
        basis_BCD = np.array([self.normal, edgeCB, edgeCD])

        edgeAB_normalized = edgeAB / np.linalg.norm(edgeAB)
        edgeCB_normalized = edgeAD / np.linalg.norm(edgeCB)

        ortho_basis_AB = np.array([self.normal,
                                   edgeAB_normalized,
                                   np.cross(edgeAB_normalized, self.normal)])
        ortho_basis_CB = np.array([self.normal,
                                   edgeCB_normalized,
                                   np.cross(edgeCB_normalized, self.normal)])

        return ortho_basis_AB.transpose(), basis_BAD.transpose(), ortho_basis_CB.transpose(), basis_BCD.transpose()

    def projection_onto_plane(self, _point):
        import numpy as np

        distance = np.dot(self.centroid-_point, self.normal)
        projected_point = _point+distance*self.normal
        return projected_point, distance

    def point_on_quad(self, u, v):
        import numpy as np

        if u+v <= 1 and u >= 0 and v >= 0:
            vertexA = self.vertices_plane[0,:]
            point = vertexA + np.dot(self.basis_BAD[:,1:3],[u,v])

        elif u+v > 1 and u <= 1 and v <= 1:
            vertexC = self.vertices_plane[2,:]
            u = -u+1
            v = -v+1
            point = vertexC + np.dot(self.basis_BCD[:,1:3],[u,v])

        else:
            print "INVALID INPUT!"
            quit()

        return point

    def projection_onto_quad(self, _point):
        from scipy.linalg import solve_triangular
        import numpy as np

        # first assume that _point is below diagonal BD
        vertexA = self.vertices_plane[0,:]
        vector_vertexA_point = _point - vertexA
        # we want to transform _point to the BASIS=[normal,AB,AC] and use QR decomposition of BASIS = Q*R
        # BASIS * coords = _point -> R * coords = Q' * _point
        R_BAD = np.dot(self.ortho_basis_AB.transpose(),self.basis_BAD)
        b = np.dot(self.ortho_basis_AB.transpose(),vector_vertexA_point)
        x = solve_triangular(R_BAD,b)
        distance = x[0]
        projected_point = _point - distance * self.normal
        u = x[1]
        v = x[2]

        # if not, _point is above diagonal BD
        if u+v > 1:
            vertexC = self.vertices_plane[2,:]
            vector_vertexC_point = _point - vertexC
            R_BCD = np.dot(self.ortho_basis_CB.transpose(),self.basis_BCD)
            b = np.dot(self.ortho_basis_CB.transpose(),vector_vertexC_point)
            x = solve_triangular(R_BCD,b)
            distance = x[0]
            projected_point = _point - distance * self.normal
            u = 1-x[1]
            v = 1-x[2]

        distance = abs(distance)

        if not (0<=u<=1 and 0<=v<=1):
            if u < 0:
                u = 0
            elif u > 1:
                u = 1

            if v < 0:
                v = 0
            elif v > 1:
                v = 1

            projected_point = self.point_on_quad(u,v)
            distance = np.linalg.norm(_point-projected_point)

        return projected_point, distance, u, v

    def measure_centroid_distance_squared(self, _point):
        import numpy as np

        r = self.centroid-_point
        return np.dot(r,r)

    def compute_plane_corner_points(self, _vertexlist):
        import numpy as np

        if self.is_plane:
            return _vertexlist[self.vertex_ids]
        else:
            #return corner points projected onto fit plane!
            vertices = _vertexlist[self.vertex_ids]
            projected_vertices = np.zeros([4,3])
            i = 0
            for vertex in vertices:
                projected_vertex, distance = self.projection_onto_plane(vertex)
                projected_vertices[i,:] = projected_vertex
                i += 1

            return projected_vertices

    def getEdges(self):

        edges = []
        n = len(self.vertices)

        for i in range(n):
            edges.append([self.vertices[i], self.vertices[(i+1)%n]])

        return edges

    def isAdjacent(self, face):
        face_edges = face.getEdges();
        flag = 0

        for edge in self.getEdges():
            if (edge in face_edges) or ([edge[1], edge[0]] in face_edges):
                flag = 1

        return flag;

    def adjacentEdges(self, vert):
        adjacent_edges = []
        for edge in self.getEdges():
            if vert in edge:
                adjacent_edges.append(edge)
        return adjacent_edges


   # def find_neighbors(self, facelist):
#
 #       neighbors = []
#
 #       edges = self.getEdges()

#        for face in facelist:
#
 #           if face.quad_id != self.quad_id:

  #              face_edges = face.getEdges()

   #             for edge in face_edges:
    #                if (edge in edges):
     #                   neighbors.append(face)

#        return neighbors