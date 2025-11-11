# pyramid-capstone

[![Release](https://img.shields.io/github/v/release/tomascorrea/pyramid-capstone)](https://github.com/tomascorrea/pyramid-capstone/releases)
[![Build status](https://img.shields.io/github/actions/workflow/status/tomascorrea/pyramid-capstone/on-release-main.yml?branch=main)](https://github.com/tomascorrea/pyramid-capstone/actions/workflows/on-release-main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/tomascorrea/pyramid-capstone/branch/main/graph/badge.svg)](https://codecov.io/gh/tomascorrea/pyramid-capstone)
[![Commit activity](https://img.shields.io/github/commit-activity/m/tomascorrea/pyramid-capstone)](https://img.shields.io/github/commit-activity/m/tomascorrea/pyramid-capstone)
[![License](https://img.shields.io/github/license/tomascorrea/pyramid-capstone)](https://img.shields.io/github/license/tomascorrea/pyramid-capstone)

**FastAPI-like decorators for Pyramid** - Build type-safe REST APIs with automatic validation, serialization, and OpenAPI documentation.

> **⚠️ Development Status Warning**
> 
> **This project is in early development (v0.1.x) and should NOT be used in production environments.**
> 
> While we have comprehensive tests and the core functionality works, the API may change significantly between versions. Use at your own risk and expect breaking changes until we reach v1.0.0.

- **📖 Documentation**: <https://tomascorrea.github.io/pyramid-capstone/>
- **🔧 Source Code**: <https://github.com/tomascorrea/pyramid-capstone/>
- **🐍 PyPI**: <https://pypi.org/project/pyramid-capstone/

## ✨ What is pyramid-capstone?

`pyramid-capstone` enhances Pyramid's already excellent foundation with modern developer conveniences. Built on Pyramid's proven architecture of robustness, flexibility, and enterprise-grade security, it adds automatic validation, serialization, and documentation generation while preserving Pyramid's minimalist philosophy.

### 🎯 Key Features

- **⚡ Developer Experience**: Modern decorators with automatic validation and serialization
- **🏗️ Pyramid Foundation**: Built on Pyramid's battle-tested, production-ready framework
- **🔗 Seamless Integration**: Works perfectly with existing Pyramid applications and middleware
- **📚 Auto Documentation**: Automatic OpenAPI/Swagger documentation generation
- **🛡️ Enterprise Security**: Leverages Pyramid's comprehensive security and authentication system
- **🧪 Production Ready**: Comprehensive test suite built on Pyramid's reliability

### 🚀 Quick Example

```python
from pyramid.config import Configurator
from pyramid_capstone import api

@api.get('/users/{user_id}')
def get_user(request, user_id: int) -> dict:
    return {"id": user_id, "name": "John Doe"}

@api.post('/users')
def create_user(request, name: str, email: str) -> dict:
    # Parameters automatically extracted and validated from JSON body
    return {"message": "User created", "name": name, "email": email}

# Pyramid app setup
def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_capstone')
    config.scan()
    return config.make_wsgi_app()
```

That's it! No manual schema definitions, no boilerplate validation code.

## 🏃‍♂️ Quick Start

### Installation

```bash
pip install pyramid-capstone
```

### Basic Setup

```python
from pyramid.config import Configurator
from pyramid_capstone import api

# Include the library in your Pyramid app
def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_capstone')
    
    # Scan for your decorated views
    config.scan()
    
    return config.make_wsgi_app()
```

## 🎯 Why Choose pyramid-capstone?

pyramid-capstone combines Pyramid's enterprise-grade foundation with modern developer experience:

| Feature | pyramid-capstone | Pure Pyramid | Pure Cornice |
|---------|------------------------|---------------|--------------|
| **Developer Experience** | ✅ Modern + Simple | ✅ Minimal | ⚠️ Schema-heavy |
| **Auto Validation** | ✅ Type-hint based | ❌ Manual setup | ✅ Schema-based |
| **OpenAPI Docs** | ✅ Auto-generated | ❌ Manual | ⚠️ Limited |
| **Production Readiness** | ✅ Pyramid foundation | ✅ Battle-tested | ✅ Pyramid foundation |
| **Security & Auth** | ✅ Full Pyramid power | ✅ Comprehensive | ✅ Full Pyramid power |
| **Flexibility** | ✅ Pyramid's strength | ✅ Maximum | ✅ Pyramid's strength |
| **Learning Curve** | ✅ Gentle enhancement | ⚠️ Framework mastery | ⚠️ Schema complexity |

**The Best of Both Worlds**: Get Pyramid's proven robustness, security, and flexibility with the convenience of automatic validation and documentation.

## 📚 Learn More

- **[📖 Full Documentation](https://tomascorrea.github.io/pyramid-capstone/)** - Complete guides and API reference
- **[🚀 Getting Started](https://tomascorrea.github.io/pyramid-capstone/getting-started/)** - Step-by-step tutorial
- **[💡 Examples](examples/blog_api/)** - Complete blog API example with advanced features
- **[🔒 Security Guide](https://tomascorrea.github.io/pyramid-capstone/security/)** - Authentication and authorization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.rst) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.