import argparse
import logging
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_check_prompt(sourceFile: str, targetFile: str, templateContent: str, promptVariableName: str, answerVariableName: str) -> str:
    """
    根据模板文件生成检查prompt

    :param sourceFile: 源文件
    :param targetFile: 目标文件
    :param templateContent: 模板内容
    :param promptVariableName: 问题文件内容的变量名
    :param answerVariableName: 答案文件内容的变量名

    :return : 返回生成的检查prompt内容
    """
    
    promptLabel: str = "${" + promptVariableName + "}"
    answerLabel: str = "${" + answerVariableName + "}"

    sourceContent: str = ""
    with open(sourceFile, 'r', encoding='utf-8') as f:
        sourceContent = f.read()
    
    targetContent: str = ""
    with open(targetFile, 'r', encoding='utf-8') as f:
        targetContent = f.read()

    result: str = templateContent.replace(promptLabel, sourceContent).replace(answerLabel, targetContent)
    return result


def create_check_prompt_in_folder(sourceFolder: str, sourceSuffix: str, targetSuffix: str, templateFile: str, outputFolder: str, promptVariableName: str, answerVariableName: str) -> list[str]:
    """
    在指定文件夹中创建检查prompt文件

    :param sourceFolder: 源文件夹
    :param sourceSuffix: 源文件后缀
    :param targetSuffix: 目标文件后缀
    :param templateFile: 模板文件
    :param outputFolder: 输出文件夹
    :param promptVariableName: 问题文件内容的变量名
    :param answerVariableName: 答案文件内容的变量名

    :return : 返回生成的检查prompt文件列表
    """

    # 生成的提示词文件列表
    promptList: list[str] = []

    # 1. 加载模板文件；只有源文件和目标文件均存在时，才生成检查prompt
    # 2. 列出 sourceFolder 中所有后缀为 sourceSuffix 的文件
    # 3. 对于每个文件，找到对应的 targetSuffix 文件
    files: list[str] = [f for f in os.listdir(sourceFolder) if f.endswith(sourceSuffix) and os.path.exists(os.path.join(sourceFolder, f+targetSuffix))]

    # 4. 如果没有找到文件，则退出
    if len(files) == 0:
        logging.info(f"No files found in {sourceFolder} with suffix {sourceSuffix} and {targetSuffix}")
        return promptList

    # 5. 加载模板文件的内容
    templateContent: str = ""
    with open(templateFile, 'r', encoding='utf-8') as f:
        templateContent = f.read()

    for file in files:
        logging.info(f"Processing file: {file}")
        sourceFile: str = os.path.join(sourceFolder, file)
        targetFile: str = os.path.join(sourceFolder, file+targetSuffix)
    
        # 6. 生成检查prompt
        prompt: str = create_check_prompt(sourceFile=sourceFile, 
                                          targetFile=targetFile, 
                                          templateContent=templateContent, 
                                          promptVariableName=promptVariableName, 
                                          answerVariableName=answerVariableName)

        # 7. 将检查prompt写入 outputFolder 中
        outputFilePath: str = os.path.join(outputFolder, file + '.check.prompt')
        with open(outputFilePath, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        logging.info(f"Created check prompt file: {outputFilePath}")
        promptList.append(outputFilePath)
    return promptList
    

def main():

    parser = argparse.ArgumentParser(description='指定工作文件夹,将文件夹中同名的文件与增加指定后缀的文件(默认.json),通过指定模板生成检查prompt(默认.check.prompt)')

    # 指定源文件夹
    parser.add_argument('-s', '--source-folder', type=str, required=True, help='指定源文件夹')

    # 指定源文件的后缀
    parser.add_argument('-ss', '--source-suffix', type=str, default='.md', help='指定源文件的后缀,默认为.md')

    # 指定目标文件的后缀
    parser.add_argument('-ts', '--target-suffix', type=str, default='.json', help='指定目标文件的后缀,默认为.json')

    # 指定模板文件
    parser.add_argument('-f', '--template-file', type=str, required=True, help='指定模板文件的路径')

    # 指定输出文件夹
    parser.add_argument('-o', '--output-folder', type=str, required=True, help='指定输出文件夹')

    # 指定问题文件内容的变量名
    parser.add_argument('-pv', '--prompt-variable-name', type=str, default='prompt-file', help='指定问题文件内容的变量名,默认为prompt-file,其占位符为${prompt-file}')

    # 指定答案文件内容的变量名
    parser.add_argument('-av', '--answer-variable-name', type=str, default='answer-file', help='指定答案文件内容的变量名,默认为answer-file,其占位符为${answer-file}')

    args = parser.parse_args()

    sourceFolder: str = args.source_folder
    sourceSuffix: str = args.source_suffix
    targetSuffix: str = args.target_suffix
    templateFile: str = args.template_file
    outputFolder: str = args.output_folder
    promptVariableName: str = args.prompt_variable_name
    answerVariableName: str = args.answer_variable_name

    logging.info(f"sourceFolder: {sourceFolder}")
    logging.info(f"sourceSuffix: {sourceSuffix}")
    logging.info(f"targetSuffix: {targetSuffix}")
    logging.info(f"templateFile: {templateFile}")
    logging.info(f"outputFolder: {outputFolder}")
    logging.info(f"promptVariableName: {promptVariableName}")
    logging.info(f"answerVariableName: {answerVariableName}")

    create_check_prompt_in_folder(sourceFolder=sourceFolder, 
                                  sourceSuffix=sourceSuffix, 
                                  targetSuffix=targetSuffix, 
                                  templateFile=templateFile, 
                                  outputFolder=outputFolder,
                                  promptVariableName=promptVariableName,
                                  answerVariableName=answerVariableName)

    print("create_2f_check_prompt done.")

if __name__ == "__main__":
    main()