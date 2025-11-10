# 📌🇷🇺 Русская версия

---

## Набор компонентов Python для упрощения разработки приложений

**ANB Python Components** — это библиотека полезных классов и модулей, предназначенная для ускорения процесса разработки
программного обеспечения на языке программирования Python. Библиотека включает широкий спектр инструментов, облегчающих
выполнение повседневных задач разработчика, от обработки файлов и сетевых запросов до автоматизации тестирования и
интеграции с популярными фреймворками.

### ✅ Основные возможности:

- Удобные инструменты для работы с файлами и каталогами.
- Классы для работы с файлами и директориями.
- Классы для удобной передачи состояния.
- Новые
  типы [GUID](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Fguid.md),
  [TwoDimSize](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Ftwo_dim_size.md), [VersionInfo](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Fversion_info.md), [ShortCodeAttributes](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Fshortcode_attributes.md)
  и [ObjectArray](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Fobject_array.md).
- Расширение массивов, типа `bool`, типа `GUID`, типа `str`.
- Класс для перевода любого типа в строку и наоборот.

### ⚙️ Установка и использование:

Установить пакет можно через pip:

```bash
pip install anb-python-components
```

Подключайте необходимые модули и начните пользоваться ими прямо сейчас:

```python
from anb_python_components import TwoDimSize

# Пример использования
two_dim = TwoDimSize.parse('100x150', 'x')

# Теперь присваиваем какому-либо объекту
some_object_width = two_dim.width
some_object_height = two_dim.height
```

### 🛠️ Поддерживаемые технологии:

- `Python` версии 3.14.0 и выше
- Совместима с большинством популярных веб-фреймворков и библиотек Python
- Оптимизирован для работы с большими объемами данных и высоконагруженными приложениями

### 💬 Вопросы и поддержка:

Для подробной справки обратитесь к руководству по библиотеке в разделе документации:

🔗 Справочное руководство → [Документация библиотеки](https://gitflic.ru/project/babaev-an/anb-python-components/wiki)

---

# 📌🇬🇧 English Version

---

## Python Component Collection for Streamlining Application Development

**ANB Python Components** is a collection of useful classes and modules specifically tailored to accelerate the process
of developing software using the Python programming language. It offers a broad spectrum of tools that simplify everyday
developer tasks, from file manipulation and network requests to test automation and seamless integration with widely
used frameworks.

### ✅ Main Features:

- Handy tools for working with files and directories.
- Classes for handling files and folders.
- Classes for convenient state transfer.
- New custom_types such
  as [GUID](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Fguid.md),
  [TwoDimSize](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Ftwo_dim_size.md), [VersionInfo](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Fversion_info.md), [ShortCodeAttributes](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Fshortcode_attributes.md)
  and [ObjectArray](https://gitflic.ru/project/babaev-an/anb-python-components/wiki/page?file=class_desc%2Fcustom_types%2Fobject_array.md).
- Extensions for arrays, `bool`, `GUID`, and `str` custom_types.
- Class for converting any type into string representation and vice versa.

### ⚙️ Installation and Usage:

You can install this package via pip:

```bash
pip install anb-python-components
```

Import required modules and start using them immediately:

```python
from anb_python_components import TwoDimSize

# Example usage
two_dim = TwoDimSize.parse('100x150', 'x')

# Now assign it to some object
some_object_width = two_dim.width
some_object_height = two_dim.height
```

### 🛠️ Supported Technologies:

- **Python**: version 3.14.0 or higher
- Compatibility with most popular Python web frameworks and libraries
- Optimized for performance with large-scale datasets and highly loaded applications

### 💬 Questions and Support:

For comprehensive guidance and support, consult the library's documentation section:

🔗 Reference Guide → [Library Documentation](https://gitflic.ru/project/babaev-an/anb-python-components/wiki) (in Russian
Only)