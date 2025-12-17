#!/usr/bin/env crystal run
require "http/client"
require "random"

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

def make_request(service_name : String, base_url : String, endpoint : String) : Int32?
  url = "#{base_url}#{endpoint}"
  begin
    response = HTTP::Client.get(url)
    response.status_code
  rescue
    nil
  end
end

def generate_load(service_name : String, base_url : String, duration : Int32, interval : Float64, channel : Channel(Int32))
  end_time = Time.monotonic + duration.seconds
  request_count = 0
  random = Random.new

  puts "🚀 Starting load generation for #{service_name}..."

  endpoints = ENDPOINTS[service_name]? || ["/health"]

  while Time.monotonic < end_time
    endpoint = endpoints.sample(random: random)
    make_request(service_name, base_url, endpoint)
    request_count += 1

    if request_count % 10 == 0
      puts "  #{service_name}: #{request_count} requests made"
    end

    sleep_interval = interval + random.rand(-0.5..0.5)
    sleep sleep_interval.seconds
  end

  puts "✅ #{service_name}: Completed #{request_count} requests"
  channel.send(request_count)
end

def main
  duration = 300
  interval = 2.0
  puts "📊 Starting continuous load generation for #{duration} seconds..."
  puts "   This will generate metrics visible in Grafana"
  puts "   Press Ctrl+C to stop early\n"

  channel = Channel(Int32).new

  Signal::INT.trap do
    puts "\n\n⏹️  Stopping load generation..."
    exit 0
  end

  SERVICES.each do |service_name, base_url|
    spawn do
      generate_load(service_name, base_url, duration, interval, channel)
    end
  end

  total_requests = 0
  SERVICES.size.times do
    total_requests += channel.receive
  end

  puts "\n✅ Load generation complete! Total requests: #{total_requests}"
  puts "\n📈 Check Grafana at http://localhost:3000"
  puts "   Dashboard: Microservices Overview"
end

main

