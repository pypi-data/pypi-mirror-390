import pandas as pd
import pickle
import argparse

def excel_to_dmp_single_file(excel_file, output_file):
    """
    将 Excel 文件的所有 sheets 保存到一个 .dmp 文件中
    
    Args:
        excel_file (str): Excel 文件路径
        output_file (str): 输出 .dmp 文件路径
    """
    # 读取 Excel 文件的所有 sheet
    excel_data = pd.read_excel(excel_file, sheet_name=None)
    
    # 将所有数据保存到一个 .dmp 文件中
    with open(output_file, 'wb') as f:
        pickle.dump(excel_data, f)
    
    print(f"所有 sheets 已保存到: {output_file}")
    print(f"包含的 sheets: {list(excel_data.keys())}")

# 使用示例
def main():

    # 此处我需要实现 从 -f 选项获取来源文件 -o 选项指定输出文件
    parser = argparse.ArgumentParser(description='将Excel文件转换为.dmp文件')
    parser.add_argument('-f', '--file', required=True, help='输入的Excel文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出的.dmp文件路径')
    
    args = parser.parse_args()
    excel_file: str = args.file
    output_file: str = args.output
    
    excel_to_dmp_single_file(excel_file, output_file)

    print("转换完成！")

if __name__ == "__main__":
    main()