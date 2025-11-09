"""
Define the functions for defining and manipulating degrees of freedom.
"""

U1 = 0
"""
This is a designation of the degree of freedom as translation along ``X``.
"""
U2 = 1
"""
This is a designation of the degree of freedom as translation along ``Z`` (in
2D models) or along ``Y`` (in 3D models).
"""
U3 = 2
"""
This is a designation of the degree of freedom as translation along ``Z`` (in 3D
models).
"""
UR1 = 3
"""
This is a designation of the degree of freedom as rotation about  ``X`` (in 3D
models).
"""
UR2 = 4
"""
This is a designation of the degree of freedom as rotation about  ``Y`` (in 3D
models).
"""
UR3 = 5
"""
This is a designation of the degree of freedom as rotation about  ``Y`` (in 2D
models) or rotation about ``Z``  (in 3D models).
"""
ALL_DOFS = 100
"""
This (``ALL_DOFS``) is a designation of all the degrees of freedom, translations and rotations
(``U1``, ``U2``, ``UR3`` in 2D models, or ``U1``, ``U2``, ``U3``, ``UR1``,
``UR2``, ``UR3`` in 3D models). It may be used to specify the clamped condition
for the joint.
"""
TRANSLATION_DOFS = 200
"""
This (``TRANSLATION_DOFS``) is a designation of the translation degrees of
freedom (``U1``, ``U2``, in 2D models, or ``U1``, ``U2``,  ``U3`` in 3D
models). It may be used to specify the pinned condition for the joint.
"""


def translation_dofs(dim):
    """
    List the translation degrees of freedom.

    Parameters
    ----------
    dim
        Dimension of the model (2 or 3).

    Returns
    -------
    list
        The list varies according to whether ``dim`` implies two dimensions (2)
        or three dimensions (3): ``[U1, U2]`` or ``[U1, U2, U3]``.
    """
    if dim == 2:
        return [U1, U2]
    else:
        return [U1, U2, U3]


def rotation_dofs(dim):
    """
    List the rotation degrees of freedom.

    Parameters
    ----------
    dim
        Dimension of the model (2 or 3).

    Returns
    -------
    list
        The list varies according to whether ``dim`` implies two dimensions (2)
        or three dimensions (3): ``[UR3]`` or ``[UR1, UR2, UR3]``.
    """
    if dim == 2:
        return [UR3]
    else:
        return [UR1, UR2, UR3]


def translation_and_rotation_dofs(dim):
    """
    List both the translation and rotation degrees of freedom.

    Parameters
    ----------
    dim
        Dimension of the model (2 or 3).

    Returns
    -------
    list
        The list varies according to whether ``dim`` implies two dimensions (2)
        or three dimensions (3).

    See Also
    --------
    :func:`translation_dofs`
    :func:`rotation_dofs`
    """
    return translation_dofs(dim) + rotation_dofs(dim)


def prescribed_dofs_and_values(dim, dof, value):
    """
    Compute prescribed degrees of freedom and values for a particular support
    type.

    Parameters
    ----------
    dim
        Dimension of the model (2 or 3).
    dof
        One of the designations of a degree of freedom. Either individual
        (``U1``, ...), or collective (``ALL_DOFS``, ...).
    value
        A single number, prescribed by the user.

    Returns
    -------
    tuple of lists
        For a single ``dof`` and ``value``, return just the tuple of the ``[dof]`` and
        ``[value]``.

        For ``dof`` equal to ``ALL_DOFS``, return the translation and rotation degrees
        of freedom and zero values.

        For ``dof`` equal to ``TRANSLATION_DOFS``, return the translation degrees of
        freedom and zero values.
    """
    if dof == ALL_DOFS:
        return translation_and_rotation_dofs(dim), [
            0.0 for d in translation_and_rotation_dofs(dim)
        ]
    elif dof == TRANSLATION_DOFS:
        return translation_dofs(dim), [0.0 for d in translation_dofs(dim)]
    return [dof], [value]
