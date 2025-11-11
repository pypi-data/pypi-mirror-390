# 🛡️ UYEIA

> **U**nified **Y**et **E**asy **I**ssue **A**lerts - A comprehensive error monitoring and status management system for Python applications.

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## 🌟 Overview

UYEIA is a sophisticated yet easy-to-use Python library designed for monitoring application health, managing error states, and providing centralized error tracking across distributed systems. It offers a thread-safe, SQLite-backed caching system with configurable status levels, automatic escalation mechanisms, and flexible logging integration.

## ✨ Key Features

- **🔄 Real-time Status Monitoring**: Track application health with customizable status levels
- **📊 Centralized Error Management**: JSON-based error configuration with dynamic message templating
- **🗃️ Persistent Cache System**: SQLite-backed storage for status persistence across sessions
- **🔒 Thread-Safe Operations**: Built-in threading support for concurrent applications
- **📈 Automatic Escalation**: Configurable error escalation based on occurrence patterns
- **🔧 Flexible Configuration**: Highly customizable status levels, logging, and behavior
- **💾 Secure Vault Storage**: Key-value storage for sensitive configuration data
- **🪵 Integrated Logging**: Seamless integration with Python's logging framework

## 🚀 Quick Start

### Installation

```bash
pip install uyeia
```

### Basic Usage

```python
import uyeia
import logging

# Configure UYEIA
config = uyeia.Config(
    status={
        "HEALTHY": 20,
        "WARNING": 40,
        "CRITICAL": 50
    },
    error_config_location="./errors.json"
)
uyeia.set_global_config(config)

# Create a watcher
logger = logging.getLogger("my_app")
watcher = uyeia.Watcher(logger=logger)

# Register an error
watcher.register("E001", "Custom error message", {"user_id": "12345"})

# Check current status
status = watcher.get_actual_status()
print(f"Current status: {status}")

# Get all errors
all_errors = uyeia.get_errors()
print(f"All errors: {all_errors}")

# Release the error when resolved
watcher.release()
```

### Error Configuration

Create an `errors.json` file to define your error codes:

```json
{
    "E001": {
        "status": "WARNING",
        "message": "Database connection timeout for user {{user_id}}",
        "solution": "Check database connectivity and retry"
    },
    "E002": {
        "status": "CRITICAL",
        "message": "Authentication service unavailable",
        "solution": "Contact system administrator immediately"
    }
}
```

## 📖 Detailed Usage

### Configuration Options

```python
from uyeia import Config

config = Config(
    # Define status hierarchy (name: log_level)
    status={
        "HEALTHY": 20,     # INFO level
        "PENDING": 20,     # INFO level  
        "LIMITED": 30,     # WARNING level
        "WARNING": 40,     # ERROR level
        "RESCUE": 50       # CRITICAL level
    },
    
    # Escalation settings
    escalation_status="RESCUE",     # Status to escalate to
    max_escalation=5,               # Max escalations before critical
    disable_escalation=False,       # Enable/disable escalation
    
    # Default values
    default_healthy="HEALTHY",
    default_solution="Contact your IT admin.",
    
    # File locations
    error_config_location="./uyeia.errors.json",
    error_cache_location="./errors_cache.db",
    
    # Behavior
    disable_logging=False           # Enable/disable automatic logging
)
```

### Advanced Watcher Usage

```python
import uyeia
import logging

# Method 1: Using logger
logger = logging.getLogger("database")
watcher = uyeia.Watcher(logger=logger)

# Method 2: Using name
watcher = uyeia.Watcher(name="api_service")

# Register error with variable substitution
watcher.register(
    error_code="DB_TIMEOUT",
    custom_message="Connection failed after {{timeout}}s",
    vars={"timeout": "30", "retry_count": "3"}
)

# Clear all errors for this watcher
watcher.release()
```

### Error Retrieval Modes

```python
# Get all errors grouped by status
all_errors = uyeia.get_errors("all")

# Get only the highest severity errors currently active
hot_errors = uyeia.get_errors("hot")

# Get only the lowest severity errors currently active  
cold_errors = uyeia.get_errors("cold")
```

### Vault Storage

```python
# Secure key-value storage
vault = uyeia.Vault()

# Store sensitive data
vault.set("api_key", "secret_key_12345")
vault.set("db_password", "super_secure_password")

# Retrieve data
api_key = vault.get("api_key")

# Remove data
vault.remove("api_key")
```

### Error Escalation

```python
# Manual escalation (increases escalation count for all non-critical errors)
uyeia.escalate()

# Errors that reach max_escalation count automatically become critical status
```

## 🏗️ Architecture

### Core Components

1. **Watcher**: Individual monitors for different application components
2. **Manager**: Central coordination of all watchers and cache operations  
3. **UyeiaCache**: SQLite-backed persistent storage system
4. **Config**: Configuration management with validation
5. **Vault**: Secure key-value storage for sensitive data

### Data Flow

```
Application Error → Watcher → Manager → Cache (SQLite) → Status Retrieval
                      ↓
                  Logging System
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_cache_operation.py

# Run with coverage
pytest --cov=src/uyeia

# Lint code
rye run lint

# Format code  
rye run format
```

## 📊 Status Hierarchy

UYEIA uses a hierarchical status system where higher values indicate more severe issues:

| Status | Default Level | Description |
|--------|---------------|-------------|
| HEALTHY | 20 (INFO) | Normal operation |
| PENDING | 20 (INFO) | Temporary issues |  
| LIMITED | 30 (WARNING) | Degraded functionality |
| WARNING | 40 (ERROR) | Significant problems |
| RESCUE | 50 (CRITICAL) | Critical failures |

## 🔧 Configuration Files

### Error Definitions (`uyeia.errors.json`)

```json
{
    "SERVICE_001": {
        "status": "WARNING",
        "message": "Service {{service_name}} is experiencing delays",
        "solution": "Monitor service performance and consider scaling"
    },
    "AUTH_002": {
        "status": "CRITICAL", 
        "message": "Authentication service completely down",
        "solution": "Immediate intervention required - check service logs"
    }
}
```

### Variable Substitution

Use `{{variable_name}}` in error messages for dynamic content:

```python
watcher.register(
    "SERVICE_001",
    vars={"service_name": "payment_processor", "latency": "2.5s"}
)
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/David-Aires/uyeia.git
cd uyeia

# Install dependencies with Rye
rye sync

# Run tests
rye run test

# Format code
rye run format

# Lint code
rye run lint
```

### Project Structure

```
uyeia/
├── src/uyeia/           # Main package
│   ├── __init__.py      # Main API and Watcher/Manager classes
│   ├── cache.py         # SQLite caching system
│   ├── type.py          # Type definitions and Config
│   ├── exceptions.py    # Custom exceptions
│   └── serializers.py   # Validation utilities
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`rye run test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/David-Aires/uyeia/issues)
- **Documentation**: [Project Wiki](https://github.com/David-Aires/uyeia/wiki)

## 🙏 Acknowledgments

- Built with ❤️ for robust application monitoring
- Inspired by the need for simple yet powerful error tracking
- Thanks to all contributors who help improve UYEIA

---

**UYEIA** - Making error monitoring unified, yet easy! 🛡️
