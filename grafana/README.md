# Grafana Observability Setup

This directory contains the configuration files for the observability stack with Grafana, Prometheus, and Loki.

## Files

- `observability-config.json` - Main observability configuration in JSON format
- `prometheus.yml` - Prometheus scrape configuration
- `datasources.yml` - Grafana data source provisioning
- `promtail-config.yml` - Promtail configuration for log collection

## Services Added to Docker Compose

1. **Prometheus** (port 9090) - Metrics collection and storage
2. **Grafana** (port 3000) - Visualization and dashboards
3. **Loki** (port 3100) - Log aggregation
4. **Promtail** - Log collection agent
5. **Postgres Exporters** - Metrics exporters for each database
6. **RabbitMQ Exporter** - Metrics exporter for RabbitMQ

## Testing

1. Start the observability stack
   ```bash
   docker compose up -d prometheus grafana loki promtail
   ```

2. Access Grafana
   - URL: http://localhost:3000
   - Username: `admin`
   - Password: `admin`

3. Access Prometheus
   - URL: http://localhost:9090

4. Verify data sources in Grafana
   - Go to Configuration > Data Sources
   - Prometheus and Loki should be automatically configured

5. Check Prometheus targets
   - Go to Status > Targets in Prometheus UI
   - All microservices should be listed

## Notes

- Make sure your microservices expose `/metrics` endpoints for Prometheus to scrape
- Logs are collected from Docker containers automatically via Promtail
- Database exporters require the databases to be running first
