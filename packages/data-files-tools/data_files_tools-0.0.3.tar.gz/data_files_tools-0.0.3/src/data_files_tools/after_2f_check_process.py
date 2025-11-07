import argparse
import logging
import os
import shutil
import json
import re
from pathlib import Path

from .json_files_2_csv import strip_json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='LLM文件处理结果校验工具')
    
    # 必需参数
    parser.add_argument('--work_dir', required=True, help='工作目录')
    parser.add_argument('--input_suffix', required=True, help='源输入文件后缀名')
    parser.add_argument('--attributes', required=True, help='JSON属性名列表,多个使用英文逗号分隔')
    
    # 可选参数 - 文件后缀
    parser.add_argument('--output_suffix', default='.json', help='LLM处理结果文件的补充后缀名,默认: .json')
    parser.add_argument('--check_prompt_suffix', default='.check.prompt', help='检查提示词的补充后缀名,默认: .check.prompt')
    parser.add_argument('--check_result_suffix', default='.json', help='校验结果文件的补充后缀名,默认: .json')
    
    # 可选参数 - 成功文件目录
    parser.add_argument('--success_input_dir', default='01.success_input_files', help='成功的源输入文件的保存路径')
    parser.add_argument('--success_output_dir', default='02.success_output_files', help='成功的LLM处理结果文件的保存路径')
    
    # 可选参数 - 重试和失败处理
    parser.add_argument('--max_retries', type=int, default=0, help='重试最大次数,小于1则不作次数限制,默认: 0')
    parser.add_argument('--failed_check_dir', default='f02.failed_check_files', help='校验失败的提示词及结果文件的保存路径')
    parser.add_argument('--retry_dir', required=True, help='校验失败且未达最大重试次数的文件拷贝目录')
    
    return parser.parse_args()

