from setuptools import setup, find_packages
import os

# Найдем ВСЕ файлы проекта
def find_all_files():
    file_list = []
    for root, dirs, files in os.walk('.'):
        # Исключаем системные папки
        if any(x in root for x in ['__pycache__', 'myenv', 'dist', 'build', '.git']):
            continue
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.md', '.txt')):
                full_path = os.path.join(root, file)
                file_list.append(full_path)
    return file_list

setup(
    name="django-imageskit-plus",
    version="2.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': find_all_files(),
    },
    install_requires=[
        "Django>=4.0",
        "Pillow>=9.0",
    ],
    entry_points={
        'console_scripts': [
            'run-coffee-project = manage:main',
        ],
    },
)