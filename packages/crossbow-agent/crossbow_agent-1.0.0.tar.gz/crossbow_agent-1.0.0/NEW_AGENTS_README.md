# New Security Agents - SOC and Threat Intelligence

## Overview

Two new specialized security agents have been added to the CrossBow Security Agent System:

1. **SOC Agent** - Security Operations Center Specialist
2. **Threat Intelligence Agent** - Cyber Threat Intelligence Analyst

Both agents are fully integrated with the existing 16 security agents and have access to all security tools.

## What's New

### 1. SOC Agent (Security Operations Center)

**Primary Focus:** Log analysis and attack investigation

**Key Capabilities:**
- **Log Analysis & Correlation**
  - Parse and analyze system logs, application logs, firewall logs, IDS/IPS logs
  - Correlate security events across different systems
  - Identify patterns and anomalies in log data
  - Extract IOCs from logs
  - Timeline reconstruction

- **Attack Investigation**
  - Investigate security incidents and breaches
  - Root cause analysis
  - Track attacker movement and lateral movement
  - Determine attack vectors and entry points
  - Assess incident scope and impact

- **Threat Detection & Monitoring**
  - Real-time monitoring for suspicious activities
  - Detect unauthorized access attempts
  - Identify malware infections and C2 communications
  - Monitor data exfiltration attempts
  - Track failed authentication and brute force attacks

- **Incident Response**
  - Coordinate with other security agents
  - Provide actionable intelligence
  - Create incident reports and timelines
  - Recommend containment and remediation

**Tools Available:**
- Log file analysis (grep, awk, sed, cut, sort, uniq)
- Network tools (netcat, nmap, tcpdump, tshark)
- JSON log parsing (jq)
- File operations and search
- Web investigation tools
- SAST tools for analyzing malicious scripts
- Encoding/decoding utilities

**Example Use Cases:**
```bash
# Analyze authentication logs for brute force
crossbow-agent > Analyze /var/log/auth.log for failed login attempts and suspicious IPs

# Investigate web server attack
crossbow-agent > Check Apache access logs for SQL injection attempts

# Data exfiltration detection
crossbow-agent > Look for unusual data transfer patterns in network logs

# Malware detection from logs
crossbow-agent > Search system logs for suspicious process execution
```

### 2. Threat Intelligence Agent

**Primary Focus:** IOC collection, threat actor profiling, and threat hunting

**Key Capabilities:**
- **IOC Collection & Analysis**
  - Collect and validate Indicators of Compromise
  - Track IOC relationships and campaigns
  - Maintain IOC databases
  - Identify false positives

- **Threat Actor Profiling**
  - Identify threat actor groups and their TTPs
  - Track APT groups and campaigns
  - Analyze attack patterns
  - Profile attacker infrastructure
  - Map to MITRE ATT&CK framework

- **Threat Hunting**
  - Proactively search for threats
  - Hunt based on threat intelligence
  - Identify unknown threats
  - Test detection rules
  - Discover new attack vectors

- **Intelligence Analysis**
  - Analyze threat trends
  - Assess threat relevance
  - Produce threat reports
  - Share intelligence with team
  - Provide strategic and tactical intelligence

**IOC Types Supported:**
- Network IOCs: IP addresses, domains, URLs
- File IOCs: MD5, SHA1, SHA256 hashes
- Email IOCs: Sender addresses, subject lines
- Behavioral IOCs: Attack patterns, TTPs

**Tools Available:**
- OSINT research and web search (DuckDuckGo)
- Network analysis tools (DNS, WHOIS, nmap)
- File analysis and hash checking
- Web browser for investigating URLs
- Log parsing for IOC extraction
- Code execution for analysis scripts
- Encoding/decoding utilities

**Example Use Cases:**
```bash
# Research suspicious IP
crossbow-agent > Research this IP for known malicious activity: 192.168.1.100

# IOC collection
crossbow-agent > Extract all IOCs from this incident log file

# Threat actor profiling
crossbow-agent > Profile the APT28 threat group and their recent campaigns

# Threat hunting
crossbow-agent > Hunt for IOCs related to ransomware attacks in our logs

# MITRE ATT&CK mapping
crossbow-agent > Map these observed behaviors to MITRE ATT&CK framework
```

