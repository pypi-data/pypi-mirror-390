#!/usr/bin/env python3
"""
QuickChart MCP 伺服器 - 可讀 URL + 固定 Chart.js v2 版 (精簡與優化版)
"""

import json
import os
import re
from copy import deepcopy
from typing import Dict, Any, List, Optional
from urllib.parse import quote
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 伺服器
mcp = FastMCP("QuickChartURL")

# QuickChart 服務位置
QUICKCHART_HOST = os.getenv("QUICKCHART_HOST", "localhost")
QUICKCHART_PORT = os.getenv("QUICKCHART_PORT", "3400")
QUICKCHART_BASE_URL = f"http://{QUICKCHART_HOST}:{QUICKCHART_PORT}"

# 對外可訪問的 URL（例如瀏覽器）
QUICKCHART_EXTERNAL_URL = os.getenv("QUICKCHART_EXTERNAL_URL", f"http://localhost:{QUICKCHART_PORT}")

# 固定 Chart.js 版本：v2
DEFAULT_CHART_VERSION = "2"

# ---------------------------------------------------------
# 可讀 URL（JS 物件字串）序列化工具
# ---------------------------------------------------------

SAFE_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

def _escape_js_str(s: str) -> str:
    return s.replace('\\', '\\\\').replace("'", "\\'")

def to_js_object(value) -> str:
    """將 Python 對象轉換為 JavaScript 對象字符串，正確處理 JavaScript 函數。"""
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            key = k if SAFE_KEY_RE.match(k) else f"'{_escape_js_str(k)}'"
            parts.append(f"{key}:{to_js_object(v)}")
        return "{" + ",".join(parts) + "}"
    elif isinstance(value, list):
        return "[" + ",".join(to_js_object(x) for x in value) + "]"
    elif isinstance(value, str):
        # ★ 關鍵修復：檢查是否為 JavaScript 函數
        if value.strip().startswith('function'):
            return value  # JavaScript 函數直接返回，不加引號
        return "'" + _escape_js_str(value) + "'"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return "null"
    else:
        return str(value)

def deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    if a is None: a = {}
    if b is None: return deepcopy(a)
    result = deepcopy(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result

# ---------------------------------------------------------
# 圖表輔助函式
# ---------------------------------------------------------

BASE_COLORS = [
    'rgba(255, 99, 132, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(255, 206, 86, 0.8)',
    'rgba(75, 192, 192, 0.8)', 'rgba(153, 102, 255, 0.8)', 'rgba(255, 159, 64, 0.8)',
    'rgba(199, 199, 199, 0.8)', 'rgba(83, 102, 255, 0.8)', 'rgba(255, 99, 255, 0.8)',
    'rgba(99, 255, 132, 0.8)',
]

def get_color_by_index(index: int) -> str:
    return BASE_COLORS[index % len(BASE_COLORS)]

def rgba_with_alpha(rgba: str, alpha: float) -> str:
    try:
        inner = rgba.split('rgba(')[1].split(')')[0]
        parts = [p.strip() for p in inner.split(',')]
        if len(parts) == 4: parts[-1] = str(alpha)
        return f"rgba({','.join(parts)})"
    except Exception: pass
    return rgba

def is_pie_like(chart_type: str) -> bool:
    return chart_type in ['pie', 'doughnut', 'polarArea']

def normalize_datasets(chart_type: str, labels: List[Any], datasets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    norm = []
    for i, ds in enumerate(datasets or []):
        ds = deepcopy(ds)
        if is_pie_like(chart_type) or chart_type == 'radar':
            if "backgroundColor" not in ds:
                if chart_type == 'radar':
                    base = get_color_by_index(i)
                    ds["borderColor"] = ds.get("borderColor", base)
                    ds["backgroundColor"] = ds.get("backgroundColor", rgba_with_alpha(base, 0.2))
                else:
                    count = len(ds.get("data", [])) or len(labels or [])
                    ds["backgroundColor"] = [get_color_by_index(j) for j in range(count)]
        else:
            if "backgroundColor" not in ds:
                base = get_color_by_index(i)
                if (ds.get("type") or chart_type) == "line":
                    ds["borderColor"] = ds.get("borderColor", base)
                    ds["backgroundColor"] = ds.get("backgroundColor", rgba_with_alpha(base, 0.2))
                    ds["fill"] = ds.get("fill", False)
                    ds["tension"] = ds.get("tension", 0.3)
                    ds["pointRadius"] = ds.get("pointRadius", 3)
                else:
                    ds["backgroundColor"] = base
        norm.append(ds)
    return norm

def add_title_options(options: Dict[str, Any], title: Optional[str]) -> Dict[str, Any]:
    if not title: return options or {}
    opts = deepcopy(options) if options else {}
    opts.setdefault("title", {"display": True, "text": title})
    opts.setdefault("plugins", {}).setdefault("title", {"display": True, "text": title})
    opts.setdefault("responsive", False)
    return opts

def add_padding_options(chart_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
    opts = deepcopy(options) if options else {}
    padding_needed = 0
    if is_pie_like(chart_type): padding_needed = 40
    elif chart_type in ['radialGauge']: padding_needed = 25

    if padding_needed > 0:
        padding_config = {"top": padding_needed, "right": padding_needed, "bottom": padding_needed, "left": padding_needed}
        opts.setdefault("layout", {})["padding"] = padding_config
    return opts

def ensure_plugins(options: Dict[str, Any]) -> Dict[str, Any]:
    opts = deepcopy(options) if options else {}
    opts.setdefault("plugins", {})
    return opts

def merge_plugin_config(options: Dict[str, Any], plugins_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not plugins_config: return options or {}
    opts = ensure_plugins(options)
    opts["plugins"] = deep_merge(opts.get("plugins", {}), plugins_config)
    return opts

def build_chart_url_from_config(
    config: Dict[str, Any], width: int, height: int, fmt: str = "png",
    background_color: Optional[str] = None, encoding_mode: str = "js",
) -> str:
    base = f"{QUICKCHART_EXTERNAL_URL}/chart"
    if encoding_mode == "js":
        c_str = to_js_object(config)
        encoded_chart = quote(c_str, safe="{}[],:()'")
    else:
        chart_json = json.dumps(config, separators=(",", ":"))
        encoded_chart = quote(chart_json)

    url = f"{base}?c={encoded_chart}&width={width}&height={height}&v={quote(DEFAULT_CHART_VERSION)}"
    if fmt in ("png", "svg"): url += f"&format={fmt}"
    if background_color: url += f"&backgroundColor={quote(background_color)}"
    return url

# ---------------------------------------------------------
# MCP 工具 (核心工具)
# ---------------------------------------------------------

@mcp.tool()
def create_chart_url(
    title: str, chart_type: str = "bar", labels: list = None, datasets: list = None,
    width: int = 500, height: int = 300, options: dict = None, raw_config: dict = None,
    format: str = "png", background_color: str = None, enable_plugins: list = None, plugins_config: dict = None,
) -> str:
    """核心圖表生成函式，建立並回傳一個 QuickChart 圖表的 Markdown 格式 URL。"""
    if raw_config:
        chart_config = deepcopy(raw_config)
        chart_config["options"] = add_title_options(chart_config.get("options"), title)
    else:
        chart_config = {
            "type": chart_type,
            "data": {"labels": labels or [], "datasets": normalize_datasets(chart_type, labels or [], datasets or [])},
            "options": add_title_options(options, title),
        }

    current_chart_type = chart_config.get("type", chart_type)
    chart_config["options"] = add_padding_options(current_chart_type, chart_config.get("options"))

    if enable_plugins or plugins_config:
        chart_config["options"] = ensure_plugins(chart_config.get("options"))
        quick_plugins = {}
        for p in (enable_plugins or []):
            if p == "datalabels": quick_plugins.setdefault("datalabels", {"anchor": "end", "align": "top"})
            elif p == "annotation": quick_plugins.setdefault("annotation", {})
            elif p == "outlabels": quick_plugins.setdefault("outlabels", {"text": "%l %p", "color": "white", "stretch": 15})
            elif p == "doughnutlabel": quick_plugins.setdefault("doughnutlabel", {})
            elif p == "colorschemes": quick_plugins.setdefault("colorschemes", {"scheme": "brewer.SetTwo8"})
        
        if quick_plugins: chart_config["options"] = merge_plugin_config(chart_config["options"], quick_plugins)
        if plugins_config: chart_config["options"] = merge_plugin_config(chart_config["options"], plugins_config)

    url = build_chart_url_from_config(
        config=chart_config, width=width, height=height,
        fmt=format, background_color=background_color,
    )
    return f"![{title}]({url})\n\n[在新分頁開啟]({url})"

# ---------------------------------------------------------
# MCP 工具 (便利工具)
# ---------------------------------------------------------

@mcp.tool()
def create_comparison_chart_url(
    title: str, chart_type: str, categories: list, series_data: dict,
    width: int = 600, height: int = 400, format: str = "png",
    background_color: str = None, enable_plugins: list = None, plugins_config: dict = None,
) -> str:
    """建立一個比較多個系列的圖表（長條圖、折線圖等）。"""
    datasets = [{"label": series_name, "data": data_values} for series_name, data_values in series_data.items()]
    return create_chart_url(
        title=title, chart_type=chart_type, labels=categories, datasets=datasets,
        width=width, height=height, format=format, background_color=background_color,
        enable_plugins=enable_plugins, plugins_config=plugins_config,
    )

@mcp.tool()
def create_mixed_bar_line_url(
    title: str, labels: list, bar_series: dict, line_series: dict,
    width: int = 700, height: int = 400, stacked: bool = False,
    format: str = "png", background_color: str = None,
) -> str:
    """建立一個混合長條圖和折線圖的圖表。"""
    datasets = []
    for name, data in bar_series.items(): datasets.append({"type": "bar", "label": name, "data": data, "yAxisID": "y-axis-1"})
    for name, data in line_series.items(): datasets.append({"type": "line", "label": name, "data": data, "fill": False, "yAxisID": "y-axis-1"})
    
    options = { "scales": { "xAxes": [{"stacked": stacked}], "yAxes": [{"id": "y-axis-1", "stacked": stacked, "ticks": {"beginAtZero": True}}] } }
    normalized_datasets = normalize_datasets("bar", labels, datasets)
    return create_chart_url(
        title=title, chart_type="bar", labels=labels, datasets=normalized_datasets,
        options=options, width=width, height=height, format=format, background_color=background_color,
    )

@mcp.tool()
def create_pie_outlabels_url(
    title: str, labels: list, values: list, width: int = 500, height: int = 500,
    format: str = "png", background_color: str = None,
) -> str:
    """建立一個帶有外部標籤的甜甜圈圖。"""
    datasets = [{"data": values}]
    plugins_config = { "outlabels": {"text": "%l %p", "color": "white", "stretch": 35, "font": {"resizable": True, "minSize": 12}, "lineColor": "#999"} }
    return create_chart_url(
        title=title, chart_type="doughnut", labels=labels, datasets=datasets,
        width=width, height=height, format=format, background_color=background_color, plugins_config=plugins_config,
    )

# --- MODIFIED ---
@mcp.tool()
def create_progress_circle_url(
    title: str, value: float, max_value: float = 100.0, width: int = 500, height: int = 300,
    format: str = "png", background_color: str = None, color: str = "rgba(54, 162, 235, 0.8)",
) -> str:
    """建立一個顯示進度的圓圈圖，中心會顯示百分比。"""
    # JS 函式字串，用於在中心顯示百分比
    # 使用 f-string 將 max_value 注入，並用 {{}} 來轉義 JS 的 {}
    center_text_func = f"function(value) {{ return Math.round(value / {max_value} * 100) + '%'; }}"

    config = {
        "type": "radialGauge",
        "data": {"datasets": [{"data": [max(0, min(max_value, value))], "backgroundColor": color, "borderWidth": 0}]},
        "options": {
            "domain": [0, max_value], 
            "trackColor": "#eee", 
            "centerPercentage": 80, 
            "roundedCorners": True,
            # 在中心顯示百分比
            "centerArea": {
                "text": center_text_func
            }
        }
    }
    return create_chart_url(
        title=title, chart_type="radialGauge", raw_config=config,
        width=width, height=height, format=format, background_color=background_color,
    )



@mcp.tool()
def create_radar_chart_url(
    title: str, categories: list, series_data: dict,
    width: int = 500, height: int = 500, format: str = "png", background_color: str = None
) -> str:
    """建立一個雷達圖（蜘蛛網圖）來比較多維度數據。"""
    return create_comparison_chart_url(
        title=title, chart_type="radar", categories=categories, series_data=series_data,
        width=width, height=height, format=format, background_color=background_color
    )

@mcp.tool()
def create_qr_url(
    text: str, size: int = 150, margin: int = 4, ecLevel: str = "M",
    dark: str = "000000", light: str = "ffffff", format: str = "png",
) -> str:
    """建立一個 QR Code 圖片。"""
    base = f"{QUICKCHART_EXTERNAL_URL}/qr"
    params = [
        f"text={quote(text)}", f"format={format}", f"size={size}",
        f"margin={margin}", f"ecLevel={ecLevel}", f"dark={dark}", f"light={light}",
    ]
    url = f"{base}?{'&'.join(params)}"
    return f"![QR Code for {text}]({url})\n\n[在新分頁開啟]({url})"

# ---------------------------------------------------------
# Prompt & Server Main
# ---------------------------------------------------------

@mcp.prompt()
def chart_prompt(data_description: str) -> str:
    # --- MODIFIED ---
    return f"""
請根據以下描述生成圖表 URL：「{data_description}」
主要工具:
- `create_chart_url()`: 通用圖表 (長條、折線等)
- `create_comparison_chart_url()`: 比較多個系列
- `create_mixed_bar_line_url()`: 混合長條圖和折線圖
- `create_pie_outlabels_url()`: 帶外部標籤的甜甜圈圖
- `create_progress_circle_url()`: 進度圓圈圖 (中心顯示百分比)
- `create_radar_chart_url()`: 雷達圖/蜘蛛網圖

若需更進階，請使用 `create_chart_url` 的 `raw_config` 與 `plugins_config`。
所有圖表固定使用 Chart.js v2。
"""

def main():
    import sys
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("啟動 QuickChart URL MCP 伺服器（可讀 URL + v2 固定）")
    logger.info(f"QuickChart 服務: {QUICKCHART_BASE_URL}")
    logger.info(f"外部訪問 URL: {QUICKCHART_EXTERNAL_URL}")
    logger.info(f"固定 Chart.js 版本: {DEFAULT_CHART_VERSION}")
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("伺服器已停止")
        sys.exit(0)
    except Exception as e:
        logger.error(f"伺服器錯誤: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()