import os
from datetime import datetime

def write_log():
    log_path = f"\\\\vasilypc\Vasily Shared (Full Access)\###\BVLog\BVLOG.txt"

    if not os.path.exists(log_path):
        with open(log_path, 'w') as file:
            file.write("")
        file.close()

    log_file = open(log_path, 'a')

    now_date_time = datetime.today().strftime("%d.%m.%Y %H:%M:%S")
    username = os.getlogin()

    log_file.write(f'{now_date_time}\t{username}\t\n')
    log_file.close()

if __name__ == '__main__':
    write_log()
