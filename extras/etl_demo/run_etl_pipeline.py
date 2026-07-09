# -*- coding: utf-8 -*-
"""
ETL 流水线编排脚本

串联 DataMate 四个算子（loader → cleaner → transformer → exporter），
完成完整的数据处理流程，提供 CLI Demo 演示。

架构：
- Layer 1: 入口与配置层 — main() + CONFIG 字典
- Layer 2: 流水线引擎层 — run_pipeline() + 4步 + 异常捕获
- Layer 3: 算子实例层 — 4个 DataMate 算子实例
- Layer 4: 支撑模块层 — 异常处理 + 进度跟踪 + 报告聚合 + 结果汇总

使用方式：
    python run_etl_pipeline.py

输出：
    output/medical_data_cleaned.csv  — 清洗后的数据文件
    output/pipeline_report.json      — 流水线执行报告
"""

import sys
import os
import json
import time
import logging
import traceback

# ===========================================================================
# Layer 3: 算子实例层 — 导入算子
# ===========================================================================

_OPERATORS_DIR = r"D:\PythonProject\ModelEngine\operators"
if _OPERATORS_DIR not in sys.path:
    sys.path.insert(0, _OPERATORS_DIR)

from data_loader import DataLoaderMapper
from data_cleaner import DataCleaner, ValidationError as CleanerValidationError, ProcessingError as CleanerProcessingError
from data_transformer import DataTransformer, ValidationError as TransformerValidationError, ProcessingError as TransformerProcessingError
from data_exporter import DataExporter, ValidationError as ExporterValidationError, ProcessingError as ExporterProcessingError

# 统一异常别名
ValidationError = (CleanerValidationError, TransformerValidationError, ExporterValidationError)
ProcessingError = (CleanerProcessingError, TransformerProcessingError, ExporterProcessingError)

# ===========================================================================
# Layer 1: 入口与配置层
# ===========================================================================

# 项目根目录（当前脚本所在目录）
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    "data_source": {
        "input_path": os.path.join(ROOT_DIR, "data", "test_medical_data.csv"),
        "output_dir": os.path.join(ROOT_DIR, "output"),
    },
    "data_loader": {
        "encoding": "utf-8",
    },
    "data_cleaner": {
        "removeDuplicates": True,
        "handleMissing": "drop",
        "trimWhitespace": True,
        "standardizeFormat": True,
        "privacyCheck": True,
        "privacyFields": ["name", "phone", "id_card"],  # 脱敏姓名、电话、身份证
    },
    "data_transformer": {
        "selectFields": "",
        "dropFields": "",
        "renameFields": '{"name": "patient_name"}',
        "typeConversions": '{"age": "int", "weight": "float", "height": "float"}',
        "valueMappings": '{"gender": {"M": "男", "F": "女"}}',
        "filterCondition": "",
        "deriveColumns": '{"bmi": "weight/((height/100)**2)"}',
    },
    "data_exporter": {
        "outputFormat": "csv",
        "outputDir": os.path.join(ROOT_DIR, "output"),
        "outputFileName": "medical_data_cleaned",
        "encoding": "utf-8",
        "includeHeader": True,
        "indexColumn": False,
        "overwrite": True,
    },
}


# ===========================================================================
# Layer 4: 支撑模块 — 日志与报告
# ===========================================================================

def print_step(step_num: int, total: int, message: str, status: str, detail: str = ""):
    """格式化打印步骤进度（只打一次，不打 running 状态）"""
    if status in ("ok", "error"):
        icons = {"ok": "✅", "error": "❌"}
        icon = icons.get(status, "✅")
        detail_str = f" — {detail}" if detail else ""
        print(f"[Step {step_num}/{total}] {message}... {icon} {detail_str}")


def print_preview(file_path: str, num_rows: int = 5):
    """打印结果文件预览"""
    if not os.path.exists(file_path):
        return
    print(f"\n📋 结果预览（前 {num_rows} 行）:")
    print("-" * 60)
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i > num_rows:
                break
            print(line.rstrip())
    print("-" * 60)


