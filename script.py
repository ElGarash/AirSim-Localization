import pandas
import math
import airsim


def destroy_stationery_vehicles(client):
    """
    Remove stationary vehicles from the environments
    List of stationary vehicles objects exist in vehicles.txt
    """
    with open("vehicles.txt") as f:
        vehicles = map(str.strip, f.readlines())
        for vehicle in vehicles:
            client.simDestroyObject(vehicle)


def adjust_recording_parameters(client, aerial_pitch=50, ground_fov=120):
    """
    Customize recording parameters.

    Recommended parameters by 2020's AirSim paper are:
    - aerial_pitch=50
    - ground_fov=120
    """
    client.simSetCameraFov("front_center", ground_fov, "GroundDrone1")
    client.simSetCameraFov("front_center", ground_fov, "GroundDrone2")
    client.simSetCameraFov("front_center", ground_fov, "GroundDrone3")
    client.simSetCameraFov("front_center", ground_fov, "GroundDrone4")
    client.simSetCameraPose(
        "bottom_center",
        airsim.Pose(
            orientation_val=airsim.to_quaternion(math.radians(aerial_pitch), 0, 0)
        ),
        "AerialDrone",
    )


def initialize_drones(client):
    """
    Allow API control and taking off.
    """
    # Allow API Control
    client.enableApiControl(True, "AerialDrone")
    client.enableApiControl(True, "GroundDrone1")
    client.enableApiControl(True, "GroundDrone2")
    client.enableApiControl(True, "GroundDrone3")
    client.enableApiControl(True, "GroundDrone4")
    # Arm the vehicles (Not really sure what it means)
    client.armDisarm(True, "AerialDrone")
    client.armDisarm(True, "GroundDrone1")
    client.armDisarm(True, "GroundDrone2")
    client.armDisarm(True, "GroundDrone3")
    client.armDisarm(True, "GroundDrone4")

    # Taking off
    f1 = client.takeoffAsync(vehicle_name="AerialDrone")
    f2 = client.takeoffAsync(vehicle_name="GroundDrone1")
    f3 = client.takeoffAsync(vehicle_name="GroundDrone2")
    f4 = client.takeoffAsync(vehicle_name="GroundDrone3")
    f5 = client.takeoffAsync(vehicle_name="GroundDrone4")
    f1.join()
    f2.join()
    f3.join()
    f4.join()
    f5.join()


def traverse_and_record_trajectory(client, aerial_altitude=-40, ground_altitude=-1):
    # Read the trajectory trajectory_data into a list
    trajectory_data = pandas.read_csv("trajectory.csv").values.tolist()

    # Append the z coordinate to the xs and ys and convert the paths into airsim vectors
    aerial_path = [airsim.Vector3r(*position, aerial_altitude) for position in trajectory_data]
    ground_path = [airsim.Vector3r(*position, ground_altitude) for position in trajectory_data]

    # Record and move on path
    client.startRecording()

    # Aerial drone
    f1 = client.moveOnPathAsync(
        aerial_path,
        velocity=10,
        drivetrain=airsim.DrivetrainType.ForwardOnly,
        yaw_mode=airsim.YawMode(False),
        vehicle_name="AerialDrone",
    )
    # First ground drone
    f2 = client.moveOnPathAsync(
        ground_path,
        velocity=10,
        drivetrain=airsim.DrivetrainType.ForwardOnly,
        yaw_mode=airsim.YawMode(False),
        vehicle_name="GroundDrone1",
    )
    # Second ground drone
    f3 = client.moveOnPathAsync(
        ground_path,
        velocity=10,
        drivetrain=airsim.DrivetrainType.ForwardOnly,
        yaw_mode=airsim.YawMode(False),
        vehicle_name="GroundDrone2",
    )
    # Third ground drone
    f4 = client.moveOnPathAsync(
        ground_path,
        velocity=10,
        drivetrain=airsim.DrivetrainType.ForwardOnly,
        yaw_mode=airsim.YawMode(False),
        vehicle_name="GroundDrone3",
    )
    # Fourth ground drone
    f5 = client.moveOnPathAsync(
        ground_path,
        velocity=10,
        drivetrain=airsim.DrivetrainType.ForwardOnly,
        yaw_mode=airsim.YawMode(False),
        vehicle_name="GroundDrone4",
    )
    f1.join()
    f2.join()
    f3.join()
    f4.join()
    f5.join()

    # Stop recording and reset
    client.stopRecording()
    client.reset()


if __name__ == "__main__":
    # Connect to the AirSim simulator
    client = airsim.MultirotorClient()
    client.confirmConnection()

    destroy_stationery_vehicles(client)
    adjust_recording_parameters(client)
    initialize_drones(client)
    traverse_and_record_trajectory(client)
