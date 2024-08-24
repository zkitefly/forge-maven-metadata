import json
import requests
from concurrent.futures import ThreadPoolExecutor

# 浏览器 User-Agent 示例
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# 读取 list.json 文件
with open('list.json', 'r') as f:
    data = json.load(f)

# 尝试读取 install.json 文件，如果不存在就创建一个空列表
try:
    with open('install.json', 'r') as f:
        install_data = json.load(f)
except FileNotFoundError:
    install_data = []

# 创建一个字典，方便检查某个 build 是否已经处理过
install_data_dict = {item['build']: item for item in install_data}

# 构造下载 URL 并检查是否返回 404
def check_url(build_info):
    build = build_info['build']

    # 如果 install.json 已经包含这个 build，跳过处理
    if build in install_data_dict:
        print(f"Build {build} already processed, skipping...")
        return None

    branch = build_info.get('branch')
    mcversion = build_info['mcversion']
    version = build_info['version']

    # 构造 URL
    url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mcversion}-{version}"
    if branch:
        url += f"-{branch}"
    url += f"/forge-{mcversion}-{version}"
    if branch:
        url += f"-{branch}"
    url += "-installer.jar"

    # 请求头部设置 User-Agent
    headers = {
        'User-Agent': USER_AGENT
    }

    # 检查 URL 是否返回 404
    response = requests.head(url, headers=headers)
    hasinstall = response.status_code != 404

    # 存储结果
    result = {
        'build': build,
        'version': version,
        'hasinstall': hasinstall
    }

    # 实时将结果保存到 install.json
    install_data.append(result)
    with open('install.json', 'w') as f:
        json.dump(install_data, f, indent=4)

    print(f"Processed build {build}, hasinstall: {hasinstall}")
    return result

# 使用多线程处理 URL 检查
with ThreadPoolExecutor() as executor:
    executor.map(check_url, data['number'].values())

# 更新 list.json 中的文件信息
for item in install_data:
    build = item['build']
    if not item['hasinstall']:
        if 'files' in data['number'][str(build)]:
            data['number'][str(build)]['files'] = [
                f for f in data['number'][str(build)]['files']
                if f[1] != 'installer' and f[1] != 'jar'
            ]

# 将更新后的 list.json 写回文件
with open('list.json', 'w') as f:
    json.dump(data, f)

with open('raw-list.json', 'w') as f:
    json.dump(data, f, indent=2)
