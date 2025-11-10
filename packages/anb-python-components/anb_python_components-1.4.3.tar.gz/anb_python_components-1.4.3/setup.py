from os import path

from setuptools import find_packages, setup

# Получаем текущую директорию
this_directory = path.abspath(path.dirname(__file__))

# Функция для чтения requirements.txt
def read_requirements () -> list[str]:
    """
    Читает файл requirements.txt и возвращает список зависимостей.
    :return: Список зависимостей.
    """
    # Путь к файлу requirements.txt в текущей директории
    requirements_path = path.join(this_directory, 'requirements.txt')
    
    # Проверяем, существует ли файл requirements.txt
    if not path.exists(requirements_path):
        # - если нет, возвращаем пустой список
        return []
    
    # Читаем файл requirements.txt
    with open(requirements_path, encoding = 'utf-8') as f:
        # - возвращаем список зависимостей, предварительно убрав пустые строки и комментарии
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Возвращаем список зависимостей
    return lines

def read_readme () -> str:
    """
    Получает содержимое файла README.md и возвращает его в виде строки.
    :return: Содержимое файла README.md.
    """
    # Задаём переменную для хранения содержимого файла README.md
    readme_content = ''
    
    # Открываем файл README.md
    with open(path.join(this_directory, 'README.md'), encoding = 'utf-8') as f:
        # - и читаем его содержимое
        readme_content = f.read()
    
    # Возвращаем содержимое файла README.md
    return readme_content

setup(
        name = 'anb_python_components',
        version = '1.4.3',
        description = 'Набор компонентов Python, которые упрощают разработку / A set of Python components that simplify development',
        long_description = read_readme(),
        long_description_content_type = 'text/markdown',
        author = 'Александр Бабаев',
        author_email = 'contact_with_us@babaev-an.ru',
        url = 'https://gitflic.ru/project/babaev-an/anb-python-components',
        packages = find_packages(),
        install_requires = read_requirements(),
        python_requires = '>=3.14.0',
        classifiers = [
                'Development Status :: 5 - Production/Stable',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Programming Language :: Python :: 3.14',
                'Operating System :: OS Independent',
                'Topic :: Software Development :: Libraries :: Python Modules',
                ],
        keywords = 'python components development utils',
        project_urls = {
                'Documentation': 'https://gitflic.ru/project/babaev-an/anb-python-components/wiki',
                'Source': 'https://gitflic.ru/project/babaev-an/anb-python-components',
                'Tracker': 'https://gitflic.ru/project/babaev-an/anb-python-components/issue?page=0',
                },
        zip_safe = False,
        )