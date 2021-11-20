import click


@click.command()
@click.option(
    "--ground_to_aerial_ratio",
    prompt="Number of ground images for each aerial image",
    default=5,
)
def main(ground_to_aerial_ratio):
    with open("airsim_rec.txt") as f:
        lines = f.readlines()
        images = [line.split()[-1] for line in lines[1:]]
        aerial_images = images[1::2][::ground_to_aerial_ratio]
        ground_images = images[::2]
        aerial_to_ground_mapping = {
            aerial_image: ground_images[
                ground_to_aerial_ratio * index : ground_to_aerial_ratio * (index + 1)
            ]
            for index, aerial_image in enumerate(aerial_images)
        }


if __name__ == "__main__":
    main()