## Installation & Configuration

### 1. Environment Setup

The Anthropic API key has been configured in `.env` file:
```bash
ANTHROPIC_API_KEY=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
```

### 2. Required Dependencies

All dependencies are already installed. If you need to reinstall:
```bash
pip install agno anthropic openai google-genai google-generativeai duckduckgo-search ddgs mcp paramiko sqlalchemy python-dotenv requests rich
```

### 3. Running the System

#### Option A: Interactive CLI
```bash
python3 crossbow_cli.py
```

Then use commands like:
```
crossbow-agent > Analyze my authentication logs for suspicious activity
crossbow-agent > Research this IP address: 192.168.1.100
crossbow-agent > Help me hunt for IOCs related to APT28
```

#### Option B: Python Script
```python
from Agent import SecurityAgentSystem

# Initialize with Claude model
system = SecurityAgentSystem(
    model_name="claude-sonnet-4-5",
    use_memory=False,
    use_storage=False
)

# Run a task - manager will delegate to appropriate agent
system.run_assessment("""
    Analyze the authentication logs at /var/log/auth.log
    for suspicious login patterns and potential brute force attacks.
""", stream=True)
```

#### Option C: Direct Agent Access
```python
from Agent import SecurityAgentSystem

system = SecurityAgentSystem(model_name="claude-sonnet-4-5")

# Get specific agent
soc_agent = system.get_agent("soc")
ti_agent = system.get_agent("threat_intel")

# Use the agent directly
# (requires more manual setup)
```

### 4. Testing the New Agents

Run the test script:
```bash
python3 test_new_agents.py
```

This demonstrates both agents' capabilities and provides usage examples.

## Architecture Changes

### Files Modified

1. **`/app/.env`** (NEW)
   - Added Anthropic API key

2. **`/app/src/prompts.py`**
   - Added `SOC_AGENT_PROMPT` with comprehensive SOC capabilities
   - Added `THREAT_INTELLIGENCE_AGENT_PROMPT` with CTI capabilities
   - Updated `CODE_AGENT` prompt

3. **`/app/Agent.py`**
   - Created `soc_agent` instance with all security tools
   - Created `threat_intelligence_agent` instance with all security tools
   - Added both agents to security team members list
   - Updated `get_agent()` method to support "soc", "threat_intel", "ti"

4. **`/app/crossbow_cli.py`**
   - Updated agent count from 16 to 18 in status display

5. **`/app/test_new_agents.py`** (NEW)
   - Comprehensive test script demonstrating new agents

6. **`/app/NEW_AGENTS_README.md`** (NEW)
   - This documentation file

## Agent Coordination

The new agents work seamlessly with existing agents:

- **SOC Agent** ↔ **Blue Team Agent**: Share defensive strategies
- **SOC Agent** ↔ **DFIR Agent**: Coordinate incident investigation
- **SOC Agent** ↔ **Network Analyzer**: Share traffic analysis
- **Threat Intelligence** ↔ **SOC Agent**: Share IOCs and intelligence
- **Threat Intelligence** ↔ **Bug Bounty**: Share vulnerability intelligence
- **Threat Intelligence** ↔ **Red Team**: Share attack techniques

The manager agent automatically delegates tasks to the most appropriate specialist(s).

## System Statistics

- **Total Agents:** 18 (up from 16)
- **Total Tools:** 40+ security tools available to all agents
- **Supported Models:** OpenAI GPT, Anthropic Claude, Google Gemini
- **Default Model:** Claude Sonnet 4.5
- **MCP Support:** Yes (optional)
- **Memory Support:** Yes (optional)
- **Storage Support:** Yes (optional)

## Example Scenarios

