import os
import sys
import urllib.request
import urllib.error
import zipfile
import shutil
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# 工具根目录
TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(TOOL_DIR, 'VERSION')

# 配置：替换为你自己仓库的真实链接
# 1. 远程 VERSION 文件的纯文本链接 (Raw URL)
REMOTE_VERSION_URL = "https://172.28.17.127/new/95claw_group/skill/test_skills/-/raw/main/VERSION"
# 2. 工具最新代码包的下载链接 (比如 GitLab/GitHub 提供的目录下载或 release zip)
UPDATE_ZIP_URL = "https://172.28.17.127/new/95claw_group/skill/test_skills/-/archive/main/test_skills-main.zip"

def get_local_version():
    """获取本地版本号"""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            return f.read().strip()
    return "0.0.0"

def check_and_update():
    print("🔍 正在检查更新...", end="\r")
    local_version = get_local_version()
    
    try:
        # 设置3秒超时，避免没网时卡住工具
        req = urllib.request.Request(REMOTE_VERSION_URL)
        with urllib.request.urlopen(req, timeout=3) as response:
            remote_version = response.read().decode('utf-8').strip()
            
        print(" " * 30, end="\r") # 清除检查提示
        
        # 简单比对版本号字符串
        if remote_version != local_version and remote_version != "":
            print(f"\033[33m🌟 发现新版本: {remote_version} (当前: {local_version})\033[0m")
            ans = input("是否立即自动更新并继续运行？[Y/n]: ").strip().lower()
            
            if ans in ('', 'y', 'yes'):
                perform_update()
            else:
                print("跳过更新，继续执行当前旧版本...")
                
    except Exception as e:
        print(f"\033[31m⚠️  更新检查失败: {e}\033[0m")
        print(" " * 30, end="\r")

def perform_update():
    """下载 ZIP 并覆盖当前目录"""
    print("⬇️  正在下载最新版本...")
    zip_path = os.path.join(TOOL_DIR, "update_temp.zip")
    
    try:
        # 1. 下载更新包
        urllib.request.urlretrieve(UPDATE_ZIP_URL, zip_path)
        
        # 2. 解压并覆盖文件
        print("📦 正在应用更新...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 注意：实际使用时，如果 ZIP 里包了一层顶层文件夹，你需要根据情况提取内层文件
            zip_ref.extractall(TOOL_DIR)
            
        # 3. 清理临时压缩包
        os.remove(zip_path)
        
        print("\033[32m✅ 更新成功！正在重新启动...\033[0m")
        print("-" * 50)
        
        # 4. 热重启 Python 脚本
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    except Exception as e:
        print(f"\033[31m❌ 更新失败: {e}\033[0m")
        
        