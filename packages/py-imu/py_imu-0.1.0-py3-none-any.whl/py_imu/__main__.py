"""Test the modules in py-imu."""

import argparse

import numpy as np
from loguru import logger

from py_imu.definitions import DEFAULT_LOG_LEVEL, LogLevel
from py_imu.fusion.madgwick import Madgwick
from py_imu.fusion.motion import Motion
from py_imu.fusion.quaternion import Vector3D
from py_imu.utils import setup_logger


def main(
    log_level: str = DEFAULT_LOG_LEVEL, stderr_level: str = DEFAULT_LOG_LEVEL
) -> None:
    """Test the modules in py-imu."""
    setup_logger(log_level=log_level, stderr_level=stderr_level)

    madgwick = Madgwick(frequency=100.0, gain=0.033)
    estimator = Motion(
        declination=9.27, latitude=32.253460, altitude=730, magfield=47392.3
    )

    sample_data = 10 * [np.array([5.0, 2.0, 0.0, 0.0, 0.0, 9.81])]
    # provide time increment dt based on time expired between each sensor reading
    for data in sample_data:
        gyr = Vector3D(data[0:3])
        acc = Vector3D(data[3:6])

        madgwick.update(gyr=gyr, acc=acc, dt=0.01)

        estimator.update(q=madgwick.q, acc=acc, timestamp=0.01, moving=True)
        logger.info(
            f"Pos: {estimator.worldPosition} m, Vel: {estimator.worldVelocity} m/s"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Run the pipeline.")
    parser.add_argument(
        "--log-level",
        "-l",
        default=DEFAULT_LOG_LEVEL,
        choices=list(LogLevel()),
        help="Set the log level.",
        required=False,
        type=str,
    )
    parser.add_argument(
        "--stderr-level",
        "-s",
        default=DEFAULT_LOG_LEVEL,
        choices=list(LogLevel()),
        help="Set the std err level.",
        required=False,
        type=str,
    )
    args = parser.parse_args()
    main(log_level=args.log_level, stderr_level=args.stderr_level)
