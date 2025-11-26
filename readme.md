# University Microservices

A microservices-based game rental and booking system built with Python and FastAPI.

## Services

- **Gateway** (port 8000) - API Gateway
- **User Account** (port 8001) - User management and authentication
- **Game Catalog** (port 8002) - Game catalog management
- **Booking** (port 8003) - Game booking service
- **Payment** (port 8004, gRPC 50051) - Payment processing
- **Rent** (port 8005) - Game rental management
- **Rating** (port 8006) - Rating and review service

## Architecture

```mermaid
graph TB
    Gateway[API Gateway<br/>:8000]
    
    UserAccount[User Account Service<br/>:8001]
    GameCatalog[Game Catalog Service<br/>:8002]
    Booking[Booking Service<br/>:8003]
    Payment[Payment Service<br/>:8004]
    Rent[Rent Service<br/>:8005]
    Rating[Rating Service<br/>:8006]
    
    UserDB[(User Account DB<br/>PostgreSQL)]
    GameDB[(Game Catalog DB<br/>PostgreSQL)]
    RentDB[(Rent DB<br/>PostgreSQL)]
    
    RabbitMQ[RabbitMQ<br/>Message Broker]
    
    ExtPerspective[Perspective API<br/>Content Moderation]
    ExtOneSignal[OneSignal<br/>Notifications]
    ExtSendGrid[SendGrid<br/>Email Service]
    ExtAcquiring[Эквайринг<br/>Payment Processing]
    ExtOFD[ОФД<br/>Fiscal Data]
    
    Gateway --> UserAccount
    Gateway --> GameCatalog
    Gateway --> Booking
    Gateway --> Payment
    Gateway --> Rent
    Gateway --> Rating
    
    UserAccount --> UserDB
    GameCatalog --> GameDB
    Rent --> RentDB
    
    UserAccount <-->|async| RabbitMQ
    GameCatalog <-->|async| RabbitMQ
    Booking <-->|async| RabbitMQ
    Payment <-->|async| RabbitMQ
    Rent <-->|async| RabbitMQ
    Rating <-->|async| RabbitMQ
    
    Rent -->|sync gRPC| Payment
    Payment -->|sync gRPC| Rent
    
    Booking -->|HTTP| UserAccount
    Rent -->|HTTP| Booking
    Rent -->|HTTP| GameCatalog
    Rent -->|HTTP| UserAccount
    Rating -->|HTTP| GameCatalog
    
    Rating --> ExtPerspective
    Rent --> ExtOneSignal
    Rent --> ExtSendGrid
    Payment --> ExtSendGrid
    Payment --> ExtAcquiring
    Payment --> ExtOFD
    
    style Gateway fill:#e1f5ff
    style UserAccount fill:#fff4e1
    style GameCatalog fill:#fff4e1
    style Booking fill:#fff4e1
    style Payment fill:#fff4e1
    style Rent fill:#fff4e1
    style Rating fill:#fff4e1
    style RabbitMQ fill:#e8f5e9
    style UserDB fill:#f3e5f5
    style GameDB fill:#f3e5f5
    style RentDB fill:#f3e5f5
    style ExtPerspective fill:#ffebee
    style ExtOneSignal fill:#ffebee
    style ExtSendGrid fill:#ffebee
    style ExtAcquiring fill:#ffebee
    style ExtOFD fill:#ffebee
```

## Prerequisites

- Docker and Docker Compose
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Quick Start

### Start all services

```bash
docker-compose up -d
```

### Access services

- API Gateway: <http://localhost:8000>
- RabbitMQ Management: <http://localhost:15672> (guest/guest)
- User Account DB: localhost:5433
- Game Catalog DB: localhost:5434
- Rent DB: localhost:5435

### Stop services

```bash
docker-compose down
```

## Project Structure

```text
code/
  services/            # Microservices
  rabbitmq/            # RabbitMQ examples
  pyproject.toml       # Workspace configuration
  docker-compose.yml   # Orchestration of all services
```

## Development

Each service has its own `pyproject.toml` and can be run independently. Pre-commit hooks are configured with Ruff for linting and formatting. Install them using `prek install`
