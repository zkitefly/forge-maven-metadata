import json
import os
import requests
import zipfile
from datetime import datetime
from dateutil import parser as date_parser
from concurrent.futures import ThreadPoolExecutor, as_completed

# 读取现有的 time.json 文件，如果存在的话
if os.path.exists('time.json'):
    with open('time.json', 'r') as f:
        saved_times = json.load(f)
else:
    saved_times = []

# 初始化存储时间信息的列表
time_entries = saved_times.copy()

# 读取 list.json 文件
with open('list.json', 'r') as f:
    data = json.load(f)

# 设置 User-Agent 模拟浏览器请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
}

# 定义处理单个条目的函数
def process_entry(key, entry):
    branch = entry.get('branch')
    mcversion = entry.get('mcversion')
    version = entry.get('version')
    build = entry.get('build')
    files = entry.get('files', [])

    # 检查 files 中是否包含 ["jar", "installer"]
    if not any(file_pair == ["jar", "installer"] for file_pair in files):
        print(f"Build {build} with version {version} does not have a 'jar' and 'installer' combination. Skipping...")
        return

    # 检查是否已存在该版本的时间信息
    if any(t['build'] == build and t['version'] == version for t in saved_times):
        print(f"Build {build} with version {version} already exists in time.json. Skipping...")
        return

    # 组合下载链接
    if branch:
        url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mcversion}-{version}-{branch}/forge-{mcversion}-{version}-{branch}-installer.jar"
    else:
        url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mcversion}-{version}/forge-{mcversion}-{version}-installer.jar"

    # 下载文件
    file_name = f'installer_{build}.jar'
    print(f"Downloading {file_name} from {url}...")

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download {file_name}. HTTP Status Code: {response.status_code}")
        return

    # 解压缩文件，查找 version.json 或 install_profile.json
    time = None
    with zipfile.ZipFile(file_name, 'r') as jar_file:
        if 'version.json' in jar_file.namelist():
            with jar_file.open('version.json') as f:
                version_data = json.load(f)
                time_str = version_data.get('time', None)
                if time_str:
                    try:
                        time = int(date_parser.parse(time_str).timestamp())
                    except ValueError:
                        print(f"Failed to parse time string '{time_str}' in version.json")
        if not time and 'install_profile.json' in jar_file.namelist():
            with jar_file.open('install_profile.json') as f:
                install_data = json.load(f)
                version_info = install_data.get('versionInfo', {})
                time_str = version_info.get('time', None)
                if time_str:
                    try:
                        time = int(date_parser.parse(time_str).timestamp())
                    except ValueError:
                        print(f"Failed to parse time string '{time_str}' in install_profile.json")

    # 保存当前条目的时间信息
    if time:
        time_entry = {
            'time': time,
            'build': build,
            'version': version
        }
        time_entries.append(time_entry)

        # 立即将时间信息保存到 time.json
        with open('time.json', 'w') as f:
            json.dump(time_entries, f, indent=4)

    # 删除下载的文件
    os.remove(file_name)
    print(f"{file_name} has been deleted.")

# 使用多线程处理所有条目
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(process_entry, key, entry) for key, entry in data['number'].items()]

    for future in as_completed(futures):
        future.result()

# 所有数据收集完毕后，读取 time.json 并更新 list.json
with open('time.json', 'r') as f:
    time_data = json.load(f)

# 遍历 time.json 中的条目并转换时间戳
for entry in time_data:
    build = entry['build']
    version = entry['version']
    iso_time = entry['time']

    # 将 ISO 8601 格式的时间字符串转换为 Unix 时间戳
    try:
        unix_timestamp = int(date_parser.parse(iso_time).timestamp())
    except ValueError:
        print(f"Failed to parse time string '{iso_time}' in time.json")
        continue

    # 在 list.json 中找到对应条目并更新 modified 属性
    for key, list_entry in data['number'].items():
        if list_entry['build'] == build and list_entry['version'] == version:
            list_entry['modified'] = unix_timestamp
            break

# 保存更新后的 list.json 文件
with open('list.json', 'w') as f:
    json.dump(data, f)

with open('raw-list.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Modified times have been updated and saved to list_updated.json.")
