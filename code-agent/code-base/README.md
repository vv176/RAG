# E-commerce API

A modern e-commerce platform built with FastAPI, featuring user authentication, product management, order processing, and real-time notifications.

## Features

- **User Management**: Registration, authentication, and profile management
- **Product Catalog**: Product CRUD operations with categories and images
- **Order Processing**: Complete order lifecycle management
- **Authentication**: JWT-based authentication with role-based access control
- **Real-time Notifications**: Redis-based notification system
- **Email Service**: Automated email notifications
- **Comprehensive Testing**: Unit tests for all major components

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Redis**: Caching and real-time notifications
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Tokens for authentication
- **Pytest**: Testing framework

## Project Structure

```
code-base/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── core/              # Core application modules
│   │   ├── config.py      # Configuration settings
│   │   ├── database.py    # Database configuration
│   │   └── security.py    # Authentication utilities
│   ├── models/            # SQLAlchemy models
│   │   ├── user.py        # User model
│   │   ├── product.py     # Product and ProductImage models
│   │   ├── order.py       # Order and OrderItem models
│   │   └── category.py    # Category model
│   ├── schemas/           # Pydantic schemas
│   │   ├── user.py        # User schemas
│   │   ├── product.py     # Product schemas
│   │   ├── order.py       # Order schemas
│   │   └── category.py    # Category schemas
│   ├── api/               # API routes
│   │   └── v1/
│   │       ├── router.py  # Main API router
│   │       └── endpoints/ # API endpoints
│   │           ├── auth.py        # Authentication endpoints
│   │           ├── users.py       # User management endpoints
│   │           ├── products.py    # Product management endpoints
│   │           ├── orders.py      # Order management endpoints
│   │           └── categories.py  # Category management endpoints
│   ├── services/          # Business logic services
│   │   ├── email.py       # Email service
│   │   └── notification.py # Notification service
│   └── utils/             # Utility functions
│       ├── validators.py  # Validation utilities
│       └── helpers.py     # Helper functions
└── tests/                 # Test files
    ├── test_auth.py       # Authentication tests
    └── test_products.py   # Product tests
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd code-base
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Install PostgreSQL and create database
   createdb ecommerce
   
   # Run migrations (if using Alembic)
   alembic upgrade head
   ```

6. **Set up Redis**
   ```bash
   # Install and start Redis
   redis-server
   ```

## Running the Application

```bash
# Development server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## Key Components

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (admin/user)

### Product Management
- CRUD operations for products
- Category management
- Image support
- Stock management
- Search and filtering

### Order Processing
- Complete order lifecycle
- Order status tracking
- Inventory management
- Order history

### Services
- **Email Service**: Automated notifications
- **Notification Service**: Real-time updates via Redis

### Utilities
- **Validators**: Input validation
- **Helpers**: Common utility functions

## Database Schema

The application uses the following main entities:
- **Users**: Customer and admin accounts
- **Products**: Product catalog with categories
- **Orders**: Order management with items
- **Categories**: Product categorization

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
