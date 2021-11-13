import csv
import airsim
import time

if __name__ == "__main__":
    # Connect to AirSim
    client = airsim.CarClient()
    client.confirmConnection()

    # Collect X, Y coordinates every 1 second while moving in the environment.
    while True:
        car_kinematics = client.getCarState().kinematics_estimated

        position = {
            "position_x": car_kinematics.position.x_val,
            "position_y": car_kinematics.position.y_val,
        }

        # Append position and orientation data to csv file each time the file is run
        with open("trajectory.csv", mode="a", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=position.keys())

            writer.writerow(position)

        time.sleep(1)
