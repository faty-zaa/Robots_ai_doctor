# TurtleBot3 Reference Specifications

> Source: ROBOTIS TurtleBot3 official e-Manual. Confirm the exact model and hardware revision before using these values.

## Official comparison

| Specification | Burger | Waffle Pi |
|---|---:|---:|
| Maximum translational velocity | 0.22 m/s | 0.26 m/s |
| Maximum rotational velocity | 2.84 rad/s | 1.82 rad/s |
| Maximum payload | 15 kg | 30 kg |
| Size (L × W × H) | 138 × 178 × 192 mm | 281 × 306 × 141 mm |
| Weight (including SBC + battery + sensors) | 1 kg | 1.8 kg |
| Climbing threshold | 10 mm or lower | 10 mm or lower |
| Expected operating time | 2 h 30 min | 2 h |
| Expected charging time | 2 h 30 min | 2 h 30 min |
| SBC listed | Raspberry Pi 4 | Raspberry Pi 4 |
| Actuator listed | XL430-W250 | XM430-W210 |
| LDS | 360° LDS-02 | 360° LDS-02 |
| IMU | 3-axis gyroscope and accelerometer | 3-axis gyroscope and accelerometer |
| Camera | Not listed for Burger | Raspberry Pi Camera Module v2.1 |

## Useful ROS topics

- `/battery_state`: battery condition information.
- `/diagnostics`: status of connected components.
- `/odom`: odometry / encoder-based position and orientation.
- `/sensor_state`: encoder values, battery, and torque status.
- `/scan`: LDS sensor readings.

The documentation does not provide one universal numeric fault threshold for every reading. Avoid hard-coding thresholds unless supported by the documentation for the exact hardware.

## Sources

- Specifications: https://emanual.robotis.com/docs/en/platform/turtlebot3/features/
- Basic Operation: https://emanual.robotis.com/docs/en/platform/turtlebot3/basic_operation/
