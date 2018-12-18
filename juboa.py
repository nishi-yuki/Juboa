#! /usr/bin/env python3
##############################################################
#                  充電しすぎを防ぐアプリ                    #
#                          Juboa                             #
# バッテリの過放電と過充電を警告するスクリプトです。実行する #
# と常駐します。                                             #
##############################################################

import subprocess
import time
import os
import sys

UPPER_THRESHOLD = 80
LOWER_THRESHOLD = 30
SLEEP_SECS = 60
APP_NAME = "Juboa"
AC_ADAPTER_PATH = "/org/freedesktop/UPower/devices/line_power_AC0"
BATTERY_PATH_LIST = [
    "/org/freedesktop/UPower/devices/battery_BAT0",
]


class NoValueError(Exception):
    '''get_value関数がupowerコマンドの結果から目的の
    箇所を見つけられなかったときに投げられる例外'''
    pass


class UnkownValueError(Exception):
    '''upowerコマンドの結果が想定外の形だったときに投げられる例外'''
    pass


def send_alert(massage):
    subprocess.call([
        "notify-send",
        "--urgency=normal",
        APP_NAME,
        massage,
    ])


def send_warning_dialog(massage):
    subprocess.call([
        "zenity",
        "--title={}".format(APP_NAME),
        "--warning",
        "--no-wrap",
        "--text={}".format(massage),
    ])


def get_juboa_pid():
    filename = os.path.basename(__file__)
    try:
        output = subprocess.check_output([
            "pgrep",
            "--full",
            filename,
        ])
        pids = [int(p) for p in output.decode().split()]
        return pids
    except subprocess.CalledProcessError:
        return []


def get_upower_result(path):
    output = subprocess.check_output(["upower", "-i", path])
    return output.decode()


def get_value(command_output, key):
    output_words = command_output.split()
    for i, word in enumerate(output_words):
        if key in word:
            return output_words[i + 1]
    else:
        raise NoValueError("'" + key + "'が見つかりません")


def is_ac_adapter_online():
    result = get_value(get_upower_result(AC_ADAPTER_PATH), "online:")
    if result == "yes":
        return True
    elif result == "no":
        return False
    else:
        raise UnkownValueError("'online:'の結果がyes, no以外です")


def get_battery_percentage(battery_path):
    resrult = get_value(get_upower_result(battery_path), "percentage:")
    battery_percentage = int(resrult.strip("%"))
    return battery_percentage


def get_average_battery_percentage():
    sum_battery_percentage = 0
    for path in BATTERY_PATH_LIST:
        sum_battery_percentage += get_battery_percentage(path)
    average = sum_battery_percentage / len(BATTERY_PATH_LIST)
    return average


def is_battery_safe():
    abp = get_average_battery_percentage()
    rtn = LOWER_THRESHOLD < abp < UPPER_THRESHOLD
    return rtn


def is_overcharge():
    return get_average_battery_percentage() > UPPER_THRESHOLD


def is_overdischarge():
    return get_average_battery_percentage() < LOWER_THRESHOLD


def main_loop():
    while True:
        # 通知条件に合致したら通知を出す
        if is_overcharge() and is_ac_adapter_online():
            send_alert("過充電しています。電源コードを抜いてください。")
        time.sleep(SLEEP_SECS)


def main():
    # 多重起動防止処理
    my_pid = os.getpid()
    pids = get_juboa_pid()
    pids.remove(my_pid)
    if len(pids) > 0:  # プロセスがすでにある場合
        print("Juboaプロセスがすでに起動されています。")
        send_alert("Juboaプロセスがすでに起動されています。")
        for pid in pids:
            print("PID:", pid)
        sys.exit()  # -------------------------------->

    # バックグラウンドで常駐する
    try:
        pid = os.fork()
    except OSError:
        m = "Juboaプロセスの起動に失敗しました"
        print(m)
        send_alert(m)
    if pid > 0:
        m = "Juboaプロセスが起動しました。\nPID: {}".format(pid)
        print(m)
        send_alert(m)
        input("wait)")
        sys.exit(0)
    if pid == 0:
        main_loop()


if __name__ == '__main__':
    main()
