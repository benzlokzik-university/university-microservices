#import "@preview/modern-g7-32:0.2.0": gost

#set text(font: "Times New Roman", lang: "ru")

#show: gost.with(
  ministry: "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ",
  organization: (
    full: "Федеральное государственное бюджетное образовательное учреждение высшего образования \"МИРЭА — Российский технологический университет\"",
    short: "РТУ МИРЭА"
  ),
  udk: none,
  research-number: none,
  report-number: none,
  approved-by: none,
  agreed-by: none,
  report-type: "отчёт",
  about: "по практическим работам №9-10",
  subject: "Микросервисная архитектура",
  manager: (
    name: "Запорожских А.И.",
    position: "Преподаватель"
  ),
  city: "Москва",

)

#outline(title: "Содержание")

#pagebreak()

= Практическая работа №9

== Цель работы

Изучение процессов непрерывной интеграции и развертывания (CI/CD) и получение практических навыков настройки автоматизированной сборки, публикации образов Docker и развертывания микросервисов в облачной инфраструктуре.

== Ход работы

Для автоматизации процессов разработки и развертывания была настроена система CI/CD с использованием GitHub Actions. Система включает непрерывную интеграцию (CI) для проверки кода и непрерывное развертывание (CD) для автоматической сборки, публикации и деплоя сервисов.

=== Настройка непрерывной интеграции (CI)

Настройка CI включает два workflow-файла: основной `ci.yaml` и рабочий `tests.yml`.

Основной workflow `ci.yaml` запускается при каждом push и pull request:

```yaml
name: CI

on:
  push:
    branches: ["**"]
  pull_request:

jobs:
  tests:
    uses: ./.github/workflows/tests.yml
```

Рабочий workflow `tests.yml` содержит два джоба: проверку кода (lint) и запуск тестов:

```yaml
name: tests

on:
  workflow_call:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v6
    - name: Install the latest version of ruff
      uses: astral-sh/ruff-action@v3
      with:
        version: "latest"
        args: check .
        src: "./code/services"

  test:
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
      rabbitmq:
        image: rabbitmq:3-management-alpine
        env:
          RABBITMQ_DEFAULT_USER: guest
          RABBITMQ_DEFAULT_PASS: guest
    strategy:
      matrix:
        service:
          - user-account
          - game-catalog
          - booking
          - payment
          - rent
          - rating
    steps:
    - uses: actions/checkout@v6
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - name: Install UV
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    - name: Install dependencies
      working-directory: ./code/services/${{ matrix.service }}
      run: |
        uv sync
        uv sync --group test
    - name: Run tests
      working-directory: ./code/services/${{ matrix.service }}
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        RABBITMQ_URL: amqp://guest:guest@localhost:5672/
      run: |
        uv run --group test pytest tests/ -v --cov=. --cov-report=xml --cov-report=term
```

На рисунке @fig-ci показан интерфейс GitHub Actions с запущенным CI workflow.

#figure(
  image("9/github ci.yaml screenshot.png", width: 90%),
  caption: [Интерфейс GitHub Actions с CI workflow],
) <fig-ci>

=== Настройка непрерывного развертывания (CD)

Workflow `cd.yaml` настроен для автоматической сборки, публикации и развертывания сервисов при push в ветку `main`. Процесс включает несколько этапов:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  tests:
    uses: ./.github/workflows/tests.yml

  build:
    needs: tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [gateway, booking]
    steps:
      - uses: actions/checkout@v6
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/${{ matrix.service }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}
      - name: Build and push image
        uses: docker/build-push-action@v5
        with:
          context: ./code/services/${{ matrix.service }}
          file: ./code/services/${{ matrix.service }}/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

На рисунке @fig-cicd показан интерфейс GitHub Actions с запущенным CD workflow.

#figure(
  image("9/github cicd.yaml screenshot.png", width: 90%),
  caption: [Интерфейс GitHub Actions с CD workflow],
) <fig-cicd>

=== Публикация образов в Docker Registry

Образы Docker публикуются в два реестра: GitHub Container Registry (GHCR) и Yandex Cloud Container Registry.

После успешной сборки образы автоматически публикуются в GHCR с тегами:
- `latest` — для основной ветки
- `main-<sha>` — с префиксом ветки и хешем коммита
- Версионированные теги при наличии тегов в репозитории

