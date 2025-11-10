"""
Fast Pip 命令行入口点
允许通过 python -m fast_pip 运行
"""

import sys
import argparse
from . import UltimateFastPip, benchmark, __version__

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="Fast Pip - 终极性能Python包安装工具",
        epilog="""
示例:
  python -m fast_pip install requests
  python -m fast_pip install "numpy>=1.20.0"
  python -m fast_pip benchmark rich
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # install 命令
    install_parser = subparsers.add_parser('install', help='安装Python包')
    install_parser.add_argument('package', help='要安装的包名（支持版本说明符）')
    install_parser.add_argument('--version', '-v', help='指定版本（已弃用，请使用package@version格式）')
    
    # benchmark 命令
    benchmark_parser = subparsers.add_parser('benchmark', help='性能测试')
    benchmark_parser.add_argument('package', help='要测试的包名')
    
    # version 命令
    subparsers.add_parser('version', help='显示版本信息')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'install':
            # 处理版本说明符
            package_name = args.package
            if args.version:
                print("⚠️  --version 参数已弃用，请使用 package@version 格式")
                package_name = f"{args.package}=={args.version}"
            
            pip = UltimateFastPip()
            success = pip.install(package_name)
            sys.exit(0 if success else 1)
            
        elif args.command == 'benchmark':
            elapsed = benchmark(args.package)
            if elapsed >= 0:
                print(f"⏱️  性能测试完成: {elapsed:.3f} 秒")
            else:
                print("❌ 性能测试失败")
                sys.exit(1)
                
        elif args.command == 'version':
            print(f"Fast Pip 版本: {__version__}")
            print(f"作者: {__author__}")
            print(f"描述: {__description__}")
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"💥 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()