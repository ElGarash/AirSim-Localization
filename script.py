import pandas
import math
import airsim

# Constant Parameters
PITCH_ANGLE = 50
AERIAL_ALTITUDE = -40
GROUND_ALTITUDE = -1

if __name__ == "__main__":
    # Connect to the AirSim simulator
    client = airsim.MultirotorClient()
    client.confirmConnection()

    # Allow API Control
    client.enableApiControl(True, "AerialDrone")
    client.enableApiControl(True, "GroundDrone")

    # Adjusting parameters to be in accordance with the paper
    client.simSetCameraFov("front_center", 120, "GroundDrone")
    client.simSetCameraPose(
        "bottom_center",
        airsim.Pose(orientation_val=airsim.to_quaternion(math.radians(PITCH_ANGLE), 0, 0)),
        "AerialDrone",
    )

    # Arm the vehicles (Not really sure what it means)
    client.armDisarm(True, "AerialDrone")
    client.armDisarm(True, "GroundDrone")

    # Taking off
    f1 = client.takeoffAsync(vehicle_name="AerialDrone")
    f2 = client.takeoffAsync(vehicle_name="GroundDrone")
    f1.join()
    f2.join()

    # Hovering (Not really sure what it means)
    f1 = client.hoverAsync("AerialDrone")
    f2 = client.hoverAsync("GroundDrone")
    f1.join()
    f2.join()

    # Read the trajectory trajectory_data into a list
    trajectory_data = pandas.read_csv("trajectory.csv").values.tolist()

    # Append the z coordinate to the xs and ys and convert the paths into airsim vectors
    aerial_path = [airsim.Vector3r(*position, AERIAL_ALTITUDE) for position in trajectory_data]
    ground_path = [airsim.Vector3r(*position, GROUND_ALTITUDE) for position in trajectory_data]

    # Record and move on path
    client.startRecording()

    f1 = client.moveOnPathAsync(
        aerial_path,
        10,
        drivetrain=airsim.DrivetrainType.ForwardOnly,
        yaw_mode=airsim.YawMode(False),
        vehicle_name="AerialDrone",
    )
    f2 = client.moveOnPathAsync(
        ground_path,
        10,
        drivetrain=airsim.DrivetrainType.ForwardOnly,
        yaw_mode=airsim.YawMode(False),
        vehicle_name="GroundDrone",
    )
    f1.join()
    f2.join()

    # Stop recording and reset
    client.stopRecording()
    client.reset()
