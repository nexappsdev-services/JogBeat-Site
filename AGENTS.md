# JogBeat-Site 維護說明(給負責網站的 agent)

這是「跑拍 / Jogbeat」iOS App 的公開支援網站,GitHub Pages 從 `main` 分支根目錄發布:
https://nexappsdev-services.github.io/JogBeat-Site/

**這個 repo 是公開的,推上去的內容任何人都看得到。** 每次 push 前先把改動摘要給 PM(SG PM)確認。

## 網站內容
- 四種語言:`zh-Hant`、`zh-Hans`、`en`、`ja`。每種語言三頁:首頁 `<lang>/`、支援 `<lang>/support/`、隱私權政策 `<lang>/privacy/`。
- 根目錄的 `index.html`、`privacy/`、`support/` 依瀏覽器語言跳轉到對應語言。
- App 內與 App Store Connect 已經寫死這些網址,**不要改路徑或刪頁面**:
  - `https://nexappsdev-services.github.io/JogBeat-Site/<lang>/privacy/`(App 的「線上版本」連結、App Store 隱私權政策網址)
  - `https://nexappsdev-services.github.io/JogBeat-Site/<lang>/support/`(App Store 客服網址)
- 客服頁必須一直有可用的聯絡方式(Apple 審核規則 1.5):nexapps.dev@gmail.com。

## 怎麼改
- 頁面是 `tools/build.py` 產生的靜態 HTML,不要手改輸出的 HTML。
  - 首頁與支援頁文字:`tools/content.py`(四種語言要一起改,意思一致)。
  - 隱私權政策原文:App repo `edward-cb-chang/superjogging-app` 的 `docs/legal/privacy-policy.<lang>.md`。**政策內容只能改 App repo 那份**,由 PM 合併後再同步到這裡;這裡不自行改寫政策。
- 重新產生:把四份 `privacy.<lang>.md` 和 `icon-1024.png`(App repo `Assets/Assets.xcassets/AppIcon.appiconset/icon-1024.png`)放進一個資料夾,執行 `python3 -I tools/build.py <該資料夾> <輸出資料夾>`,再把輸出複製到 repo 根目錄(保留 `tools/`、`README.md`、`AGENTS.md`)。
- 常見問題裡提到的 App 操作路徑與按鈕名稱,要和 App 裡實際的文字一致(App repo `iOS/Localizable.xcstrings`)。
- 不加追蹤、分析或第三方腳本(隱私權政策寫明沒有),不載入外部字型。

## 版面與素材
- 首頁插畫 `tools/assets-src/hero.webp`(Codex 依設計稿畫的乾淨插畫:白底、無文字、左側淡出已畫進圖裡;要換圖時保持白底);App 畫面 `tools/assets-src/shots/<lang>/{1,2,4}.webp` 來自 App repo 的 App Store 截圖(每張 ≤ 200KB)。`build.py` 會把它們複製到 `assets/`。
- 上架後把 `tools/content.py` 的 `APP_STORE_ID` 填上數字:「即將上架」會換成下載連結,每頁加上 Safari 智慧橫幅。官方徽章要另外下載 SVG 放進 `assets/`(使用者同意後),位置在 `build.py` 的註解處。
- 隱私權政策頁的目錄、手機版表格卡片只是呈現方式;改完後要確認去掉標籤後的政策純文字與改之前一致。

## 發布後檢查
push 後等 1–2 分鐘,確認下列網址都回 200,並實際打開看版面:
根目錄、`privacy/`、`support/`,以及四種語言的首頁、`privacy/`、`support/`、`assets/style.css`。

## 待辦(PM 會另外通知)
- App 上架後:把首頁的「即將在 App Store 上架」換成 App Store 連結與官方徽章。
- 視需要加 `app-ads.txt`:它必須放在網域根目錄,需要另一個名為 `nexappsdev-services.github.io` 的 repo,由使用者決定是否建立。
