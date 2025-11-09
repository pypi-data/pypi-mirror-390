# CrossBow Security Agent - Modern Terminal UI

## Overview

A beautiful, modern Terminal User Interface (TUI) for CrossBow Security Agent, built with [Textual](https://textual.textualize.io/).

![TUI Screenshot](https://textual.textualize.io/img/splash.png)

## Features

### 🎨 Modern Dark Theme
- Professional dark color scheme optimized for long sessions
- High contrast for excellent readability
- Syntax highlighting for code and logs
- Smooth animations and transitions

### 🎯 Intuitive Layout
- **Sidebar:** Configuration controls and settings
- **Main Area:** Conversation log with rich formatting
- **Status Bar:** Real-time configuration display
- **Header:** Branding with live clock
- **Footer:** Keyboard shortcuts

### ⚙️ Configuration Management
- Visual model selector (GPT-4o, Claude, Gemini)
- One-click toggle buttons for Memory, Storage, MCP
- Auto-save configuration
- Real-time status updates

### 💬 Rich Conversation Interface
- Markdown rendering for responses
- Syntax highlighting for code blocks
- Timestamped messages
- Color-coded panels (user, agent, errors)
- Scrollable conversation history

### ⌨️ Keyboard Shortcuts
- `Enter` - Send message
- `Ctrl+C` - Quit
- `Ctrl+M` - Toggle memory
- `Ctrl+S` - Toggle storage
- `Ctrl+P` - Toggle MCP
- `Ctrl+L` - Clear log

### 🤖 Full Agent System Integration
- All 18 security agents available
- Real-time agent coordination
- Streaming responses
- Error handling with user-friendly messages

## Installation

### Requirements
```bash
pip install textual textual-dev rich
```

### Quick Start
```bash
cd /app
python3 crossbow_tui.py
```

Or use the launcher:
```bash
./run_tui.sh
```

## Usage

### Starting the TUI

```bash
python3 crossbow_tui.py
```

You'll see:
- Header with clock
- Configuration sidebar on the left
- Main conversation area in the center
- Input field at the bottom
- Footer with keyboard shortcuts

### Changing the Model

1. Click the dropdown in the sidebar
2. Select your preferred model:
   - GPT-4o
   - GPT-4o Mini (default)
   - Claude Sonnet 4.5
   - Gemini 2.0 Flash

Configuration is automatically saved!

### Toggling Features

Click the buttons in the sidebar:
- **🧠 Toggle Memory** - Enable/disable conversation memory
- **💾 Toggle Storage** - Enable/disable agent storage
- **🔌 Toggle MCP** - Enable/disable MCP servers

Or use keyboard shortcuts:
- `Ctrl+M` for memory
- `Ctrl+S` for storage
- `Ctrl+P` for MCP

### Asking Questions

1. Type your security question in the input field
2. Press `Enter` or click "Send"
3. Watch as the agents collaborate to answer

**Example queries:**
```
Analyze authentication logs for suspicious activity
Research IP address 192.168.1.100
Hunt for IOCs related to APT28
Explain SQL injection vulnerabilities
```

### Using Commands

Type `/` commands for special actions:

- `/help` - Show help information
- `/clear` - Clear conversation log
- `/config` - Show current configuration
- `/agents` - List all 18 available agents
- `/memory` - Toggle memory
- `/storage` - Toggle storage
- `/mcp` - Toggle MCP

### Clearing the Log

- Click the "Clear" button
- Type `/clear`
- Press `Ctrl+L`

### Getting Help

- Click the "Help" button
- Type `/help`
- Check the footer for keyboard shortcuts

## UI Components

### Header
- **Title:** CrossBow Security Agent
- **Subtitle:** AI-Powered Security Testing Platform
- **Clock:** Live time display

### Sidebar (Left)
- **Configuration Section:**
  - Status bar showing current settings
  - Model selector dropdown
  - Toggle buttons for features
- **Active Agents:** Count of available specialists

### Main Content Area (Center)
- **Conversation Log:**
  - Rich formatted messages
  - Markdown rendering
  - Code syntax highlighting
  - Color-coded panels
  - Timestamps
  - Scrollable history

### Input Area (Bottom)
- **Text Input:** Multi-line support, autocomplete ready
- **Action Buttons:**
  - Send (Primary action)
  - Clear (Clear log)
  - Help (Show help)

### Footer
- Keyboard shortcuts display
- Context-sensitive tips

## Color Scheme

The TUI uses a professional dark theme:

| Element | Color | Purpose |
|---------|-------|---------|
| Background | Dark grey/black | Reduce eye strain |
| Primary text | Off-white | High readability |
| Accent | Cyan | Highlights & focus |
| Success | Green | Confirmations & agents |
| Error | Red | Errors & warnings |
| Warning | Yellow | Processing & info |
| Dim | Grey | Secondary info |

## Advanced Features

### Markdown Support

Agent responses support full Markdown:

```markdown
# Headers
**Bold text**
*Italic text*
`Code snippets`
- Lists
- Items

1. Numbered
2. Lists

> Blockquotes

[Links](https://example.com)
```

### Code Syntax Highlighting

Code blocks are automatically highlighted:

```python
def example():
    print("Syntax highlighted!")
```

```bash
#!/bin/bash
echo "Shell scripts too!"
```

### Panels & Borders

Different message types have different panel styles:
- **User messages:** Cyan border
- **Agent responses:** Green border
- **Errors:** Red border
- **Info/Processing:** Yellow border

### Auto-Save Configuration

All settings changes are automatically saved to `crossbow_config.json`:
- Model selection
- Memory toggle
- Storage toggle
- MCP toggle
- MCP servers

No manual save needed!

## Comparison with CLI

| Feature | CLI | TUI |
|---------|-----|-----|
| Interface | Text-based | Visual/Interactive |
| Model Selection | Menu prompt | Dropdown selector |
| Configuration | Commands | Toggle buttons |
| Status Display | Text output | Live status bar |
| Conversation | Plain text | Rich formatting |
| Code Display | Plain text | Syntax highlighted |
| Navigation | Scroll back | Mouse + keyboard |
| Keyboard Shortcuts | Limited | Extensive |
| Visual Feedback | Text only | Colors, borders, panels |
| User Experience | Good | Excellent |

## Development

### Project Structure

```
/app/
├── crossbow_tui.py       # Main TUI application
├── crossbow_cli.py       # Original CLI (unchanged)
├── Agent.py              # Agent system
├── src/                  # Agent source code
├── crossbow_config.json  # Auto-saved configuration
└── run_tui.sh           # TUI launcher script
```

### Textual Components Used

- **App:** Main application class
- **Header/Footer:** Standard layout components
- **Container:** Layout containers
- **Vertical/Horizontal:** Layout helpers
- **Static:** Static text display
- **Label:** Text labels
- **Button:** Interactive buttons
- **Input:** Text input field
- **Select:** Dropdown selector
- **RichLog:** Rich text log with scrolling
- **Reactive:** Reactive properties for live updates

### Customization

The TUI is highly customizable via CSS-like styling:

```python
CSS = """
Screen {
    background: $surface;
}

#chat-log {
    border: solid $primary;
    padding: 1;
}
"""
```

Modify colors, spacing, borders, and more!

### Adding New Features

1. Add new widgets in `compose()`
2. Handle events with `on_*` methods
3. Update reactive properties for live changes
4. Style with CSS in the `CSS` string

## Troubleshooting

### TUI doesn't start

**Issue:** Import errors or missing dependencies

**Solution:**
```bash
pip install textual textual-dev rich
```

### Characters display incorrectly

**Issue:** Terminal doesn't support Unicode

**Solution:** Use a modern terminal:
- iTerm2 (macOS)
- Windows Terminal (Windows)
- GNOME Terminal, Alacritty, Kitty (Linux)

### Colors not showing

**Issue:** Terminal doesn't support 256 colors

**Solution:** Check terminal settings or use:
```bash
export TERM=xterm-256color
```

### Slow performance

**Issue:** Large log history

**Solution:** Clear the log regularly with `/clear` or `Ctrl+L`

### Configuration not saving

**Issue:** No write permissions

**Solution:**
```bash
chmod 644 crossbow_config.json
```

## Tips & Tricks

### Efficient Workflow

1. **Use keyboard shortcuts** - Faster than clicking
2. **Keep the log clean** - Clear regularly with `Ctrl+L`
3. **Save your preferred model** - It's auto-loaded next time
4. **Use commands** - Type `/agents` to see all available specialists

### Best Practices

1. **Start with help** - Type `/help` to learn commands
2. **Configure first** - Set your model and features before asking questions
3. **Clear between topics** - Use `/clear` for fresh context
4. **Check config** - Type `/config` to verify settings

### Power User Tips

```bash
# Launch with specific terminal
kitty python3 crossbow_tui.py

# Launch in tmux for session management
tmux new -s crossbow 'python3 crossbow_tui.py'

# Create alias for quick access
alias crossbow='python3 /app/crossbow_tui.py'
```

## FAQ

**Q: Can I use both TUI and CLI?**  
A: Yes! They're completely separate. Use whichever you prefer.

**Q: Does the TUI use the same agents as CLI?**  
A: Yes, identical agent system and capabilities.

**Q: Can I customize the colors?**  
A: Yes, edit the `CSS` string in `crossbow_tui.py`

**Q: Does it work over SSH?**  
A: Yes, as long as your terminal supports the features.

**Q: Can I run multiple instances?**  
A: Yes, each instance is independent.

**Q: Is the config shared with CLI?**  
A: Yes, both use `crossbow_config.json`

## Credits

Built with:
- **[Textual](https://textual.textualize.io/)** - Modern TUI framework by Textualize
- **[Rich](https://rich.readthedocs.io/)** - Rich text and formatting
- **[Agno](https://docs.agno.com/)** - Agent orchestration framework

## License

Same as CrossBow Security Agent.

## Support

For issues or questions:
1. Check this README
2. Run `/help` in the TUI
3. Review the main project documentation

---

**Enjoy the modern CrossBow TUI experience!** 🎯