На рисунке @fig-ghcr показан интерфейс GitHub Container Registry с опубликованными образами.

#figure(
  image("9/github docker registry screenshot.png", width: 90%),
  caption: [GitHub Container Registry с образами микросервисов],
) <fig-ghcr>

Затем образы копируются в Yandex Cloud Container Registry:

```yaml
push-to-yandexcloud:
  needs: build
  runs-on: ubuntu-latest
  strategy:
    matrix:
      service: [gateway, booking]
  steps:
    - name: Log in to Yandex Cloud Registry
      uses: docker/login-action@v3
      with:
        registry: cr.yandex
        username: json_key
        password: ${{ secrets.YC_KEYS }}
    - name: Copy image from GHCR to Yandex Cloud
      run: |
        docker buildx imagetools create \
          -t cr.yandex/${{ secrets.YC_REGISTRY_ID }}/board-games-backend/${{ steps.yc_meta.outputs.name }}:latest \
          ghcr.io/${{ github.repository }}/${{ matrix.service }}:latest
```

На рисунке @fig-yc-images показаны образы в Yandex Cloud Container Registry.

#figure(
  image("9/yc project's docker images.png", width: 90%),
  caption: [Образы Docker в Yandex Cloud Container Registry],
) <fig-yc-images>

На рисунках @fig-yc-gateway-images и @fig-yc-booking-images показаны образы для конкретных сервисов.

#figure(
  image("9/yc gateway docker images.png", width: 90%),
  caption: [Образы сервиса Gateway в Yandex Cloud],
) <fig-yc-gateway-images>

#figure(
  image("9/yc booking docker images.png", width: 90%),
  caption: [Образы сервиса Booking в Yandex Cloud],
) <fig-yc-booking-images>

=== Создание релизов в GitHub

После успешной сборки автоматически создаются релизы в GitHub:

```yaml
release-on-github:
  needs: build
  runs-on: ubuntu-latest
  strategy:
    matrix:
      service: [gateway, booking]
  steps:
    - name: Get version tag
      id: version
      run: |
        if [[ "${{ github.ref }}" == refs/tags/* ]]; then
          VERSION="${GITHUB_REF#refs/tags/}"
        else
          VERSION="$(date +'%Y%m%d')-${GITHUB_SHA:0:7}"
        fi
        echo "version=$VERSION" >> $GITHUB_OUTPUT
    - name: Create ${{ matrix.service }} release
      uses: softprops/action-gh-release@v1
      with:
        tag_name: ${{ steps.release_meta.outputs.name }}-${{ steps.version.outputs.version }}
        name: ${{ steps.release_meta.outputs.name }} ${{ steps.version.outputs.version }}
        body: |
          ${{ matrix.service }} service release
          **Image Tags:**
          - `ghcr.io/${{ github.repository }}/${{ matrix.service }}:latest`
          - `ghcr.io/${{ github.repository }}/${{ matrix.service }}:${{ github.ref_name }}`
```

На рисунках @fig-gateway-release и @fig-booking-release показаны созданные релизы для сервисов.

#figure(
  image("9/github benzlokzik-gateway release screenshot.png", width: 90%),
  caption: [Релиз сервиса Gateway в GitHub],
) <fig-gateway-release>

#figure(
  image("9/github PointThrow-booking release screenshot.png", width: 90%),
  caption: [Релиз сервиса Booking в GitHub],
) <fig-booking-release>

=== Развертывание в Yandex Cloud Serverless Containers

После публикации образов выполняется автоматическое развертывание сервисов в Yandex Cloud Serverless Containers:

```yaml
deploy-on-yc:
  needs: push-to-yandexcloud
  runs-on: ubuntu-latest
  strategy:
    matrix:
      service: [gateway, booking]
  steps:
    - name: Deploy ${{ matrix.service }} serverless container
      uses: yc-actions/yc-sls-container-deploy@v4
      with:
        yc-sa-json-credentials: ${{ secrets.YC_KEYS }}
        container-name: ${{ steps.yc_meta.outputs.name }}
        folder-id: ${{ secrets.YC_FOLDER_ID }}
        revision-image-url: cr.yandex/${{ secrets.YC_REGISTRY_ID }}/board-games-backend/${{ steps.yc_meta.outputs.name }}:latest
        revision-service-account-id: ${{ secrets.YC_SA_ID }}
        revision-memory: 512Mb
```

