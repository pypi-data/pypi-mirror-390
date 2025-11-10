# QuickChart MCP 伺服器

這個專案提供了一個伺服器，作為使用 [QuickChart](https://quickchart.io/) 生成圖表影像的簡化介面。它被設計為一個「受管圖表提供者」(MCP)，並提供了對標準 QuickChart API 的多項增強功能。

該伺服器使用 `FastMCP` 框架構建，並公開了一組工具，用於創建具有人類可讀 URL 的各種圖表。

## 功能

-   **人類可讀的 URL**：生成具有類似 JavaScript 物件語法的圖表 URL，使其更容易調試和理解。
-   **固定 Chart.js 版本**：將所有圖表固定為 Chart.js v2，以實現一致的渲染和行為。
-   **簡化圖表創建**：提供高階工具來創建常見的圖表類型，如長條圖、折線圖、圓餅圖、雷達圖和混合圖表，而無需編寫複雜的 Chart.js JSON 配置。
-   **自動樣式設定**：自動應用顏色、填充和其他樣式屬性的合理預設值。
-   **插件支援**：輕鬆啟用和配置 Chart.js 插件，如 `datalabels`、`outlabels` 和 `annotation`。
-   **QR Code 生成**：包含一個用於生成 QR Code 的實用工具。

## 先決條件

在運行此伺服器之前，您需要一個正在運行的 QuickChart 服務實例。您可以使用 Docker 在本地運行它。

有關更多資訊，請參閱 [QuickChart 文件](https://quickchart.io/documentation/docker/)。

## 安裝

此專案使用 Python，其依賴項在 `pyproject.toml` 中定義。

1.  **克隆儲存庫：**
    ```bash
    git clone <repository-url>
    cd lcp-chart-mcp
    ```

2.  **安裝依賴項：**
    建議使用虛擬環境。
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # 在 Windows 上，使用 `.venv\Scripts\activate`
    pip install .
    ```

## 配置

伺服器使用環境變數進行配置：

-   `QUICKCHART_HOST`：您的 QuickChart 實例的主機名。（預設值：`localhost`）
-   `QUICKCHART_PORT`：您的 QuickChart 實例運行的埠號。（預設值：`3400`）
-   `QUICKCHART_EXTERNAL_URL`：QuickChart 服務的公共可訪問 URL。這是將嵌入到生成的圖表影像中的 URL。（預設值：`http://localhost:3400`）

**`.env` 檔案範例：**
```
QUICKCHART_HOST=127.0.0.1
QUICKCHART_PORT=3400
QUICKCHART_EXTERNAL_URL=http://127.0.0.1:3400
```

## 運行伺服器

要啟動伺服器，請運行 `server.py` 腳本：

```bash
python src/lcp_chart_mcp/server.py
```

伺服器將啟動並根據 `FastMCP` 框架中的配置監聽請求。

## 可用工具 (API)

伺服器公開了以下工具，可以透過 MCP 介面呼叫：

-   `create_chart_url`：創建圖表的核心功能。它可用於各種圖表類型，如 `bar`、`line`、`pie` 等。
-   `create_comparison_chart_url`：一個輔助工具，用於創建具有多個系列的圖表（例如，比較不同組的長條圖）。
-   `create_mixed_bar_line_url`：創建結合長條圖和折線圖的圖表。
-   `create_pie_outlabels_url`：使用 `outlabels` 插件創建帶有外部標籤的甜甜圈圖。
-   `create_progress_circle_url`：生成一個徑向儀表圖，看起來像一個進度圓圈，中心顯示百分比。
-   `create_radar_chart_url`：創建雷達圖（或蜘蛛網圖）以比較多維數據。
-   `create_qr_url`：從給定文本生成 QR Code 影像。