# 🎯 CrossBow Security Agent

**World's First Fully Autonomous AI Security Engineer**

[![PyPI version](https://badge.fury.io/py/crossbow-agent.svg)](https://badge.fury.io/py/crossbow-agent)
[![Python Versions](https://img.shields.io/pypi/pyversions/crossbow-agent.svg)](https://pypi.org/project/crossbow-agent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CrossBow is a revolutionary AI-powered autonomous security engineer that can perform everything a human security expert does—from ethical hacking to malware analysis, from securing applications to solving CTF challenges. It's your complete AI security team in a single command.

## 🚀 Why CrossBow?

**Replace an entire security team** with one AI agent. CrossBow can:
- 🔓 **Hack anything** - Websites, IoT devices, networks, applications (ethically)
- 🛡️ **Secure everything** - Audit and harden your applications before production
- 🔍 **Investigate incidents** - Analyze breaches and identify attack vectors
- 🦠 **Reverse engineer malware** - Disassemble, analyze, and create detection rules
- 🏆 **Dominate CTFs** - Solve complex security challenges automatically
- ⚡ **Work 24/7** - Never sleeps, never tires, always learning

**What took hours or days now takes minutes.** CrossBow is trained on thousands of security scenarios and has access to professional security tools, making it more comprehensive than most human security teams.

## ✨ What CrossBow Can Do

CrossBow replicates the complete skill set of an expert security engineer, capable of:

### 🔓 Offensive Security
- **Ethical Website Hacking** - Discover and exploit vulnerabilities in web applications, APIs, and services
- **IoT Device Penetration** - Hack into IoT devices like cameras, routers, smart home devices (ethically)
- **Network Penetration Testing** - Break into networks, find misconfigurations, exploit weaknesses
- **Mobile App Security Testing** - Android & iOS security assessment and exploitation
- **Wireless Security Testing** - WiFi hacking, Bluetooth exploitation, RF analysis

### 🛡️ Defensive Security
- **Pre-Production Security Hardening** - Secure your applications before shipping to production
- **Vulnerability Assessment** - Comprehensive security scanning and vulnerability discovery
- **Security Code Review** - Static and dynamic code analysis for security flaws
- **Configuration Auditing** - Identify misconfigurations and security weaknesses
- **Threat Modeling** - Identify potential attack vectors and security risks

### 🔍 Incident Response & Forensics
- **Attack Investigation** - Investigate security breaches and incidents you've faced
- **Log Analysis** - Deep dive into logs to find attack patterns and indicators
- **Timeline Reconstruction** - Rebuild attack sequences and identify entry points
- **Memory Forensics** - Analyze memory dumps to find malicious activity
- **Network Traffic Analysis** - Detect anomalies and malicious communications

### 🦠 Malware Analysis
- **Reverse Engineering** - Disassemble and analyze malware binaries
- **Detection Rule Writing** - Create YARA rules, Sigma rules, and IDS signatures
- **Behavioral Analysis** - Understand malware behavior and capabilities
- **Threat Intelligence** - Extract IOCs and track threat actors

### 🏆 Competitive Security
- **CTF Solver** - Automatically solve Capture The Flag challenges
- **Bug Bounty Hunting** - Find vulnerabilities worthy of bug bounty rewards
- **Security Research** - Discover new attack techniques and vulnerabilities

### 📊 Reporting & Compliance
- **Automated Security Reports** - Generate professional security assessment reports
- **Compliance Checking** - OWASP Top 10, CIS benchmarks, security standards
- **Risk Assessment** - Evaluate and prioritize security risks

### 🧠 Powered by Advanced AI

- **Multi-Model Support**: GPT-4o, Claude Sonnet, Gemini
- **18 Specialized Agents**: Coordinated multi-agent system working together
- **40+ Security Tools**: Integrated arsenal of professional security tools
- **Autonomous Decision Making**: Intelligently chains tools and techniques
- **Learning & Adaptation**: Improves with each security task

### 🎨 Two Powerful Interfaces

- **CLI** - Traditional command-line interface for scripting and automation
- **TUI** - Modern terminal UI with rich formatting and visual feedback

### ⚙️ Enterprise Features

- **Conversation Memory**: Context-aware across complex multi-step operations
- **State Persistence**: Resume complex security assessments
- **MCP Support**: Model Context Protocol for extended capabilities
- **Auto-Configuration**: Settings automatically saved and restored
- **Fully Autonomous**: Minimal human intervention required

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

### Example Tasks

```bash
# Ethical Hacking
"Hack into this website and find all vulnerabilities: example.com"
"Find ways to compromise this IoT camera at 192.168.1.50"
"Break into this web application and identify OWASP Top 10 issues"

# Pre-Production Security
"Security audit my application before production deployment"
"Find all security issues in this codebase and suggest fixes"
"Harden the security configuration of my web server"

# Incident Investigation
"Investigate the security breach we faced last week"
"Analyze these logs and tell me how the attacker got in"
"Reconstruct the attack timeline from these artifacts"

# Malware Analysis
"Reverse engineer this malware binary and explain what it does"
"Write YARA rules to detect this malware family"
"Analyze this suspicious file and extract IOCs"

# CTF Challenges
"Solve this CTF challenge: [challenge description]"
"Help me with this reverse engineering CTF"
"Exploit this binary and capture the flag"

# Network Security
"Hack into this network and document all vulnerabilities"
"Analyze this packet capture for malicious activity"
"Find weaknesses in this wireless network configuration"
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

## 🎯 Real-World Applications

### For Security Professionals
- **Penetration Testers** - Automate reconnaissance, vulnerability discovery, and exploitation
- **Red Teamers** - Plan and execute sophisticated attack simulations
- **Bug Bounty Hunters** - Find vulnerabilities faster and more comprehensively
- **Security Researchers** - Discover new attack techniques and security issues

### For Development Teams
- **DevSecOps** - Integrate security into CI/CD pipelines
- **Security Audits** - Pre-production security assessments
- **Code Reviews** - Automated security code analysis
- **Vulnerability Remediation** - Fix security issues before deployment

### For Incident Responders
- **Breach Investigation** - Rapid incident analysis and containment
- **Forensic Analysis** - Deep dive into security incidents
- **Threat Hunting** - Proactive threat detection
- **Attack Attribution** - Identify threat actors and TTPs

### For CTF Players & Students
- **Learning Platform** - Learn security concepts through practice
- **CTF Competition** - Solve challenges faster with AI assistance
- **Skill Development** - Improve hacking and security skills
- **Challenge Creation** - Generate security challenges for practice

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

## ⚡ Real-World Examples

### Example 1: Ethical Website Hacking
```bash
$ crossbow
crossbow-agent > Hack into https://testsite.com ethically and document all vulnerabilities
[CrossBow performs reconnaissance, vulnerability scanning, exploitation attempts]
[Generates comprehensive report with findings and remediation steps]
```

### Example 2: IoT Device Security Testing
```bash
$ crossbow
crossbow-agent > Test the security of this IoT camera at 192.168.1.100
[CrossBow analyzes firmware, finds default credentials, tests for vulnerabilities]
[Demonstrates exploitation paths and provides hardening recommendations]
```

### Example 3: Pre-Production Security
```bash
$ crossbow
crossbow-agent > Security audit my application before deploying to production
[CrossBow performs comprehensive security assessment]
[Identifies vulnerabilities, misconfigurations, and security weaknesses]
[Provides prioritized remediation plan]
```

### Example 4: Attack Investigation
```bash
$ crossbow
crossbow-agent > Investigate the breach from last night - logs are in /var/log/
[CrossBow analyzes logs, identifies attack vectors, reconstructs timeline]
[Provides detailed incident report with IOCs and remediation steps]
```

### Example 5: Malware Reverse Engineering
```bash
$ crossbow
crossbow-agent > Reverse engineer malware.bin and write detection rules
[CrossBow disassembles binary, analyzes behavior, extracts IOCs]
[Generates YARA rules, Sigma rules, and detection signatures]
```

### Example 6: CTF Challenge Solving
```bash
$ crossbow
crossbow-agent > Solve this CTF challenge: [binary exploitation challenge]
[CrossBow analyzes challenge, finds vulnerability, develops exploit]
[Captures flag and explains exploitation technique]
```

---

**Start securing your systems with AI-powered security agents today!** 🎯🔒
