import sys
import os
import json

def write_to_mcversion_file(mcversion, data):
    filename = f"list/{mcversion}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def process_version(version):
    parts = version.split('-')
    mcversion = parts[0]
    forgeversion = parts[1]
    return {
        "rawversion": version,
        "mcversion": mcversion,
        "version": forgeversion
    }

def process_json(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    versions = data["versioning"]["versions"]["version"]
    processed_versions = [process_version(version) for version in versions]

    mcversion_data = {}
    for version_data in processed_versions:
        mcversion = version_data["mcversion"]
        if mcversion not in mcversion_data:
            mcversion_data[mcversion] = []
        mcversion_data[mcversion].append(version_data)

    for mcversion, version_list in mcversion_data.items():
        write_to_mcversion_file(mcversion, version_list)

    with open(output_file, 'w') as f:
        json.dump(processed_versions, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 list.py input.json output.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists("list"):
        os.makedirs("list")

    process_json(input_file, output_file)
