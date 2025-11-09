# 🎯 CrossBow Security Agent

**AI-Powered Security Testing Platform with 18 Specialized Security Agents**

[![PyPI version](https://badge.fury.io/py/crossbow-agent.svg)](https://badge.fury.io/py/crossbow-agent)
[![Python Versions](https://img.shields.io/pypi/pyversions/crossbow-agent.svg)](https://pypi.org/project/crossbow-agent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CrossBow is a comprehensive AI-powered security testing platform that orchestrates 18 specialized security agents to perform advanced security assessments, threat analysis, and vulnerability testing.

## ✨ Features

### 🤖 18 Specialized Security Agents

1. **SOC Analyst** - Log analysis & attack investigation
2. **Threat Intelligence Analyst** - IOC collection & threat profiling
3. **Android SAST Specialist** - Android security testing
4. **Blue Team Defender** - Defensive security measures
5. **Bug Bounty Hunter** - Vulnerability discovery
6. **Security Developer** - Security code development
7. **DFIR Investigator** - Digital forensics & incident response
8. **Email Security Analyst** - Email threat analysis
9. **Memory Forensics Expert** - Memory analysis
10. **Network Security Analyst** - Network monitoring & analysis
11. **Red Team Operator** - Offensive security testing
12. **Replay Attack Specialist** - Attack replay analysis
13. **Security Reporter** - Report generation
14. **Vulnerability Validator** - Exploit verification
15. **Reverse Engineer** - Binary analysis
16. **RF Security Expert** - Radio frequency security
17. **WiFi Security Tester** - Wireless security
18. **Source Code Analyzer** - Static code analysis

### 🎨 Two Interfaces

- **CLI** - Traditional command-line interface
- **TUI** - Modern terminal UI with rich formatting (Textual-based)

### ⚙️ Advanced Capabilities

- **Multi-Model Support**: GPT-4o, Claude, Gemini
- **Conversation Memory**: Persistent context across sessions
- **Agent Storage**: State persistence for complex tasks
- **MCP Support**: Model Context Protocol integration
- **Auto-Configuration**: Settings automatically saved
- **40+ Security Tools**: Integrated security testing toolkit

## 🚀 Quick Start

### Installation

```bash
pip install crossbow-agent
```

### Basic Usage

**Start the CLI:**
```bash
crossbow
```

**Start the Modern TUI:**
```bash
crossbow-tui
```

### First Steps

1. **Configure your AI model** (choose from GPT-4o, Claude, Gemini)
2. **Enable features** (memory, storage, MCP as needed)
3. **Ask security questions** or give testing tasks

### Example Queries

```bash
# Security Analysis
"Analyze authentication logs for suspicious activity"

# Threat Intelligence
"Research IP address 192.168.1.100 for malicious activity"

# Vulnerability Assessment
"Help me test my web application for SQL injection"

# Network Security
"Analyze this network traffic for anomalies"

# Code Security
"Review this Python code for security vulnerabilities"

# Incident Response
"Investigate this security incident and provide timeline"
```

## 📖 Documentation

### Configuration

CrossBow automatically saves your preferences in `crossbow_config.json`:

```json
{
  "model": "claude-sonnet-4-5",
  "memory": true,
  "storage": true,
  "mcp": false,
  "mcp_servers": []
}
```

All settings changes are automatically persisted!

### CLI Commands

```
/model     - Choose AI model
/memory    - Toggle conversation memory
/storage   - Toggle agent storage
/mcp       - Toggle MCP support
/config    - Show configuration
/status    - Show current session
/help      - Show help
/quit      - Exit
```

### TUI Features

The modern TUI provides:
- **Visual model selector** - Dropdown menu
- **Toggle buttons** - One-click feature control
- **Live status bar** - Real-time configuration display
- **Rich formatting** - Markdown, syntax highlighting
- **Keyboard shortcuts** - Efficient navigation
- **Color-coded panels** - Clear visual hierarchy

**Keyboard Shortcuts:**
- `Ctrl+C` - Quit
- `Ctrl+M` - Toggle memory
- `Ctrl+S` - Toggle storage
- `Ctrl+L` - Clear log
- `Enter` - Send message

## 🔧 Advanced Usage

### API Keys

CrossBow requires API keys for AI models:

```bash
# Set via environment variables
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
```

Or create a `.env` file:
```bash
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
```

### Programmatic Usage

```python
from Agent import SecurityAgentSystem

# Initialize
system = SecurityAgentSystem(
    model_name="claude-sonnet-4-5",
    use_memory=True,
    use_storage=True
)

# Run assessment
response = system.run_assessment(
    "Analyze this security issue...",
    stream=True
)
```

### With Memory Persistence

```python
system = SecurityAgentSystem(
    model_name="gpt-4o",
    use_memory=True,  # Enable conversation history
    use_storage=True  # Enable agent state persistence
)
```

## 🛠️ Available Tools

CrossBow agents have access to 40+ security tools:

**Network Tools:**
- nmap, netcat, curl, wget
- DNS tools (dig, nslookup, whois)
- Traffic analysis (tcpdump, tshark)

**Security Scanners:**
- nuclei (10,200+ templates)
- bandit (Python SAST)
- semgrep (multi-language SAST)

**Analysis Tools:**
- Log parsing (grep, awk, sed)
- File operations
- Code execution
- Web browsing

**And many more!**

## 🎯 Use Cases

### Security Operations Center (SOC)
- Log analysis and correlation
- Attack investigation
- Incident response
- Timeline reconstruction

### Threat Intelligence
- IOC collection and validation
- Threat actor profiling
- Threat hunting
- MITRE ATT&CK mapping

### Penetration Testing
- Vulnerability discovery
- Exploit development
- Attack simulation
- Security assessments

### Digital Forensics
- Memory analysis
- Disk forensics
- Network forensics
- Evidence collection

### Code Security
- Static code analysis
- Vulnerability detection
- Security code review
- Compliance checking

## 📊 Requirements

- **Python**: 3.9 or higher
- **Terminal**: 256 color support, UTF-8
- **API Keys**: For AI models (Anthropic, OpenAI, or Google)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

**Harish Santhanalakshmi Ganesan**
- Email: harishsg99@gmail.com
- GitHub: [@harishsg99](https://github.com/harishsg99)

## 🙏 Acknowledgments

Built with:
- [Agno](https://docs.agno.com/) - Agent orchestration
- [Textual](https://textual.textualize.io/) - Modern TUI framework
- [Rich](https://rich.readthedocs.io/) - Rich text formatting

## 📈 Project Status

CrossBow is actively maintained and under continuous development.

- ✅ 18 specialized security agents
- ✅ Multi-model AI support
- ✅ CLI and TUI interfaces
- ✅ Auto-configuration
- ✅ Comprehensive documentation

## 🔗 Links

- [PyPI Package](https://pypi.org/project/crossbow-agent/)
- [Documentation](https://github.com/harishsg99/crossbow-agent)
- [Issue Tracker](https://github.com/harishsg99/crossbow-agent/issues)

## ⚡ Quick Examples

### Example 1: Security Assessment
```bash
$ crossbow
crossbow-agent > Assess my web application for OWASP Top 10 vulnerabilities
```

### Example 2: Log Analysis
```bash
$ crossbow
crossbow-agent > Analyze /var/log/auth.log for brute force attempts
```

### Example 3: Threat Intelligence
```bash
$ crossbow
crossbow-agent > What are the latest IOCs for ransomware attacks?
```

### Example 4: Code Review
```bash
$ crossbow
crossbow-agent > Review this Python code for security issues
```

---

**Start securing your systems with AI-powered security agents today!** 🎯🔒
