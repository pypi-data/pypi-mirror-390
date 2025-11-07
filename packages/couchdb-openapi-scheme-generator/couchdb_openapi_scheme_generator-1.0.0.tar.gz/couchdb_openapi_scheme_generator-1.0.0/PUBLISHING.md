# 📦 Инструкции по публикации в PyPI и использованию через uvx

## 🎯 Цель

Опубликовать пакет `couchdb-openapi-scheme-generator` в PyPI, чтобы его можно было использовать через `uvx`:

```bash
uvx couchdb-openapi-scheme-generator --url http://localhost:5984
```

## 📋 Предварительные требования

1. **Аккаунт на PyPI**:
   - Создайте аккаунт на [pypi.org](https://pypi.org/account/register/)
   - Для тестирования создайте аккаунт на [test.pypi.org](https://test.pypi.org/account/register/)

2. **API токены**:
   - Перейдите в настройки аккаунта PyPI → API tokens
   - Создайте токен для публикации пакетов
   - Сохраните токен в безопасном месте

3. **Установите инструменты для публикации**:
   ```bash
   # Установите uv (если еще не установлен)
   # Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   # Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Установите build и twine через uv
   uv pip install build twine
   ```

## 🚀 Шаги публикации

### 1. Подготовка проекта

Убедитесь, что все файлы готовы:

```bash
# Проверьте, что pyproject.toml настроен правильно
cat pyproject.toml

# Убедитесь, что версия обновлена (если нужно)
# Отредактируйте version в pyproject.toml
```

### 2. Сборка пакета

```bash
# Соберите пакет (создаст папки dist/ и build/)
uv run python -m build

# Или используйте uv напрямую
uv build
```

Это создаст:
- `dist/couchdb-openapi-scheme-generator-1.0.0.tar.gz` (исходный код)
- `dist/couchdb_openapi_scheme_generator-1.0.0-py3-none-any.whl` (wheel)

### 3. Проверка пакета (опционально)

```bash
# Проверьте пакет на ошибки
uv run twine check dist/*

# Проверьте содержимое пакета
tar -tzf dist/couchdb-openapi-scheme-generator-1.0.0.tar.gz
```

### 4. Тестовая публикация (рекомендуется)

Сначала опубликуйте на Test PyPI:

```bash
# Загрузите на Test PyPI
uv run twine upload --repository testpypi dist/*

# Введите ваши учетные данные Test PyPI:
# Username: __token__
# Password: pypi-ваш-токен-для-test-pypi
```

Проверьте установку из Test PyPI:

```bash
# Установите из Test PyPI
uvx --index-url https://test.pypi.org/simple/ couchdb-openapi-scheme-generator --url http://localhost:5984
```

### 5. Публикация в PyPI

После успешного тестирования опубликуйте в основной PyPI:

```bash
# Загрузите на PyPI
uv run twine upload dist/*

# Введите ваши учетные данные PyPI:
# Username: __token__
# Password: pypi-ваш-токен-для-pypi
```

### 6. Проверка публикации

Проверьте, что пакет доступен:

```bash
# Проверьте на сайте PyPI
# https://pypi.org/project/couchdb-openapi-scheme-generator/

# Установите и используйте через uvx
uvx couchdb-openapi-scheme-generator --url http://localhost:5984
```

## 🔄 Обновление версии

При обновлении пакета:

1. **Обновите версию** в `pyproject.toml`:
   ```toml
   version = "1.0.1"  # или другая версия
   ```

2. **Соберите и опубликуйте**:
   ```bash
   uv build
   uv run twine upload dist/*
   ```

## 📝 Настройка автоматической публикации

Вы можете настроить автоматическую публикацию через GitHub Actions. Создайте файл `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: Build package
        run: uv build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

## 🐛 Решение проблем

### Ошибка: "Package already exists"

Если пакет с такой версией уже существует, обновите версию в `pyproject.toml`.

### Ошибка: "Invalid distribution"

Убедитесь, что:
- `pyproject.toml` правильно настроен
- Все необходимые файлы включены
- Нет синтаксических ошибок

### Команда не найдена после установки

Убедитесь, что:
- Entry point правильно настроен в `pyproject.toml`:
  ```toml
  [project.scripts]
  couchdb-openapi-scheme-generator = "openapi_generator:main"
  ```
- Функция `main()` существует в `openapi_generator.py`

## 📚 Дополнительные ресурсы

- [PyPI Documentation](https://packaging.python.org/en/latest/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Python Packaging Guide](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)

