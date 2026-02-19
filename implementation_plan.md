# 專案計畫書：AI 摩擦學診斷及模擬專家 (Web-based SDA Simulator)

## 1. 專案目標
開發一個整合「歷史診斷」與「未來模擬」的 Web 平台，針對二行程主機 SDA 殘油進行分析。使用者可視化磨損趨勢，並透過「控制桿聯動模擬」預測調整運作參數對磨損的影響。

## 2. 核心分析維度升級

### A. 關鍵監控指標 (Key Indicators)
*   **Total Iron Content (Fe)**: 總磨損指標。
*   **PQ-Index**: 磁性顆粒大小監控。
*   **Residual BN (殘留鹼值)**: 中和能力監控。
*   **Chromium (Cr)**: **[新增]** 專門監控活塞環塗層 (Piston Ring Coating) 的磨損。

### B. 聯動模擬因子 (Simulation Controls)
介面將提供滑動桿 (Sliders)，模擬以下變動對磨損曲線的影響：
*   **Engine Load**: 負荷變化。
*   **Fuel Sulfur content**: 燃油硫份變化（直接影響酸腐蝕風險）。
*   **Cylinder Oil Feed Rate**: 注油率調整（直接影響油膜強度與鹼量供給）。
*   **Cylinder Oil BN Choice**: 潤滑油鹼值級別切換。

## 3. 網站介面與功能設計 (Website Interface)

### A. 數據視覺化中心 (Trending Chart)
*   **橫軸 (X-axis)**: 時間序列。
*   **縱軸 (Y-axis)**: 磨損元素濃度 (ppm) 或 PQ 值。
*   **臨界線 (Limit Lines)**: 基於廠家 (WinGD/MAN) 基準線的 Warning 與 Critical 警戒線。
*   **雙曲線對照**:
    *   **真實曲線 (Solid Line)**: 基於 Excel 導入的真實化驗數據。
    *   **模擬曲線 (Dashed Line)**: 當使用者調整「控制桿」時，系統根據數學模型生成的預測磨損路徑。

### B. 自動警訊 (Smart Alerts)
*   當真實曲線接近或突破臨界線時，系統自動跳出紅/黃色警告，並提供「應對建議」文字。

## 4. 模擬技術邏輯
*   **靜態對比分析**: 基於歷史數據建立該主機的磨損回歸模型。
*   **靈敏度係數**: 定義 $Wear \approx f(Load, Sulfur, FeedRate, BN)$ 的影響係數（依據領域專業知識設定）。

## 5. MVP 開發時程

### 第一階段：數據與算法 (Week 1)
*   [ ] 定義 Excel 格式並實作 JSON 解析。
*   [ ] 建立包含 Cr 的完整數據結構與基準線 CONFIG。

### 第二階段：前端視圖開發 (Week 2)
*   [ ] 使用 Chart.js / D3.js 繪製趨勢圖與臨界線。
*   [ ] 實現 Slider 聯動邏輯與「模擬曲線」計算。

### 第三階段：UI/UX 優化 (Week 3)
*   [ ] 設計直觀的診斷儀表板。
*   [ ] 部署至 Web 環境供快速訪問。

---

## 6. 使用者確認事項
> [!IMPORTANT]
> 1. 原有的歷史數據 Excel 中，是否有 Cr 這一欄位？
> 2. 模擬曲線的「權重」是否有參考依據？（例如：當硫份增加 1%，Fe 預期上升多少 ppm？）
