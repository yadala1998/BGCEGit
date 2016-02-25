__author__ = 'erik'

from getExtraOrdCornerIndexMask import getExtraOrdCornerIndexMask
from createBicubicCoefMatrices import createBicubicCoefMatrices
from getBezierPointCoefs import getBiquadraticPatchCoefs
from get3x3ControlPointIndexMask import get3x3ControlPointIndexMask
from raiseBezDegree import raiseDeg2D

def multiply_patch(point_coefs, points):
    import numpy as np

    assert type(point_coefs) is np.ndarray
    assert type(points) is np.ndarray

    i_max = np.size(point_coefs, 2)
    j_max = np.size(point_coefs, 3)

    result = np.zeros(i_max, j_max, 3)
    for d in range(np.size(points, 2)):
        for l in range(np.size(point_coefs, 1)):
            for k in range(np.size(point_coefs, 0)):
                result[:, :, d] = result[:, :, d] + point_coefs[k, l, :, :] * points[:, :, d]

    return result


def createNURBSMatricesAllraised(quad_list, AVertexList, B1VertexList, B2VertexList, CVertexList, quad_control_point_indices, control_points):

    import numpy as np

    assert type(control_points) is np.ndarray

    whichCornerList = np.array([[0, 3], [1, 2]], dtype=int)

    one4toone2 = lambda x: np.floor(x/3)

    whichCornerFun = lambda x, y: whichCornerList[one4toone2(x), one4toone2(y)]

    is_in_corner = lambda x, y: (x == 0 or x == 3) and (y == 0 or y == 3)

    number_of_quads = np.size(quad_list, 0)
    ordinaryCoefsRaw = np.zeros((3,3,3,3))
    allCoefsRaw = np.zeros((4, 7, 7, 4, 4))
    verticesTemp = np.zeros(4, 7, 3)
    tempBiquadBezierMatrix = np.zeros(3, 3, 3)
    NURBSMatrix = np.zeros(13*13*number_of_quads, 3)
    NURBSIndices = np.zeros(number_of_quads, 13*13)

    for num_quads in range(3,8):
        allCoefsRaw[0, num_quads-1, 0:num_quads, :, :], \
            allCoefsRaw[1, num_quads-1, 0:num_quads, :, :], \
            allCoefsRaw[2, num_quads-1, 0:num_quads, :, :], \
            allCoefsRaw[3, num_quads-1, 0:num_quads, :, :] = createBicubicCoefMatrices(num_quads)

    for bezierI in range(3):
        for bezierJ in range(3):
            ordinaryCoefsRaw[:, :, bezierI, bezierJ] = getBiquadraticPatchCoefs(bezierI, bezierJ)

    getLinearIndexing = lambda x, y, width: x + y*width
    for q in range(number_of_quads):
        for j in range(4):
            for i in range(4):
                addToIndexI = i*3
                addToIndexJ = j*3

                if is_in_corner(i, j):
                    whichCorner = whichCornerFun(i, j)
                    indexMask = getExtraOrdCornerIndexMask(quad_list, AVertexList, B1VertexList, B2VertexList, CVertexList, quad_control_point_indices, q, whichCorner)
                    numberOfEdges = np.size(indexMask,1)

                    for k in range(4):
                        verticesTemp[k, 0:numberOfEdges, :] = control_points[indexMask[k, :], :]

                    patch = multiply_patch(allCoefsRaw[:, numberOfEdges-1, 0:numberOfEdges, :, :], verticesTemp)

                    #shift the points to lie in the same order as the nurbs
                    #patch: corner 3 is in the correct orientation, the next
                    #(corner 4) needs to be rotated one 90deg rotation
                    #clockwise, the next another one clockwise etc...
                    patch = np.rot90(patch, whichCorner-2)

                    for jPatch in range(4):
                        for iPatch in range(4):
                            NURBScurrentIndex = q*13*13 + getLinearIndexing(iPatch+addToIndexI, jPatch+addToIndexJ, 13)
                            NURBSMatrix[NURBScurrentIndex, :] = patch[iPatch, jPatch, :]
                            NURBSIndices[q, getLinearIndexing(iPatch+addToIndexI, jPatch+addToIndexJ, 13)] = NURBScurrentIndex

                else:
                    neighbourMask = get3x3ControlPointIndexMask(quad_list, quad_control_point_indices, q, np.array([i,j]))

                    for jPatch in range(3):
                        for iPatch in range(3):
                            tempBiquadBezierMatrix[iPatch, jPatch, :] = control_points[neighbourMask[iPatch,jPatch],:]

                    tempBiquadBezierMatrix = multiply_patch(ordinaryCoefsRaw, tempBiquadBezierMatrix)
                    raisedBiquadMatrix = raiseDeg2D(tempBiquadBezierMatrix)

                    for jPatch in range(3):
                        for iPatch in range(3):
                            NURBScurrentIndex = q*13*13 + getLinearIndexing(iPatch+addToIndexI,jPatch+addToIndexJ, 13)
                            NURBSMatrix[NURBScurrentIndex, :] = raisedBiquadMatrix[iPatch, jPatch, :]
                            NURBSIndices[q,getLinearIndexing(iPatch+addToIndexI, jPatch+addToIndexJ, 13)] = NURBScurrentIndex

    return NURBSMatrix, NURBSIndices
