import sys
from xmljson import parker
from xml.etree.ElementTree import fromstring
import json

def xml_to_json(xml_file, json_file):
    with open(xml_file, 'r') as f:
        xml_data = f.read()

    # Parse XML data to ElementTree object
    root = fromstring(xml_data)

    # Convert ElementTree to JSON using xmljson library
    json_data = parker.data(root)

    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 xml_to_json.py input.xml output.json")
        sys.exit(1)

    input_xml = sys.argv[1]
    output_json = sys.argv[2]

    xml_to_json(input_xml, output_json)
