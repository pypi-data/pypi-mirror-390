import argparse
import getpass
from .auth import activation_manager

def activate_command():
    """激活命令"""
    print("欢迎使用 poxiaoai!")
    print("请输入激活码:")

    try:
        activation_code = getpass.getpass("激活码: ")
        if activation_manager.activate(activation_code):
            print("激活成功!")
        else:
            print("激活码错误!")
    except KeyboardInterrupt:
        print("\n取消激活")
    except Exception as e:
        print(f"激活失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='poxiaoai 工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # code 命令
    code_parser = subparsers.add_parser('code', help='输入激活码')

    args = parser.parse_args()

    if args.command == 'code':
        activate_command()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()