def ensure_directory(directory):
    """确保目录存在,如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"创建目录: {directory}")

def is_check_passed(check_result_file, attributes):
    """检查校验结果是否通过"""
    try:
        with open(check_result_file, 'r', encoding='utf-8') as f:
            json_str: str = f.read()
            json_str = strip_json(json_str)
            data = json.loads(json_str)
        
        for attr in attributes:
            if attr in data:
                value = data[attr]
                if isinstance(value, bool):
                    if not value:
                        return False
                elif isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower not in ['true', '是', 'yes', 'y']:
                        return False
                else:
                    # 其他类型视为不通过
                    return False
            else:
                # 属性不存在视为不通过
                return False
        
        return True
    except Exception as e:
        logging.error(f"读取校验结果文件失败 {check_result_file}: {e}")
        return False

def get_retry_count(filename):
    """从文件名中提取重试次数"""
    pattern = r'\.(\d+)$'
    match = re.search(pattern, filename)
    if match:
        return int(match.group(1))
    return 0

def get_base_filename(filename):
    """获取基础文件名（去除重试计数）"""
    pattern = r'\.\d+$'
    return re.sub(pattern, '', filename)

def create_retry_filename(input_file, retry_count, output_dir):
    """创建重试文件名"""
    file_path = Path(input_file)
    base_name = get_base_filename(file_path.stem)
    new_filename = f"{base_name}.{retry_count}{file_path.suffix}"
    return Path(output_dir + "/" + new_filename)

def move_file(src, dst_dir, description=""):
    """移动文件到指定目录"""
    try:
        ensure_directory(dst_dir)
        dst_path = os.path.join(dst_dir, os.path.basename(src))
        shutil.move(src, dst_path)
        if description:
            logging.info(f"{description}: {os.path.basename(src)} -> {dst_dir}")
        return True
    except Exception as e:
        logging.error(f"移动文件失败 {src} -> {dst_dir}: {e}")
        return False

def copy_file(src, dst_dir, description=""):
    """拷贝文件到指定目录"""
    try:
        ensure_directory(dst_dir)
        dst_path = os.path.join(dst_dir, os.path.basename(src))
        shutil.copy2(src, dst_path)
        if description:
            logging.info(f"{description}: {os.path.basename(src)} -> {dst_dir}")
        return True
    except Exception as e:
        logging.error(f"拷贝文件失败 {src} -> {dst_dir}: {e}")
        return False

def remove_file(file_path, description=""):
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            if description:
                logging.info(f"{description}: {os.path.basename(file_path)}")
            return True
    except Exception as e:
        logging.error(f"删除文件失败 {file_path}: {e}")
    return False

def process_files(args):
    """处理文件的主逻辑"""
    work_dir = Path(args.work_dir)
    attributes = [attr.strip() for attr in args.attributes.split(',')]
    
    # 构建目录路径
    success_input_dir = work_dir / args.success_input_dir
    success_output_dir = work_dir / args.success_output_dir
    failed_check_dir = work_dir / args.failed_check_dir
    retry_dir = args.retry_dir
    
    # 确保目录存在
    ensure_directory(success_input_dir)
    ensure_directory(success_output_dir)
    ensure_directory(failed_check_dir)
    ensure_directory(retry_dir)
    
    # 查找所有源输入文件
    input_files = list(work_dir.glob(f"*{args.input_suffix}"))
    logging.info(f"找到 {len(input_files)} 个源输入文件")
    
    success_count = 0
    retry_count = 0
    failed_count = 0
    
    for input_file in input_files:
        input_filename = input_file.name
        base_name = get_base_filename(input_file.stem)
        current_retry_count = get_retry_count(input_file.stem)
        
        # 构建相关文件路径
        output_file = work_dir / f"{input_filename}{args.output_suffix}"
        check_prompt_file = work_dir / f"{input_filename}{args.check_prompt_suffix}"
        check_result_file = work_dir / f"{input_filename}{args.check_prompt_suffix}{args.check_result_suffix}"
        
        # 检查校验结果文件是否存在
        if not check_result_file.exists():
            logging.warning(f"校验结果文件不存在: {check_result_file.name}")
            # 视为校验失败
            check_passed = False
        else:
            check_passed = is_check_passed(check_result_file, attributes)
        
        if check_passed:
            # 校验成功
            success_count += 1
            
            # 移动成功的文件
            move_file(input_file, success_input_dir, "移动成功源文件")
            
            if output_file.exists():
                move_file(output_file, success_output_dir, "移动成功输出文件")
            
            # 移动检查相关的临时文件
            if check_prompt_file.exists():
                move_file(check_prompt_file, success_input_dir, "移动检查提示词文件")
            if check_result_file.exists():
                move_file(check_result_file, success_input_dir, "移动检查结果文件")
                
            logging.info(f"文件处理成功: {input_filename}")
            
        else:
            # 校验失败
            if args.max_retries > 0 and current_retry_count >= args.max_retries:
                # 达到最大重试次数,移动到失败目录
                failed_count += 1
                move_file(input_file, failed_check_dir, "移动失败源文件")
                
                if check_prompt_file.exists():
                    move_file(check_prompt_file, failed_check_dir, "移动失败提示词文件")
                if check_result_file.exists():
                    move_file(check_result_file, failed_check_dir, "移动失败结果文件")
                    
                logging.warning(f"达到最大重试次数,文件标记为失败: {input_filename}")
                
            else:
                # 未达最大重试次数,进行重试
                retry_count += 1
                new_retry_count = current_retry_count + 1
                new_input_file = create_retry_filename(input_file=input_file, retry_count=new_retry_count, output_dir=retry_dir)
                
                # 拷贝源文件到重试目录
                copy_file(input_file, failed_check_dir, f"拷贝重试文件(第{new_retry_count}次)")
                
                # 重命名源文件（添加重试计数）
                shutil.move(input_file, new_input_file)
                logging.info(f"重试文件重命名: {input_filename} -> {new_input_file.name}")
                
                # 移动处理结果文件到 failed_check_dir
                if output_file.exists():
                    move_file(output_file, failed_check_dir, "移动失败输出文件")
                if check_prompt_file.exists():
                    move_file(check_prompt_file, failed_check_dir, "移动失败提示词文件")
                if check_result_file.exists():
                    move_file(check_result_file, failed_check_dir, "移动失败结果文件")
                    
                logging.info(f"文件准备重试(第{new_retry_count}次): {new_input_file.name}")
    
    # 输出统计信息
    logging.info(f"处理完成! 成功: {success_count}, 重试: {retry_count}, 失败: {failed_count}")

def main():
    """主函数"""
    try:
        args = parse_arguments()
        logging.info(f"开始处理工作目录: {args.work_dir}")
        logging.info(f"源文件后缀: {args.input_suffix}")
        logging.info(f"检查属性: {args.attributes}")
        
        process_files(args)
        
    except Exception as e:
        logging.error(f"程序执行出错: {e}")
        raise

if __name__ == "__main__":
    main()