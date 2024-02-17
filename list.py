import sys
import json

def process_version(version):
    parts = version.split('-')
    mcversion = parts[0]
    if len(parts) == 2:
        forgeversion = f"{mcversion}-{parts[1]}"
    else:
        forgeversion = '-'.join(parts[:-1])
    return {
        "rawVersion": version,
        "mcversion": mcversion,
        "version": forgeversion
    }

def process_json(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    versions = data["versioning"]["versions"]["version"]
    processed_versions = [process_version(version) for version in versions]

    with open(output_file, 'w') as f:
        json.dump(processed_versions, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 list.py input.json output.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_json(input_file, output_file)