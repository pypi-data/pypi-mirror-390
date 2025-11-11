"""
命令行接口模块
这个模块不会被加密，因为需要用于激活
"""
import argparse
import getpass
import sys
from .auth import activate, is_activated, get_activation_info


def main():
    parser = argparse.ArgumentParser(description='poxiaoai 工具包')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 激活命令
    activate_parser = subparsers.add_parser('code', help='输入激活码')

    # 状态命令
    status_parser = subparsers.add_parser('status', help='查看激活状态')

    # 测试命令
    test_parser = subparsers.add_parser('test', help='测试功能')

    # 日志测试命令
    log_test_parser = subparsers.add_parser('log-test', help='测试日志功能')

    args = parser.parse_args()

    if args.command == 'code':
        activation_code = getpass.getpass("请输入激活码: ")
        if activate(activation_code):
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.command == 'status':
        if is_activated():
            info = get_activation_info()
            print("✅ 软件已激活")
            print(f"🖥️  机器指纹: {info['fingerprint']}")

            # 测试加载加密模块
            try:
                from . import np_log
                print("✅ 加密模块加载正常")
            except Exception as e:
                print(f"❌ 模块加载失败: {e}")
        else:
            print("❌ 软件未激活")
            print("请运行 'poxiaoai code' 进行激活")

    elif args.command == 'test':
        if not is_activated():
            print("错误: 软件未激活！请先运行 'poxiaoai code' 进行激活。")
            sys.exit(1)

        try:
            # 测试所有功能模块
            from . import np_log, file_utils, data_processor

            # 测试日志
            logger = np_log.setup_logging(name="test")
            logger.info("✅ 日志功能测试通过")

            print("✅ 所有功能测试通过！")

        except Exception as e:
            print(f"❌ 功能测试失败: {e}")
            sys.exit(1)

    elif args.command == 'log-test':
        if not is_activated():
            print("错误: 软件未激活！请先运行 'poxiaoai code' 进行激活。")
            sys.exit(1)

        try:
            from . import np_log
            logger = np_log.setup_logging()
            logger.info("这是一条信息日志")
            logger.warning("这是一条警告日志")
            logger.error("这是一条错误日志")
            print("✅ 日志测试完成，请查看日志文件")
        except Exception as e:
            print(f"❌ 日志测试失败: {e}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()