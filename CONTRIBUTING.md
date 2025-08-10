# Contributing to LumiSync

Thank you for your interest in contributing to LumiSync! This document provides guidelines and information for contributors.

## 🌟 Ways to Contribute

- **Bug Reports** - Help us identify and fix issues
- **Feature Requests** - Suggest new functionality
- **Code Contributions** - Submit pull requests
- **Documentation** - Improve guides and documentation
- **Testing** - Test on different distributions
- **Translations** - Help localize the application

## 🚀 Getting Started

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/lumi-sync.git
   cd lumi-sync
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/ -v
   ```

### Project Structure

```
lumisync/
├── lumisync/           # Main application package
│   ├── core/          # Core backup/restore logic
│   ├── gui/           # User interface components
│   ├── utils/         # Utility functions
│   ├── config/        # Configuration management
│   └── cloud_providers/ # Cloud storage integrations
├── tests/             # Test suite
├── docs/              # Documentation
└── assets/            # Icons and resources
```

## 📝 Coding Standards

### Python Style Guide

- Follow **PEP 8** style guidelines
- Use **type hints** for function parameters and return values
- Write **docstrings** for all public functions and classes
- Maximum line length: **88 characters** (Black formatter)

### Code Quality Tools

We use the following tools to maintain code quality:

```bash
# Format code
black lumisync/

# Sort imports
isort lumisync/

# Lint code
flake8 lumisync/

# Type checking
mypy lumisync/
```

### Example Code Style

```python
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages backup operations for Linux settings."""
    
    def __init__(self, cloud_provider: str) -> None:
        """Initialize backup manager.
        
        Args:
            cloud_provider: Name of the cloud storage provider
        """
        self.cloud_provider = cloud_provider
        self.logger = logger
    
    def create_backup(
        self, 
        categories: List[str],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Create a backup of selected categories.
        
        Args:
            categories: List of categories to backup
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing backup information
            
        Raises:
            BackupError: If backup operation fails
        """
        try:
            # Implementation here
            pass
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            raise BackupError(f"Failed to create backup: {e}")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_backup_manager.py

# Run with coverage
python -m pytest --cov=lumisync tests/
```

### Writing Tests

- Write tests for all new functionality
- Use **pytest** framework
- Mock external dependencies
- Test both success and failure cases

Example test:

```python
import pytest
from unittest.mock import Mock, patch
from lumisync.core.backup_manager import BackupManager

class TestBackupManager:
    """Test cases for BackupManager."""
    
    def test_create_backup_success(self):
        """Test successful backup creation."""
        manager = BackupManager("google_drive")
        
        with patch('lumisync.core.backup_manager.create_cloud_provider') as mock_provider:
            mock_provider.return_value.upload.return_value = True
            
            result = manager.create_backup(['gnome_settings'])
            
            assert result['status'] == 'success'
            assert 'backup_id' in result
    
    def test_create_backup_failure(self):
        """Test backup creation failure."""
        manager = BackupManager("google_drive")
        
        with patch('lumisync.core.backup_manager.create_cloud_provider') as mock_provider:
            mock_provider.return_value.upload.side_effect = Exception("Upload failed")
            
            with pytest.raises(BackupError):
                manager.create_backup(['gnome_settings'])
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **System Information**
   - Operating System and version
   - Python version
   - LumiSync version
   - Desktop environment

2. **Steps to Reproduce**
   - Detailed steps to reproduce the issue
   - Expected behavior
   - Actual behavior

3. **Logs and Screenshots**
   - Application logs (from Logs tab)
   - Screenshots if applicable
   - Error messages

4. **Additional Context**
   - Any other relevant information

## 💡 Feature Requests

For feature requests, please provide:

1. **Problem Description**
   - What problem does this solve?
   - Who would benefit from this feature?

2. **Proposed Solution**
   - Detailed description of the feature
   - How should it work?

3. **Alternatives Considered**
   - Other solutions you've considered
   - Why this approach is preferred

## 🔄 Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test Your Changes**
   ```bash
   python -m pytest
   flake8 lumisync/
   mypy lumisync/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new backup category support"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use conventional commit format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks

## 🌍 Internationalization

Help us make LumiSync available in more languages:

1. **Adding New Language**
   ```bash
   # Create new translation file
   cp lumisync/i18n/en.json lumisync/i18n/YOUR_LANGUAGE.json
   ```

2. **Translate Strings**
   - Translate all text strings
   - Keep placeholders intact
   - Test with your language

3. **Update Language List**
   - Add your language to supported languages
   - Update documentation

## 📚 Documentation

### Types of Documentation

- **User Documentation** - Installation, usage guides
- **Developer Documentation** - API docs, architecture
- **Code Documentation** - Docstrings, comments

### Documentation Standards

- Use **Markdown** for documentation files
- Include code examples
- Keep documentation up-to-date with code changes
- Use clear, concise language

## 🏆 Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** page

## 📞 Getting Help

- **GitHub Discussions** - General questions and ideas
- **GitHub Issues** - Bug reports and feature requests
- **Discord Server** - Real-time chat and support
- **Email** - Direct contact for sensitive issues

## 📄 License

By contributing to LumiSync, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to LumiSync! Together, we're making Linux settings synchronization better for everyone. 🚀
