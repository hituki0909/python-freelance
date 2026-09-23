# ============================================
# セキュリティログ解析ツール
# ============================================

from pathlib import Path
from datetime import datetime
import argparse
import csv

import matplotlib.pyplot as plt


# ============================================
# 1. 基本設定
# ============================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"

ALERT_FILE = OUTPUT_DIR / "alerts.csv"

SUMMARY_FILE = OUTPUT_DIR / "log_summary.csv"

GRAPH_FILE = OUTPUT_DIR / "log_levels.png"


# 何秒以内を短時間とするか
TIME_WINDOW = 60


# 何回以上で要確認とするか
ALERT_THRESHOLD = 3


# ============================================
# 2. コマンドライン引数
# ============================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "セキュリティログを解析して、"
            "ログレベルとログイン失敗を"
            "調査します。"
        )
    )

    parser.add_argument(
        "logfile",
        help="解析するログファイル"
    )

    return parser.parse_args()


# ============================================
# 3. ログファイルのパスを作る
# ============================================

def resolve_log_file(logfile):

    log_file = Path(logfile)

    # 絶対パスでない場合
    if not log_file.is_absolute():

        log_file = (
            BASE_DIR / log_file
        )

    return log_file


# ============================================
# 4. ログを解析する
# ============================================

def analyze_log(log_file):

    # -----------------------------
    # ログレベル
    # -----------------------------

    info_count = 0

    warning_count = 0

    error_count = 0


    # -----------------------------
    # ログイン失敗情報
    # -----------------------------

    failed_logins = {}

    failed_login_times = {}


    # -----------------------------
    # ファイルを読み込む
    # -----------------------------

    try:

        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()


                # 空行を無視
                if not line:

                    continue


                # =========================
                # ログレベル集計
                # =========================

                if "INFO" in line:

                    info_count += 1


                elif "WARNING" in line:

                    warning_count += 1


                elif "ERROR" in line:

                    error_count += 1


                # =========================
                # ログイン失敗
                # =========================

                if (
                    "Login failed" in line
                    and "user=" in line
                ):

                    # ユーザー名
                    username = (
                        line
                        .split("user=")[1]
                        .strip()
                    )


                    # 日時
                    time_text = line[:19]


                    # =====================
                    # datetime変換
                    # =====================

                    try:

                        log_time = (
                            datetime.strptime(
                                time_text,
                                "%Y-%m-%d %H:%M:%S"
                            )
                        )


                    except ValueError:

                        print(
                            "\n日時形式を"
                            "読み取れないログを"
                            "スキップしました:"
                        )

                        print(line)

                        continue


                    # =====================
                    # 失敗回数
                    # =====================

                    if (
                        username
                        in failed_logins
                    ):

                        failed_logins[
                            username
                        ] += 1


                    else:

                        failed_logins[
                            username
                        ] = 1


                    # =====================
                    # 失敗時刻
                    # =====================

                    if (
                        username
                        in failed_login_times
                    ):

                        failed_login_times[
                            username
                        ].append(
                            log_time
                        )


                    else:

                        failed_login_times[
                            username
                        ] = [
                            log_time
                        ]


    except FileNotFoundError:

        print(
            "\n=============================="
        )

        print("エラー")

        print(
            "=============================="
        )

        print(
            "ログファイルが"
            "見つかりません。"
        )

        print(
            f"確認した場所: {log_file}"
        )

        raise SystemExit


    # -----------------------------
    # 合計
    # -----------------------------

    total_count = (
        info_count
        + warning_count
        + error_count
    )


    # -----------------------------
    # 結果をまとめる
    # -----------------------------

    log_counts = {
        "INFO": info_count,
        "WARNING": warning_count,
        "ERROR": error_count,
        "TOTAL": total_count
    }


    return (
        log_counts,
        failed_logins,
        failed_login_times
    )


# ============================================
# 5. 短時間ログイン失敗を検出
# ============================================

def detect_alerts(
    failed_login_times
):

    alerts = []


    for username, times in (
        failed_login_times.items()
    ):

        # 時刻順に並べる
        times.sort()


        # 必要な回数に達していない
        if (
            len(times)
            < ALERT_THRESHOLD
        ):

            continue


        # =============================
        # スライディングウィンドウ
        # =============================

        for start in range(
            len(times)
            - ALERT_THRESHOLD
            + 1
        ):

            first_time = (
                times[start]
            )


            last_time = (
                times[
                    start
                    + ALERT_THRESHOLD
                    - 1
                ]
            )


            difference = (
                last_time
                - first_time
            )


            seconds = (
                difference
                .total_seconds()
            )


            # =========================
            # 警告条件
            # =========================

            if seconds <= TIME_WINDOW:

                alerts.append(
                    [
                        username,
                        ALERT_THRESHOLD,
                        int(seconds)
                    ]
                )

                # 同じユーザーは
                # 1回だけ警告
                break


    return alerts


# ============================================
# 6. 解析結果を表示
# ============================================

