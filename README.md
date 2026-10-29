# 跑拍 Jogbeat — 支援網站

GitHub Pages 靜態網站：首頁、支援（客服與常見問題）、隱私權政策，四種語言（zh-Hant / zh-Hans / en / ja）。

- 隱私權政策原文在 App repo 的 `docs/legal/privacy-policy.<lang>.md`；首頁與支援頁文字在 `tools/content.py`。
- 重新產生：把四份政策 md（`privacy.<lang>.md`）和 `icon-1024.png` 放進一個資料夾，執行 `python3 tools/build.py <該資料夾> <輸出資料夾>`，再把輸出複製到 repo 根目錄（保留 `tools/` 與本檔）。
