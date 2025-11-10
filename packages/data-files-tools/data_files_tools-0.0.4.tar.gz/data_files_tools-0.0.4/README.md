
```bash
python -m build
```


```
json2csv -d D:/BaiduSyncdisk/20251008_学专科专病数据库（程远）/06.过程结果/20251030_按第三版本生成的100例数据 -s .json -o v3.1_100.csv
```

```
json2csv -d D:/BaiduSyncdisk/20250709_少英姐的医保自动问答/20251030_第一次反馈数据/results -s .json -o r1-0528_20.csv
```

```
json2csv -d D:/cangjie_distributions/demos/llm_client4cj/demo04/0501.result/results -s .json -o D:/cangjie_distributions/demos/llm_client4cj/demo04/0502.result/r1-0528_20.csv
```

生成较验的提示词
```
ccprompt -s D:/git-gitee/data_files_tools/demo/create_2f_check_prompt -ss .md -ts .json -f D:/git-gitee/data_files_tools/demo/create_2f_check_prompt/create_2f_check_prompt_template.md -o D:/git-gitee/data_files_tools/demo/create_2f_check_prompt/output
```

生成检验的提示词
```
ccprompt -s Y:/huawei_DeepSeek-R1-64K-0528_02/results -ss .md -ts .json -f D:/git-gitee/data_files_tools/demo/create_2f_check_prompt/create_2f_check_prompt_template.md -o Y:/huawei_DeepSeek-R1-64K-0528_02/results/check/
```

```
ccprompt -s Y:/huawei_DeepSeek-R1-32K-0528_03/results -ss .md -ts .json -f D:/git-gitee/data_files_tools/demo/create_2f_check_prompt/create_2f_check_prompt_template.md -o Y:/huawei_DeepSeek-R1-32K-0528_03/
```

对校验完成的文件进行分类
```
acprocess --work_dir Y:/huawei_DeepSeek-R1-32K-0528_03/results --input_suffix .md --attributes 是否通过检查字段数量,是否通过检查字段顺序符合要求,是否通过检查字段提取内容均属实 --max_retries 6 --retry_dir Y:/huawei_DeepSeek-R1-32K-0528_03/results/retry
```


#### waituntil 等待完成命令的使用

这个程序的主要特点：

1. **完整的参数解析**：
   - `directory`：必需参数，指定要监测的文件夹
   - `-e/--extensions`：可选，指定文件后缀名，默认为 `.md,.txt,.pro,.json,.prompt`
   - `-c/--check-interval`：可选，监测间隔时间，默认为20秒
   - `-l/--log-interval`：可选，日志打印间隔时间，默认为900秒（15分钟）

2. **健壮的错误处理**：
   - 检查目录是否存在
   - 处理键盘中断（Ctrl+C）
   - 参数验证

3. **详细的日志输出**：
   - 格式化的时间戳日志
   - 定期显示找到的文件列表
   - 监测结束时的统计信息

4. **使用示例**：
```bash
# 基本使用
waituntil /path/to/monitor

# 自定义后缀名和间隔
waituntil /path/to/monitor -e .txt .log -c 10 -l 300

# 只监测 .md 文件，每30秒检查一次
waituntil /path/to/monitor --extensions .md --check-interval 30
```

#### merge2c 文件案例合并命令

这个程序的主要功能包括：

1. **命令行参数解析**：
   - `-d/--directory`: 要搜索的目录路径
   - `-s/--suffix`: 文件后缀名（如 ".txt"）
   - `-o/--output`: 输出文件路径
   - `-l/--level`: 标题层级（1-6）
   - `--verbose`: 显示详细日志

2. **核心功能**：
   - 搜索指定目录下所有指定后缀的文件
   - 按文件名排序处理
   - 为每个文件添加指定层级的Markdown标题
   - 原样复制文件内容
   - 处理不同的文件编码（UTF-8和GBK）

3. **错误处理**：
   - 目录不存在检查
   - 文件读取错误处理
   - 编码问题处理

4. **日志记录**：
   - 显示处理进度和错误信息

**使用示例**：

```bash
# 基本用法
merge2m -d /path/to/files -s .txt -o ./output.md -l 3

# 显示详细日志
merge2m -d /path/to/files -s .txt -o ./output.md -l 3 --verbose

# 处理其他类型的文件
merge2m -d /path/to/code -s .py -o ./code_examples.md -l 2
```

**输出示例**：
如果处理两个txt文件，输出内容如下：
```markdown
### 案例1
这是文件a的内容

### 案例2
这是文件b的内容
```

这个程序具有良好的错误处理和日志记录，能够处理各种常见的使用场景。

运行示例：
```bash
merge2m -d D:/BaiduSyncdisk/20251008_学专科专病数据库（程远）/06.过程结果/20251107_加入校验后的处理100条/004.process/f02.failed_check_files -s .prompt.json -o D:/BaiduSyncdisk/20251008_学专科专病数据库（程远）/06.过程结果/20251107_加入校验后的处理100条/12.error_cases/output.4.txt -l 4 -b 4

merge2m -d D:/BaiduSyncdisk/20251008_学专科专病数据库（程远）/06.过程结果/20251107_加入校验后的处理100条/003.process/f02.failed_check_files -s .prompt.json -o D:/BaiduSyncdisk/20251008_学专科专病数据库（程远）/06.过程结果/20251107_加入校验后的处理100条/12.error_cases/output.3.txt -l 4 -b 4

merge2m -d D:/BaiduSyncdisk/20251008_学专科专病数据库（程远）/06.过程结果/20251107_加入校验后的处理100条/002.process/f02.failed_check_files -s .prompt.json -o D:/BaiduSyncdisk/20251008_学专科专病数据库（程远）/06.过程结果/20251107_加入校验后的处理100条/12.error_cases/output.2.txt -l 4 -b 4
```