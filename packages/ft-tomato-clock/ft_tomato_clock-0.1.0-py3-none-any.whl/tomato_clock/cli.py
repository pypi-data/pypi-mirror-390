#!C:\Users\86199\AppData\Local\Programs\Python\Python312\python.exe
# -*- coding: utf-8 -*-

# ====== 🍅 Tomato Clock =======

import sys
import time
import datetime
import warnings
import os

# --- 屏蔽 pkg_resources 警告 ---
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources.*")

# --- 全局常量 ---
WORK_MINUTES = 25
BREAK_MINUTES = 5
LOG_FILE = 'tomato_log.txt'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def main():
    # 在 Windows 上启用 ANSI 颜色支持
    if sys.platform == 'win32':
        os.system('color')

    try:
        if len(sys.argv) <= 1:
            print(f'🍅 Tomato {WORK_MINUTES} minutes. {RED}Ctrl+C to Exit{RESET}')
            tomato(WORK_MINUTES, 'Good job, time for break.', session_type="work")
            print(f'🧊 Break {BREAK_MINUTES} minutes. {RED}Ctrl+C to Exit{RESET}')
            tomato(BREAK_MINUTES, 'Break ended.', session_type="break")

        elif sys.argv[1] == '-t':
            minutes = int(sys.argv[2]) if len(sys.argv) > 2 else WORK_MINUTES
            print(f'🍅 Tomato {minutes} minutes. {RED}Ctrl+C to Exit{RESET}')
            tomato(minutes, 'Good job, time for break.', session_type="work")

        elif sys.argv[1] == '-b':
            minutes = int(sys.argv[2]) if len(sys.argv) > 2 else BREAK_MINUTES
            print(f'🧊 Break {minutes} minutes. {RED}Ctrl+C to Exit{RESET}')
            tomato(minutes, 'Break ended.', session_type="break")

        elif sys.argv[1] == '-f':
            focus_mode()

        # --- 新增：-all 和 -clear ---
        elif sys.argv[1] == '-all':
            show_all_stats()

        elif sys.argv[1] == '-clear':
            clear_all_stats()
        # --- 结束 ---

        elif sys.argv[1] == '-h':
            help()

        else:
            help()

    except KeyboardInterrupt:
        print('\n🏳️ Timer cancelled.')
    except Exception as ex:
        print(ex)
        exit(1)


def tomato(minutes, notify_msg, session_type="work"):
    start_time = time.perf_counter()
    total_seconds_to_run = minutes * 60

    while True:
        diff_seconds = int(round(time.perf_counter() - start_time))
        left_seconds = total_seconds_to_run - diff_seconds
        if left_seconds <= 0:
            print('')
            break

        minutes_left = int(left_seconds / 60)
        seconds_left = int(left_seconds % 60)
        countdown = f'{minutes_left:02d}:{seconds_left:02d} ⏰'

        duration = min(minutes, 25)
        progressbar(diff_seconds, total_seconds_to_run, duration, countdown)
        time.sleep(1)

    notify_me(notify_msg, session_type)

    if session_type == "work":
        log_duration_and_stats(total_seconds_to_run)


def focus_mode():
    start_time = time.perf_counter()
    print(f'🍅 Unlimited Focus. {RED}Ctrl+C to Exit{RESET}')
    try:
        while True:
            diff_seconds = int(round(time.perf_counter() - start_time))

            minutes = int(diff_seconds / 60)
            seconds = int(diff_seconds % 60)
            countdown = f'{minutes:02d}:{seconds:02d} ⏰'

            print(f'\r{countdown}', end='')
            time.sleep(1)

    except KeyboardInterrupt:
        end_time = time.perf_counter()
        total_seconds = int(round(end_time - start_time))
        print(f'\n👍 Focus session ended.')

        if total_seconds > 60:
            log_duration_and_stats(total_seconds)
        else:
            print(f'{RED}Focus session too short (< 1 min), won\'t be logged.{RESET}')


# --- 新增：日志读写辅助函数 ---
def read_log_data():
    """读取日志文件并返回一个 {日期: 秒数} 的字典"""
    data = {}
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) == 2:
                        date_str, sec_str = parts
                        data[date_str] = int(sec_str)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[{RED}Log read error.{RESET}] {e}")
    return data


def write_log_data(data):
    """将 {日期: 秒数} 字典写回日志文件，按日期排序"""
    try:
        sorted_dates = sorted(data.keys())
        with open(LOG_FILE, 'w') as f:
            for date_str in sorted_dates:
                f.write(f'{date_str},{data[date_str]}\n')
    except Exception as e:
        print(f"[{RED}Log write error.{RESET}] {e}")


