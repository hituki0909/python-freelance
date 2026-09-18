# ============================================
# 売上データ分析ツール
# ============================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================
# 1. ファイル・フォルダ設定
# ============================================

# analysis.py があるフォルダを取得
BASE_DIR = Path(__file__).resolve().parent

# 入力CSVファイル
CSV_FILE = BASE_DIR / "sales.csv"

# 出力フォルダ
OUTPUT_DIR = BASE_DIR / "output"

# outputフォルダがなければ自動作成
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================
# 2. CSVを読み込む関数
# ============================================

def load_data(csv_file):
    """CSVファイルを読み込む"""

    try:
        df = pd.read_csv(csv_file)

        return df

    except FileNotFoundError:
        print("エラー: sales.csv が見つかりません。")
        print(f"確認する場所: {csv_file}")
        return None

    except pd.errors.EmptyDataError:
        print("エラー: sales.csv の中身が空です。")
        return None

    except pd.errors.ParserError:
        print("エラー: sales.csv の形式を確認してください。")
        return None


# ============================================
# 3. 必要な列を確認する関数
# ============================================

def validate_columns(df):
    """CSVに必要な列があるか確認する"""

    required_columns = [
        "date",
        "product",
        "category",
        "price",
        "quantity"
    ]

    for column in required_columns:

        if column not in df.columns:
            print(
                f"エラー: 必要な列 '{column}' がありません。"
            )

            return False

    return True


# ============================================
# 4. データを加工する関数
# ============================================

def prepare_data(df):
    """日付・数値を変換してsales列を作成する"""

    try:
        # 日付へ変換
        df["date"] = pd.to_datetime(
            df["date"]
        )

        # 数値へ変換
        df["price"] = pd.to_numeric(
            df["price"]
        )

        df["quantity"] = pd.to_numeric(
            df["quantity"]
        )

    except (ValueError, TypeError):
        print(
            "エラー: CSVのデータ形式を確認してください。"
        )

        return None

    # 売上 = 価格 × 数量
    df["sales"] = (
        df["price"] * df["quantity"]
    )

    # 年月列を作成
    df["month"] = (
        df["date"]
        .dt
        .to_period("M")
    )

    return df


# ============================================
# 5. 売上を分析する関数
# ============================================

def analyze_sales(df):
    """総売上・商品別売上・月別売上を計算する"""

    # 総売上
    total_sales = df["sales"].sum()

    # 商品別売上
    product_sales = (
        df
        .groupby("product")["sales"]
        .sum()
    )

    # 月別売上
    monthly_sales = (
        df
        .groupby("month")["sales"]
        .sum()
    )

    return (
        total_sales,
        product_sales,
        monthly_sales
    )


# ============================================
# 6. 分析結果を表示する関数
# ============================================

def display_results(
    df,
    total_sales,
    product_sales,
    monthly_sales
):
    """分析結果を画面に表示する"""

    print("\n==============================")
    print("売上データ")
    print("==============================")

    print(df)


    # --------------------------
    # 総売上
    # --------------------------

    print("\n==============================")
    print("総売上")
    print("==============================")

    print(f"{total_sales:,}円")


    # --------------------------
    # 商品別売上
    # --------------------------

    print("\n==============================")
    print("商品別売上")
    print("==============================")

    print(product_sales)


    # --------------------------
    # 売上トップ商品
    # --------------------------

    top_product = product_sales.idxmax()

    top_sales = product_sales.max()

    print("\n==============================")
    print("売上トップ商品")
    print("==============================")

    print(f"商品名: {top_product}")

    print(
        f"売上金額: {top_sales:,}円"
    )


    # --------------------------
    # 月別売上
    # --------------------------

    print("\n==============================")
    print("月別売上")
    print("==============================")

    print(monthly_sales)


    # --------------------------
    # 売上トップ月
    # --------------------------

    top_month = monthly_sales.idxmax()

    top_month_sales = monthly_sales.max()

    print("\n==============================")
    print("売上が最も高い月")
    print("==============================")

    print(f"年月: {top_month}")

    print(
        f"月間売上: {top_month_sales:,}円"
    )


# ============================================
# 7. 分析結果をCSVとして保存する関数
# ============================================

def save_results(
    product_sales,
    monthly_sales
):
    """分析結果をCSVファイルとして保存する"""

    # 商品別売上CSV
    product_file = (
        OUTPUT_DIR / "product_sales.csv"
    )

    product_sales.to_csv(
        product_file,
        header=["sales"],
        encoding="utf-8-sig"
    )


    # 月別売上CSV
    monthly_file = (
        OUTPUT_DIR / "monthly_sales.csv"
    )

    monthly_sales.to_csv(
        monthly_file,
        header=["sales"],
        encoding="utf-8-sig"
    )


    print("\n==============================")
    print("CSV保存完了")
    print("==============================")

    print(f"保存先: {product_file}")

    print(f"保存先: {monthly_file}")


# ============================================
# 8. グラフを作成する関数
# ============================================

def create_chart(monthly_sales):
    """月別売上の棒グラフを作成する"""

    # 月を文字列へ変換
    months = (
        monthly_sales
        .index
        .astype(str)
    )


    # グラフサイズ
    plt.figure(
        figsize=(8, 5)
    )


    # 棒グラフ
    plt.bar(
        months,
        monthly_sales.values
    )


    # タイトル
    plt.title(
        "Monthly Sales"
    )


    # 横軸
    plt.xlabel(
        "Month"
    )


    # 縦軸
    plt.ylabel(
        "Sales"
    )


    # レイアウト調整
    plt.tight_layout()


    # グラフ保存先
    graph_file = (
        OUTPUT_DIR / "monthly_sales.png"
    )


    # PNG保存
    plt.savefig(
        graph_file
    )


    print("\n==============================")
    print("グラフ保存完了")
    print("==============================")

    print(
        f"保存先: {graph_file}"
    )


    # グラフ表示
    plt.show()


# ============================================
# 9. メイン処理
# ============================================

def main():
    """プログラム全体を実行する"""

    print("==============================")
    print("売上データ分析ツール")
    print("==============================")


    # --------------------------
    # CSV読み込み
    # --------------------------

    df = load_data(
        CSV_FILE
    )

    if df is None:
        return


    # --------------------------
    # 必要な列を確認
    # --------------------------

    if not validate_columns(df):
        return


    # --------------------------
    # データ加工
    # --------------------------

    df = prepare_data(df)

    if df is None:
        return


    # --------------------------
    # 売上分析
    # --------------------------

    (
        total_sales,
        product_sales,
        monthly_sales
    ) = analyze_sales(df)


    # --------------------------
    # 結果表示
    # --------------------------

    display_results(
        df,
        total_sales,
        product_sales,
        monthly_sales
    )


    # --------------------------
    # CSV保存
    # --------------------------

    save_results(
        product_sales,
        monthly_sales
    )


    # --------------------------
    # グラフ作成
    # --------------------------

    create_chart(
        monthly_sales
    )


    print("\n==============================")
    print("分析が完了しました。")
    print("==============================")


# ============================================
# 10. プログラム開始
# ============================================

if __name__ == "__main__":
    main()