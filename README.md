# CCF ModelEngine — 数据→知识→洞察 智能体实现

> 基于 Nexent + DataMate 平台的医疗数据处理、知识图谱构建与数据分析智能体系统。
> **赛道**：基于Nexent的"数据—知识—洞察"的智能体与算子实现

---

## 🎯 三任务总览

| 任务 | 名称 | 核心产出 |
|:---:|:---|:---|
| 1 | **数据处理智能体** | 4个ETL算子 + 一键ETL |
| 2 | **知识图谱问答智能体** | 3个KG算子 + 问答系统 |
| 3 | **数据分析可视化智能体** | 分析/图表/报告 + 洞察引擎 |

---

## 🚀 快速开始

### 一键Demo（无需Docker，纯本地）

```bash
pip install -r requirements.txt
python run_demo.py
```

交互菜单中选择 1-4 即可体验三个任务。

### 完整部署（需要 Nexent + Docker）

```bash
# 1. 启动MCP服务器
cd mcp_server
python server.py

# 2. Nexent 中导入智能体配置
# 任务一: task1-data-processing/nexent_config/...import.json
# 任务二: task2-knowledge-graph/nexent_config/kg_qa_agent_nexent_v3.0_import.json
# 任务三: task3-analysis-visualization/nexent_config/task3_analysis_agent_v1.0_import.json

# 3. 绑定 MCP 服务器: http://host.docker.internal:8089
```

---

## 📂 项目结构

```
CCF-ModelEngine-2026/
├── run_demo.py                      # 一键CLI Demo
├── requirements.txt                 # Python依赖
├── README.md
├── LICENSE
│
├── operators/                       # 7个DataMate算子
│   ├── data_loader/                 # ETL-数据读取
│   ├── data_cleaner/                # ETL-清洗去重脱敏
│   ├── data_transformer/            # ETL-类型转换
│   ├── data_exporter/               # ETL-导出CSV/JSON
│   ├── kg_entity_recognizer/        # KG-实体识别
│   ├── kg_relation_extractor/       # KG-关系抽取
│   └── kg_triple_generator/         # KG-三元组生成
│
├── mcp_server/                      # MCP服务器
│   ├── server.py                    # 7个MCP工具
│   └── kg_data/                     # 知识图谱三元组数据
│
├── tests/                           # 测试（optional，见各task目录docs）  │
├── task1-data-processing/           # 📊 任务一
│   ├── nexent_config/
│   ├── agents/
│   ├── operators/
│   └── docs/task1_report.md
│
├── task2-knowledge-graph/           # 🧠 任务二
│   ├── nexent_config/
│   ├── prompts/
│   ├── schema/
│   └── docs/task2_report.md
│       + performance_report.md
│
├── task3-analysis-visualization/    # 📈 任务三
│   ├── nexent_config/
│   └── docs/task3_report.md
│
└── docs/demo/                       # 演示视频（见下方百度网盘）
```

---

## 📊 测试结果

| 测试 | 场景数 | 通过率 |
|:---|:---:|:---:|
| KG算子测试 | 10场景 | 100% |
| KG性能评测（1000条） | 35维度 | 33.5μs/条 |
| kg_analyze测试 | 15场景 | 100% |
| kg_visualize测试 | 46场景 | 100% |
| kg_report测试 | 35场景 | 100% |
| **端到端综合测试** | **15场景** | **100% (44/44)** |

---

## 📝 技术文档

| 文档 | 路径 |
|:---|:---|
| 任务一技术报告 | `task1-data-processing/docs/task1_report.md` |
| 任务二技术报告 | `task2-knowledge-graph/docs/task2_report.md` |
| 任务二性能报告 | `task2-knowledge-graph/docs/performance_report.md` |
| 任务三技术报告 | `task3-analysis-visualization/docs/task3_report.md` |

---

## 🎬 演示视频

> 视频文件较大，已上传至百度网盘：

| 内容 | 链接 |
|:---|:---|
| 📦 **Nexent 演示（三任务全流程）** | [百度网盘](https://pan.baidu.com/s/1-u9zrliYjX2wVUaCoTjhFQ?pwd=vp3p) |
| 🔑 提取码 | `vp3p` |
