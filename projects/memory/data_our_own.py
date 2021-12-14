import argparse
import csv
import logging
import os
from collections import Counter
from glob import glob

from run_prompts import read_json, write_json
from tqdm import tqdm

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main(data_path: str, save_path: str) -> None:
    """Create semantic knowledge using our own data.

    Args
    ----
    path: directory path where our csv data are saved

    """
    data = {}
    for path in tqdm(glob(f"./{data_path}/*.csv")):
        rows = []
        with open(path, "r") as file:
            csvreader = csv.reader(file)
            header = next(csvreader)
            for row in csvreader:
                head = row[0]
                head = "_".join(head.split())
                if head not in data:
                    data[head] = []
                else:
                    for location in row[1].split(","):
                        data[head].append(location.strip())

    data = {key: dict(Counter(val)) for key, val in data.items()}
    data = {
        key: {
            "AtLocation": sorted(
                [{"tail": k, "weight": v} for k, v in val.items()],
                key=lambda x: x["weight"],
                reverse=True,
            )
        }
        for key, val in data.items()
    }

    write_json(data, save_path)
    logging.info(f"{data} saved at {save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create semantic knowledge using our own data."
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="data/ours",
        help="directory path where our csv data are saved.",
    )

    parser.add_argument(
        "--save_path",
        type=str,
        default="data/ours/raw/semantic-knowledge-our-own.json",
        help="file name to save our data at.",
    )
    args = vars(parser.parse_args())

    logging.info(f"args: {args}")

    main(**args)
