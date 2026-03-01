# Contributing to pyRofex-to-Excel

Thank you for your interest in contributing to this project! This guide covers development setup, architecture, and best practices.

## 🚀 Development Setup

### Prerequisites

- Python 3.9 or higher
- Microsoft Excel (for xlwings integration)
- Windows OS (recommended for Excel integration)
- Git for version control

### Installation for Development

#### Modern Editable Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/ChuchoCoder/pyRofex-to-Excel.git
cd pyRofex-to-Excel

# Create & activate a virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# Install package in editable mode with dev extras
pip install -e ".[dev]"
```

#### Manual Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install project + dev extras from pyproject.toml
pip install -e ".[dev]"
```

## 📦 Dependency Management

This project uses modern Python dependency management via `pyproject.toml`:

### Files Overview

- **`pyproject.toml`** - Modern Python project configuration (PEP 518/621)
- **`setup.ps1`** - PowerShell setup script for Windows users
- **`Makefile`** - Unix-style command shortcuts

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pyRofex | ≥0.5.0 | Market data API integration |
| xlwings | ≥0.31.0 | Excel integration |
| pandas | ≥2.0.0 | Data manipulation |
| python-dotenv | ≥1.0.0 | Environment variable management |
| python-dateutil | ≥2.8.0 | Date/time utilities |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| ruff | ≥0.1.0 | Modern linting and formatting |
| mypy | ≥1.0.0 | Static type checking |
| pre-commit | ≥3.0.0 | Git hooks for code quality |

## 🛠️ Development Commands

### Core Dev Tasks (Modern Way)

```bash
pip install -e ".[dev]"   # Install dev dependencies
ruff check .               # Lint
ruff format .              # Auto-format
mypy src/pyRofex_To_Excel      # Type check
pytest                     # (When tests added)
```

### PowerShell Convenience (Optional)

```powershell
# Activate environment first
.venv\Scripts\activate
ruff check .
ruff format .
mypy src/pyRofex_To_Excel
```

### Using Make (Unix/Linux/Mac)

```bash
make install-dev             # Install development dependencies
make lint                    # Run linting
make format                  # Format code
make type-check             # Run type checking
make quality                # Run all quality checks
```

## 📁 Project Structure

```text
pyRofex_To_Excel/
├── pyproject.toml          # Modern project configuration
├── setup.ps1              # PowerShell helper commands
├── Makefile               # Unix command shortcuts
│
├── src/pyRofex_To_Excel/      # Main application package
│   ├── __init__.py
│   ├── main.py           # Application entry point
│   ├── config/           # Configuration modules
│   │   ├── __init__.py
│   │   ├── excel_config.py
│   │   └── pyrofex_config.py
│   ├── market_data/      # Market data operations
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── websocket_handler.py
│   │   └── data_processor.py
│   ├── excel/            # Excel operations
│   │   ├── __init__.py
│   │   ├── workbook_manager.py
│   │   ├── symbol_loader.py
│   │   └── sheet_operations.py
│   └── utils/            # Utility functions
│       ├── __init__.py
│       ├── logging.py
│       ├── validation.py
│       └── helpers.py
│
├── tools/                # Development tools
│   ├── create_configs.py # Configuration migration utility
│   ├── validate_system.py
│   ├── validate_quickstart.py
│   └── check_tickers.py
│
├── data/                 # Data files
│   └── cache/           # Instrument cache storage
│       └── instruments_cache.json
│
├── tests/               # Test suite
│   ├── __init__.py
│   └── conftest.py
│
├── docs/                # Documentation
│   ├── STRUCTURE_PROPOSAL.md
│   ├── MIGRATION_STATUS.md
│   └── specs/          # Feature specifications
│
├── .env.example        # Environment variable template
├── pyRofex-Market-Data.xlsb  # Excel workbook
├── .gitignore          # Git ignore patterns
├── README.md           # User documentation (Spanish)
└── CONTRIBUTING.md     # Developer documentation (English)
```

> Legacy monolithic files (`main_HM.py`, `Options_Helper_HM.py`) were removed after migration.

## 🐛 Debugging in VS Code

The project includes pre-configured debug configurations in `.vscode/launch.json`:

1. **Python: pyRofex-to-Excel (Main)** - Debug the main application (looks for `.env` in root)
2. **Python: Validation Script** - Debug the validation tool
3. **Python: Create Configs** - Debug config generation

