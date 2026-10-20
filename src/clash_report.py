"""clash_report.py — 工程碰撞报表与 openBIM BCF 3.0 视点包导出器。

本模块提供将碰撞排查结果导出为：
1. 结构化工程排查 CSV / Excel 报表；
2. openBIM BCF (BIM Collaboration Format) 3.0 视点相机与标记 JSON 数据。
"""

from __future__ import annotations

import csv
import json
import os
from typing import Any, Optional

from collision import ClashRecord, ClashReport


def export_clash_report_csv_excel(report: ClashReport, filepath: str) -> str:
    """将碰撞冲突汇总报表导出为结构化 CSV 电子表格 (带 utf-8-sig BOM 保证 Excel 打开中文正常)."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    headers = [
        "ClashID",
        "ClashType",
        "Severity",
        "ObjectA",
        "ObjectB",
        "SystemA",
        "SystemB",
        "Location_X",
        "Location_Y",
        "Location_Z",
        "Clearance_mm",
        "PenetrationDepth_mm",
        "PenetrationVolume_mm3",
        "Recommendation",
        "Status",
    ]

    with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for c in report.clashes:
            writer.writerow([
                c.clash_id,
                c.clash_type.value if hasattr(c.clash_type, "value") else str(c.clash_type),
                c.severity.value if hasattr(c.severity, "value") else str(c.severity),
                c.object_a_id,
                c.object_b_id,
                c.system_a,
                c.system_b,
                f"{c.location.x:.2f}",
                f"{c.location.y:.2f}",
                f"{c.location.z:.2f}",
                f"{c.clearance:.2f}",
                f"{c.penetration_depth:.2f}",
                f"{c.penetration_volume:.2f}",
                c.recommendation,
                c.status,
            ])

    return filepath


def export_bcf_viewpoint(record: ClashRecord, filepath: Optional[str] = None) -> dict[str, Any]:
    """生成 openBIM BCF 3.0 视点相机定位与构件高亮标记数据.

    如果指定 filepath，则自动保存为 JSON 视点文件。
    """
    # 视点相机计算：位于碰撞点斜上方 2000mm 处，俯视观察
    camera_pos = {
        "x": record.location.x,
        "y": record.location.y - 2000.0,
        "z": record.location.z + 1200.0,
    }
    camera_target = {
        "x": record.location.x,
        "y": record.location.y,
        "z": record.location.z,
    }

    components_info = {
        "selection": [
            {"ifc_guid": record.object_a_id},
            {"ifc_guid": record.object_b_id},
        ],
        "coloring": [
            {
                "color": "FF0000",
                "components": [{"ifc_guid": record.object_a_id}, {"ifc_guid": record.object_b_id}],
            }
        ],
    }

    bcf_data: dict[str, Any] = {
        "topic": {
            "guid": record.clash_id,
            "topic_type": record.clash_type.value if hasattr(record.clash_type, "value") else str(record.clash_type),
            "topic_status": record.status,
            "title": f"BIM冲突: {record.object_a_id} vs {record.object_b_id}",
            "priority": record.severity.value if hasattr(record.severity, "value") else str(record.severity),
            "description": (
                f"系统[{record.system_a}]构件[{record.object_a_id}]与系统[{record.system_b}]构件[{record.object_b_id}]冲突。\n"
                f"穿透深度: {record.penetration_depth:.1f}mm，实测净距: {record.clearance:.1f}mm。\n"
                f"整改建议: {record.recommendation}"
            ),
        },
        "viewpoint": {
            "perspective_camera": {
                "camera_view_point": camera_pos,
                "camera_direction": {"x": 0.0, "y": 0.857, "z": -0.514},
                "camera_up_vector": {"x": 0.0, "y": 0.514, "z": 0.857},
                "field_of_view": 60.0,
            },
            "components": components_info,
            "clipping_planes": [
                {
                    "location": camera_target,
                    "direction": {"x": 0.0, "y": 0.0, "z": 1.0},
                }
            ],
        },
        "components": components_info,
    }

    if filepath:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, mode="w", encoding="utf-8") as f:
            json.dump(bcf_data, f, indent=2, ensure_ascii=False)

    return bcf_data
