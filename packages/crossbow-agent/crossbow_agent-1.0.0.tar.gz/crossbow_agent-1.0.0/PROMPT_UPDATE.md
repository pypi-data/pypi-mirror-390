# CLI Prompt Update

## Change Summary

The CrossBow CLI prompt has been updated for better clarity and branding.

### Before:
```
🎯 > 
```

### After:
```
crossbow-agent > 
```

## Files Updated

1. **`/app/crossbow_cli.py`** (Line 418)
   - Changed the input prompt from `🎯 > ` to `crossbow-agent > `

2. **`/app/QUICKSTART.md`**
   - Updated all example prompts throughout the documentation

3. **`/app/NEW_AGENTS_README.md`**
   - Updated all example prompts throughout the documentation

## Example Usage

When you run the CLI now, you'll see:

```
┌─────────────────────────────────────────────────────────────────┐
│ 🎯 CrossBow Security Agent (v1.0.0)                          │
└─────────────────────────────────────────────────────────────────┘

model:     claude-sonnet-4-5     /model to change
memory:    disabled              /memory to toggle
storage:   disabled              /storage to toggle
directory: /app

crossbow-agent > Analyze authentication logs for suspicious activity
crossbow-agent > Research IP 192.168.1.100
crossbow-agent > Help me hunt for IOCs related to APT28
crossbow-agent > /status
crossbow-agent > /quit
```

## Testing

Run the CLI to see the new prompt:

```bash
cd /app
python3 crossbow_cli.py
```

Or use the launcher script:

```bash
cd /app
./run_crossbow.sh
```

## Benefits

- **More descriptive**: Clearly identifies the agent system
- **Professional**: Better for command-line interface
- **Consistent**: Matches the tool name "crossbow"
- **Cleaner**: Text-based prompt instead of emoji

## Backwards Compatibility

This is a cosmetic change only. All functionality remains identical:
- All commands still work (`/model`, `/memory`, `/status`, etc.)
- All agents still function the same way
- All documentation updated to reflect the new prompt

✅ Change complete and verified!