**Quick Start:**

1. Open the project in VS Code
2. Set breakpoints in your code (click left of line numbers)
3. Press `F5` or go to Run → Start Debugging
4. Select "Python: pyRofex-to-Excel (Main)" from the dropdown

**Debug Features:**

- Step through code line by line (`F10` = step over, `F11` = step into)
- Inspect variables in the Variables pane
- Watch expressions in the Watch pane
- View call stack and breakpoints
- Use Debug Console for runtime evaluation

**Tips:**

- Set breakpoints in `src/pyRofex_To_Excel/main.py` initialization
- Check `api_client.py` for API connection issues
- Monitor `websocket_handler.py` for real-time data flow
- Use conditional breakpoints (right-click breakpoint) for specific scenarios

## ⚙️ Configuration Management

The application uses a modern configuration system:

1. **Configuration Modules (generated / maintained):**
   - `src/pyRofex_To_Excel/config/excel_config.py`
   - `src/pyRofex_To_Excel/config/pyrofex_config.py`

2. **Environment Variables:**
   - `.env` file in project root for local development
   - Environment variables override config files

3. **Security Features:**
   - Startup credential validation with descriptive failures
   - `.env` excluded via `.gitignore`
   - No plaintext password defaults retained

## 🔧 Environment Setup Validation

Check your setup with:

```bash
python tools/validate_system.py
```

Validates:

- ✅ Imports & package structure
- ✅ Entry point availability (`pyrofex-to-excel`)
- ✅ Config modules + environment template presence

## 🎯 Development Workflow

### Standard Workflow

```bash
# 1. Install in development mode
pip install -e ".[dev]"

# 2. Copy & edit environment
copy .env.example .env
notepad .env

# 3. (Optional) generate config stubs
python tools/create_configs.py

# 4. Make your changes
# ... edit code ...

# 5. Run quality checks
ruff check .
ruff format .
mypy src/pyRofex_To_Excel

# 6. Test your changes
pyrofex-to-excel

# 7. Commit
git add .
git commit -m "Your descriptive message"
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:

```bash
pre-commit install
```

This will automatically run:
- Code formatting (ruff)
- Linting (ruff)
- Type checking (mypy)

## 🔒 Security Considerations

- **Never commit `.env` files** - Contains sensitive credentials
- **Set appropriate file permissions** on configuration files
- **Use environment variables** in production deployments
- **Regularly rotate API credentials**
- **Review security implications** of any changes to authentication/API code

## 📋 Troubleshooting

### Common Issues

1. **Import errors:**

   ```bash
   pip install -e .
   pip install -e ".[dev]"
   ```

2. **Excel connection issues:**
   - Ensure Excel is installed and accessible
   - Check file permissions on Excel workbook
   - Verify xlwings installation

3. **API authentication errors:**
   - Verify credentials in `.env` file
   - Check pyRofex API status
   - Validate account permissions

### Development Tools

1. **Run validation suite:**

   ```bash
   python tools/validate_system.py
   ```

2. **Run configuration migration:**

   ```bash
   python tools/create_configs.py
   ```

3. **Upgrade dependencies:**

   ```bash
   .\setup.ps1 upgrade
   ```

## 🤝 Contributing Guidelines

1. **Setup development environment:**

   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

2. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**
   - Follow existing code style
   - Add type hints where appropriate
   - Update documentation as needed

4. **Run quality checks:**

   ```bash
   ruff check .
   ruff format .
   mypy src/pyRofex_To_Excel
   ```

5. **Test your changes:**

   ```bash
   pyrofex-to-excel
   python tools/validate_system.py
   ```

6. **Commit with descriptive messages:**

   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

7. **Push and create a pull request:**

   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Code Style

- Follow PEP 8 conventions
- Use type hints for function signatures
- Write docstrings for public functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable names

## 🧪 Testing

While the test suite is still being developed, please:

- Manually test your changes thoroughly
- Verify Excel integration works correctly
- Test API connectivity and data flow
- Check for edge cases and error handling

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support for Developers

For development issues:

- Run `python tools/validate_system.py` to validate setup
- Review `src/pyRofex_To_Excel/config/` modules
- Ensure `.env` is present with populated credentials
- Confirm virtual environment is active
- Check the `docs/` folder for architecture documentation

