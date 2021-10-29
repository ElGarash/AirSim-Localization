import math
import airsim
import os
import tempfile
import time


class TrajectoryRecorder:
    aerial_counter = 0
    ground_counter = 0
    current_position = airsim.Vector3r()
    last_position = airsim.Vector3r()
    tmp_dir = os.path.join(tempfile.gettempdir(), "airsim_cv_mode")

    def __init__(self):
        self.client = airsim.VehicleClient()

        # Connect to AirSim and confirm connection.
        self.client.confirmConnection()
        self.create_destination_directory()

    def adjust_ground_parameters(self, fov_degrees=120):
        # Set the FOV degrees of the ground camera to 120°.
        self.client.simSetCameraFov("front_center", fov_degrees)

        initial_pose = self.client.simGetVehiclePose()
        initial_position = initial_pose.position
        initial_orientation = initial_pose.orientation

        # Put the ground vehicle at a height of 1m.
        self.client.simSetVehiclePose(
            airsim.Pose(
                airsim.Vector3r(initial_position.x_val, initial_position.y_val, -1),
                initial_orientation,
            ),
            True,
        )

    def create_destination_directory(self):
        # Make a temp directory and store the images in it for now.
        print("Saving images to %s" % self.tmp_dir)
        try:
            os.makedirs(self.tmp_dir)
        except OSError:
            if not os.path.isdir(self.tmp_dir):
                raise

    def get_ground_image(self):
        """
        Captures a ground image using the images API.
        """
        ground_images_requests = [
            airsim.ImageRequest("front_center", airsim.ImageType.Scene)
        ]
        ground_images = self.client.simGetImages(ground_images_requests, external=False)
        self.save_images(ground_images, "ground")

    def save_images(self, responses, prefix):
        """
        Writes images to disk.
        """
        global aerial_counter
        global ground_counter

        for response in responses:
            if prefix == "aerial":
                filename = os.path.join(
                    self.tmp_dir, prefix + "_" + str(self.aerial_counter)
                )
                self.aerial_counter += 1
            else:
                filename = os.path.join(
                    self.tmp_dir, prefix + "_" + str(self.ground_counter)
                )
                self.ground_counter += 1

            airsim.write_file(
                os.path.normpath(filename + ".png"), response.image_data_uint8
            )

    def get_aerial_image(self, altitude=40, pitch_angle=50):
        """
        Captures an aerial image using the images API.
        """
        # Quick note: the pitch and the roll angles are fixed, will only need to change the yaw angle.
        vehicle_pose = self.client.simGetVehiclePose()
        vehicle_position = vehicle_pose.position
        vehicle_orientation = vehicle_pose.orientation
        new_yaw_angle = airsim.utils.to_eularian_angles(vehicle_orientation)[2]

        self.client.simSetCameraPose(
            "AerialCamera",
            airsim.Pose(
                airsim.Vector3r(
                    vehicle_position.x_val, vehicle_position.y_val, -altitude
                ),
                airsim.to_quaternion(
                    math.radians(-90 + pitch_angle), 0, new_yaw_angle
                ),  # -90 (bottom down) + 50 angle pitch
            ),
            external=True,
        )
        aerial_images_requests = [
            airsim.ImageRequest("AerialCamera", airsim.ImageType.Scene)
        ]
        aerial_images = self.client.simGetImages(aerial_images_requests, external=True)
        self.save_images(aerial_images, "aerial")

    def capture_trajectory(self):
        try:
            while True:
                self.current_position = self.client.simGetVehiclePose().position
                # Capture images only if current position doesn't equal last position
                if not self.current_eq_last():
                    self.get_ground_image()
                    self.get_aerial_image()
                    self.last_position = self.client.simGetVehiclePose().position
                    time.sleep(1)

        except KeyboardInterrupt:
            print("The program has been terminated.")

    def current_eq_last(self):
        return (
            (self.current_position.x_val == self.last_position.x_val)
            and (self.current_position.y_val == self.last_position.y_val)
            and (self.current_position.z_val == self.last_position.z_val)
        )


if __name__ == "__main__":
    airsim_recorder = TrajectoryRecorder()
    airsim_recorder.capture_trajectory()
