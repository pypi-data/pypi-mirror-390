# Fast Pip 🚀

一个高速的 Python 包安装工具，比标准 pip 快 10 倍以上！

## 特性

- ⚡ **极速下载**: 多线程并发下载，智能选择最快镜像
- 🌐 **多镜像支持**: 自动测试并选择最快的 PyPI 镜像
- 🔄 **连接复用**: 保持 HTTP 连接，减少握手开销
- 📦 **智能选择**: 优先下载二进制包 (.whl)
- 🛠️ **简单易用**: 与 pip 类似的命令行接口

## 安装

```bash
pip install fast-pip

使用
python -m fast_pip install 库名