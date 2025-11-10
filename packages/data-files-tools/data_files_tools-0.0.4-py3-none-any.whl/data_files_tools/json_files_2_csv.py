import argparse
import json
import csv
import os
import glob
import sys

def load_json_files(directory, file_suffix):
    """加载指定目录下所有指定后缀的JSON文件"""
    pattern = os.path.join(directory, f"*{file_suffix}")
    files = glob.glob(pattern)
    return sorted(files)

def validate_structure(json_data, reference_structure):
    """验证JSON文件结构与参考结构是否一致"""
    if len(json_data) != len(reference_structure):
        return False, f"条目数量不一致: 期望`{len(reference_structure)}`条，实际`{len(json_data)}`条"
    
    for i, (ref_item, current_item) in enumerate(zip(reference_structure, json_data)):
        if ref_item.get("序号") != current_item.get("序号"):
            return False, f"第{i+1}条序号不一致: 期望`{current_item.get('序号')}`，实际`{ref_item.get('序号')}`"
        
        if ref_item.get("name") != current_item.get("name"):
            return False, f"第{i+1}条name不一致: 期望`{current_item.get('name')}`，实际`{ref_item.get('name')}`"
    
    return True, "结构验证通过"

def json_to_csv_row(json_data):
    """将JSON数据转换为CSV的一行"""
    row = {}
    for item in json_data:
        row[item["name"]] = item["value"]
    return row

def strip_json(json_text: str) -> str:
    """
    由于 json 文件可能包含 ``` 或  ```json 或  说明内容... ``` 或  说明内容... ```json 等作为开始 ``` 作为结尾等情况
    所以，需要对这些非 json 内容进行剔除
    :param json_text: json 文件内容
    :return: 剔除后的 json 文件内容
    """

    result: str = json_text  # 初始化结果变量为输入的json文本

    # 查找等一个 ```json\n 的位置
    start_index: int = json_text.find("```json\n")

    # 如果找到，```json\n 则返回之后的内容
    if start_index >= 0:
        result = json_text[start_index + len("```json\n"):]

    # 如果没有找到，则查找第一个 ```\n 的位置
    else:
        start_index = json_text.find("```\n")

        # 如果找到，```\n 则返回之后的内容
        if start_index >= 0:
            result = json_text[start_index + len("```\n"):]
    
    # 如果没有则原文返回
    if start_index == -1:
        return result
            
    else:

        # 从后方找 ``` 截取 之前的内容
        end_index = result.rfind("```")
        if end_index >= 0:
            result = result[:end_index]

        return result

def move_err_files_to_folder(err_json_file: str, err_folder: str):
    if not os.path.exists(err_folder):
        os.makedirs(err_folder)
        print(f"创建错误文件存放文件夹: {err_folder}")
    
    errJsonFile: str = os.path.basename(err_json_file)
    os.rename(err_json_file, os.path.join(err_folder, os.path.basename(errJsonFile)))

    # 检查一下支除 .json 后缀的文件是否存在，如果存在，一同移动到错误文件夹
    errProFile: str = err_json_file[:-5]

    if os.path.exists(errProFile):
        os.rename(errProFile, os.path.join(err_folder, os.path.basename(errProFile)))
    print(f"{errProFile} 与 {errJsonFile}, 错误文件已移动到: {err_folder}")
    

def main():
    parser = argparse.ArgumentParser(description='将多个JSON文件合并为CSV文件')
    parser.add_argument('-d', '--directory', required=True, help='来源文件夹路径')
    parser.add_argument('-s', '--file-suffix', required=True, help='文件后缀名(如.json)')
    parser.add_argument('-o', '--output-file', required=True, help='输出的CSV文件路径')
    parser.add_argument('-e', '--err-folder', required=False, default='error', help='错误文件存放文件夹')
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.isdir(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在")
        sys.exit(1)
    
    # 加载所有JSON文件
    json_files = load_json_files(args.directory, args.file_suffix)
    
    if not json_files:
        print(f"在目录 '{args.directory}' 中未找到后缀为 '{args.file_suffix}' 的文件")
        sys.exit(1)
    
    print(f"找到 {len(json_files)} 个JSON文件")
    
    # 读取第一个文件作为参考结构
    try:
        with open(json_files[0], 'r', encoding='utf-8') as f:

            jsonText: str = f.read()
            jsonText = strip_json(jsonText)
            first_json_data = json.loads(jsonText)

        print(f"已加载参考文件: {os.path.basename(json_files[0])}")
    except Exception as e:
        print(f"读取参考文件失败: {e}")
        sys.exit(1)
    
    # 获取列标题（按序号排序）
    reference_structure = sorted(first_json_data, key=lambda x: x["序号"])
    headers = [item["name"] for item in reference_structure]
    
    all_rows = []

    errFloder: str = os.path.join(args.directory, args.err_folder)
    
    # 处理每个文件
    for i, file_path in enumerate(json_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                jsonText: str = f.read()
                jsonText = strip_json(jsonText)
                json_data = json.loads(jsonText)
            
            # 对当前文件的数据按序号排序
            current_structure = sorted(json_data, key=lambda x: x["序号"])
            
            # 验证结构（第一个文件跳过自我验证）
            if i > 0:
                is_valid, message = validate_structure(reference_structure, current_structure)
                if not is_valid:
                    print(f"文件 {os.path.basename(file_path)} 结构验证失败: {message}")

                    move_err_files_to_folder(file_path, errFloder)

                    continue
            
            # 转换为CSV行
            row = json_to_csv_row(current_structure)
            all_rows.append(row)
            print(f"已处理: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            # 将错误文件移动到错误文件夹        
            move_err_files_to_folder(file_path, errFloder)

            continue
    
    # 写入CSV文件
    try:
        with open(args.output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_rows)
        
        print(f"成功生成CSV文件: {args.output_file}")
        print(f"共处理 {len(all_rows)} 个患者记录")
        print(f"CSV文件包含 {len(headers)} 列")
        
    except Exception as e:
        print(f"写入CSV文件失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()