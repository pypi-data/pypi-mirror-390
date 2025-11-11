"""Quaternion and Vector3D data types and functions."""

import math
import numbers

import numpy as np
from numpy.typing import NDArray

from py_imu.definitions import EPSILON


class Quaternion:
    """Quaternion Class.

    q1 = Quaternion(1., 2., 3., 4.)
    q2 = Quaternion(w=5., x=6., y=7., z=8.)
    q3 = Quaternion(np.array([9,10,11,12]))

    q5 = q1 + q2
    q6 = q1 * q2
    q7 = 2 * q1

    q1.conjugate
    q1.inverse
    q1.normalize()
    q1.r33 (cosine matrix)
    q1.norm: length of quaternion
    q1.v: vector part of quaternion as Vector3D
    q1.q: quaternion as np.array
    """

    def __init__(self, w=0.0, x=0.0, y=0.0, z=0.0, v=None):
        # allows any possible combination to be passed in
        if v is None:
            if isinstance(w, numbers.Number):
                self.w = w
                self.x = x
                self.y = y
                self.z = z

    def __str__(self):
        return f"Quaternion({self.w}, {self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        """Add two quaternions or quaternion and scalar."""
        if isinstance(other, Quaternion):
            return Quaternion(
                self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z
            )
        elif isinstance(other, np.ndarray):
            return Quaternion(
                self.w + other[0],
                self.x + other[1],
                self.y + other[2],
                self.z + other[3],
            )
        elif isinstance(other, numbers.Number):
            return Quaternion(
                self.w + other, self.x + other, self.y + other, self.z + other
            )
        else:
            raise TypeError(
                f"Unsupported operand type for +: Quaternion and {type(other)}"
            )

    def __sub__(self, other):
        """Subtract two quaternions or quaternion and scalar."""
        if isinstance(other, Quaternion):
            return Quaternion(
                self.w - other.w, self.x - other.x, self.y - other.y, self.z - other.z
            )
        elif isinstance(other, np.ndarray):
            return Quaternion(
                self.w - other[0],
                self.x - other[1],
                self.y - other[2],
                self.z - other[3],
            )
        elif isinstance(other, numbers.Number):
            return Quaternion(
                self.w - other, self.x - other, self.y - other, self.z - other
            )
        else:
            raise TypeError(
                f"Unsupported operand type for -: Quaternion and {type(other)}"
            )

    def __mul__(self, other):
        """Multiply two quaternions or quaternion and vector."""
        if isinstance(other, Quaternion):
            w = (
                (self.w * other.w)
                - (self.x * other.x)
                - (self.y * other.y)
                - (self.z * other.z)
            )
            x = (
                (self.w * other.x)
                + (self.x * other.w)
                + (self.y * other.z)
                - (self.z * other.y)
            )
            y = (
                (self.w * other.y)
                - (self.x * other.z)
                + (self.y * other.w)
                + (self.z * other.x)
            )
            z = (
                (self.w * other.z)
                + (self.x * other.y)
                - (self.y * other.x)
                + (self.z * other.w)
            )
            return Quaternion(w, x, y, z)
        elif isinstance(other, Vector3D):
            """
            multiply quaternion with vector
            vector is converted to quaternion with [0,vector]
            then computed the same as above with other.w=0
            """
            w = -(self.x * other.x) - (self.y * other.y) - (self.z * other.z)
            x = self.w * other.x + self.y * other.z - self.z * other.y
            y = self.w * other.y - self.x * other.z + self.z * other.x
            z = self.w * other.z + self.x * other.y - self.y * other.x
            return Quaternion(w, x, y, z)
        elif isinstance(other, numbers.Number):
            """multiply with scalar"""
            return Quaternion(
                self.w * other, self.x * other, self.y * other, self.z * other
            )
        else:
            raise TypeError("Unsupported operand type")

    def __rmul__(self, other):
        """Right multiplication."""
        return self.__mul__(other)

    def __truediv__(self, other):
        """Division."""
        if isinstance(other, numbers.Number):
            return Quaternion(
                self.w / other, self.x / other, self.y / other, self.z / other
            )
        else:
            raise TypeError("Unsupported operand type")

    def __floordiv__(self, other):
        """Floor division."""
        if isinstance(other, numbers.Number):
            return Quaternion(
                self.w // other, self.x // other, self.y // other, self.z // other
            )
        else:
            raise TypeError("Unsupported operand type")

    def __eq__(self, other):
        """Check that the two quaternions are equal."""
        return (
            self.w == other.w
            and self.x == other.x
            and self.y == other.y
            and self.z == other.z
        )

    def normalize(self):
        """Normalize the quaternion."""
        mag = self.norm
        if mag != 0:
            self.w = self.w / mag
            self.x = self.x / mag
            self.y = self.y / mag
            self.z = self.z / mag

    @property
    def v(self) -> NDArray:
        """Extract the vector component of the quaternion."""
        # return np.array([self.x,self.y,self.z])
        return Vector3D(self.x, self.y, self.z)

    @property
    def q(self) -> NDArray:
        """Convert the quaternion to np.array."""
        # return np.array([self.x,self.y,self.z])
        return np.array([self.w, self.x, self.y, self.z])

    @property
    def conjugate(self):
        """Conjugate of quaternion."""
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    @property
    def norm(self) -> float:
        """Length of quaternion."""
        return math.sqrt(
            self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z
        )

    @property
    def inverse(self):
        """Inverse of quaternion."""
        return self.conjugate / self.norm

    @property
    def r33(self) -> NDArray:
        """Quaternion to 3x3 rotation matrix."""
        # Normalize quaternion
        # self.normalize()

        # Compute rotation matrix elements
        xx = self.x * self.x
        xy = self.x * self.y
        xz = self.x * self.z
        xw = self.x * self.w
        yy = self.y * self.y
        yz = self.y * self.z
        yw = self.y * self.w
        zz = self.z * self.z
        zw = self.z * self.w

        # Construct the rotation matrix
        return np.array(
            [
                [1.0 - 2.0 * (yy + zz), 2.0 * (xy - zw), 2.0 * (xz + yw)],
                [2.0 * (xy + zw), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - xw)],
                [2.0 * (xz - yw), 2.0 * (yz + xw), 1.0 - 2.0 * (xx + yy)],
            ]
        )

    @property
    def isZero(self) -> bool:
        """Check whether the quaternion is zero."""
        return (
            abs(self.w) <= EPSILON
            and abs(self.x) <= EPSILON
            and abs(self.y) <= EPSILON
            and abs(self.z) <= EPSILON
        )


class Vector3D:
    """3D Vector Class.

    v1 = Vector3D(1., 2., 3.)
    v2 = Vector3D(x=4., y=5., z=6.)
    v3 = Vector3D(np.array([7,8,9]))

    v4 = v1 + v2
    v5 = v1 * v2
    v6 = 2. * v1

    v1.dot(v2)
    v1.cross(v2)
    v1.normalize()
    v1.norm: length of vector
    v1.rotate(np.array[3x3])
    v1.v: vector as np.array
    v1.q: vector as quaternion with w=0.
    """

    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, numbers.Number):
            self.x = x
            self.y = y
            self.z = z
        elif isinstance(x, np.ndarray):
            if len(x) == 3:
                self.x = x[0]
                self.y = x[1]
                self.z = x[2]
        elif isinstance(x, Vector3D):
            self.x = x.x
            self.y = x.y
            self.z = x.z

    def __copy__(self):
        """Copy the vector."""
        return Vector3D(self.x, self.y, self.z)

    def __bool__(self):
        """Check whether the vector is non-zero."""
        return not self.isZero

    def __abs__(self):
        """Absolute value of the vector."""
        return Vector3D(abs(self.x), abs(self.y), abs(self.z))

    def __neg__(self):
        """Negate the vector."""
        return Vector3D(-self.x, -self.y, -self.z)

    def __len__(self):
        """Length of the vector."""
        return 3

    def __str__(self):
        """Representation of the vector."""
        return f"Vector3D({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        """Representation of the vector."""
        return str(self)

    def __add__(self, other):
        """Add two vectors."""
        if isinstance(other, Vector3D):
            return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, numbers.Number):
            return Vector3D(self.x + other, self.y + other, self.z + other)
        else:
            raise TypeError(
                f"Unsupported operand type for +: Vector3D and {type(other)}"
            )

    def __sub__(self, other):
        """Subtract two vectors."""
        if isinstance(other, Vector3D):
            return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, numbers.Number):
            return Vector3D(self.x - other, self.y - other, self.z - other)
        else:
            raise TypeError(
                f"Unsupported operand type for -: Vector3D and {type(other)}"
            )

    def __mul__(self, other):
        """Multiplication."""
        if isinstance(other, numbers.Number):
            return Vector3D(self.x * other, self.y * other, self.z * other)
        elif isinstance(other, Vector3D):
            return Vector3D(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, np.ndarray):
            shape = other.shape
            if len(shape) == 1:
                if shape[0] == 3:
                    return Vector3D(
                        self.x * other[0], self.y * other[1], self.z * other[2]
                    )
                elif shape[0] == 4:
                    # other is quaternion of w,x,y,z convert vector to quaternion [0,x,y,z]

                    # x1, y1, z1     = self.v # w1 is 0, dont use
                    other_w, other_x, other_y, other_z = other
                    w = -self.x * other_x - self.y * other_y - self.z * other_z
                    x = self.x * other_w + self.y * other_z - self.z * other_y
                    y = -self.x * other_z + self.y * other_w + self.z * other_x
                    z = self.x * other_y - self.y * other_x + self.z * other_w
                    return Quaternion(w, x, y, z)

            elif shape == (3, 3):
                """Matrix Multiplication"""
                rotated_vector = np.dot(other, np.array([self.x, self.y, self.z]))
                # rotated_vector = np.dot(np.array([self.x,self.y,self.z]),other)
                return Vector3D(
                    x=rotated_vector[0], y=rotated_vector[1], z=rotated_vector[2]
                )

        elif isinstance(other, Quaternion):
            w = -self.x * other.x - self.y * other.y - self.z * other.z
            x = self.x * other.w + self.y * other.z - self.z * other.y
            y = -self.x * other.z + self.y * other.w + self.z * other.x
            z = self.x * other.y - self.y * other.x + self.z * other.w
            return Quaternion(w, x, y, z)
        else:
            raise TypeError(
                f"Unsupported operand type for *: Vector3D and {type(other)}"
            )

    def __rmul__(self, other):
        """Right multiplication."""
        return self.__mul__(other)

    def __truediv__(self, other):
        """Division."""
        if isinstance(other, numbers.Number):
            return Vector3D(self.x / other, self.y / other, self.z / other)
        elif isinstance(other, Vector3D):
            return Vector3D(self.x / other.x, self.y / other.y, self.z / other.z)
        else:
            raise ValueError(f"Unsupported operand type for /: {other}")

    def __floordiv__(self, other):
        """Floor division."""
        if isinstance(other, numbers.Number):
            return Vector3D(self.x // other, self.y // other, self.z // other)
        elif isinstance(other, Vector3D):
            return Vector3D(self.x // other.x, self.y // other.y, self.z // other.z)
        else:
            raise ValueError(f"Unsupported operand type for //: {other}")

    def __pow__(self, other):
        """Potentiate."""
        if isinstance(other, numbers.Number):
            return Vector3D(self.x**other, self.y**other, self.z**other)
        elif isinstance(other, Vector3D):
            return Vector3D(self.x**other.x, self.y**other.y, self.z**other.z)
        else:
            raise TypeError(
                f"Unsupported operand type for **: Vector3D and {type(other)}"
            )

    def __eq__(self, other):
        """Check whether the vectors are equal."""
        if isinstance(other, numbers.Number):
            return Vector3D(self.x == other, self.y == other, self.z == other)
        elif isinstance(other, Vector3D):
            return Vector3D(self.x == other.x, self.y == other.y, self.z == other.z)
        else:
            raise TypeError(
                f"Unsupported operand type for ==: Vector3D and {type(other)}"
            )

    def __lt__(self, other):
        """Is vector smaller than the other."""
        if isinstance(other, numbers.Number):
            return Vector3D(self.x < other, self.y < other, self.z < other)
        elif isinstance(other, Vector3D):
            return Vector3D(x=self.x < other.x, y=self.y < other.y, z=self.z < other.z)
        else:
            raise TypeError(
                f"Unsupported operand type for <=: Vector3D and {type(other)}"
            )

    def normalize(self):
        """Normalize vector."""
        mag = math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        if mag != 0:
            self.x = self.x / mag
            self.y = self.y / mag
            self.z = self.z / mag

    def rotate(self, other):
        """Rotate vector by rotation matrix."""
        if isinstance(other, np.ndarray):
            if other.shape == (3, 3):
                rotated_vector = np.dot(other, np.array([self.x, self.y, self.z]))
                # rotated_vector = np.dot(np.array([self.x,self.y,self.z]),other)
                return Vector3D(
                    x=rotated_vector[0], y=rotated_vector[1], z=rotated_vector[2]
                )
            else:
                raise TypeError(
                    f"Unsupported operand type for cross product: Vector3D and nd.array of shape {other.shape}"
                )
        else:
            raise TypeError(
                f"Unsupported operand type for cross product: Vector3D and {type(other)}"
            )

    @property
    def q(self):
        """Return np array with rotation 0 and vector x, y, z."""
        return Quaternion(w=0, x=self.x, y=self.y, z=self.z)

    @property
    def v(self) -> NDArray:
        """Returns np array of vector."""
        return np.array([self.x, self.y, self.z])

    @property
    def isZero(self) -> bool:
        """Check if vector is zero."""
        return (
            abs(self.x) <= EPSILON and abs(self.y) <= EPSILON and abs(self.z) <= EPSILON
        )
