# 🚀 KaliAI New Features Guide

This guide covers the new features added to KaliAI v2.0.

## 📋 Table of Contents

1. [Command Templates Library](#command-templates-library)
2. [Playbook System](#playbook-system)
3. [Target Validation](#target-validation)
4. [Quick Start Examples](#quick-start-examples)

---

## 1. Command Templates Library

Pre-built, categorized command templates with AI explanations for common security testing scenarios.

### Features
- **15+ Built-in Templates** across multiple categories
- **Risk Level Indicators** (Low, Medium, High)
- **Parameter Guidance** with examples
- **Category Filtering**

### Usage

#### List All Templates
```bash
kaliagent templates list
```

#### List Templates by Category
```bash
kaliagent templates list --category web-application
kaliagent templates list --category reconnaissance
```

#### View Template Categories
```bash
kaliagent templates categories
```

#### Show Template Details
```bash
kaliagent templates show network-discovery
kaliagent templates show web-scan-basic
```

#### Use a Template
```bash
# Generate command (without executing)
kaliagent templates use port-scan-basic -p target=192.168.1.10

# Generate and execute command
kaliagent templates use port-scan-basic -p target=192.168.1.10 --execute
```

### Available Categories

- **reconnaissance**: Network discovery, port scanning, OS detection
- **web-application**: Web server scanning, directory enumeration, WordPress testing
- **database**: SQL injection testing, database enumeration
- **password-attack**: SSH brute force, HTTP form attacks
- **wireless**: WiFi monitoring, network scanning
- **sniffing**: Traffic capture, packet analysis
- **exploitation**: Metasploit, exploitation frameworks

### Example Templates

1. **network-discovery** - Quick host discovery
2. **port-scan-basic** - Standard port scanning
3. **web-scan-basic** - Basic web vulnerability scan
4. **directory-enumeration** - Find hidden directories
5. **sql-injection-test** - Test for SQL injection
6. **ssh-bruteforce** - SSH password attack
7. **wifi-scan** - Wireless network discovery

---

## 2. Playbook System

Save, organize, and replay multi-step security testing workflows.

### Features
- **Step-by-Step Workflows** for common testing scenarios
- **Interactive Execution** with prompts before each step
- **Progress Tracking** and result logging
- **Export to Markdown** for documentation
- **Built-in Default Playbooks**

### Usage

#### List Available Playbooks
```bash
kaliagent playbooks list
```

#### Show Playbook Details
```bash
kaliagent playbooks show web_application_pentest.json
```

#### Create a New Playbook
```bash
kaliagent playbooks create
# Follow the interactive prompts
```

#### Add Steps to Current Playbook
```bash
kaliagent playbooks add-step
```

#### Execute a Playbook
```bash
# Interactive mode (prompts before each step)
kaliagent playbooks execute web_application_pentest.json

# Auto mode (runs all steps)
kaliagent playbooks execute web_application_pentest.json --auto

# Start from specific step
kaliagent playbooks execute web_application_pentest.json --start-step 3
```

#### Export Playbook to Markdown
```bash
kaliagent playbooks export web_application_pentest.json --output report.md
```

### Default Playbooks

#### 1. Web Application Pentest
Complete workflow for web application security testing:
1. Service identification (nmap)
2. Vulnerability scanning (nikto)
3. Directory enumeration (dirb)
4. SQL injection testing (sqlmap)

#### 2. Network Reconnaissance
Comprehensive network discovery:
1. Host discovery
2. Port scanning
3. Service version detection
4. OS fingerprinting

### Playbook Structure

```json
{
  "name": "My Custom Playbook",
  "description": "Description of the workflow",
  "author": "Your Name",
  "category": "web-application",
  "target_type": "web-app",
  "tags": ["owasp", "web", "security"],
  "steps": [
    {
      "command": "nmap -sV {target}",
      "description": "Scan for services",
      "expected_outcome": "List of running services",
      "notes": "Optional notes"
    }
  ]
}
```

---

## 3. Target Validation

Validate targets before scanning to ensure they're in scope and prevent accidents.

### Features
- **DNS Resolution** for hostnames
- **Private/Public IP Detection**
- **Reachability Checks** (ping)
- **Network Range Validation** (CIDR)
- **Scope Confirmation Prompts**
- **Common Issue Detection**

### Usage

#### Validate a Single Target
```bash
kaliagent validate 192.168.1.10
kaliagent validate example.com
```

#### Validate Network Range
```bash
kaliagent validate 192.168.1.0/24 --network
```

#### Skip Reachability Check
```bash
kaliagent validate example.com --no-ping
```

#### Allow Only Public IPs
```bash
kaliagent validate target.com --no-private
```

### What It Checks

✅ **DNS Resolution**: Can the hostname be resolved?  
✅ **IP Type**: Is it private (RFC1918) or public?  
✅ **Reachability**: Can the target be pinged?  
✅ **Format Validation**: Is the IP/hostname format valid?  
✅ **Common Issues**: Localhost, cloud providers, gateway IPs  

### Example Output

```
Target Validation
Target: example.com
Type: hostname
IP Address: 93.184.216.34
Network: Public
Status: Reachable

IMPORTANT: Only scan systems you have explicit permission to test.
Unauthorized scanning may be illegal in your jurisdiction.

Do you have authorization to scan this target? (yes/no):
```

---

## 4. Quick Start Examples

### Example 1: Web Application Scan
```bash
# 1. List web application templates
kaliagent templates list --category web-application

# 2. Validate target
kaliagent validate myapp.com

# 3. Use template to scan
kaliagent templates use web-scan-basic -p target=http://myapp.com --execute
```

### Example 2: Network Discovery
```bash
# 1. Validate network range
kaliagent validate 192.168.1.0/24 --network

# 2. Use discovery template
kaliagent templates use network-discovery -p network=192.168.1.0/24 --execute

# 3. Scan discovered hosts
kaliagent templates use port-scan-basic -p target=192.168.1.10 --execute
```

### Example 3: Run a Complete Playbook
```bash
# 1. List available playbooks
kaliagent playbooks list

# 2. Show playbook details
kaliagent playbooks show web_application_pentest.json

# 3. Execute playbook interactively
kaliagent playbooks execute web_application_pentest.json

# 4. Export results to markdown
kaliagent playbooks export web_application_pentest.json --output pentest_report.md
```

### Example 4: Create Custom Workflow
```bash
# 1. Create new playbook
kaliagent playbooks create
# Name: My Custom Test
# Description: Custom security test workflow
# Category: custom
# Target Type: mixed

# 2. Add steps
kaliagent playbooks add-step
# Command: nmap -sV {target}
# Description: Service scanning
# Expected: List of services

# 3. Save playbook
kaliagent playbooks save my_custom_test.json

# 4. Execute later
kaliagent playbooks execute my_custom_test.json
```

---

## 🎯 Best Practices

### 1. Always Validate Targets
```bash
# Before any scan
kaliagent validate <target>
```

### 2. Use Templates for Consistency
```bash
# Instead of typing commands manually
kaliagent templates use <template-name>
```

### 3. Document with Playbooks
```bash
# Save successful workflows
kaliagent playbooks create
# Export for reports
kaliagent playbooks export <playbook> --output report.md
```

### 4. Start with Low Risk
```bash
# Use low-risk templates first
kaliagent templates list | grep "LOW"
```

### 5. Review Before Executing
```bash
# Generate command first (without --execute)
kaliagent templates use <template> -p param=value
# Review, then add --execute if safe
```

---

## 🔒 Security Reminders

⚠️ **Authorization Required**: Only scan systems you have explicit permission to test

⚠️ **Legal Compliance**: Unauthorized scanning may be illegal

⚠️ **Safe Mode**: KaliAI runs in safe mode by default (no command execution)

⚠️ **Documentation**: Always document your testing activities

⚠️ **Ethical Use**: Follow responsible disclosure practices

---

## 📚 Additional Resources

- [Main README](../README.md)
- [Security Fixes Documentation](../SECURITY_FIXES.md)
- [Configuration Guide](../docs/configuration.md)

---

## 🐛 Troubleshooting

### Templates Not Found
```bash
# Reinstall package
pip install -e .
```

### Playbooks Not Loading
```bash
# Check playbooks directory
ls ~/.kaliagent/playbooks/

# Create default playbooks
python -c "from kaliagent.playbooks import create_default_playbooks, PlaybookManager; from pathlib import Path; create_default_playbooks(PlaybookManager(Path.home() / '.kaliagent' / 'playbooks'))"
```

### Validation Fails
```bash
# Check network connectivity
ping <target>

# Check DNS
nslookup <target>

# Skip validation if needed (not recommended)
kaliagent analyze "<command>" --skip-validation
```

---

**Version**: 2.0  
**Last Updated**: November 7, 2025
