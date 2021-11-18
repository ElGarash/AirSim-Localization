import csv
import airsim
import time

FILE_NAME = "trajectory.csv"


def write_csv_header(filename=FILE_NAME):
    with open(filename, mode="a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["position_x", "position_y"])
        writer.writeheader()


def write_csv_row(client: airsim.CarClient, filename=FILE_NAME, time_delay=0.8):
    """
    Collect X, Y coordinates every 1 second while moving in the environment.
    """
    car_kinematics = client.getCarState().kinematics_estimated

    position = {
        "position_x": car_kinematics.position.x_val,
        "position_y": car_kinematics.position.y_val,
    }

    # Append position and orientation data to csv file each time the file is run
    with open(filename, mode="a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=position.keys())
        writer.writerow(position)

    time.sleep(time_delay)


if __name__ == "__main__":
    client = airsim.CarClient()
    client.confirmConnection()

    write_csv_header()

    while True:
        write_csv_row(client)
