__author__ = 'anna'
import numpy as np
from vertex import Vertex
from quad import Quad

def DooSabin(vertices, faces, alpha, iter):
    vertices_refined = []
    faces_refined = []

    vertices_children = [ [] for _ in range(len(vertices))]#[None]*len(vertices)
    edges = []

    #get list of edges
    for face in faces:
        for edge in face.getEdges():
            if not ((edge in edges) or ([edge[1], edge[0]] in edges)):
                edges.append(edge)

    edges_children = [ [] for _ in range(len(edges))]

    for face in faces:
        F = face.centroid
        numberOfVertices = len(face.vertex_ids)

        newVertices = []
        for j in range(numberOfVertices):
            v = Vertex(len(vertices_refined),[face.vertices[j].coordinates[l]*(1 - alpha) + F[l]*alpha for l in range(3)])
            vertices_children[face.vertices[j].id].append([face, v])
            vertices_refined.append(v)

            for edge in face.adjacentEdges(face.vertices[j]):
                if edge in edges:
                    edges_children[edges.index(edge)].append([v, edge.index(face.vertices[j]), face, "asIs"])
                else:
                    #positioning is assigned with respect to the orientation of the edge in the list
                    edges_children[edges.index([edge[1], edge[0]])].append([v, 1-edge.index(face.vertices[j]), face, "reversed"])

            newVertices.append(v)

        new_face = Quad(len(faces_refined), newVertices)

        if iter == 1:
            new_face.type = "center"
            new_face.parents.append(face)
        if iter == 2:
            new_face.type = "center"
            new_face.parent_type = face.type

            if face.type == "center":
                globalIndicesInOrderedOriginalQuad = [5, 6, 10, 9]
                for i in range(len(face.parents[0].vertices)):
                    face.parents[0].ordered_refined_vertices[globalIndicesInOrderedOriginalQuad[i]] = newVertices[i]
                    face.parents[0].vertices[i].A.append([face.parents[0], newVertices[i]])

            if face.type == "vertex":
                globalIndicesInOrderedOriginalQuad = [0, 3, 15, 12]
                parent_faces = face.parents
             #   print("list of parents when try to add to the refined list", [parent_faces[i].quad_id for i in range(len(parent_faces))])
                for i in range(numberOfVertices):
                    face.parent_vertex.C.append([face.parents[i], newVertices[i]])
                    ind = face.parents[i].vertices.index(face.parent_vertex)
                    #print(face.parents[i].quad_id)
                    face.parents[i].ordered_refined_vertices[globalIndicesInOrderedOriginalQuad[ind]] = newVertices[i]

            if face.type == "edge":
                globalIndicesInOrderedOriginalQuad = [[1, 7, 14, 8], [2, 11, 13, 4]]

                parent_edge = face.parent_edge
                positioning = face.edge_face_positioning

                for parent_local_id in range(2):
                    if parent_edge in face.parents[parent_local_id].edges:
                        #ids in the face parent_local_id*2, parent_local_id*2+1
                        edge_id = face.parents[parent_local_id].edges.index(parent_edge)
                        face.parents[parent_local_id].ordered_refined_vertices[globalIndicesInOrderedOriginalQuad[positioning[parent_local_id*2]][edge_id]] = newVertices[parent_local_id*2]
                        face.parents[parent_local_id].ordered_refined_vertices[globalIndicesInOrderedOriginalQuad[positioning[parent_local_id*2+1]][edge_id]] = newVertices[parent_local_id*2+1]

                    else:
                        edge_id = face.parents[parent_local_id].edges.index([parent_edge[1], parent_edge[0]])

                        face.parents[parent_local_id].ordered_refined_vertices[globalIndicesInOrderedOriginalQuad[1-positioning[parent_local_id*2]][edge_id]] = newVertices[parent_local_id*2]
                        face.parents[parent_local_id].ordered_refined_vertices[globalIndicesInOrderedOriginalQuad[1-positioning[parent_local_id*2+1]][edge_id]] = newVertices[parent_local_id*2+1]

                #get the neighbouring "vertex" faces with respect to our current "edge" face
                neighbouringVertexFaces = [face.parent_edge[i].childFace for i in range(2)]
                for i in range(2):
                    #for each of the neighbouring faces find the shared edge
                    sharedEdge = neighbouringVertexFaces[i].isAdjacent(face)
                    indexOfSharedEdge = neighbouringVertexFaces[i].edges.index(sharedEdge)
                    #ordered original faces containing the vertices of the "vertex" face
                    for vert in sharedEdge:
                        #the local id of the face in original grid, containing the current vertex
                         localFaceId = neighbouringVertexFaces[i].vertices.index(vert)
                         grandParentFace = neighbouringVertexFaces[i].parents[localFaceId]
                        # if parent_edge in grandParentFace.edges:
                        #     positioning = face.edge_face_positioning
                        #     localInd = face.vertices.index(vert)
                        #     grandParentFace.ordered_refined_vertices[globalIndicesInOrderedOriginalQuad[positioning[localInd]][grandParentFace.edges.index(parent_edge)]]
                        # else:
                        #     positioning = face.edge_face_positioning
                        #     localInd = face.vertices.index(vert)
                        #     grandParentFace.ordered_refined_vertices[globalIndicesInOrderedOriginalQuad[1-positioning[localInd]][grandParentFace.edges.index([parent_edge[1], parent_edge[0]])]]
                         if localFaceId == indexOfSharedEdge:
                            #print("Here!")
                            face.parent_edge[i].B2.append([grandParentFace, newVertices[face.vertices.index(vert)], face.parent_edge])
                         else:
                            face.parent_edge[i].B1.append([grandParentFace, newVertices[face.vertices.index(vert)], face.parent_edge])




        for vertex in newVertices:
            vertex.addNeighbouringFace(new_face)

        faces_refined.append(new_face)

    #Loop through vertices, getting the faces of the type "vertex"
    for vert in vertices:
        n = len(vertices_children[vert.id])
        new_face_vertices = [vertices_children[vert.id][i][1] for i in range(n)]
        parent_faces = [vertices_children[vert.id][i][0] for i in range(n)]
       # print("Parent faces when create a vertex face ids", [parent_faces[i].quad_id for i in range(len(parent_faces))])
        face_ordered = [vertices_children[vert.id][0][1]]
        parent_faces_ordered = [vertices_children[vert.id][0][0]]
        current_face = parent_faces[0]

        for i in range(1, n, 1):
            j = 0
            while (not current_face.isAdjacent(parent_faces[j])) or (new_face_vertices[j] in face_ordered):
                j += 1

            face_ordered.append(new_face_vertices[j])
            parent_faces_ordered.append(parent_faces[j])
          #  print("ordered face",[parent_faces_ordered[i].quad_id for i in range(len(face_ordered))])
            current_face = parent_faces[j]

        face_object = Quad(len(faces_refined), face_ordered)
        vert.childFace = face_object

        if iter == 1:
            face_object.type = "vertex"
            for i in range(len(parent_faces_ordered)):
                face_object.parents.append(parent_faces_ordered[i])
            face_object.parent_vertex = vert

        for vertex in new_face_vertices:
            vertex.addNeighbouringFace(face_object)

        faces_refined.append(face_object)

    #Loop through edges, getting the faces of the type "edge"
    for i in range(len(edges)):
        n = 4 #edge always has four children!
        new_face_vertices_positioning = [edges_children[i][j][1] for j in range(n)]

        new_face_vertices = [edges_children[i][0][0], edges_children[i][1][0]]
        if new_face_vertices_positioning[2] == new_face_vertices_positioning[1]:
            new_face_vertices.append(edges_children[i][2][0])
            new_face_vertices.append(edges_children[i][3][0])

        else:
            new_face_vertices.append(edges_children[i][3][0])
            new_face_vertices.append(edges_children[i][2][0])
            temp = new_face_vertices_positioning[3]
            new_face_vertices_positioning[3] = new_face_vertices_positioning[2]
            new_face_vertices_positioning[2] = temp

        face_object = Quad(len(faces_refined), new_face_vertices)
        face_object.edge_face_positioning = new_face_vertices_positioning
        face_object.parent_edge = edges[i]
        face_object.parents = [edges_children[i][j][2] for j in range(0,4, 2)]

        if iter == 1:
            face_object.type = "edge"

        faces_refined.append(face_object)


    return [vertices_refined, faces_refined]




def addFace(verts):

    return