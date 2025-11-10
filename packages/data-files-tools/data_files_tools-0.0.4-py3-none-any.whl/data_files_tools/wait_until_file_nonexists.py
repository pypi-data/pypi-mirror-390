"""
这个py文件的作用是检测指定文件夹中,指定后缀名的文件是否已全部不存在,否则的话就等待,实现循环监测,如果全部不存在则结束监测
"""

import argparse
import logging
import os
import time
import sys


def setup_logging():
    """设置日志格式"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def check_files_exist(directory, extensions):
    """
    检查指定目录中是否存在指定后缀名的文件
    
    Args:
        directory: 要监测的目录
        extensions: 文件后缀名列表
    
    Returns:
        tuple: (是否存在文件, 找到的文件列表)
    """
    if not os.path.exists(directory):
        logging.error(f"目录不存在: {directory}")
        return False, []
    
    if not os.path.isdir(directory):
        logging.error(f"路径不是目录: {directory}")
        return False, []
    
    found_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in extensions:
                found_files.append(os.path.join(root, file))
    
    return len(found_files) > 0, found_files


def monitor_directory(directory, extensions, check_interval, log_interval):
    """
    监测目录中的文件
    
    Args:
        directory: 要监测的目录
        extensions: 文件后缀名列表
        check_interval: 检查间隔时间(秒)
        log_interval: 日志打印间隔时间(秒)
    """
    logging.info(f"开始监测目录: {directory}")
    logging.info(f"监测的文件后缀: {', '.join(extensions)}")
    logging.info(f"检查间隔: {check_interval}秒")
    logging.info(f"日志打印间隔: {log_interval}秒")
    
    start_time = time.time()
    last_log_time = start_time
    check_count = 0
    
    try:
        while True:
            check_count += 1
            current_time = time.time()
            
            # 检查文件是否存在
            files_exist, found_files = check_files_exist(directory, extensions)
            
            # 如果文件全部不存在,结束监测
            if not files_exist:
                logging.info(f"监测完成！所有指定后缀的文件都已不存在。")
                logging.info(f"总共检查次数: {check_count}")
                logging.info(f"总监测时间: {current_time - start_time:.2f}秒")
                return
            
            # 定期打印日志
            if current_time - last_log_time >= log_interval:
                logging.info(f"第 {check_count} 次检查 - 找到 {len(found_files)} 个文件")
                if found_files:
                    logging.info("最近找到的文件:")
                    for i, file_path in enumerate(found_files[:5]):  # 只显示前5个文件
                        logging.info(f"  {i+1}. {file_path}")
                    if len(found_files) > 5:
                        logging.info(f"  ... 还有 {len(found_files) - 5} 个文件")
                last_log_time = current_time
            
            # 等待下一次检查
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        logging.info("监测被用户中断")
    except Exception as e:
        logging.error(f"监测过程中发生错误: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="监测指定目录中指定后缀名的文件是否全部不存在",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python file_monitor.py /path/to/monitor
  python file_monitor.py /path/to/monitor -e .txt .log -c 10 -l 300
  python file_monitor.py /path/to/monitor --extensions .md .txt --check-interval 30
        """
    )
    
    # 必需参数
    parser.add_argument(
        'directory',
        help='要监测的文件夹路径'
    )
    
    # 可选参数
    parser.add_argument(
        '-e', '--extensions',
        nargs='+',
        default=['.md', '.txt', '.pro', '.json', '.prompt'],
        help='要监测的文件后缀名列表(默认: .md .txt .pro .json .prompt)'
    )
    
    parser.add_argument(
        '-c', '--check-interval',
        type=int,
        default=20,
        help='监测的间隔时间,单位：秒(默认: 20)'
    )
    
    parser.add_argument(
        '-l', '--log-interval',
        type=int,
        default=60 * 15,  # 15分钟
        help='打印日志的间隔时间,单位：秒(默认: 900)'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 验证参数
    if args.check_interval <= 0:
        logging.error("检查间隔时间必须大于0")
        sys.exit(1)
    
    if args.log_interval <= 0:
        logging.error("日志间隔时间必须大于0")
        sys.exit(1)
    
    # 确保扩展名都是小写并以点开头
    extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                 for ext in args.extensions]
    
    # 设置日志
    setup_logging()
    
    # 开始监测
    monitor_directory(
        directory=args.directory,
        extensions=extensions,
        check_interval=args.check_interval,
        log_interval=args.log_interval
    )


if __name__ == '__main__':
    main()