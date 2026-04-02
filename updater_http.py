import os
import sys
import ssl
import shutil
import zipfile
import tempfile
import urllib.request

if hasattr(ssl, "_create_unverified_context"):
    ssl._create_default_https_context = ssl._create_unverified_context

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(TOOL_DIR, "VERSION")

# 1) 远程 VERSION 纯文本地址（GitHub Raw）
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/keang1/skills/refs/heads/main/VERSION"
# 2) 代码包下载地址（GitHub codeload zip）
UPDATE_ZIP_URL = "https://codeload.github.com/keang1/skills/zip/refs/heads/main"


def get_local_version() -> str:
    """读取本地版本号。"""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "0.0.0"


def check_and_update() -> None:
    print("正在检查更新...", end="\r")
    local_version = get_local_version()

    try:
        req = urllib.request.Request(REMOTE_VERSION_URL)
        with urllib.request.urlopen(req, timeout=3) as response:
            remote_version = response.read().decode("utf-8").strip()

        print(" " * 30, end="\r")

        if remote_version and remote_version != local_version:
            print(f"发现新版本 {remote_version}（当前: {local_version}）")
            ans = input("是否立即自动更新并继续运行？[Y/n]: ").strip().lower()

            if ans in ("", "y", "yes"):
                perform_update(remote_version)
            else:
                print("跳过更新，继续执行当前版本。")

    except Exception as e:
        print(f"更新检查失败: {e}")
        print(" " * 30, end="\r")


def _copy_project_content(src_root: str, dst_root: str) -> None:
    """把 src_root 下的内容覆盖到 dst_root。"""
    for name in os.listdir(src_root):
        src_path = os.path.join(src_root, name)
        dst_path = os.path.join(dst_root, name)

        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


def perform_update(remote_version: str) -> None:
    """下载并应用更新，最后写回本地 VERSION。"""
    print("正在下载最新版本...")
    zip_path = os.path.join(TOOL_DIR, "update_temp.zip")
    extract_dir = tempfile.mkdtemp(prefix="update_extract_", dir=TOOL_DIR)
    should_restart = False

    try:
        urllib.request.urlretrieve(UPDATE_ZIP_URL, zip_path)

        print("正在应用更新...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        entries = os.listdir(extract_dir)
        if not entries:
            raise RuntimeError("更新包为空，无法应用更新")

        # codeload 压缩包通常为 <repo>-<branch> 顶层目录
        project_root = os.path.join(extract_dir, entries[0])
        if not os.path.isdir(project_root):
            raise RuntimeError("更新包结构异常，未找到项目根目录")

        _copy_project_content(project_root, TOOL_DIR)

        # 明确写回版本号，防止下次仍提示更新
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            f.write(remote_version + "\n")

        should_restart = True

    except Exception as e:
        print(f"更新失败: {e}")

    finally:
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except OSError:
                pass
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)

    if should_restart:
        print("更新成功，正在重启...")
        print("-" * 50)
        os.execv(sys.executable, [sys.executable] + sys.argv)
