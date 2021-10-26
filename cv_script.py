import math
import airsim
import os
import tempfile
import time

# Connect to AirSim and confirm connection.
client = airsim.VehicleClient()
client.confirmConnection()

# Set the FOV degrees of the ground camera to 120°.
client.simSetCameraFov("front_center", 120)

# The pose object has two attributes
# 1) position (x_val, y_val, z_val)
# 2) orientation (w_val, x_val, y_val, z_val)
initial_pose = client.simGetVehiclePose()
initial_position = initial_pose.position
initial_orientation = initial_pose.orientation

# Put the ground vehicle at a height of 1m.
client.simSetVehiclePose(
    airsim.Pose(
        airsim.Vector3r(initial_position.x_val, initial_position.y_val, -1),
        initial_orientation,
    ),
    True,
)


# Make a temp directory and store the images in it for now.
tmp_dir = os.path.join(tempfile.gettempdir(), "airsim_cv_mode")
print("Saving images to %s" % tmp_dir)
try:
    os.makedirs(tmp_dir)
except OSError:
    if not os.path.isdir(tmp_dir):
        raise

aerial_counter = 0
ground_counter = 0


def get_ground_image():
    """
    Captures a ground image using the images API.
    """
    ground_images_requests = [
        airsim.ImageRequest("front_center", airsim.ImageType.Scene)
    ]
    ground_images = client.simGetImages(ground_images_requests, external=False)
    save_images(ground_images, "ground")


def get_aerial_image():
    """
    Captures an aerial image using the images API.
    """
    # Quick note: the pitch and the roll angles are fixed, will only need to change the yaw angle.
    vehicle_pose = client.simGetVehiclePose()
    vehicle_position = vehicle_pose.position
    vehicle_orientation = vehicle_pose.orientation
    new_yaw_angle = airsim.utils.to_eularian_angles(vehicle_orientation)[2]

    client.simSetCameraPose(
        "AerialCamera",
        airsim.Pose(
            airsim.Vector3r(
                vehicle_position.x_val, vehicle_position.y_val, -40
            ),  # Height of 10m base height + 30m
            airsim.to_quaternion(
                math.radians(-40), 0, new_yaw_angle
            ),  # -90 (bottom down) + 50 angle pitch
        ),
        external=True,
    )
    aerial_images_requests = [
        airsim.ImageRequest("AerialCamera", airsim.ImageType.Scene)
    ]
    aerial_images = client.simGetImages(aerial_images_requests, external=True)
    save_images(aerial_images, "aerial")


def save_images(responses, prefix):
    """
    Writes images to disk.
    """
    global aerial_counter
    global ground_counter

    for response in responses:
        if prefix == "aerial":
            filename = os.path.join(tmp_dir, prefix + "_" + str(aerial_counter))
            aerial_counter += 1
        else:
            filename = os.path.join(tmp_dir, prefix + "_" + str(ground_counter))
            ground_counter += 1

        airsim.write_file(
            os.path.normpath(filename + ".png"), response.image_data_uint8
        )


try:
    while True:
        get_ground_image()
        get_aerial_image()
        time.sleep(1)

except KeyboardInterrupt:
    print("Program has terminated.")
