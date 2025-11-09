# CrossBow Security Agent - Quick Start Guide

## Installation

### Option 1: Using the Launcher Script (Recommended)
```bash
cd /app
./run_crossbow.sh
```

### Option 2: Direct Python
```bash
cd /app
python3 crossbow_cli.py
```

### Option 3: Install Dependencies First
If you encounter any import errors, install dependencies:
```bash
cd /app
pip install -r requirements.txt
```

## First Time Setup

1. **Check the .env file exists:**
```bash
cat /app/.env
```
Should show your Anthropic API key.

2. **Test the installation:**
```bash
cd /app
python3 test_new_agents.py
```

3. **Launch the interactive CLI:**
```bash
cd /app
python3 crossbow_cli.py
```

## Using the New Agents

### Example 1: SOC Agent - Log Analysis
```
crossbow-agent > Analyze authentication logs for failed login attempts
crossbow-agent > Investigate suspicious activity in /var/log/auth.log
crossbow-agent > Show me how to detect brute force attacks in logs
crossbow-agent > Help me correlate security events across multiple log files
```

### Example 2: Threat Intelligence Agent
```
crossbow-agent > Research IP address 192.168.1.100 for malicious activity
crossbow-agent > What are the latest IOCs for APT28?
crossbow-agent > Profile the Lazarus Group threat actor
crossbow-agent > Help me hunt for ransomware IOCs in our logs
crossbow-agent > Map these attack behaviors to MITRE ATT&CK
```

### Example 3: Combined Investigation
```
crossbow-agent > We detected unusual traffic to 185.220.100.240. 
     Can you help investigate this? Check if it's malicious, 
     analyze our logs for connections to this IP, and provide 
     threat intelligence context.
```

The manager agent will automatically coordinate between SOC, Threat Intelligence, and other relevant agents to provide a comprehensive response.

## CLI Commands

Once in the CLI, you can use:

- `/model` - Switch between AI models (GPT-4o, Claude, Gemini)
- `/memory` - Toggle conversation memory (keeps context between sessions)
- `/storage` - Toggle agent storage/state persistence
- `/config` - **Save/load your preferences** (NEW! ⭐)
  - `/config save` - Save current settings
  - `/config show` - View configuration
  - `/config reset` - Clear saved settings
- `/status` - Show current configuration
- `/clear` - Clear the screen
- `/help` - Show detailed help
- `/quit` - Exit the CLI

## Save Your Configuration ⭐ NEW!

CrossBow now remembers your preferences! Configure once, use forever.

**Example workflow:**
```
crossbow-agent > /model
[Select claude-sonnet-4-5]

crossbow-agent > /memory
[Memory enabled]

crossbow-agent > /config save
✓ Configuration saved!
```

**Next time you start CrossBow, your settings are automatically loaded!**

See [CONFIG_FEATURE.md](CONFIG_FEATURE.md) for full documentation.

## Choosing Your Model

By default, the system uses GPT-4o-mini (or your saved preference). You can change this:

**In the CLI:**
```
crossbow-agent > /model
```
Then select from the menu.

**Via Command Line:**
```bash
python3 crossbow_cli.py --model gpt-4o
python3 crossbow_cli.py --model claude-sonnet-4-5
python3 crossbow_cli.py --model gemini-2.0-flash-exp
```

## Enable Features

**Memory (conversation history):**
```bash
python3 crossbow_cli.py --memory
```

**Storage (persistent state):**
```bash
python3 crossbow_cli.py --storage
```

**Both:**
```bash
python3 crossbow_cli.py --memory --storage
```

## Python API Usage

```python
from Agent import SecurityAgentSystem

# Initialize the system
system = SecurityAgentSystem(
    model_name="claude-sonnet-4-5",
    use_memory=False,
    use_storage=False
)

# Run an assessment (auto-delegates to appropriate agent)
system.run_assessment("""
    Analyze the authentication logs at /var/log/auth.log
    for suspicious login patterns and potential brute force attacks.
""", stream=True)

# Or get a specific agent
soc_agent = system.get_agent("soc")
ti_agent = system.get_agent("threat_intel")
```

## Available Agents

The system now has **18 specialized security agents**:

1. Android SAST Specialist
2. Blue Team Defender
3. Bug Bounty Hunter
4. Security Developer
5. DFIR Investigator
6. Email Security Analyst
7. Memory Forensics Expert
8. Network Security Analyst
9. Red Team Operator
10. Replay Attack Specialist
11. Security Reporter
12. Vulnerability Validator
13. Reverse Engineer
14. RF Security Expert
15. WiFi Security Tester
16. Source Code Analyzer
17. **SOC Analyst** ⭐ NEW
18. **Threat Intelligence Analyst** ⭐ NEW

## Troubleshooting

### "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "No module named 'agno'"
```bash
pip install -r /app/requirements.txt
```

### API Key Issues
Make sure `/app/.env` exists and contains:
```
ANTHROPIC_API_KEY=your-key-here
```

### Import Errors
Ensure you're in the correct directory:
```bash
cd /app
python3 crossbow_cli.py
```

## Example Session

```
$ cd /app
$ python3 crossbow_cli.py

┌─────────────────────────────────────────────────────────────────┐
│ 🎯 CrossBow Security Agent (v1.0.0)                            │
└─────────────────────────────────────────────────────────────────┘

model:     claude-sonnet-4-5     /model to change
memory:    disabled              /memory to toggle
storage:   disabled              /storage to toggle
directory: /app

crossbow-agent > I need to investigate suspicious login activity from IP 192.168.1.100

[Manager coordinates SOC and Threat Intelligence agents]
[SOC Agent analyzes logs]
[Threat Intelligence Agent researches the IP]
[Comprehensive response with findings and recommendations]

crossbow-agent > /quit

👋 Goodbye! Stay secure!
```

## Next Steps

- Review `/app/NEW_AGENTS_README.md` for detailed agent capabilities
- Check `/app/test_new_agents.py` for example usage
- Explore the prompts in `/app/src/prompts.py` to understand agent behaviors
- Try different models with `/model` command

## Need Help?

The system has built-in help:
```
crossbow-agent > /help
```

For agent-specific capabilities, check the documentation:
- `/app/NEW_AGENTS_README.md` - New agents overview
- `/app/src/prompts.py` - Agent prompts and capabilities

Happy hunting! 🎯🔒
