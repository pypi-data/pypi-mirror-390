# Python Sensor Fusion
Fuse IMU data into a Quaternion pose.

## Install
To install the library run: `pip install py-imu`

## Development
0. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
1. `make init` to create the virtual environment and install dependencies
2. `make format` to format the code and check for errors
3. `make test` to run the test suite
4. `make clean` to delete the temporary files and directories
5. `poetry publish --build` to build and publish to https://pypi.org/project/py-imu

## Usage
```
from py_imu.madgwick import Madgwick
from py_imu.motion import Motion
from py_imu.quaternion import Vector3D

def main():
    """Test the modules in py-imu."""
    madgwick = Madgwick(frequency=100.0, gain=0.033)
    estimator = Motion(
        declination=9.27, latitude=32.253460, altitude=730, magfield=47392.3
    )

    # provide time increment dt based on time expired between each sensor reading
    for data in data_stream:
        gyr = Vector3D(data[0:3])
        acc = Vector3D(data[3:6])
        madgwick.update(gyr=gyr, acc=acc, dt=0.01)
        estimator.update(q=madgwick.q, acc=acc, timestamp=0.01, moving=True)

if __name__ == "__main__":
    main()
```
