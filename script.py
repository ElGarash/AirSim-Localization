import pandas
import math
import airsim
import click


class TrajectoryRecorder:
    def __init__(self, aerial_pitch, ground_fov, aerial_altitude, ground_altitude):
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.aerial_pitch = aerial_pitch
        self.ground_fov = ground_fov
        self.aerial_altitude = -aerial_altitude
        self.ground_altitude = -ground_altitude

    def destroy_stationery_vehicles(self):
        """
        Remove stationary vehicles from the environments
        List of stationary vehicles objects exist in vehicles.txt
        """
        with open("vehicles.txt") as f:
            vehicles = map(str.strip, f.readlines())
            for vehicle in vehicles:
                self.client.simDestroyObject(vehicle)

    def adjust_recording_parameters(self):
        """
        Customize recording parameters.

        Recommended parameters by 2020's AirSim paper are:
        - aerial_pitch=50
        - ground_fov=120
        """
        self.client.simSetCameraFov("front_center", self.ground_fov, "GroundDrone")
        self.client.simSetCameraPose(
            "bottom_center",
            airsim.Pose(
                orientation_val=airsim.to_quaternion(
                    math.radians(self.aerial_pitch), 0, 0
                )
            ),
            "AerialDrone",
        )

    def initialize_drones(self):
        """
        Allow API control and taking off.
        """
        # Allow API Control
        self.client.enableApiControl(True, "AerialDrone")
        self.client.enableApiControl(True, "GroundDrone")
        # Arm the vehicles (Not really sure what it means)
        self.client.armDisarm(True, "AerialDrone")
        self.client.armDisarm(True, "GroundDrone")

        # Taking off
        f1 = self.client.takeoffAsync(vehicle_name="AerialDrone")
        f2 = self.client.takeoffAsync(vehicle_name="GroundDrone")
        f1.join()
        f2.join()

        f1 = self.client.moveToZAsync(
            z=self.aerial_altitude, velocity=5, vehicle_name="AerialDrone"
        )
        f2 = self.client.moveToZAsync(
            z=self.ground_altitude, velocity=5, vehicle_name="GroundDrone"
        )
        f1.join()
        f2.join()

        # Hovering (Not really sure what that means)
        f1 = self.client.hoverAsync("AerialDrone")
        f2 = self.client.hoverAsync("GroundDrone")
        f1.join()
        f2.join()

    def traverse_and_record_trajectory(self):
        # Read the trajectory trajectory_data into a list
        trajectory_data = pandas.read_csv("trajectory.csv").values.tolist()

        # Append the z coordinate to the xs and ys and convert the paths into airsim vectors
        aerial_path = [
            airsim.Vector3r(*position, self.aerial_altitude)
            for position in trajectory_data
        ]
        ground_path = [
            airsim.Vector3r(*position, self.ground_altitude)
            for position in trajectory_data
        ]

        # Record and move on path
        self.client.startRecording()

        # Aerial drone
        f1 = self.client.moveOnPathAsync(
            aerial_path,
            velocity=10,
            drivetrain=airsim.DrivetrainType.ForwardOnly,
            yaw_mode=airsim.YawMode(False),
            vehicle_name="AerialDrone",
        )
        # Ground drone
        f2 = self.client.moveOnPathAsync(
            ground_path,
            velocity=10,
            drivetrain=airsim.DrivetrainType.ForwardOnly,
            yaw_mode=airsim.YawMode(False),
            vehicle_name="GroundDrone",
        )
        f1.join()
        f2.join()

        # Stop recording and reset
        self.client.stopRecording()
        self.client.reset()


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

    trajectory_recorder = TrajectoryRecorder(
        aerial_pitch, ground_fov, aerial_altitude, ground_altitude
    )

    trajectory_recorder.destroy_stationery_vehicles()
    trajectory_recorder.adjust_recording_parameters()
    trajectory_recorder.initialize_drones()
    trajectory_recorder.traverse_and_record_trajectory()


if __name__ == "__main__":
    main()
