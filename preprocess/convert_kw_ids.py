import argparse
import glob
import json
import os.path
import re


def load(path: str):
    with open(path, "r") as file:
        json_file = json.load(file)
    return json_file

def save(json_obj, path):
    with open(path, "w") as file:
        json.dump(json_obj, file)

def format_as_id(original_string: str):
    return re.findall("([a-zA-Z0-9]*)(\.jpg){0,1}$", os.path.basename(original_string))[0][0]

def main():
    parser = argparse.ArgumentParser(description='Converting file from using absolute path to just identifier')
    parser.add_argument('--path', type=str, required=True)

    opt = parser.parse_args()

    path = opt.path

    assert os.path.exists(path)



    if os.path.isfile(path):
        files = [path]
    else:
        files = glob.glob(os.path.join(path, "*.json"))

    data_json_files = {}
    for path in files:
        data_json_files[path] = load(path)

    print(len(data_json_files))

    for path, data_json_file in data_json_files.items():
        modified = False

        new_dict = {}
        for key, value in data_json_file.items():
            id_key = format_as_id(key)

            if id_key != key:
                modified = True

            new_dict[id_key] = data_json_file[key]

        print(f"{path}: Modified {modified}")

        if modified:
            save(new_dict, path)


if __name__ == "__main__":
    main()

