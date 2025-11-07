# Changelog

All notable changes to KaliAI will be documented in this file.

## [2.0.0] - 2025-11-07

### 🚀 New Features

#### Command Templates Library
- Added 15+ pre-built command templates across 7 categories
- Template categories: reconnaissance, web-application, database, password-attack, wireless, sniffing, exploitation
- Risk level indicators (low, medium, high) for each template
- Parameter guidance and usage examples
- CLI commands: `templates list`, `templates show`, `templates use`, `templates categories`

#### Playbook System  
- Create, save, and replay multi-step security testing workflows
- Interactive and automated execution modes
- Built-in default playbooks for common scenarios
- Export playbooks to Markdown for documentation
- Step-by-step progress tracking with results logging
- CLI commands: `playbooks list`, `playbooks show`, `playbooks execute`, `playbooks create`

#### Target Validation
- DNS resolution and hostname validation
- Private/Public IP detection
- Reachability checks via ping
- Network range validation (CIDR notation)
- Scope confirmation prompts
- Common issue detection (localhost, cloud IPs, gateways)
- CLI command: `validate <target>`

### 🔒 Security Fixes

#### Critical
- **Command Injection Vulnerability Fixed**: Replaced `shell=True` with `shell=False` and `shlex.split()`
- Added command timeout protection (5 minutes)
- Improved input validation and sanitization

#### Cross-Platform
- Replaced Unix `which` command with `shutil.which()` for Windows/Linux/Mac compatibility
- Fixed file path issues on Windows (colon characters in timestamps)
- Added platform-specific ping parameter detection

#### Error Handling
- Added comprehensive try-except blocks around file I/O
- Added specific exception handling for subprocess operations
- UTF-8 encoding specification for all file operations
- Improved error messages for debugging

#### Code Quality
- Fixed logging handler duplication
- Updated type hints for Python 3.8 compatibility (`Tuple` instead of `tuple[]`)
- Added command parsing validation
- Improved null/empty string handling

### ⚙️ Configuration Changes

- **Default Model**: Changed from `gpt-4` to `gpt-3.5-turbo` (10x cheaper, still effective)
- Users can still configure `gpt-4` via settings if needed

### 📁 Project Management

- Added comprehensive `.gitignore` file
- Created `SECURITY_FIXES.md` documentation
- Created `NEW_FEATURES.md` user guide
- Added this `CHANGELOG.md`

### 🐛 Bug Fixes

- Fixed file I/O errors on Windows systems
- Fixed logging handler multiplication on repeated initialization
- Fixed command parsing edge cases
- Fixed empty command validation

### 📚 Documentation

- Updated main README with new features
- Added comprehensive feature documentation in `NEW_FEATURES.md`
- Added security fixes documentation in `SECURITY_FIXES.md`
- Improved inline code documentation

### 🔧 Developer Changes

- New modules: `kaliagent/templates/`, `kaliagent/playbooks/`, `kaliagent/utils/target_validator.py`
- Enhanced CLI with new command groups
- Improved code organization and modularity

---

## [1.0.0] - 2025-11-06

### Initial Release

- Basic KaliAI agent with OpenAI integration
- Command execution with safe mode
- Interactive chat interface
- Support for common Kali Linux tools
- Basic configuration management
- Demo scripts

---

## Legend

- 🚀 New Features
- 🔒 Security Fixes
- 🐛 Bug Fixes
- ⚙️ Configuration Changes
- 📚 Documentation
- 🔧 Developer Changes
- ⚠️ Breaking Changes
- 🗑️ Deprecated Features

---

**Note**: Version numbers follow [Semantic Versioning](https://semver.org/)
