import json
import os
from shutil import copyfile

DATA_DIRECTORY = "."
IS_WINDOWS = True


def main():
    os.makedirs(f"{DATA_DIRECTORY}/json", exist_ok=True)
    
    for root, dirs, files in os.walk(f"{DATA_DIRECTORY}/messages/inbox"):
        for name in files:
            if not name.endswith(".json"):
                continue
            src_file_path = os.path.join(root, name)
            convo_name = root.split("\\" if IS_WINDOWS else "/")[-1]

            des_file_path = f"{DATA_DIRECTORY}/json/" + convo_name + name.split("_")[1]

            copyfile(src_file_path, des_file_path)


if __name__ == "__main__":
    main()