def save_report(report: dict, output_dir: str):
    """保存流水线报告为 JSON 文件"""
    report_path = os.path.join(output_dir, "pipeline_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(f"📊 报告已保存到 {report_path}")


# ===========================================================================
# Layer 2: 流水线引擎 — 每步实现
# ===========================================================================

def step_load(config: dict) -> dict:
    """
    Step 1: 加载数据

    注意：DataLoaderMapper 使用 execute(sample) 接口，
    与其他三个算子的 process(input_data, params) 不同，需要适配。
    """
    start = time.perf_counter()

    # 创建 DataLoaderMapper 实例（配置在 __init__ 中传入）
    loader = DataLoaderMapper(
        file_paths=[config["data_source"]["input_path"]],
        encoding=config["data_loader"].get("encoding", "utf-8"),
    )

    # 执行加载（execute 模式）
    sample = {"data": [], "count": 0, "sources": [], "errors": []}
    result = loader.execute(sample)

    elapsed = (time.perf_counter() - start) * 1000

    # 格式对齐：DataLoaderMapper 输出 → 下游算子输入格式
    data = result.get("data", [])
    aligned = {
        "data": data,
        "schema": {
            "columns": list(data[0].keys()) if data else [],
            "row_count": len(data),
        },
    }

    # 构造步骤报告
    aligned["step_report"] = {
        "step": "load",
        "rows": len(data),
        "sources": result.get("sources", []),
        "errors": result.get("errors", []),
        "time_ms": round(elapsed, 2),
    }

    return aligned


def step_clean(data: dict, params: dict) -> dict:
    """Step 2: 清洗数据"""
    start = time.perf_counter()
    cleaner = DataCleaner()
    result = cleaner.process(data, params)
    elapsed = (time.perf_counter() - start) * 1000
    result["report"]["step"] = "clean"
    result["report"]["time_ms"] = round(elapsed, 2)
    return result


def step_transform(data: dict, params: dict) -> dict:
    """Step 3: 转换数据"""
    start = time.perf_counter()
    transformer = DataTransformer()
    result = transformer.process(data, params)
    elapsed = (time.perf_counter() - start) * 1000
    result["report"]["step"] = "transform"
    result["report"]["time_ms"] = round(elapsed, 2)
    return result


def step_export(data: dict, params: dict) -> dict:
    """Step 4: 导出数据"""
    start = time.perf_counter()
    exporter = DataExporter()
    result = exporter.process(data, params)
    elapsed = (time.perf_counter() - start) * 1000
    result["report"]["step"] = "export"
    result["report"]["time_ms"] = round(elapsed, 2)
    return result


# ===========================================================================
# Layer 2: 流水线引擎 — 主编排逻辑
# ===========================================================================

def run_pipeline(config: dict) -> dict:
    """
    执行完整 ETL 流水线

    三层异常处理策略：
    - ValidationError → 快速失败，直接退出
    - ProcessingError → 中断流程，记录前几步报告
    - 其他异常 → 捕获并记录，标记失败
    """
    pipeline_report = {
        "config": {k: v for k, v in config.items() if k != "data_source"},
        "steps": [],
        "total_time_ms": 0,
        "success": False,
        "error": None,
        "output_path": None,
    }
    total_start = time.perf_counter()

    # ── Step 1: 加载数据 ──
    try:
        data = step_load(config)
        rows = data["step_report"]["rows"]
        src = ", ".join(data["step_report"]["sources"])
        print_step(1, 4, "加载数据", "ok", f"{rows} 行，来源: {src}")
        pipeline_report["steps"].append(data.pop("step_report"))
    except Exception as e:
        pipeline_report["error"] = f"加载数据失败: {str(e)}"
        pipeline_report["total_time_ms"] = round((time.perf_counter() - total_start) * 1000, 2)
        return pipeline_report

    # ── Step 2: 清洗数据 ──
    try:
        data = step_clean(data, config["data_cleaner"])
        report = data["report"]
        detail = f"{report['input_rows']} → {report['output_rows']} 行"
        print_step(2, 4, "清洗数据", "ok", detail)
        pipeline_report["steps"].append(report)
    except ValidationError as e:
        pipeline_report["error"] = f"清洗参数校验失败: {str(e)}"
        break_out(pipeline_report, total_start)
        return pipeline_report
    except ProcessingError as e:
        pipeline_report["error"] = f"清洗处理失败: {str(e)}"
        pipeline_report["partial_step"] = 2
        break_out(pipeline_report, total_start)
        return pipeline_report
    except Exception as e:
        pipeline_report["error"] = f"清洗数据失败: {str(e)}"
        break_out(pipeline_report, total_start)
        return pipeline_report

    # ── Step 3: 转换数据 ──
    try:
        data = step_transform(data, config["data_transformer"])
        report = data["report"]
        ts = report.get("transform_summary", {})
        details = []
        if ts.get("rename_count", 0) > 0:
            details.append(f"重命名 {ts['rename_count']} 字段")
        if ts.get("type_convert_count", 0) > 0:
            details.append(f"类型转换 {ts['type_convert_count']} 字段")
        if ts.get("value_replace_count", 0) > 0:
            details.append(f"值替换 {ts['value_replace_count']} 处")
        if ts.get("derive_count", 0) > 0:
            details.append(f"派生 {ts['derive_count']} 列")
        detail_str = "；".join(details) if details else "无转换操作"
        print_step(3, 4, "转换数据", "ok", detail_str)
        pipeline_report["steps"].append(report)
    except ValidationError as e:
        pipeline_report["error"] = f"转换参数校验失败: {str(e)}"
        break_out(pipeline_report, total_start)
        return pipeline_report
    except ProcessingError as e:
        pipeline_report["error"] = f"转换处理失败: {str(e)}"
        pipeline_report["partial_step"] = 3
        break_out(pipeline_report, total_start)
        return pipeline_report
    except Exception as e:
        pipeline_report["error"] = f"转换数据失败: {str(e)}"
        break_out(pipeline_report, total_start)
        return pipeline_report

    # ── Step 4: 导出数据 ──
    try:
        result = step_export(data, config["data_exporter"])
        report = result["report"]
        export_path = report.get("export_summary", {}).get("output_path", "")
        detail = f"输出到 {export_path}"
        print_step(4, 4, "导出数据", "ok", detail)
        pipeline_report["steps"].append(report)
        pipeline_report["output_path"] = export_path
    except ValidationError as e:
        pipeline_report["error"] = f"导出参数校验失败: {str(e)}"
        break_out(pipeline_report, total_start)
        return pipeline_report
    except ProcessingError as e:
        pipeline_report["error"] = f"导出处理失败: {str(e)}"
        pipeline_report["partial_step"] = 4
        break_out(pipeline_report, total_start)
        return pipeline_report
    except Exception as e:
        pipeline_report["error"] = f"导出数据失败: {str(e)}"
        break_out(pipeline_report, total_start)
        return pipeline_report

    # ── 全部成功 ──
    pipeline_report["success"] = True
    pipeline_report["total_time_ms"] = round((time.perf_counter() - total_start) * 1000, 2)

    return pipeline_report


def break_out(report: dict, start_time: float):
    """记录中断时的总耗时"""
    report["total_time_ms"] = round((time.perf_counter() - start_time) * 1000, 2)


def print_summary(report: dict):
    """打印最终汇总"""
    print()
    if report["success"]:
        print(f"✅ 流水线执行成功！总耗时 {report['total_time_ms']}ms")
        if report.get("output_path"):
            print(f"📄 输出文件: {report['output_path']}")
    else:
        print(f"❌ 流水线执行失败！")
        print(f"错误: {report['error']}")
        completed = len(report["steps"])
        if completed > 0:
            print(f"已成功完成 {completed}/4 步")
    print()


# ===========================================================================
# Layer 1: 入口
# ===========================================================================

def main():
    """CLI 入口"""
    print("=" * 60)
    print("  ETL 数据处理流水线")
    print("  DataMate 算子编排 Demo")
    print("=" * 60)
    print()

    # 确保输出目录存在
    output_dir = CONFIG["data_source"]["output_dir"]
    os.makedirs(output_dir, exist_ok=True)

    # 检查输入文件
    input_path = CONFIG["data_source"]["input_path"]
    if not os.path.exists(input_path):
        print(f"❌ 输入文件不存在: {input_path}")
        return

    print(f"📂 输入文件: {input_path}")
    print(f"📂 输出目录: {output_dir}")
    print()

    # 执行流水线
    report = run_pipeline(CONFIG)

    # 打印汇总
    print_summary(report)

    # 保存报告
    save_report(report, output_dir)

    # 打印结果预览
    if report.get("output_path") and os.path.exists(report["output_path"]):
        print_preview(report["output_path"])

    # 退出码
    sys.exit(0 if report["success"] else 1)


if __name__ == "__main__":
    main()
