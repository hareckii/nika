#!/usr/bin/env python3
import subprocess
import sys


def launch_application(app_name):
    """
    Запускает приложение по имени
    """
    try:
        # Пробуем запустить приложение
        result = subprocess.run([app_name], check=True)
        print(f"Приложение {app_name} успешно запущено")
        return True
    except FileNotFoundError:
        print(f"Ошибка: Приложение '{app_name}' не найдено")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске приложения: {e}")
        return False


if __name__ == "__main__":
    # Укажите здесь имя приложения, которое хотите запустить
    application_name = "spotify"  # Замените на нужное приложение

    if len(sys.argv) > 1:
        application_name = sys.argv[1]

    launch_application(application_name)