def display_results(
    log_file,
    log_counts,
    failed_logins,
    alerts
):

    print(
        "\n=============================="
    )

    print("ログ解析結果")

    print(
        "=============================="
    )


    print(
        f"解析ファイル: {log_file}"
    )

    print(
        f"INFO    : "
        f"{log_counts['INFO']}件"
    )

    print(
        f"WARNING : "
        f"{log_counts['WARNING']}件"
    )

    print(
        f"ERROR   : "
        f"{log_counts['ERROR']}件"
    )

    print(
        f"合計    : "
        f"{log_counts['TOTAL']}件"
    )


    # ========================================
    # ログイン失敗
    # ========================================

    print(
        "\n=============================="
    )

    print("ログイン失敗")

    print(
        "=============================="
    )


    if failed_logins:

        for username, count in (
            failed_logins.items()
        ):

            print(
                f"{username} : {count}回"
            )


    else:

        print(
            "ログイン失敗はありません。"
        )


    # ========================================
    # 警告
    # ========================================

    print(
        "\n=============================="
    )

    print(
        "短時間ログイン失敗チェック"
    )

    print(
        "=============================="
    )


    if alerts:

        for alert in alerts:

            username = alert[0]

            failures = alert[1]

            seconds = alert[2]


            print(
                f"⚠ {username} : "
                f"{seconds}秒以内に"
                f"{failures}回"
                f"ログイン失敗"
            )


    else:

        print(
            "短時間に集中した"
            "ログイン失敗はありません。"
        )


# ============================================
# 7. alerts.csv を保存
# ============================================

def save_alerts(alerts):

    with open(
        ALERT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(
            file
        )


        writer.writerow(
            [
                "username",
                "failures",
                "seconds"
            ]
        )


        writer.writerows(
            alerts
        )


# ============================================
# 8. log_summary.csv を保存
# ============================================

def save_summary(log_counts):

    with open(
        SUMMARY_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(
            file
        )


        writer.writerow(
            [
                "level",
                "count"
            ]
        )


        writer.writerow(
            [
                "INFO",
                log_counts["INFO"]
            ]
        )


        writer.writerow(
            [
                "WARNING",
                log_counts["WARNING"]
            ]
        )


        writer.writerow(
            [
                "ERROR",
                log_counts["ERROR"]
            ]
        )


        writer.writerow(
            [
                "TOTAL",
                log_counts["TOTAL"]
            ]
        )


# ============================================
# 9. グラフを作成
# ============================================

def create_chart(log_counts):

    levels = [
        "INFO",
        "WARNING",
        "ERROR"
    ]


    counts = [
        log_counts["INFO"],
        log_counts["WARNING"],
        log_counts["ERROR"]
    ]


    # グラフサイズ
    plt.figure(
        figsize=(8, 5)
    )


    # 棒グラフ
    bars = plt.bar(
        levels,
        counts
    )


    # タイトル
    plt.title(
        "Security Log Levels"
    )


    # 横軸
    plt.xlabel(
        "Log Level"
    )


    # 縦軸
    plt.ylabel(
        "Count"
    )


    # ========================================
    # 棒の上に件数を表示
    # ========================================

    for bar in bars:

        height = (
            bar.get_height()
        )


        plt.text(
            bar.get_x()
            + bar.get_width() / 2,

            height,

            str(
                int(height)
            ),

            ha="center",

            va="bottom"
        )


    # レイアウト調整
    plt.tight_layout()


    # PNG保存
    plt.savefig(
        GRAPH_FILE
    )


    # グラフを閉じる
    plt.close()


# ============================================
# 10. main関数
# ============================================

def main():

    # outputフォルダ作成
    OUTPUT_DIR.mkdir(
        exist_ok=True
    )


    # コマンドライン引数
    args = parse_arguments()


    # ログファイルのパス
    log_file = resolve_log_file(
        args.logfile
    )


    # ログ解析
    (
        log_counts,
        failed_logins,
        failed_login_times
    ) = analyze_log(
        log_file
    )


    # 警告検出
    alerts = detect_alerts(
        failed_login_times
    )


    # 結果表示
    display_results(
        log_file,
        log_counts,
        failed_logins,
        alerts
    )


    # CSV保存
    save_alerts(
        alerts
    )


    save_summary(
        log_counts
    )


    # グラフ作成
    create_chart(
        log_counts
    )


    # ========================================
    # 保存結果
    # ========================================

    print(
        "\n=============================="
    )

    print("ファイル保存完了")

    print(
        "=============================="
    )


    print(
        f"警告結果: {ALERT_FILE}"
    )

    print(
        f"ログ集計: {SUMMARY_FILE}"
    )

    print(
        f"グラフ: {GRAPH_FILE}"
    )


    print(
        "\n=============================="
    )

    print("ログ解析完了")

    print(
        "=============================="
    )


# ============================================
# 11. プログラム開始地点
# ============================================

if __name__ == "__main__":

    main()