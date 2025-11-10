"""
这个程序用于将指定文件夹内的,指定后缀名的所有文件,以固定的形式,合并到一个markdown文件中.文件的内容原样照搬,而每一个案例的标题层级也是由命令的参数指定
"""

import argparse
import logging
import os
import glob
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def merge_files_to_markdown(directory, suffix, output_file, heading_level, back_quote_level):
    """
    将指定文件夹内指定后缀名的所有文件合并到一个markdown文件中
    
    Args:
        directory (str): 要搜索的目录路径
        suffix (str): 文件后缀名,如 ".txt"
        output_file (str): 输出文件路径
        heading_level (int): 标题层级,1-12
        back_quote_level (int): 反引号层级,1-99
    """
    
    # 验证标题层级
    if heading_level < 1 or heading_level > 12:
        logger.error("标题层级必须在1-12之间")
        return False

    # 验证反引号层级
    if back_quote_level < 1 or back_quote_level > 99:
        logger.error("反引号层级必须在1-99之间")
        return False
    
    # 构建搜索模式
    search_pattern = os.path.join(directory, f"*{suffix}")
    logger.info(f"搜索模式: {search_pattern}")
    
    # 获取所有匹配的文件
    files = glob.glob(search_pattern)
    files.sort()  # 按文件名排序
    
    if not files:
        logger.warning(f"在目录 {directory} 中没有找到后缀为 {suffix} 的文件")
        return False
    
    logger.info(f"找到 {len(files)} 个文件")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as out_f:
            for i, file_path in enumerate(files, 1):
                file_name = os.path.basename(file_path)
                logger.info(f"处理文件: {file_name}")
                
                # 写入标题
                heading_prefix = '#' * heading_level
                out_f.write(f"{heading_prefix} 案例{i}\n\n")
                
                # 读取并写入文件内容
                try:

                    if back_quote_level > 0:
                        out_f.write('`' * back_quote_level + '\n')

                    with open(file_path, 'r', encoding='utf-8') as in_f:
                        content = in_f.read()
                        out_f.write(content)
                        
                        # 如果内容不以换行符结尾,添加一个空行
                        if content and not content.endswith('\n'):
                            out_f.write('\n')
                        out_f.write('\n')
                    
                    if back_quote_level > 0:
                        out_f.write('`' * back_quote_level + '\n')
                        
                except UnicodeDecodeError:
                    logger.warning(f"文件 {file_name} 编码可能不是UTF-8,尝试其他编码")
                    try:
                        with open(file_path, 'r', encoding='gbk') as in_f:
                            content = in_f.read()
                            out_f.write(content)
                            if content and not content.endswith('\n'):
                                out_f.write('\n')
                            out_f.write('\n')
                    except Exception as e:
                        logger.error(f"无法读取文件 {file_name}: {e}")
                        out_f.write(f"*无法读取此文件: {str(e)}*\n\n")
                except Exception as e:
                    logger.error(f"读取文件 {file_name} 时出错: {e}")
                    out_f.write(f"*读取文件时出错: {str(e)}*\n\n")
        
        logger.info(f"成功合并 {len(files)} 个文件到 {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"写入输出文件时出错: {e}")
        return False

def main():
    """主函数,解析命令行参数并执行合并操作"""
    parser = argparse.ArgumentParser(description='将指定文件夹内指定后缀名的文件合并到markdown文件')
    
    parser.add_argument('-d', '--directory', required=True, 
                        help='要搜索的目录路径')
    parser.add_argument('-s', '--suffix', required=True,
                        help='文件后缀名,如 ".txt"')
    parser.add_argument('-o', '--output', required=True,
                        help='输出文件路径')
    parser.add_argument('-l', '--level', type=int, required=True,
                        help='标题层级,1-6')
    parser.add_argument('-b', '--back-quote-level', type=int, default=4, 
                        help='反引号的数量,默认为4')
    parser.add_argument('--verbose', action='store_true',
                        help='显示详细日志信息')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 验证目录是否存在
    if not os.path.isdir(args.directory):
        logger.error(f"目录不存在: {args.directory}")
        return
    
    # 确保后缀以点开头
    if not args.suffix.startswith('.'):
        args.suffix = '.' + args.suffix
    
    # 执行合并操作
    success = merge_files_to_markdown(
        directory=args.directory,
        suffix=args.suffix,
        output_file=args.output,
        heading_level=args.level,
        back_quote_level=args.back_quote_level        
    )
    
    if success:
        logger.info("文件合并完成！")
    else:
        logger.error("文件合并失败！")

if __name__ == '__main__':
    main()