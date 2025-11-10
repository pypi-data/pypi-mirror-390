
#!/usr/bin/env python3
"""
Fast Pip - 终极性能Python包安装工具
为所有文件提供统一的高速优化，保持5个镜像
"""

import os
import sys
import time
import subprocess
import requests
import tempfile
import re
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import threading

class ProgressBar:
    """进度条可视化类"""
    
    def __init__(self, description="Progress", total=100, length=30):
        self.description = description
        self.total = total
        self.length = length
        self.current = 0
        self.start_time = time.time()
        
    def update(self, value, status=""):
        """更新进度条"""
        self.current = value
        percent = min(100, max(0, int(100 * value / self.total)))
        filled_length = int(self.length * value // self.total)
        bar = '█' * filled_length + '░' * (self.length - filled_length)
        
        elapsed = time.time() - self.start_time
        if elapsed > 0 and value > 0:
            speed = value / elapsed
            eta = (self.total - value) / speed if speed > 0 else 0
            time_info = f" {eta:.1f}s"
        else:
            time_info = ""
            
        sys.stdout.write(f'\r{self.description}: |{bar}| {percent}% {status}')
        sys.stdout.flush()
        
    def finish(self, message="完成"):
        """完成进度条"""
        self.update(self.total, message)
        sys.stdout.write('\n')
        sys.stdout.flush()

class UltimateFastPip:
    def __init__(self):
        # 保持5个镜像源
        self.mirrors = [
            "https://pypi.tuna.tsinghua.edu.cn/simple/",
            "https://mirrors.aliyun.com/pypi/simple/", 
            "https://pypi.douban.com/simple/",
            "https://pypi.mirrors.ustc.edu.cn/simple/",
            "https://mirrors.cloud.tencent.com/pypi/simple/",
        ]
        
        # 获取系统信息用于平台匹配
        self.system_info = self.get_system_info()
        
        # 极致优化会话 - 为所有文件优化
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UltimatePip/3.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # 超高性能连接池 - 为所有文件优化
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=50,
            pool_maxsize=50,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.download_dir = tempfile.mkdtemp(prefix="ultra_pip_")
        
        # 预编译正则
        self.link_pattern = re.compile(r'href="(\.\./\.\./[^"]*\.(?:whl|tar\.gz))')
        
    def get_system_info(self):
        """获取系统平台信息用于兼容性检测"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        python_version = platform.python_version()
        
        # 检测架构
        if system == "windows":
            platform_tag = "win_amd64" if machine in ["amd64", "x86_64", "x64"] else "win32"
        elif system == "linux":
            platform_tag = "linux_x86_64" if machine in ["x86_64", "amd64"] else f"linux_{machine}"
        elif system == "darwin":
            # macOS
            import platform as pl
            mac_version = pl.mac_ver()[0]
            if mac_version:
                major_version = mac_version.split('.')[0]
                if int(major_version) >= 11:
                    platform_tag = "macosx_11_0_x86_64" if machine == "x86_64" else f"macosx_11_0_{machine}"
                else:
                    platform_tag = "macosx_10_9_x86_64" if machine == "x86_64" else f"macosx_10_9_{machine}"
            else:
                platform_tag = "macosx_10_9_x86_64"
        else:
            platform_tag = f"{system}_{machine}"
            
        # Python标签
        python_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
        
        return {
            "system": system,
            "machine": machine,
            "platform_tag": platform_tag,
            "python_tag": python_tag,
            "python_version": python_version,
            "abi_tag": f"cp{sys.version_info.major}{sys.version_info.minor}"
        }
    
    def is_compatible_wheel(self, filename, package_name):
        """检查wheel文件是否与当前系统兼容"""
        if not filename.endswith('.whl'):
            return True  # 源码包总是兼容
            
        # 解析wheel文件名格式: {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl
        name_part = filename[:-4]  # 去掉.whl
        parts = name_part.split('-')
        
        if len(parts) < 5:
            return False
            
        # 检查包名匹配
        clean_package_name = package_name.lower().replace('_', '-')
        clean_filename_part = parts[0].lower().replace('_', '-')
        if not clean_filename_part.startswith(clean_package_name):
            return False
            
        # 获取平台标签（最后一部分）
        platform_tag = parts[-1]
        python_tag = parts[-3]
        abi_tag = parts[-2]
        
        # 检查Python版本兼容性
        current_python = self.system_info['python_tag']
        
        # 宽松的Python版本检查：允许较新Python安装旧包（有一定限制）
        if python_tag.startswith('cp'):
            # 提取Python主版本号
            wheel_py_version = int(python_tag[2:])
            current_py_version = int(current_python[2:])
            
            # 如果wheel的Python版本比当前Python版本旧很多，可能不兼容
            if current_py_version - wheel_py_version > 2:
                return False
        elif not (python_tag.startswith('py') or python_tag.startswith('cp')):
            return False
            
        # 特殊处理：any平台总是兼容
        if platform_tag == 'any':
            return True
            
        # 检查平台兼容性
        system_info = self.system_info
        
        if system_info['system'] == 'windows':
            return ('win' in platform_tag and system_info['machine'] in platform_tag)
        elif system_info['system'] == 'linux':
            return ('linux' in platform_tag and system_info['machine'] in platform_tag)
        elif system_info['system'] == 'darwin':
            return 'macosx' in platform_tag
        else:
            return False
    
    def ultra_search(self, package_name):
        """极致并行搜索 - 使用5个镜像"""
        print(f"🔍 超速搜索: {package_name}")
        print(f"📋 系统平台: {self.system_info['platform_tag']}")
        print(f"🐍 Python: {self.system_info['python_tag']}")
        
        # 进度条初始化
        progress = ProgressBar("搜索镜像", total=len(self.mirrors))
        
        start_time = time.perf_counter()
        results = []
        success_mirrors = set()
        
        def search_mirror(mirror, index):
            try:
                url = f"{mirror}{package_name}/"
                response = self.session.get(url, timeout=3)
                if response.status_code == 200:
                    links = self.lightning_parse(response.text, package_name, mirror)
                    progress.update(index + 1, f"找到 {len(links)} 文件")
                    return mirror, links
                else:
                    progress.update(index + 1, f"HTTP {response.status_code}")
            except Exception as e:
                progress.update(index + 1, f"失败: {str(e)[:20]}")
            return mirror, []
        
        # 极致并行搜索 - 使用5个镜像
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_mirror = {}
            for i, mirror in enumerate(self.mirrors):
                future = executor.submit(search_mirror, mirror, i)
                future_to_mirror[future] = mirror
            
            for future in as_completed(future_to_mirror):
                mirror, links = future.result()
                if links:
                    print(f"\n📦 从 {mirror.split('/')[2]} 找到 {len(links)} 个文件")
                    
                    # 优先选择兼容版本的文件
                    compatible_links = []
                    for link in links:
                        filename = os.path.basename(link)
                        if self.is_compatible_wheel(filename, package_name):
                            compatible_links.append(link)
                        elif filename.endswith('.tar.gz'):
                            # 源码包总是兼容
                            compatible_links.append(link)
                    
                    if compatible_links:
                        sorted_links = self.sort_by_version(compatible_links)
                        results.extend(sorted_links)
                        success_mirrors.add(mirror)
                        print(f"✅ {mirror.split('/')[2]} - {len(compatible_links)} 兼容文件")
                    else:
                        print(f"❌ {mirror.split('/')[2]} - 无兼容文件")
                    
                    # 只要有三个镜像成功就提前返回
                    if len(success_mirrors) >= 3:
                        for f in future_to_mirror:
                            if not f.done():
                                f.cancel()
                        break
        
        progress.finish("搜索完成")
        search_time = time.perf_counter() - start_time
        
        if results:
            print(f"🎯 找到 {len(results)} 个候选文件 ({search_time:.3f}s)")
        else:
            print(f"❌ 未找到兼容文件 ({search_time:.3f}s)")
            
        return results
    
    def sort_by_version(self, urls):
        """按版本号排序，优先选择较新版本"""
        def extract_version(url):
            filename = os.path.basename(url)
            version_pattern = r'-(\d+\.\d+(?:\.\d+)*)'
            match = re.search(version_pattern, filename)
            if match:
                version_parts = match.group(1).split('.')
                return tuple(int(part) for part in version_parts)
            return (0, 0, 0)
        
        # 优先选择.whl文件，然后按版本号降序
        wheel_files = [url for url in urls if url.endswith('.whl')]
        source_files = [url for url in urls if url.endswith('.tar.gz')]
        
        # 按版本号排序（从高到低）
        wheel_files.sort(key=extract_version, reverse=True)
        source_files.sort(key=extract_version, reverse=True)
        
        return wheel_files + source_files
    
    def lightning_parse(self, html, package_name, mirror):
        """闪电解析 - 优化性能"""
        links = []
        seen = set()
        
        raw_links = self.link_pattern.findall(html)
        
        parsed = urlparse(mirror)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        for link in raw_links[:50]:  # 处理前50个链接
            if len(links) >= 20:  # 最多20个候选
                break
                
            clean_link = link.split('#')[0]
            if clean_link in seen:
                continue
            seen.add(clean_link)
            
            if clean_link.startswith('../../'):
                relative_path = clean_link[6:]
                if not relative_path.startswith('/'):
                    relative_path = '/' + relative_path
                full_url = base_url + relative_path
                
                # 更宽松的包名匹配
                filename = os.path.basename(full_url).lower()
                package_name_lower = package_name.lower()
                if (package_name_lower in filename or 
                    package_name_lower.replace('-', '_') in filename):
                    links.append(full_url)
        
        return links
    
    def hyper_download(self, urls):
        """超高速下载 - 为所有文件优化"""
        if not urls:
            return None
            
        print(f"⚡ 极速下载: {len(urls)}个候选")
        
        # 显示前几个候选
        for i, url in enumerate(urls[:3]):
            filename = os.path.basename(url)
            print(f"  {i+1}. {filename}")
        
        # 下载进度条
        download_progress = ProgressBar("下载文件", total=min(6, len(urls)))
        start_time = time.perf_counter()
        
        def download_single(url, index):
            try:
                filename = url.split('/')[-1].split('?')[0]
                filepath = os.path.join(self.download_dir, filename)
                
                download_progress.update(index + 1, f"{filename[:20]}...")
                
                # 为所有文件优化下载参数
                response = self.session.get(url, stream=True, timeout=30)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=65536):  # 增大到64KB
                            if chunk:
                                f.write(chunk)
                    
                    file_size = os.path.getsize(filepath)
                    if file_size > 10000:
                        download_progress.update(index + 1, f"✅ 成功 ({file_size//1024}KB)")
                        return filepath
                    else:
                        download_progress.update(index + 1, f"❌ 文件过小")
                        os.remove(filepath)
                else:
                    download_progress.update(index + 1, f"❌ HTTP {response.status_code}")
            except Exception as e:
                download_progress.update(index + 1, f"❌ 失败")
            return None
        
        # 超高速并行下载 - 为所有文件优化
        downloaded_files = []
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            for i, url in enumerate(urls[:6]):  # 尝试前6个候选
                future = executor.submit(download_single, url, i)
                futures.append(future)
            
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                if result:
                    downloaded_files.append(result)
                    # 取消其他下载任务
                    for f in futures[i+1:]:
                        if not f.done():
                            f.cancel()
                    break
        
        download_progress.finish("下载完成")
        download_time = time.perf_counter() - start_time
        
        if downloaded_files:
            print(f"✅ 下载完成 ({download_time:.3f}s)")
            return downloaded_files[0]
        else:
            print(f"❌ 主要候选下载失败，尝试备用候选...")
            # 尝试剩余的候选
            for i, url in enumerate(urls[6:12]):
                result = download_single(url, i)
                if result:
                    return result
            print(f"❌ 下载完全失败 ({download_time:.3f}s)")
            return None
    
    def instant_install(self, package_file, package_name):
        """瞬时安装 - 为所有文件优化"""
        if not package_file or not os.path.exists(package_file):
            print(f"❌ 安装文件不存在: {package_file}")
            return False
            
        filename = os.path.basename(package_file)
        print(f"🔧 瞬时安装: {filename}")
        
        # 安装进度条
        install_progress = ProgressBar("安装包", total=100)
        start_time = time.perf_counter()
        
        try:
            # 为所有文件优化安装参数
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "--disable-pip-version-check",
                "--no-warn-script-location",
                package_file
            ], capture_output=True, text=True, timeout=300)  # 增加超时时间
            
            # 模拟安装进度
            for i in range(10):
                install_progress.update((i + 1) * 10)
                time.sleep(0.05)
            
            install_time = time.perf_counter() - start_time
            
            if result.returncode == 0:
                install_progress.finish("安装成功")
                return True
            else:
                install_progress.finish("安装失败")
                if result.stderr:
                    error_lines = result.stderr.strip().split('\n')
                    for line in error_lines:
                        if line.strip():
                            print(f"  错误: {line}")
                return False
                
        except subprocess.TimeoutExpired:
            install_progress.finish("安装超时")
            return False
        except Exception as e:
            install_progress.finish("安装错误")
            print(f"❌ 安装错误: {e}")
            return False
    
    def turbo_pip_install(self, package_name):
        """涡轮加速pip安装 - 为所有文件优化"""
        print(f"🚀 启动涡轮加速pip安装: {package_name}")
        
        # 使用最快的镜像
        best_mirror = self.mirrors[0]
        mirror_name = best_mirror.split('/')[2]
        
        print(f"🎯 使用镜像: {mirror_name}")
        
        # 为所有文件优化的pip参数
        pip_command = [
            sys.executable, "-m", "pip", "install", 
            package_name,
            "-i", best_mirror,
            "--trusted-host", mirror_name,
            "--timeout", "120",
            "--retries", "5",
            "--progress-bar", "on",
            "--no-cache-dir",
            "--disable-pip-version-check",
        ]
        
        # Windows特定优化 - 为所有文件
        if platform.system().lower() == 'windows':
            pip_command.extend([
                "--use-feature=fast-deps",
                "--no-build-isolation",
                "--prefer-binary",  # 为所有文件优先使用二进制
            ])
        
        progress = ProgressBar("涡轮下载", total=100)
        start_time = time.perf_counter()
        
        try:
            result = subprocess.run(
                pip_command,
                capture_output=True,
                text=True,
                timeout=600,
                encoding='utf-8',
                errors='ignore'
            )
            
            elapsed = time.perf_counter() - start_time
            
            # 快速完成进度条
            for i in range(10):
                progress.update((i + 1) * 10)
                time.sleep(0.05)
            progress.finish("安装完成")
            
            if result.returncode == 0:
                print(f"✅ 涡轮加速安装成功! 耗时: {elapsed:.2f}秒")
                return True
            else:
                print(f"❌ 涡轮加速安装失败! 耗时: {elapsed:.2f}秒")
                if result.stderr:
                    error_lines = result.stderr.strip().split('\n')
                    for line in error_lines[-3:]:
                        if line.strip() and any(keyword in line.lower() for keyword in 
                              ['error', 'failed', 'not found']):
                            print(f"  错误: {line}")
                return False
                
        except subprocess.TimeoutExpired:
            progress.finish("安装超时")
            print("❌ 安装超时")
            return False
        except Exception as e:
            progress.finish("安装异常")
            print(f"💥 安装异常: {e}")
            return False
    
    def install(self, package_name):
        """主安装流程 - 为所有文件优化"""
        total_start = time.perf_counter()
        print(f"🚀 ULTIMATE FAST PIP 启动: {package_name}")
        
        # 对于复杂包，直接使用涡轮加速
        complex_packages = ['tensorflow', 'pytorch', 'torch', 'opencv-python']
        if package_name.lower() in complex_packages:
            print(f"🔧 检测到复杂包，直接涡轮加速...")
            success = self.turbo_pip_install(package_name)
        else:
            try:
                # 1. 极致并行搜索（使用5个镜像）
                links = self.ultra_search(package_name)
                if not links:
                    print("❌ 搜索失败，使用涡轮加速安装...")
                    success = self.turbo_pip_install(package_name)
                else:
                    # 检查版本是否合理
                    latest_file = os.path.basename(links[0])
                    if self.is_reasonable_version(latest_file, package_name):
                        # 2. 超高速下载
                        package_file = self.hyper_download(links)
                        if package_file:
                            # 3. 瞬时安装
                            success = self.instant_install(package_file, package_name)
                            if success:
                                total_time = time.perf_counter() - total_start
                                print(f"🎉 极速模式成功! 总耗时: {total_time:.3f}秒")
                                self.cleanup()
                                return True
                    
                    # 快速模式失败，切换到涡轮加速
                    print("🔄 切换到涡轮加速pip模式...")
                    success = self.turbo_pip_install(package_name)
                    
            except Exception as e:
                print(f"💥 系统错误: {e}")
                success = self.turbo_pip_install(package_name)
        
        total_time = time.perf_counter() - total_start
        
        if success:
            print(f"🎉 安装完成! 总耗时: {total_time:.3f}秒")
        else:
            print(f"❌ 安装失败! 总耗时: {total_time:.3f}秒")
        
        self.cleanup()
        return success
    
    def is_reasonable_version(self, filename, package_name):
        """检查版本是否合理"""
        version_pattern = r'-(\d+\.\d+(?:\.\d+)*)'
        match = re.search(version_pattern, filename)
        
        if match:
            version = match.group(1)
            # 对于知名包，检查版本是否过旧
            old_version_packages = {
                'tensorflow': '2.',
                'numpy': '1.',
                'pandas': '1.',
                'matplotlib': '3.',
            }
            
            for pkg, min_version in old_version_packages.items():
                if package_name.lower() == pkg and not version.startswith(min_version):
                    print(f"⚠️  发现过旧版本 {version}，使用涡轮加速安装最新版")
                    return False
        return True
    
    def cleanup(self):
        """快速清理"""
        try:
            import shutil
            if os.path.exists(self.download_dir):
                shutil.rmtree(self.download_dir, ignore_errors=True)
        except:
            pass

def main():
    """命令行入口"""
    if len(sys.argv) != 3 or sys.argv[1] != 'install':
        print("用法: python fast_pip.py install <package>")
        sys.exit(1)
    
    package_name = sys.argv[2]
    pip = UltimateFastPip()
    
    try:
        success = pip.install(package_name)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
        sys.exit(1)

if __name__ == '__main__':
    main()
