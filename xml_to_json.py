import os
import requests
import sys
from xmljson import parker
from xml.etree.ElementTree import fromstring
import json

# 请求头部设置 User-Agent
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def download_xml(url, local_file):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(local_file, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
        sys.exit(1)

def xml_to_json(xml_file, json_file):
    with open(xml_file, 'r') as f:
        xml_data = f.read()

    root = fromstring(xml_data)

    json_data = parker.data(root)

    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=4)

if __name__ == "__main__":
    xml_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml"
    xml_file = "forge-maven-metadata.xml"
    json_file = "forge-maven-metadata.json"

    download_xml(xml_url, xml_file)

    xml_to_json(xml_file, json_file)

    os.remove(xml_file)

    print(f"Conversion complete. JSON data saved to {json_file}")
