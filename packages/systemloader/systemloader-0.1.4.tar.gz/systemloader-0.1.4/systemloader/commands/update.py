import os
import shutil
from pathlib import Path


def get_engine_path():
    """
    Получить путь к движку
    """
    current_dir = Path(__file__).parent
    template_path = current_dir.parent / 'core'
    return template_path


def copy_directory_contents(src, dst):
    # Проверяем, существует ли исходный каталог
    if not os.path.exists(src):
        raise ValueError(f"Источник {src} не существует!")

    # Создаем целевой каталог, если его нет
    os.makedirs(dst, exist_ok=True)

    # Рекурсивно копируем файлы и папки
    for item in os.listdir(src):
        if item == '__init__.py':
            continue
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)


def init_engine():
    copy_directory_contents(get_engine_path(), './')


def update_engine():
    src_path = os.path.join(get_engine_path(), 'system')
    dst_path = os.path.join('./', 'system')
    shutil.rmtree(dst_path, ignore_errors=True)
    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
