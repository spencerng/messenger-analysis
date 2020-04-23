import json
import os
from shutil import copyfile


def main():
    try:
        os.mkdir("json")
    except FileExistsError:
        pass

    for root, dirs, files in os.walk("."):
        for name in files:
            if not name.endswith(".json"):
                continue
            src_file_path = os.path.join(root, name)
            convo_name = root.split("\\")[-1]

            des_file_path = ".\\json\\" + convo_name + name.split("_")[1]

            copyfile(src_file_path, des_file_path)


if __name__ == "__main__":
    main()
