#!/bin/bash

set -e

GATEWAY_URL="http://localhost:8000"
USER_ACCOUNT_URL="http://localhost:8001"
GAME_CATALOG_URL="http://localhost:8002"
BOOKING_URL="http://localhost:8003"
PAYMENT_URL="http://localhost:8004"
RENT_URL="http://localhost:8005"
RATING_URL="http://localhost:8006"

echo "🚀 Generating test data for Grafana dashboards..."
echo "This will make requests to all services to generate metrics"
echo ""

make_request() {
    local url=$1
    local method=${2:-GET}
    local data=${3:-""}

    if [ "$method" = "GET" ]; then
        curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000"
    else
        curl -s -o /dev/null -w "%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" "$url" || echo "000"
    fi
}

test_service() {
    local service_name=$1
    local url=$2
    local endpoint=${3:-/health}

    echo "Testing $service_name..."
    for i in {1..10}; do
        make_request "$url$endpoint" "GET"
        sleep 0.5
    done
    echo "✅ $service_name tested"
}

echo "📊 Testing Gateway Service..."
test_service "Gateway" "$GATEWAY_URL" "/health"
test_service "Gateway" "$GATEWAY_URL" "/"
sleep 1

echo "📊 Testing User Account Service..."
test_service "User Account" "$USER_ACCOUNT_URL" "/health"
for i in {1..5}; do
    make_request "$USER_ACCOUNT_URL/api/v1/users/test-user-$i" "GET"
    sleep 0.3
done
sleep 1

echo "📊 Testing Game Catalog Service..."
test_service "Game Catalog" "$GAME_CATALOG_URL" "/health"
for i in {1..5}; do
    make_request "$GAME_CATALOG_URL/api/v1/games/game-$i" "GET"
    sleep 0.3
done
sleep 1

echo "📊 Testing Booking Service..."
test_service "Booking" "$BOOKING_URL" "/health"
for i in {1..5}; do
    make_request "$BOOKING_URL/api/v1/bookings/booking-$i" "GET"
    sleep 0.3
done
sleep 1

echo "📊 Testing Payment Service..."
test_service "Payment" "$PAYMENT_URL" "/health"
for i in {1..5}; do
    make_request "$PAYMENT_URL/api/v1/payments/payment-$i" "GET"
    sleep 0.3
done
sleep 1

echo "📊 Testing Rent Service..."
test_service "Rent" "$RENT_URL" "/health"
for i in {1..5}; do
    make_request "$RENT_URL/api/v1/orders/order-$i" "GET"
    sleep 0.3
done
sleep 1

echo "📊 Testing Rating Service..."
test_service "Rating" "$RATING_URL" "/health"
for i in {1..5}; do
    make_request "$RATING_URL/api/v1/ratings/rating-$i" "GET"
    sleep 0.3
done

echo ""
echo "✅ Test data generation complete!"
echo "📈 Check Grafana dashboards at http://localhost:3000"
echo "   - Go to Dashboards → Microservices Overview"
echo "   - Metrics should appear within 15-30 seconds"