На рисунках @fig-yc-gateway-deploy и @fig-yc-booking-deploy показаны развернутые сервисы в Yandex Cloud.

#figure(
  image("9/yc gateway deploy.png", width: 90%),
  caption: [Развертывание сервиса Gateway в Yandex Cloud],
) <fig-yc-gateway-deploy>

#figure(
  image("9/yc booking deploy.png", width: 90%),
  caption: [Развертывание сервиса Booking в Yandex Cloud],
) <fig-yc-booking-deploy>

== Вывод

В ходе выполнения практической работы была настроена система CI/CD с использованием GitHub Actions. Настроена непрерывная интеграция для автоматической проверки кода и запуска тестов. Реализовано непрерывное развертывание с автоматической сборкой Docker-образов, публикацией в GitHub Container Registry и Yandex Cloud Container Registry, созданием релизов и развертыванием сервисов в Yandex Cloud Serverless Containers. Получены практические навыки настройки и использования инструментов автоматизации процессов разработки и развертывания микросервисов.

#pagebreak()

= Практическая работа №10

== Цель работы

Изучение инструментов мониторинга микросервисной архитектуры и получение практических навыков настройки системы наблюдения с использованием Prometheus, Grafana и Loki.

== Ход работы

Для обеспечения мониторинга микросервисной архитектуры была настроена система наблюдения, включающая следующие компоненты:

#list(
  [*Prometheus* — система сбора и хранения метрик;],
  [*Grafana* — платформа для визуализации метрик и логов;],
  [*Loki* — система агрегации логов;],
  [*Promtail* — агент для сбора логов из Docker-контейнеров.],
)

В файле `docker-compose.yml` были добавлены следующие сервисы для мониторинга:

=== Prometheus

Prometheus настроен для сбора метрик со всех микросервисов и экспортеров. Конфигурация включает:

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./grafana/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus-data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
```

В конфигурационном файле `prometheus.yml` настроены следующие задачи сбора метрик:

#list(
  [*microservices* — сбор метрик со всех микросервисов (gateway, user-account, game-catalog, booking, payment, rent, rating);],
  [*postgres-user-account* — метрики базы данных пользователей;],
  [*postgres-game-catalog* — метрики базы данных каталога игр;],
  [*postgres-rent* — метрики базы данных аренды;],
  [*rabbitmq* — метрики брокера сообщений.],
)

На рисунке @fig-prometheus показан интерфейс Prometheus с собранными метриками.

#figure(
  image("10/prometheus.jpg", width: 90%),
  caption: [Интерфейс Prometheus с метриками микросервисов],
) <fig-prometheus>

=== Grafana

Grafana настроена для визуализации метрик и логов. Конфигурация включает:

```yaml
grafana:
  image: grafana/grafana:latest
  container_name: grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_USERS_ALLOW_SIGN_UP=false
    - GF_PATHS_PROVISIONING=/etc/grafana/provisioning
  volumes:
    - grafana-data:/var/lib/grafana
    - ./grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    - ./grafana/dashboards.yml:/etc/grafana/provisioning/dashboards/dashboards.yml
    - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
```

В файле `datasources.yml` настроены источники данных:

#list(
  [*Prometheus* — основной источник метрик, доступен по адресу `http://prometheus:9090`;],
  [*Loki* — источник логов, доступен по адресу `http://loki:3100`.],
)

=== Loki и Promtail

Loki настроен для агрегации логов:

```yaml
loki:
  image: grafana/loki:latest
  container_name: loki
  ports:
    - "3100:3100"
  volumes:
    - loki-data:/loki
  command: -config.file=/etc/loki/local-config.yaml
```

Promtail собирает логи из Docker-контейнеров и отправляет их в Loki:

```yaml
promtail:
  image: grafana/promtail:latest
  container_name: promtail
  volumes:
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
    - /var/run/docker.sock:/var/run/docker.sock
    - ./grafana/promtail-config.yml:/etc/promtail/config.yml
  command: -config.file=/etc/promtail/config.yml
```

В конфигурации Promtail настроен автоматический сбор логов из всех Docker-контейнеров с добавлением меток для идентификации сервисов.

