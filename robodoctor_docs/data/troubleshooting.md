# TurtleBot3 Troubleshooting Notes

> Summary of the ROBOTIS TurtleBot3 official e-Manual. Check the full documentation for your exact model and ROS version.

## Useful status topics

- `/battery_state`: battery information, including voltage and remaining capacity.
- `/diagnostics`: status of connected components such as the IMU, DYNAMIXEL motors, LDS sensor, battery, and OpenCR.
- `/odom`: encoder-based odometry / position and orientation.
- `/sensor_state`: encoder values, battery, and torque status.
- `/scan`: laser distance sensor readings.

## Robot does not move

1. Confirm the robot is powered and the correct TurtleBot3 model is configured.
2. Check `/diagnostics` and `/sensor_state` for reported component or torque status.
3. Check `/battery_state` for battery information.
4. Inspect motor connections and follow the official model-specific motor setup procedure.
5. Confirm robot bringup is running before teleoperation.

## Battery or power concern

1. Check `/battery_state` for reported voltage and remaining capacity.
2. Inspect the battery and connectors for visible damage.
3. Stop testing if the battery is swollen, damaged, unusually hot, or smells unusual.
4. Follow the manufacturer's charging guidance. The official FAQ says charging and discharging at the same time is not recommended.

Do not diagnose battery health from voltage alone; use the official limits for the exact model.

## Sensor readings missing or stale

1. Open `rqt` and select Topic Monitor.
2. Enable the relevant topic and check whether values update.
3. Check `/diagnostics` for component status.
4. Verify bringup, sensor drivers, and ROS/model compatibility.

## Wireless / remote-control issues

1. Confirm the robot and remote computer are on the expected network.
2. Verify that bringup is running.
3. For remote access, check SSH configuration and the hostname/IP address.
4. The official FAQ notes time synchronization assumes both devices have internet access on the same network.

## Motor configuration

The official FAQ documents a model-specific DYNAMIXEL setup procedure using OpenCR. Follow it for the exact model; do not guess motor IDs, baud rates, or firmware.

## Robot Starts or Turns On Unexpectedly

### Symptoms
- The robot powers on without an expected command.
- The robot starts moving unexpectedly.

### Possible Causes
- An automatic startup script or scheduled process.
- A remote-control command.
- A faulty power switch or electrical circuit.
- A control-system configuration issue.

### Recommended Checks
1. Check the power switch and wiring.
2. Inspect startup scripts and automatic launch settings.
3. Check remote-control commands and logs.
4. If the robot moves unexpectedly, stop it safely and disconnect power if safe to do so.
5. Do not assume the cause until the hardware and software have been inspected.


## Sources

- Basic Operation: https://emanual.robotis.com/docs/en/platform/turtlebot3/basic_operation/
- FAQ: https://emanual.robotis.com/docs/en/platform/turtlebot3/faq/
- Bringup: https://emanual.robotis.com/docs/en/platform/turtlebot3/bringup/
