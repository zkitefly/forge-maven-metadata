import sys
import os
import json

def write_to_mcversion_file(mcversion, data):
    filename = f"list/{mcversion}.json"
    with open(filename, 'w') as f:
        json.dump(data, f)

def process_version(version):
    parts = version.split('-')
    mcversion = parts[0]
    forgeversion = parts[1]
    branch = parts[2] if len(parts) > 2 else None

    forge_parts = forgeversion.split('.')
    if len(forge_parts) == 4:  # e.g., 1.2.3.4
        count = int(forge_parts[-1])  # Use the last part as count
    elif len(forge_parts) == 3:  # e.g., 1.2.3
        count = int(forge_parts[0]) * 1000000 + int(forge_parts[1]) * 10000 + int(forge_parts[2])  # Create a large integer
    else:
        count = 0  # Default count if the structure doesn't match expected patterns

    return {
        "branch": branch,
        "build": count,
        "mcversion": mcversion,
        "modified": 0,
        "version": forgeversion,
        "files": [["jar","installer"]],
        # "rawversion": version
    }

def process_json(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    versions = data["versioning"]["versions"]["version"]
    processed_versions = [process_version(version) for version in versions]

    mcversion_data = {}
    numbered_data = {
        # "adfocus": "271228",
        "artifact": "forge",
        # "homepage": "https://files.minecraftforge.net/maven/net/minecraftforge/forge/",
        # "name": "Minecraft Forge",
        "webpath": "https://files.minecraftforge.net/maven/net/minecraftforge/forge/",
        # "branches": {},
        "mcversion": {},
        "number": {},
        # "promos": {}
    }
    
    for version_data in processed_versions:
        count = version_data["build"]  # Use the calculated build value as the count
        mcversion = version_data["mcversion"]
        
        if mcversion not in numbered_data["mcversion"]:
            numbered_data["mcversion"][mcversion] = []
        numbered_data["mcversion"][mcversion].append(count)

        numbered_data["number"][str(count)] = version_data

        mcversion = version_data["mcversion"]
        if mcversion not in mcversion_data:
            mcversion_data[mcversion] = []
        mcversion_data[mcversion].append(version_data)

        # branch = version_data["branch"] if version_data["branch"] else "null"
        # if branch not in numbered_data["branches"]:
        #     numbered_data["branches"][branch] = []
        # numbered_data["branches"][branch].append(version_data["build"])

    # for mcversion, version_list in mcversion_data.items():
    #     write_to_mcversion_file(mcversion, version_list)

    with open(output_file, 'w') as f:
        json.dump(numbered_data, f)

if __name__ == "__main__":
    process_json("forge-maven-metadata.json", "list.json")
    os.remove("forge-maven-metadata.json")
