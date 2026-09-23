from pathlib import Path
from datetime import datetime


# ============================================
# ファイル設定
# ============================================

BASE_DIR = Path(__file__).resolve().parent

LOG_FILE = BASE_DIR / "sample.log"


# ============================================
# ログレベルのカウンター
# ============================================

info_count = 0
warning_count = 0
error_count = 0


# ============================================
# ログイン失敗情報
# ============================================

# ユーザーごとの失敗回数
failed_logins = {}

# ユーザーごとの失敗時刻
failed_login_times = {}


# ============================================
# ログファイルを読み込む
# ============================================

try:

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            # ----------------------------
            # ログレベルを集計
            # ----------------------------

            if "INFO" in line:
                info_count += 1

            elif "WARNING" in line:
                warning_count += 1

            elif "ERROR" in line:
                error_count += 1


            # ----------------------------
            # ログイン失敗を検出
            # ----------------------------

            if (
                "Login failed" in line
                and "user=" in line
            ):

                # ユーザー名を取得
                username = (
                    line
                    .split("user=")[1]
                    .strip()
                )


                # 日時部分を取得
                time_text = line[:19]


                # 文字列からdatetimeへ変換
                log_time = datetime.strptime(
                    time_text,
                    "%Y-%m-%d %H:%M:%S"
                )


                # ----------------------------
                # 失敗回数を保存
                # ----------------------------

                if username in failed_logins:

                    failed_logins[username] += 1

                else:

                    failed_logins[username] = 1


                # ----------------------------
                # 失敗時刻を保存
                # ----------------------------

                if username in failed_login_times:

                    failed_login_times[
                        username
                    ].append(log_time)

                else:

                    failed_login_times[
                        username
                    ] = [log_time]


except FileNotFoundError:

    print(
        f"エラー: ログファイルが見つかりません。\n"
        f"確認する場所: {LOG_FILE}"
    )

    exit()


# ============================================
# ログ解析結果
# ============================================

total_count = (
    info_count
    + warning_count
    + error_count
)


print("\n==============================")
print("ログ解析結果")
print("==============================")

print(f"INFO    : {info_count}件")
print(f"WARNING : {warning_count}件")
print(f"ERROR   : {error_count}件")
print(f"合計    : {total_count}件")


# ============================================
# ログイン失敗回数
# ============================================

print("\n==============================")
print("ログイン失敗")
print("==============================")


for username, count in failed_logins.items():

    print(
        f"{username} : {count}回"
    )


# ============================================
# 短時間のログイン失敗を検出
# ============================================

print("\n==============================")
print("短時間ログイン失敗チェック")
print("==============================")


# 何秒以内を見るか
TIME_WINDOW = 60

# 何回以上で要確認にするか
ALERT_THRESHOLD = 3


alert_found = False


for username, times in failed_login_times.items():

# ============================================
# 短時間のログイン失敗を検出
# ============================================

print("\n==============================")
print("短時間ログイン失敗チェック")
print("==============================")


# 何秒以内を見るか
TIME_WINDOW = 60

# 何回以上で要確認にするか
ALERT_THRESHOLD = 3


alert_found = False


for username, times in failed_login_times.items():

    # 時刻を古い順に並べる
    times.sort()


    # 3回以上失敗している場合
    if len(times) >= ALERT_THRESHOLD:

        # チェック開始位置を
        # 1つずつずらす
        for start in range(
            len(times) - ALERT_THRESHOLD + 1
        ):

            # 最初の時刻
            first_time = times[start]

            # 3回目の時刻
            last_time = times[
                start + ALERT_THRESHOLD - 1
            ]


            # 時間差を計算
            difference = (
                last_time - first_time
            )

            seconds = (
                difference.total_seconds()
            )


            # 60秒以内に3回以上なら要確認
            if seconds <= TIME_WINDOW:

                print(
                    f"⚠ {username} : "
                    f"{seconds:.0f}秒以内に"
                    f"{ALERT_THRESHOLD}回"
                    f"ログイン失敗"
                )

                alert_found = True

                # 同じユーザーを
                # 何度も表示しない
                break


if not alert_found:

    print(
        "短時間に集中した"
        "ログイン失敗はありません。"
    )