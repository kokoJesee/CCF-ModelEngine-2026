# ETL 数据处理流水线 Demo

> 基于 DataMate 4 个算子（loader → cleaner → transformer → exporter）的完整 ETL 流程编排脚本。
>
> 适用于 CCF 开源创新大赛 · Nexent 赛道 · 任务一。

---

## 快速开始

### 0. 安装依赖

```bash
pip install pandas numpy
```

### 1. 运行

```bash
python run_etl_pipeline.py
```

### 2. 查看输出

```
output/
├── medical_data_cleaned.csv    # 清洗后的数据文件
└── pipeline_report.json        # 流水线执行报告
```

---

## 流水线流程

```
Step 1: data_loader     — 加载 CSV 数据文件
Step 2: data_cleaner    — 去重、空值处理、脱敏、日期标准化
Step 3: data_transformer — 字段重命名、类型转换、值替换、派生列
Step 4: data_exporter   — 导出为 CSV 文件
```

## 配置说明

所有参数在 `run_etl_pipeline.py` 的 `CONFIG` 字典中集中管理：

| 模块 | 参数 | 说明 |
|:---|:---|:---|
| `data_loader` | encoding | 文件编码（默认 utf-8） |
| `data_cleaner` | removeDuplicates, handleMissing, trimWhitespace, standardizeFormat, privacyCheck | 清洗规则 |
| `data_transformer` | renameFields, typeConversions, valueMappings, deriveColumns | 转换规则 |
| `data_exporter` | outputFormat, outputDir, outputFileName, encoding, includeHeader | 导出配置 |

## 算子依赖

- **类名**：`DataLoaderMapper`、`DataCleaner`、`DataTransformer`、`DataExporter`
- **源码位置**：`D:\PythonProject\ModelEngine\operators\`
- **架构模式**：独立类 + process/execute + PIPELINE_ORDER + STEP_HANDLERS

## 输出示例

```
[Step 1/4] 加载数据... ✅ 10 行，来源: data/test_medical_data.csv
[Step 2/4] 清洗数据... ✅ 10 → 8 行
[Step 3/4] 转换数据... ✅ 重命名 1 字段；类型转换 3 字段；值替换 1 处；派生 1 列
[Step 4/4] 导出数据... ✅ 输出到 output/medical_data_cleaned.csv

✅ 流水线执行成功！总耗时 150.34ms
📊 报告已保存到 output/pipeline_report.json
```
