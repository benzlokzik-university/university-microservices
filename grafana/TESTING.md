# Testing Grafana Dashboards

This guide explains how to generate test data to see metrics in Grafana dashboards.

## Quick Test (One-time)

Run the shell script to generate a quick burst of requests:

```bash
./grafana/generate_test_data.sh
```

This will:
- Make requests to all services
- Generate metrics for Prometheus to scrape
- Take about 30-60 seconds

## Continuous Load (Recommended)

For better visualization, run the Python script to generate continuous load:

```bash
python3 grafana/continuous_load.py
```

This will:
- Generate continuous requests for 5 minutes (300 seconds)
- Create realistic traffic patterns
- Show metrics in real-time in Grafana

Press `Ctrl+C` to stop early.

## Manual Testing

You can also manually test services using curl:

```bash
# Test Gateway
curl http://localhost:8000/health
curl http://localhost:8000/

# Test User Account
curl http://localhost:8001/health

# Test Game Catalog
curl http://localhost:8002/health

# Test Booking
curl http://localhost:8003/health

# Test Payment
curl http://localhost:8004/health

# Test Rent
curl http://localhost:8005/health

# Test Rating
curl http://localhost:8006/health
```

## Viewing Metrics in Grafana

1. **Access Grafana**: http://localhost:3000
   - Username: `admin`
   - Password: `admin`

2. **View Dashboards**:
   - Go to **Dashboards** → **Browse**
   - Open **Microservices Overview**
   - You should see:
     - Service Health Status
     - Request Rate by Service
     - Response Time by Service (p95)
     - Error Rate by Service

3. **Check Prometheus**:
   - Go to **Explore** → Select **Prometheus** datasource
   - Try queries like:
     - `up{job="microservices"}` - Service health
     - `rate(http_requests_total[5m])` - Request rate
     - `http_request_duration_seconds` - Response times

## Expected Metrics

After running the test scripts, you should see:

- **HTTP Request Count**: Number of requests per service
- **Request Duration**: Response times
- **Status Codes**: Success/error rates
- **Service Health**: Up/down status

## Troubleshooting

### No Data in Dashboards

1. **Check Prometheus Targets**:
   - Go to http://localhost:9090/targets
   - All services should show as "UP"

2. **Verify Services are Running**:
   ```bash
   docker compose ps
   ```

3. **Check Metrics Endpoint**:
   ```bash
   curl http://localhost:8000/metrics
   ```

4. **Wait for Scrape Interval**:
   - Prometheus scrapes every 15 seconds
   - Wait 15-30 seconds after generating load

### Services Not Responding

1. **Check Service Logs**:
   ```bash
   docker compose logs gateway
   docker compose logs user-account
   ```

2. **Restart Services**:
   ```bash
   docker compose restart
   ```

## Advanced Testing

For more realistic load, you can use tools like:

- **Apache Bench (ab)**:
  ```bash
  ab -n 1000 -c 10 http://localhost:8000/health
  ```

- **wrk**:
  ```bash
  wrk -t4 -c100 -d30s http://localhost:8000/health
  ```

- **k6** (if installed):
  ```bash
  k6 run - <(echo 'import http from "k6/http"; export default function() { http.get("http://localhost:8000/health"); }')
  ```
