"""
Define utility for assembling.
"""

from numpy import arange


def assemble(kg, dof, k):
    """
    Assemble local matrix into a global matrix.

    Assemble local (stiffness or mass) matrix ``k`` into global (stiffness or
    mass) matrix ``kg``, using the array of degrees of freedom, ``dof``, for both
    the rows and columns. In other words, ``k`` must be symmetric.

    Parameters
    ----------
    kg
        Global matrix.
    dof
        Array of degrees of freedom.
    k
        Local (for instance, member) matrix.

    Returns
    -------
    kg
    """
    for r in arange(len(dof)):
        for c in arange(len(dof)):
            gr, gc = dof[r], dof[c]
            kg[gr, gc] += k[r, c]
    return kg
