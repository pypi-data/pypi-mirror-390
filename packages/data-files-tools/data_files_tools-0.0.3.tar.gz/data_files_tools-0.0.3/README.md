
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