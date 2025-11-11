# LLM Common

[AGENTS.md](AGENTS.md) промпт для подключения метрик в проект, там информация более подробная.

Общая библиотека для работы с LLM приложениями, включающая инструменты для мониторинга с Prometheus и HTTP клиенты с встроенным трекингом метрик.

Есть готовые дашборды для этих метрик. После интеграции в свой проект, вы увидите метрики на этих дашбордах.

Для фабрики микросервисов:
- [Дашборд](https://grafana.megafon.ru/d/IyOEiiCNk/gen-app-http-requests?orgId=45&refresh=10s&var-env=prod&var-app=All&var-app_type=All&var-__rate_interval=1m&refresh=30s) HTTP запросов
- [Дашборд](https://grafana.megafon.ru/d/gNWjqkCNk/gen-app-actions?var-env=prod&var-app=All&var-app_type=All&var-__rate_interval=1m&from=now-24h&to=now&orgId=45&refresh=30s) Actions (отслеживание секций кода)


Для llmgpu серверов (вос 28):
- [Дашборд](https://iti-grafana.megafon.ru/d/bex4zcp7vvzeod/gen-app-http-requests?folderUid=dea4zkv3i5d6oa&orgId=1&from=now-24h&to=now&timezone=browser&var-env=prod&var-app=$__all&var-__rate_interval=1m&var-adhoc=&refresh=30s&var-app_type=$__all) HTTP запросов
- [Дашборд](https://iti-grafana.megafon.ru/d/fex4zvl8arv28a/gen-app-actions?orgId=1&from=now-24h&to=now&timezone=Europe%2FMoscow&var-env=prod&var-app=$__all&var-prompt_name=$__all&var-__rate_interval=2m&var-adhoc=&refresh=10s&var-app_type=$__all) Actions (отслеживание секций кода)

## 🚀 Основные возможности

- **Prometheus мониторинг**: Полнофункциональная система метрик для HTTP запросов и действий приложения
- **HTTP клиенты**: Готовые к использованию HTTP клиенты для LLM и аутентификации с автоматическим трекингом
- **Декораторы и контекст-менеджеры**: Готовые примитивы для отслеживания
- **FastAPI интеграция**: Middleware для отслеживания http метрик и endpoint для экспорта метрик
- **Flask интеграция**: endpoint для экспорта метрик

## 📦 Установка

Python 3.11+

```python
pip install llm_common prometheus_client
```

```python
uv add llm_common prometheus_client
```

### Из исходного кода
```bash
git clone <repository-url>
cd llm_common
pip install -e .
```

### Для разработки
```bash
git clone <repository-url>
cd llm_common
pip install -e ".[dev]"
pre-commit install
```

## 🔧 Быстрый старт

```bash
pip install llm_common
```

### 1. Инициализация метрик

```python
from llm_common.prometheus import build_prometheus_metrics

# Инициализация системы мониторинга
metrics = build_prometheus_metrics(
    project_name="projectname",
    env="dev"  # dev, preprod, или prod
)
```

### 2. Использование HTTP клиентов

```python
from llm_common.clients.llm_http_client import LLMHttpClient
from langchain_openai import ChatOpenAI

# LLM клиент с OpenAI интеграцией и мониторингом
custom_aclient = LLMHttpClient(verify=False)

chat_model = ChatOpenAI(
    ...,
    http_async_client=custom_aclient,
)
```

```python
from llm_common.clients.auth_client import AuthHttpClient

async with AuthHttpClient() as client:
    response = await client.post("https://auth-service.com/api/check")
```

### 3. Трекинг действий

```python
from llm_common.prometheus import action_tracking, action_tracking_decorator

# Использование контекст-менеджера
with action_tracking("data_processing") as tracker:
    # Ваш код
    process_data()
    # Опционально: трекинг размера данных
    tracker.size(len(processed_data))

# Использование декоратора
@action_tracking_decorator("llm_request")
async def make_llm_request():
    # Ваш код
    return result
```

### 4. Интеграция с FastAPI

```python
from fastapi import FastAPI
from llm_common.prometheus import fastapi_tracking_middleware, fastapi_endpoint_for_prometheus

app = FastAPI()

# Добавление middleware для трекинга HTTP запросов
app.middleware("http")(fastapi_tracking_middleware)

# Endpoint для экспорта метрик Prometheus
app.get("/prometheus")(fastapi_endpoint_for_prometheus)
```

## 📖 API Документация

### HTTP Клиенты

#### LLMHttpClient
```python
class LLMHttpClient(HttpxClientWithMonitoring):
    """HTTP клиент для LLM запросов с автоматическим мониторингом"""
    name_for_monitoring = "llm"
```

#### AuthHttpClient
```python
class AuthHttpClient(HttpxClientWithMonitoring):
    """HTTP клиент для аутентификации с кастомной обработкой путей"""
    name_for_monitoring = "auth_api"
```

### Утилиты мониторинга

#### action_tracking(name: str)
Контекст-менеджер для отслеживания действий:
- Автоматически измеряет время выполнения
- Подсчитывает успешные и ошибочные выполнения
- Позволяет трекить размер обработанных данных

#### action_tracking_decorator(name: str)
Декоратор для функций и корутин, поддерживает все возможности `action_tracking`.

#### http_tracking(...)
Функция для ручного трекинга HTTP запросов с подробными параметрами.

## 🔍 Метрики и мониторинг

### Доступные метрики

Все метрики имеют префикс `genapp_`:

#### HTTP метрики:
- `genapp_http_requests_total` - Общее количество HTTP запросов
- `genapp_http_request_duration_sec` - Гистограмма времени выполнения
- `genapp_http_request_size_bytes` - Размер запросов/ответов

#### Метрики действий:
- `genapp_action_count_total` - Количество выполненных действий
- `genapp_action_duration_sec` - Время выполнения действий
- `genapp_action_size_total` - Размер обработанных данных

### Labels (теги)

Метрики содержат стандартные labels:
- `env` - Окружение (dev/preprod/prod)
- `app` - Название приложения
- `app_type` - Тип приложения (telegram_api, llm, app_api, etc.)
- `method` - HTTP метод
- `status` - Статус ответа/результата
- `resource` - Путь ресурса (очищенный от ID)

## 🛠️ Разработка

### Требования
- Python 3.11+
- httpx
- prometheus_client

### Инструменты разработки
- `ruff` - Линтер и форматтер
- `black` - Форматирование кода
- `pre-commit` - Хуки для проверки кода
- `vulture` - Поиск неиспользуемого кода

### Запуск линтеров
```bash
ruff check llm_common
ruff format llm_common
black llm_common
```

### Pre-commit хуки
```bash
pre-commit install
pre-commit run --all-files
```

## 📝 Примеры использования

### Полный пример FastAPI приложения

```python
from fastapi import FastAPI
from llm_common.prometheus import (
    build_prometheus_metrics,
    fastapi_tracking_middleware,
    fastapi_endpoint_for_prometheus,
    action_tracking_decorator
)

# Инициализация метрик
build_prometheus_metrics(project_name="my_llm_service", env="dev")

app = FastAPI()
app.middleware("http")(fastapi_tracking_middleware)
app.get("/prometheus")(fastapi_endpoint_for_prometheus)
```

### Пример с ручным трекингом

```python
from llm_common.prometheus import action_tracking

def process_large_dataset(data):
    with action_tracking("dataset_processing") as tracker:
        # Обработка данных
        processed_data = []
        for item in data:
            processed_item = transform(item)
            processed_data.append(processed_item)
        
        # Трекинг размера обработанных данных
        tracker.size(len(processed_data))
        
        return processed_data
```

## 🤖 Для LLM моделей

Эта библиотека предоставляет готовые инструменты для:

1. **Мониторинга LLM запросов**: Используйте `LLMHttpClient` в качестве `http_async_client` для ChatOpenAI и других LLM клиентов для автоматического трекинга всех запросов к LLM API
2. **Интеграции с OpenAI/LangChain**: Передавайте `LLMHttpClient` в параметр `http_async_client` для получения метрик без изменения кода работы с LLM
3. **Отслеживания производительности**: Декораторы `@action_tracking_decorator` для мониторинга функций обработки
4. **Интеграции в веб-сервисы**: FastAPI middleware для полного мониторинга веб-приложений
5. **Экспорта метрик**: Готовый endpoint `/prometheus` для интеграции с Prometheus/Grafana

Все метрики собираются автоматически и готовы для использования в системах мониторинга.