# --- 重构：统计与日志功能 (支持历史记录) ---
def log_duration_and_stats(seconds_to_add):
    today_str = datetime.date.today().isoformat()

    # 1. 读取 *所有* 旧数据
    all_data = read_log_data()

    # 2. 获取今天的当前总数 (如果不存在则为 0)
    current_total_seconds = all_data.get(today_str, 0)

    # 3. 计算新数据并更新
    new_total_seconds = current_total_seconds + seconds_to_add
    all_data[today_str] = new_total_seconds

    # 4. 将 *所有* 数据（包括历史）写回
    write_log_data(all_data)

    # 5. 打印 *今天* 的统计报告
    session_minutes = seconds_to_add / 60.0
    total_minutes_today = new_total_seconds / 60.0
    pomodoros_today = total_minutes_today / WORK_MINUTES

    print(f'{GREEN}===== 📊 {YELLOW}Stats{GREEN} ====={RESET}')
    print(f'This Session:  {session_minutes:.1f} min')
    print(f'Today Total:   {total_minutes_today:.1f} min')
    print(f'Equivalent to: {pomodoros_today:.1f} pomodoros 🍅')


# --- 重构结束 ---


def progressbar(curr, total, duration=10, extra=''):
    frac = curr / total
    filled = round(frac * duration)
    print('\r', '➡️' * filled + '--' * (duration - filled), '[{:.0%}]'.format(frac), extra, end='')


def notify_me(msg, session_type):
    print(msg)
    try:
        if sys.platform == 'win32':
            try:
                from plyer import notification
            except ImportError:
                print("\n[Info] Plyer library not installed, cannot send desktop notification.")
                print("Please run: pip install plyer")
                print('\a', end='')
                return
            try:
                if session_type == "work":
                    title = "🍅 Focus completed"
                else:
                    title = "🧊 Break ended"

                notification.notify(
                    title=title,
                    message=msg,
                    app_name="Pomodoro",
                    timeout=5
                )
            except Exception as e:
                print(f"\n[Notification Error] Plyer notification failed: {e}")
                print('\a', end='')

    except Exception as e:
        print(f"\n[Notification Error] Failed to send notification: {e}")
        pass


# --- 新增：显示所有历史统计 (-all) ---
def show_all_stats():
    all_data = read_log_data()

    if not all_data:
        print(f'{GREEN}No log data found. Start focusing!{RESET}')
        return

    try:
        first_date = min(all_data.keys())
        total_seconds_all_time = sum(all_data.values())

        total_minutes = total_seconds_all_time / 60.0
        total_pomodoros = total_minutes / WORK_MINUTES  # 总分钟 / 25

        print(f'{GREEN}====== 🍅 {BLUE}All-Time Stats{GREEN} ======{RESET}')
        print(f'First Record:    {first_date}')
        print(f'Total Days:      {len(all_data)} days')
        print(f'Total Time:      {total_minutes:.1f} min')
        print(f'Total Pomodoros: {total_pomodoros:.1f} 🍅')

    except Exception as e:
        print(f"[{RED}Error calculating stats.{RESET}] {e}")


# --- 新增：清除所有记录 (-clear) ---
def clear_all_stats():
    if not os.path.exists(LOG_FILE):
        print(f'{GREEN}Log file ({LOG_FILE}) does not exist. Nothing to clear.{RESET}')
        return

    try:
        # 安全确认
        print(f'{RED}WARNING:{RESET} This will permanently delete all your stats from {LOG_FILE}.')
        choice = input(f'Are you sure you want to proceed? (y/N) ')

        if choice.lower() == 'y':
            os.remove(LOG_FILE)
            print(f'{GREEN}All stats cleared.{RESET}')
        else:
            print('Operation cancelled.')
    except Exception as e:
        print(f"[{RED}Error clearing file.{RESET}] {e}")


# --- 修改：help 函数 ---
def help():
    appname = sys.argv[0]
    appname = appname if appname.endswith('.py') else 'tomato'
    print(f'{GREEN}====== 🍅 {RED}Tomato Clock{GREEN} ======={RESET}')
    print(f'{appname}           # Start {WORK_MINUTES}-min focus + {BREAK_MINUTES}-min break')
    print(f'{appname} -t        # Start {WORK_MINUTES}-min focus')
    print(f'{appname} -t <n>    # Start <n>-min focus')
    print(f'{appname} -b        # Start {BREAK_MINUTES}-min break')
    print(f'{appname} -b <n>    # Start <n>-min break')
    print(f'{appname} -f        # Start unlimited focus (Ctrl+C to Exit)')
    print(f'{appname} -all      # {GREEN}Show all-time total stats{RESET}')
    print(f'{appname} -clear    # {RED}Clear all log data{RESET}')
    print(f'{appname} -h        # Show help')


if __name__ == "__main__":
    main()