# Automatic Configuration Persistence

## Overview

CrossBow now **automatically saves your settings**! No manual save commands needed.

## How It Works

1. **Start CrossBow:**
   ```bash
   python3 crossbow_cli.py
   ```

2. **Change any setting:**
   ```
   crossbow-agent > /model
   [Select claude-sonnet-4-5]
   ✓ Now using claude-sonnet-4-5
   ✓ Configuration saved
   
   crossbow-agent > /memory
   🧠 Memory enabled
   ✓ Configuration saved
   ```

3. **Settings are automatically saved to `crossbow_config.json`**

4. **Next time you start CrossBow, your settings are restored:**
   ```bash
   python3 crossbow_cli.py
   ✓ Loaded configuration from crossbow_config.json
   
   model:     claude-sonnet-4-5     
   memory:    enabled              
   storage:   disabled             
   mcp:       disabled  
   ```

## What Gets Auto-Saved?

✅ **Model selection** - Your preferred AI model  
✅ **Memory toggle** - Conversation memory on/off  
✅ **Storage toggle** - Agent storage on/off  
✅ **MCP toggle** - MCP server support on/off  
✅ **MCP servers** - List of configured MCP servers  

## Configuration File

**Location:** `./crossbow_config.json` (in your current directory)

**Example file:**
```json
{
  "model": "claude-sonnet-4-5",
  "memory": true,
  "storage": true,
  "mcp": false,
  "mcp_servers": []
}
```

## Commands

### View Current Configuration
```
crossbow-agent > /config
```

Shows your current settings and config file location.

### Reset to Defaults
Just delete the config file:
```bash
rm crossbow_config.json
```

Next startup will use defaults.

## Example Workflow

```bash
# First time - configure your preferences
$ python3 crossbow_cli.py

crossbow-agent > /model
[Select claude-sonnet-4-5]
✓ Configuration saved

crossbow-agent > /memory
✓ Configuration saved

crossbow-agent > /storage
✓ Configuration saved

crossbow-agent > /quit

# Next time - everything is already configured!
$ python3 crossbow_cli.py
✓ Loaded configuration from crossbow_config.json

model:     claude-sonnet-4-5
memory:    enabled
storage:   enabled
mcp:       disabled

# Your preferences are restored automatically! 🎉
```

## Benefits

✅ **Zero effort** - Changes save automatically  
✅ **Persistent** - Settings survive across sessions  
✅ **Per-directory** - Different settings for different projects  
✅ **Transparent** - Plain JSON file you can edit manually  
✅ **Flexible** - Delete file to reset anytime  

## FAQ

**Q: When does it save?**  
A: Immediately after you change model, memory, storage, MCP, or add MCP servers.

**Q: Where is the file saved?**  
A: In your current working directory as `crossbow_config.json`

**Q: Can I have different configs for different projects?**  
A: Yes! Since the file is in the current directory, each project folder can have its own config.

**Q: What if I delete the file?**  
A: CrossBow will start with default settings and create a new config file when you change any setting.

**Q: Can I edit the JSON file manually?**  
A: Yes! It's a plain JSON file. Just make sure it's valid JSON.

**Q: What are the default settings?**  
A: model=gpt-4o-mini, memory=false, storage=false, mcp=false

## Per-Project Configurations

Since the config is saved in the current directory, you can have different settings for different projects:

```bash
# Project A - Use Claude with memory
cd ~/project-a
python3 /app/crossbow_cli.py
crossbow-agent > /model
[Select claude-sonnet-4-5]
crossbow-agent > /memory

# Project B - Use GPT-4o without memory  
cd ~/project-b
python3 /app/crossbow_cli.py
crossbow-agent > /model
[Select gpt-4o]

# Each project now has its own crossbow_config.json!
```

## That's It!

No manual save commands. No complex configuration management. Just use CrossBow and your preferences are automatically remembered! 🎯