### Scenario 1: Investigating a Security Incident
```
User asks: "I see unusual login activity from IP 192.168.1.100"

Manager delegates to:
1. SOC Agent - Analyzes auth logs, identifies failed attempts
2. Threat Intelligence Agent - Researches IP reputation
3. Network Analyzer - Checks network traffic patterns
4. DFIR Agent - Preserves evidence and forensic analysis

Result: Complete incident investigation with IOCs and recommendations
```

### Scenario 2: Threat Hunting
```
User asks: "Hunt for signs of ransomware in our environment"

Manager delegates to:
1. Threat Intelligence Agent - Gets latest ransomware IOCs
2. SOC Agent - Hunts for IOCs in logs
3. Network Analyzer - Checks for C2 communications
4. Memory Agent - Analyzes running processes

Result: Comprehensive threat hunting report
```

### Scenario 3: Log Analysis
```
User asks: "Analyze web server logs for attacks"

Manager delegates to:
1. SOC Agent - Parses and analyzes access logs
2. Bug Bounty Agent - Identifies attack patterns (SQLi, XSS)
3. Threat Intelligence Agent - Checks attacker IPs against threat feeds
4. Reporting Agent - Creates comprehensive report

Result: Detailed analysis of web attacks with mitigation steps
```

## CLI Commands

```bash
# Start the CLI
python3 crossbow_cli.py

# Available commands in CLI:
/model     - Switch between AI models
/memory    - Toggle conversation memory
/storage   - Toggle agent storage/state
/mcp       - Toggle MCP server support
/add-mcp   - Add MCP server
/status    - Show current configuration
/clear     - Clear screen
/help      - Show help
/quit      - Exit

# Query examples:
crossbow-agent > Analyze authentication logs for suspicious activity
crossbow-agent > Research IP address 192.168.1.100
crossbow-agent > Hunt for IOCs related to APT28
crossbow-agent > Investigate this login pattern
crossbow-agent > Profile threat actor Lazarus Group
crossbow-agent > Extract IOCs from this malware sample
```

## Verification

To verify the agents are working:

```bash
# Test 1: Import and initialize
python3 -c "from Agent import SecurityAgentSystem; s=SecurityAgentSystem(model_name='claude-sonnet-4-5'); print('✅ Success')"

# Test 2: Check agent count
python3 -c "from Agent import SecurityAgentSystem; s=SecurityAgentSystem(model_name='claude-sonnet-4-5'); print(f'Total agents: {len(s.security_team.members)}')"

# Test 3: Access agents
python3 -c "from Agent import SecurityAgentSystem; s=SecurityAgentSystem(model_name='claude-sonnet-4-5'); print('SOC:', s.get_agent('soc').name); print('TI:', s.get_agent('threat_intel').name)"

# Test 4: Run demo
python3 test_new_agents.py
```

All tests should pass successfully.

## Future Enhancements

Potential improvements for these agents:

1. **SOC Agent:**
   - Integration with SIEM platforms (Splunk, ELK)
   - Automated playbook execution
   - Machine learning for anomaly detection
   - Real-time alerting capabilities

2. **Threat Intelligence Agent:**
   - Integration with threat intelligence platforms (MISP, OpenCTI)
   - Automated IOC enrichment from multiple sources
   - Threat actor attribution engine
   - Automated threat report generation

3. **Both Agents:**
   - Integration with ticketing systems
   - Automated response capabilities
   - Enhanced collaboration features
   - Custom dashboards and visualization

## Support

For issues or questions about these new agents:

1. Check the agent prompts in `/app/src/prompts.py`
2. Review the implementation in `/app/Agent.py`
3. Run the test script: `python3 test_new_agents.py`
4. Check the main README.md for system-wide documentation

## Summary

✅ **SOC Agent** - Fully integrated, ready for log analysis and attack investigation
✅ **Threat Intelligence Agent** - Fully integrated, ready for IOC collection and threat profiling
✅ **18 Total Agents** - All working together seamlessly
✅ **All Security Tools** - Available to both new agents
✅ **Anthropic API** - Configured and ready to use
✅ **Tested & Verified** - All tests passing

The CrossBow Security Agent System now has comprehensive coverage for Security Operations and Threat Intelligence!
