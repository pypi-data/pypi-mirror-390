"""
Define rotation utilities.

"""

from math import pi, cos, sin
import numpy
from pystran.geometry import delt, vlen


def rotmat3(rotvec):
    """
    Compute a 3D rotation matrix from a rotation vector.

    Parameters
    ----------
    rotvec
        Array: rotation vector.

    Returns
    -------
    array
    """
    R = numpy.zeros((3, 3))
    vn = numpy.linalg.norm(rotvec)
    if vn == 0.0:
        R = numpy.identity(3)
    else:
        rotvecn = (rotvec[0] / vn, rotvec[1] / vn, rotvec[2] / vn)
        ca = cos(vn)
        sa = sin(vn)
        oca = 1.0 - ca
        for j in range(3):
            for i in range(3):
                R[i, j] = oca * rotvecn[i] * rotvecn[j]

        R[0, 1] += sa * -rotvecn[2]
        R[0, 2] += sa * rotvecn[1]
        R[1, 0] += sa * rotvecn[2]
        R[1, 2] += sa * -rotvecn[0]
        R[2, 0] += sa * -rotvecn[1]
        R[2, 1] += sa * rotvecn[0]
        R[0, 0] += ca
        R[1, 1] += ca
        R[2, 2] += ca
    return R


def rotate(i, j, v, angleindegrees):
    """
    Rotate a 3D vector ``v`` by an angle about the unit vector defined by joints
    ``i`` and ``j``.

    Parameters
    ----------
    i
        First joint.
    j
        Second joint.
    v
        Vector to be rotated. Can be supplied as a list, tuple, or array.
    angleindegrees
        Angle in degrees. Positive when counterclockwise about the vector
        ``j["coordinates"] - i["coordinates"]``.

    Returns
    -------
    array
        Rotated vector ``v``.
    """
    ci, cj = i["coordinates"], j["coordinates"]
    uv = delt(ci, cj) / vlen(ci, cj)
    angle = angleindegrees * pi / 180.0
    return rotmat3(uv * angle).dot(numpy.array(v))