=== Экспортеры метрик

Для мониторинга баз данных и брокера сообщений были добавлены экспортеры:

#list(
  [*postgres-exporter-user-account* — экспорт метрик базы данных пользователей;],
  [*postgres-exporter-game-catalog* — экспорт метрик базы данных каталога игр;],
  [*postgres-exporter-rent* — экспорт метрик базы данных аренды;],
  [*rabbitmq-exporter* — экспорт метрик RabbitMQ.],
)

=== Дашборды

В Grafana были созданы дашборды для мониторинга различных аспектов системы:

На рисунке @fig-dashboard-overview представлен общий обзор микросервисов с ключевыми метриками производительности.

#figure(
  image("10/dashboard microservices overview.png", width: 90%),
  caption: [Дашборд общего обзора микросервисов],
) <fig-dashboard-overview>

На рисунке @fig-dashboard-rabbitmq показан дашборд мониторинга RabbitMQ с метриками очередей и обмена сообщениями.

#figure(
  image("10/dashboard rabbitmq monitoring.png", width: 90%),
  caption: [Дашборд мониторинга RabbitMQ],
) <fig-dashboard-rabbitmq>

На рисунке @fig-dashboard-database представлен дашборд производительности баз данных с метриками запросов и соединений.

#figure(
  image("10/dashboard database performance.png", width: 90%),
  caption: [Дашборд производительности баз данных],
) <fig-dashboard-database>

=== Генерация нагрузки для тестирования мониторинга

Для тестирования системы мониторинга был создан скрипт генерации нагрузки на микросервисы. Скрипт написан на языке Crystal и выполняет параллельные запросы ко всем сервисам в течение заданного времени.

Основные компоненты скрипта:

```crystal
SERVICES = {
  "gateway"      => "http://localhost:8000",
  "user-account" => "http://localhost:8001",
  "game-catalog" => "http://localhost:8002",
  "booking"      => "http://localhost:8003",
  "payment"      => "http://localhost:8004",
  "rent"         => "http://localhost:8005",
  "rating"       => "http://localhost:8006",
}

ENDPOINTS = {
  "gateway"      => ["/", "/health", "/docs"],
  "user-account" => ["/health", "/api/v1/users/test-user"],
  "game-catalog" => ["/health", "/api/v1/games/test-game"],
  "booking"      => ["/health", "/api/v1/bookings/test-booking"],
  "payment"      => ["/health", "/api/v1/payments/test-payment"],
  "rent"         => ["/health", "/api/v1/orders/test-order"],
  "rating"       => ["/health", "/api/v1/ratings/test-rating"],
}
```

Скрипт использует параллельные волокна (fibers) для генерации нагрузки на каждый сервис независимо. Для каждого сервиса случайным образом выбираются эндпоинты из предопределенного списка, что позволяет имитировать реальную нагрузку. Интервал между запросами также варьируется случайным образом для более естественного распределения нагрузки.

Функция генерации нагрузки:

```crystal
def generate_load(service_name : String, base_url : String, duration : Int32, interval : Float64, channel : Channel(Int32))
  end_time = Time.monotonic + duration.seconds
  request_count = 0
  random = Random.new

  endpoints = ENDPOINTS[service_name]? || ["/health"]

  while Time.monotonic < end_time
    endpoint = endpoints.sample(random: random)
    make_request(service_name, base_url, endpoint)
    request_count += 1

    sleep_interval = interval + random.rand(-0.5..0.5)
    sleep sleep_interval
  end

  channel.send(request_count)
end
```

Скрипт запускается на 300 секунд (5 минут) с интервалом около 2 секунд между запросами. Это позволяет собрать достаточное количество метрик для анализа в Grafana и проверить корректность работы системы мониторинга.

== Вывод

В ходе выполнения практической работы была настроена система мониторинга микросервисной архитектуры с использованием Prometheus для сбора метрик, Grafana для визуализации и Loki для агрегации логов. Были настроены экспортеры для баз данных и брокера сообщений, а также созданы дашборды для отслеживания состояния системы. Получены практические навыки настройки и использования инструментов наблюдения за микросервисной архитектурой.

== Ссылка на репозиторий

https://github.com/benzlokzik-university/university-microservices
