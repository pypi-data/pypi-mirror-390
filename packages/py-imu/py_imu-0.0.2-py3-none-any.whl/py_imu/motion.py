"""Motion calculation from IMU data."""

import time
from copy import copy

import numpy as np

from py_imu.quaternion import Quaternion, Vector3D
from py_imu.utilities import RunningAverage, gravity, sensorAcc

MIN_MOTION_TIME = 0.5  # seconds, need to have had at least half of second motion to update velocity bias
HEADING_AVG_HISTORY = 5


class Motion:
    """IMU Motion Estimation."""

    def __init__(self, **kwargs):
        # Default values are for Tucson, Arizona, USA
        # This will is needed to compute magnitude of gravity
        #   which is subtracted from measured acceleration
        self.latitude = kwargs.get("latitude", 32.253460)  # decimal degrees
        self.altitude = kwargs.get("altitude", 730)  # meter

        self.m_heading_X = RunningAverage(HEADING_AVG_HISTORY)
        self.m_heading_Y = RunningAverage(HEADING_AVG_HISTORY)

        self.residuals_bias = Vector3D(0, 0, 0)  # on  the device frame coordinates

        self.worldResiduals = Vector3D(0, 0, 0)
        self.worldResiduals_previous = Vector3D(0, 0, 0)

        self.worldVelocity = Vector3D(0, 0, 0)
        self.worldVelocity_drift = Vector3D(0, 0, 0)  # in world corrdinate system
        self.world_velocity_previous = Vector3D(0, 0, 0)

        self.worldPosition = Vector3D(0, 0, 0)
        self.worldPosition_previous = Vector3D(0, 0, 0)

        self.driftLearningAlpha = 0.01  # Poorman's low-pass filter

        self.heading_X_avg = 0.0
        self.heading_Y_avg = 0.0
        self.m_heading = 0.0  # average heading in radians

        self.motion = False  # is the device moving?
        self.motion_previous = False
        self.motionStart_time = time.perf_counter()

        self.timestamp_previous = -1.0
        self.dt_motion = (
            0.0  # no motion has occurred yet, length of motion period in seconds
        )
        self.dt = 0.0

        self.localGravity = gravity(
            latitude=self.latitude, altitude=self.altitude
        )  # Gravity on Earth's (ellipsoid) Surface

    def reset(self):
        """Reset Motion Estimation."""
        self.residuals_bias = Vector3D(0, 0, 0)
        self.worldVelocity = Vector3D(0, 0, 0)
        self.worldPosition = Vector3D(0, 0, 0)
        self.world_velocity_previous = Vector3D(0, 0, 0)
        self.worldVelocity_drift = Vector3D(0, 0, 0)
        self.motion = False

    def resetPosition(self):
        """Reset Position."""
        self.worldPosition = Vector3D(0, 0, 0)
        self.worldPosition_previous = Vector3D(0, 0, 0)

    def updateAverageHeading(self, heading) -> float:
        """Update Average Heading."""
        ## this needs two component because of 0 - 360 jump at North
        self.m_heading_X.update(np.cos(heading))
        self.m_heading_Y.update(np.sin(heading))
        self.m_heading = np.atan2(self.m_heading_Y.avg, self.m_heading_X.avg)
        if self.m_heading < 0:
            self.m_heading += 2 * np.pi
        return self.m_heading

    def update(self, q: Quaternion, acc: Vector3D, moving: bool, timestamp: float):
        """Update Motion Estimation."""
        # Input:
        #  Quaternion
        #  Timestamp
        # Calculates:
        #  Acceleration in world coordinate system
        #  Velocity in world coordinate system
        #  Position in world coordinate system
        # If there is no motion
        #  Acceleration bias is updated
        #  Velocity bias is updated

        # Integration Time Step
        if self.timestamp_previous < 0.0:
            dt = 0.0
        else:
            dt = timestamp - self.timestamp_previous
            if dt > 1.0:
                # we had reconnection, avoid updating with large dt
                dt = 0.0
        self.timestamp_previous = copy(timestamp)

        # Acceleration residuals on the sensor
        self.residuals = sensorAcc(acc=acc, q=q, g=self.localGravity)
        self.residuals -= self.residuals_bias

        # Acceleration residuals in world coordinate system
        # self.worldResiduals = (q * self.residuals * q.conjugate).v
        self.worldResiduals = self.residuals.rotate(q.r33)

        # Motion Status, ongoing, no motion, ended?
        motion_ended = False
        if not self.motion_previous:
            if moving:
                # Motion Started
                self.motionStart_time = copy(timestamp)
        elif not moving:
            # Motion Ended
            motion_ended = True
        # Keep track of previous status
        self.motion_previous = copy(moving)

        # Update Velocity and Position when moving
        if moving:
            # Integrate acceleration and add to velocity (uses trapezoidal integration technique
            self.worldVelocity = self.world_velocity_previous + (
                (self.worldResiduals + self.worldResiduals_previous) * 0.5 * dt
            )
            self.dt_motion += dt

            # Update Velocity
            self.worldVelocity = self.worldVelocity - (self.worldVelocity_drift * dt)

            # Integrate velocity and add to position
            self.worldPosition = (
                self.worldPosition_previous
                + (self.worldVelocity + self.world_velocity_previous) * 0.5 * dt
            )

            # keep a history of previous values
            self.worldResiduals_previous = copy(self.worldResiduals)
            self.world_velocity_previous = copy(self.worldVelocity)
            self.worldPosition_previous = copy(self.worldPosition)

        else:  # no Motion
            # Estimate Velocity Bias when not moving
            # When motion ends, velocity should be zero
            if motion_ended and (self.dt_motion > MIN_MOTION_TIME):
                self.worldVelocity_drift = (
                    self.worldVelocity_drift * (1.0 - self.driftLearningAlpha)
                ) + ((self.worldVelocity / self.dt_motion) * self.driftLearningAlpha)
                self.dt_motion = 0.0

            # Reset Residuals
            self.worldResiduals_previous = Vector3D(x=0.0, y=0.0, z=0.0)
            # Reset Velocity
            self.worldVelocity = Vector3D(x=0.0, y=0.0, z=0.0)
            self.world_velocity_previous = Vector3D(x=0.0, y=0.0, z=0.0)

            # Update acceleration bias, when not moving residuals should be zero
            # If the accelerometer is not calibrated properly, subtracting bias will cause drift
            self.residuals_bias = (
                self.residuals_bias * (1.0 - self.driftLearningAlpha)
            ) + (self.residuals * self.driftLearningAlpha)

        self.dt = dt
