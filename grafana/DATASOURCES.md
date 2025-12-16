# Grafana Data Sources Configuration

This document describes the data sources configured for Grafana observability.

## Current Data Sources

### 1. Prometheus (Default)

- **Type**: Prometheus
- **URL**: http://prometheus:9090
- **Purpose**: Metrics collection and storage
- **Status**: ✅ Configured and working
- **Features**:
  - Default data source for dashboards
  - 15s query interval
  - POST method for queries
  - Exemplar support for tracing integration

### 2. Loki

- **Type**: Loki
- **URL**: http://loki:3100
- **Purpose**: Log aggregation and querying
- **Status**: ✅ Configured and working
- **Features**:
  - LogQL query language
  - Derived fields for trace correlation
  - Max 1000 lines per query

## Optional Data Sources (Require Plugins)

### PostgreSQL Data Sources

To add PostgreSQL data sources, you need to install the PostgreSQL plugin:

1. **Install Plugin** (add to docker-compose.yml):
   ```yaml
   environment:
     - GF_INSTALL_PLUGINS=grafana-postgresql-datasource
   ```

2. **Add to datasources.yml**:
   ```yaml
   - name: PostgreSQL - User Account
     type: postgres
     url: user-account-db:5432
     database: user_account
     user: postgres
     secureJsonData:
       password: postgres
     jsonData:
       sslmode: disable
   ```

### RabbitMQ Data Source

RabbitMQ metrics are available through Prometheus via the RabbitMQ exporter. No additional Grafana datasource is needed.

## Verification

To verify data sources are working:

1. **Access Grafana**: http://localhost:3000
2. **Login**: admin/admin
3. **Navigate**: Configuration → Data Sources
4. **Test**: Click "Test" button for each data source

## Troubleshooting

### Data Source Not Found Error

- Ensure services (Prometheus, Loki) are running and healthy
- Check network connectivity between Grafana and data source services
- Verify URLs are correct (use service names in Docker network)

### PostgreSQL Plugin Issues

- Plugin requires Grafana restart after installation
- Check plugin compatibility with Grafana version
- Verify database credentials and network access

## Metrics Available

### From Prometheus

- HTTP request metrics (count, duration, status codes)
- Service health status
- Database connection metrics (via postgres exporters)
- RabbitMQ queue metrics (via rabbitmq exporter)

### From Loki

- Application logs from all services
- Container logs
- Structured JSON logs
