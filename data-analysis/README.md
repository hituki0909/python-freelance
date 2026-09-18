# 売上データ分析ツール

Pythonとpandasを使用して、CSV形式の売上データを分析するツールです。

商品別売上や月別売上を集計し、分析結果をCSVファイルとグラフ画像として出力します。

## 主な機能

- CSVファイルの読み込み
- 必要な列のチェック
- 日付データの変換
- 売上金額の自動計算
- 総売上の計算
- 商品別売上の集計
- 売上トップ商品の取得
- 月別売上の集計
- 売上トップ月の取得
- 分析結果のCSV保存
- 月別売上グラフの作成
- エラー処理

## 使用技術

- Python
- pandas
- Matplotlib
- pathlib
- Git
- GitHub

## フォルダ構成

```text
data-analysis/
├── analysis.py
├── sales.csv
├── README.md
└── output/
    ├── monthly_sales.png
    ├── monthly_sales.csv
    └── product_sales.csv