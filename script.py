import pandas
import math
import airsim
import click


def destroy_stationery_vehicles(client):
    """
    Remove stationary vehicles from the environments
    List of stationary vehicles objects exist in vehicles.txt
    """
    with open("vehicles.txt") as f:
        vehicles = map(str.strip, f.readlines())
        for vehicle in vehicles:
            client.simDestroyObject(vehicle)


def adjust_recording_parameters(client, aerial_pitch, ground_fov):
    """
    Customize recording parameters.

    Recommended parameters by 2020's AirSim paper are:
    - aerial_pitch=50
    - ground_fov=120
    """
    client.simSetCameraFov("front_center", ground_fov, "GroundDrone")
    client.simSetCameraPose(
        "bottom_center",
        airsim.Pose(
            orientation_val=airsim.to_quaternion(math.radians(aerial_pitch), 0, 0)
        ),
        "AerialDrone",
    )


def initialize_drones(client, aerial_altitude, ground_altitude):
    """
    Allow API control and taking off.
    """
    # Allow API Control
    client.enableApiControl(True, "AerialDrone")
    client.enableApiControl(True, "GroundDrone")
    # Arm the vehicles (Not really sure what it means)
    client.armDisarm(True, "AerialDrone")
    client.armDisarm(True, "GroundDrone")

    # Taking off
    f1 = client.takeoffAsync(vehicle_name="AerialDrone")
    f2 = client.takeoffAsync(vehicle_name="GroundDrone")
    f1.join()
    f2.join()

    f1 = client.moveToZAsync(z=aerial_altitude, velocity=5, vehicle_name="AerialDrone")
    f2 = client.moveToZAsync(z=ground_altitude, velocity=5, vehicle_name="GroundDrone")
    f1.join()
    f2.join()

    # Hovering (Not really sure what that means)
    f1 = client.hoverAsync("AerialDrone")
    f2 = client.hoverAsync("GroundDrone")
    f1.join()
    f2.join()


def traverse_and_record_trajectory(client, aerial_altitude, ground_altitude):
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
    # Ground drone
    f2 = client.moveOnPathAsync(
        ground_path,
        velocity=10,
        drivetrain=airsim.DrivetrainType.ForwardOnly,
        yaw_mode=airsim.YawMode(False),
        vehicle_name="GroundDrone",
    )
    f1.join()
    f2.join()

    # Stop recording and reset
    client.stopRecording()
    client.reset()


@click.command()
@click.option(
    "--aerial_pitch",
    default=50,
    prompt="Aerial drone camera pitch",
    help="Aerial drone camera pitch",
)
@click.option(
    "--ground_fov",
    default=120,
    prompt="Ground drone camera FOV degrees",
    help="Ground drone camera FOV degrees",
)
@click.option(
    "--aerial_altitude",
    default=40,
    prompt="Aerial drone height",
    help="Aerial drone height",
)
@click.option(
    "--ground_altitude",
    default=1,
    prompt="Ground drone height",
    help="Ground drone height",
)
def main(aerial_pitch, ground_fov, aerial_altitude, ground_altitude):
    """
    A script used to collect ground and aerial views for a scene using drones in AirSim.
    """
    # Connect to the AirSim simulator
    client = airsim.MultirotorClient()
    client.confirmConnection()

    destroy_stationery_vehicles(client)
    adjust_recording_parameters(client, aerial_pitch, ground_fov)
    initialize_drones(client, -aerial_altitude, -ground_altitude)
    traverse_and_record_trajectory(client, -aerial_altitude, -ground_altitude)


if __name__ == "__main__":
    main()
