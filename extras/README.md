# 补充材料

本目录包含项目开发过程中的辅助材料，供评委查阅。

---

## 目录结构

```
extras/
├── operators_upload/          # 7个算子ZIP包（直接上传DataMate使用）
│   ├── data_loader.zip
│   ├── data_cleaner.zip
│   ├── data_transformer.zip
│   ├── data_exporter.zip
│   ├── kg_entity_recognizer.zip
│   ├── kg_relation_extractor.zip
│   └── kg_triple_generator.zip
│
├── benchmark/                 # KG算子性能评测
│   ├── benchmark_kg_operators.py    # 评测脚本
│   ├── benchmark_texts_1000.json    # 1000条医疗测试数据
│   ├── gen_test_texts_1000.py       # 测试数据生成器
│   └── log/                         # 5次运行日志
│
├── etl_demo/                  # ETL流水线完整Demo
│   ├── run_etl_pipeline.py          # 四步流水线编排脚本
│   ├── requirements.txt
│   ├── data/                        # 测试数据
│   └── output/                      # 运行输出（清洗后数据+报告）
│
├── nexent-modified.zip        # 更改后的Nexent平台源码（提交至百度网盘）
└── datamate-modified.zip      # 更改后的DataMate平台源码（提交至百度网盘）
```

---

## 用途说明

### operators_upload/

已打包好的 DataMate 算子 ZIP 文件。可直接通过 DataMate 平台的算子市场上传使用，无需手动打包。

### benchmark/

KG 算子性能评测工具。使用 `benchmark_texts_1000.json`（1000 条覆盖 28 个维度的医疗文本）对三个 KG 算子进行吞吐量、延迟、内存占用评测。评分结果可输出为 Markdown 报告。

使用方法：

```bash
cd extras/benchmark
pip install pandas
python benchmark_kg_operators.py
```

### etl_demo/

完整的 ETL 数据流水线演示脚本。数据加载→清洗→转换→导出四步全自动执行，输出 CSV + JSON 报告。

使用方法：

```bash
cd extras/etl_demo
pip install -r requirements.txt
python run_etl_pipeline.py
```

### Nexent/DataMate 源码

完整的平台源代码压缩包。因文件较大（约 47MB + 30MB），已上传至百度网盘，下载后解压即可获得完整的魔改版源代码。

> ⚠️ **注意**：压缩包中不包含 `node_modules/`、`.git/`、`__pycache__/` 等缓存和依赖目录。部署前需根据各平台的 README 执行依赖安装（`npm install` / `pip install`）。
