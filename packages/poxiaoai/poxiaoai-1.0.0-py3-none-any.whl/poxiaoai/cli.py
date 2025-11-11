import argparse
import getpass
import sys
from .auth import activate, is_activated


def main():
    parser = argparse.ArgumentParser(description='poxiaoai 工具包')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 激活命令
    activate_parser = subparsers.add_parser('code', help='输入激活码')

    # 状态命令
    status_parser = subparsers.add_parser('status', help='查看激活状态')

    args = parser.parse_args()

    if args.command == 'code':
        activation_code = getpass.getpass("请输入激活码: ")
        if activate(activation_code):
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.command == 'status':
        if is_activated():
            print("✅ 软件已激活")
        else:
            print("❌ 软件未激活")
            print("请运行 'poxiaoai code' 进行激活")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()