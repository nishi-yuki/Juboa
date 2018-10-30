#! /usr/bin/env python3
#############################################################
#                  充電しすぎを防ぐアプリ                   #
#                          Juboa                            #
# バッテリの過放電と過充電を警告するスクリプトです。crontab #
# コマンドを使用して定期的に実行するよう設定してください。  #
#############################################################

import subprocess

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

def send_alart(massage):
    subprocess.call([
        "notify-send",
        "-a", "BATNOTYFY",
        "-u", "critical",
        massage,
    ])

def send_warning_dialog(massage):
    subprocess.call([
        "zenity",
        "--title=充電池通知",
        "--warning",
        "--no-wrap",
        "--text={}".format(massage),
    ])

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
    if   result == "yes":
        return True
    elif result == "no":
        return False
    else:
        raise UnkownValueError("'online:'の結果がyes, no以外です")

def get_battery_percentage(battery_path):
    resrult = get_value(get_upower_result(battery_path), "percentage:")
    battery_percentage = int(resrult.stlip("%"))
    return battery_percentage
