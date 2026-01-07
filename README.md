名言佳句管理系統 (114Scripting期末考)

📂 專案組成架構

本系統由以下核心模組組成：

pacho.py (資料爬蟲): 利用 Selenium 模擬瀏覽器抓取動態網頁，並自動初始化 SQLite 資料庫。

api.py (FastAPI): 基於 FastAPI 提供完整的 CRUD 介面，負責與資料庫進行資料互動。

gui.py (Tkinter介面): 使用 Tkinter 實作多執行緒 UI，確保在進行網路連線時介面仍保持流暢。

quotes.db (資料庫檔案): 儲存所有名言與作者資訊的 SQLite 資料庫。

🛠️ 環境需求與安裝

請確保您的系統已安裝 Python 3.12+，並依序執行以下步驟：

1. 安裝必要套件

在終端機執行以下指令：

```bash
pip install -r requirements.txt
```

🚀 執行步驟指南

請務必按照下列順序啟動系統，以確保資料鏈結正確：

1. 初始化資料 (執行爬蟲)

執行此指令會啟動背景瀏覽器抓取約 50 筆名言，並產生 quotes.db。

```bash
python pacho.py
```

2. 啟動 API 伺服器

執行此指令啟動後端，API 預設運行於 http://127.0.0.1:8000。

注意： GUI 執行期間，此視窗必須保持開啟。

```bash
uvicorn api:app --reload
```

3. 開啟管理系統介面 (GUI)

最後執行此指令開啟管理視窗。

```bash
python gui.py
```

📊 成果展示
1. API Swagger 互動式文件
FastAPI 提供自動化的 Swagger UI，方便開發者測試各種 API 接口。

存取位址：http://127.0.0.1:8000/docs

<img width="1888" height="854" alt="API Swagger 截圖" src="https://github.com/user-attachments/assets/2f8fcf45-99fe-4211-bd41-f64c3784fc35" />

<img width="993" height="845" alt="GUI 運作截圖" src="https://github.com/user-attachments/assets/403e10bd-c696-4faa-b4f0-59205318de0f" />