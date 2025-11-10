#!/usr/bin/env python3
"""
Enhanced Error Handler - User-Friendly Error Messages

Provides helpful error messages and recovery suggestions
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from typing import Optional


class ErrorHandler:
    """Handles errors with user-friendly messages and recovery suggestions"""

    def __init__(self):
        self.console = Console()

    def handle_authentication_error(self, error_message: str = None):
        """Handle authentication errors with helpful suggestions"""
        error_text = """
# ❌ Authentication Error

**Problem**: You're not authenticated with Cite-Agent.

## 🔧 How to Fix:

### Step 1: Run Setup
```bash
cite-agent --setup
```

This will prompt you for:
- Email address (must be academic: .edu, .ac.uk, etc.)
- Password

### Step 2: Verify Credentials
Make sure your email is from an academic institution:
- ✅ Valid: user@university.edu, student@ac.uk
- ❌ Invalid: user@gmail.com, user@company.com

### Step 3: Check Network
Make sure you have internet connection:
```bash
ping google.com
```

## 💡 Alternative: Use Environment Variables

Set credentials in your environment:
```bash
export NOCTURNAL_ACCOUNT_EMAIL="your@email.edu"
export NOCTURNAL_ACCOUNT_PASSWORD="your_password"
```

Then restart cite-agent.

---

**Still having issues?** Check the troubleshooting guide:
https://github.com/Spectating101/cite-agent#troubleshooting
"""
        self.console.print(Panel(
            Markdown(error_text),
            title="[bold red]Authentication Required[/]",
            border_style="red"
        ))

    def handle_backend_unreachable(self, backend_url: str = None):
        """Handle backend connection errors"""
        error_text = f"""
# ❌ Backend Unreachable

**Problem**: Cannot connect to Cite-Agent backend.

{'**Backend URL**: ' + backend_url if backend_url else ''}

## 🔧 Troubleshooting Steps:

### 1. Check Internet Connection
```bash
# Test basic connectivity
ping 8.8.8.8

# Test DNS resolution
ping google.com
```

### 2. Check Backend Status
The backend might be temporarily down for maintenance.

### 3. Verify Backend URL
Current backend: {backend_url or 'https://cite-agent-api-720dfadd602c.herokuapp.com'}

Check if URL is correct in your configuration.

### 4. Check Firewall/Proxy
If you're behind a corporate firewall:
- Check if HTTPS connections are allowed
- Configure proxy if needed

### 5. Try Offline Mode (if available)
Some features work without backend:
```bash
cite-agent --library        # View saved papers offline
cite-agent --history        # View query history
```

## ⏰ If Backend is Down

The Cite-Agent team is automatically notified. Service typically:
- Returns within 15 minutes for routine issues
- Updates posted at: https://status.cite-agent.com (if exists)

## 💡 Workaround

While waiting, you can:
1. Work with previously saved papers in your library
2. Export existing citations to BibTeX
3. Review your search history

---

**Still stuck?** Report the issue:
https://github.com/Spectating101/cite-agent/issues
"""
        self.console.print(Panel(
            Markdown(error_text),
            title="[bold red]Connection Failed[/]",
            border_style="red"
        ))

    def handle_rate_limit_error(self, limit: int = None, reset_time: str = None):
        """Handle rate limiting errors"""
        error_text = f"""
# ⚠️ Rate Limit Exceeded

**Problem**: You've hit your query limit.

{f'**Current Limit**: {limit} queries/hour' if limit else ''}
{f'**Resets At**: {reset_time}' if reset_time else ''}

## 🔧 Solutions:

### Option 1: Wait
Your quota will reset automatically.

### Option 2: Upgrade Your Plan
```bash
cite-agent --upgrade
```

**Pricing Tiers:**
- Free: 100 queries/month (100/hour)
- Pro: 1,000 queries/month (1,000/hour) - $9/month
- Academic: 500 queries/month (500/hour) - $5/month
- Enterprise: Unlimited - $99/month

### Option 3: Work Offline
Use saved papers and citations:
```bash
cite-agent --library          # Browse saved papers
cite-agent --export-bibtex    # Export citations
cite-agent --history          # View past queries
```

## 💡 Tips to Avoid Rate Limits

1. **Batch Your Queries**: Use batch processing for multiple searches
2. **Save Results**: Use `--save` to avoid re-searching
3. **Export Regularly**: Keep local copies of important papers
4. **Use Library**: Search your library before querying APIs

---

**Check your usage**: `cite-agent --status`
"""
        self.console.print(Panel(
            Markdown(error_text),
            title="[bold yellow]Rate Limit Reached[/]",
            border_style="yellow"
        ))

    def handle_pdf_library_error(self):
        """Handle missing PDF processing library errors"""
        error_text = """
# ❌ PDF Processing Libraries Missing

**Problem**: Required PDF processing libraries are not installed.

## 🔧 How to Fix:

### Quick Fix: Reinstall cite-agent
```bash
pip install --upgrade --force-reinstall cite-agent
```

This will install all required dependencies including:
- pypdf2 (PDF text extraction)
- pdfplumber (Advanced PDF parsing)
- pymupdf (Fast PDF processing)

### Manual Installation (if needed)
```bash
pip install pypdf2>=3.0.0 pdfplumber>=0.10.0 pymupdf>=1.23.0
```

### Verify Installation
```bash
python -c "import pypdf2, pdfplumber, fitz; print('✅ PDF libraries installed')"
```

## 💡 What This Enables

With PDF libraries installed, you can:
- 📄 Read full academic papers automatically
- 🤖 Get AI-powered summaries of papers
- 📊 Extract tables and figures from PDFs
- 🔍 Search within PDF content
- 💾 Build a searchable paper library

## Example Usage

Once fixed, try:
```bash
cite-agent "Read and summarize the BERT paper"
```

---

**Still having issues?** Check Python version (requires 3.9+):
```bash
python --version
```
"""
        self.console.print(Panel(
            Markdown(error_text),
            title="[bold red]Missing Dependencies[/]",
            border_style="red"
        ))

    def handle_generic_error(self, error: Exception, context: str = None):
        """Handle generic errors with helpful context"""
        error_text = f"""
# ❌ Error Occurred

**Error Type**: {type(error).__name__}
**Error Message**: {str(error)}

{f'**Context**: {context}' if context else ''}

## 🔧 General Troubleshooting:

### 1. Check Logs
Enable debug mode to see detailed logs:
```bash
export NOCTURNAL_DEBUG=1
cite-agent "your query"
```

### 2. Update to Latest Version
```bash
cite-agent --update
```

### 3. Clear Cache
Sometimes cached data can cause issues:
```bash
rm -rf ~/.nocturnal_archive
cite-agent --setup
```

### 4. Check System Requirements
- Python 3.9 or higher
- Active internet connection
- At least 100MB free disk space

### 5. Report the Bug
If this persists, please report it:
```bash
cite-agent --feedback
```

Or open an issue at:
https://github.com/Spectating101/cite-agent/issues

---

**Include in your bug report:**
- Error message above
- Python version: `python --version`
- Cite-agent version: `cite-agent --version`
- Operating system
"""
        self.console.print(Panel(
            Markdown(error_text),
            title="[bold red]Unexpected Error[/]",
            border_style="red"
        ))

    def show_help_message(self):
        """Show general help message"""
        help_text = """
# 🆘 Getting Help

## Quick Commands

```bash
cite-agent --help         # Show all available commands
cite-agent --tips         # Show usage tips
cite-agent --setup        # Reconfigure authentication
cite-agent --version      # Show version info
cite-agent --update       # Update to latest version
```

## Common Issues & Solutions

### "Not authenticated"
→ Run `cite-agent --setup`

### "Backend unreachable"
→ Check internet connection
→ Try again in a few minutes

### "Rate limit exceeded"
→ Wait for quota reset
→ Upgrade plan: `cite-agent --upgrade`

### "Command not found"
→ Add to PATH: `export PATH="$HOME/.local/bin:$PATH"`
→ Or use: `python -m cite_agent.cli`

## Resources

- **Documentation**: https://github.com/Spectating101/cite-agent
- **Examples**: Check `examples/` directory
- **Issues**: https://github.com/Spectating101/cite-agent/issues
- **Email**: support@cite-agent.com (if configured)

## Debug Mode

For detailed error information:
```bash
export NOCTURNAL_DEBUG=1
cite-agent "your query"
```
"""
        self.console.print(Panel(
            Markdown(help_text),
            title="[bold cyan]Cite-Agent Help[/]",
            border_style="cyan"
        ))


# Global error handler instance
_error_handler = ErrorHandler()


def handle_error(error: Exception, error_type: str = "generic", **kwargs):
    """
    Global error handling function

    Args:
        error: The exception that occurred
        error_type: Type of error (authentication, backend, rate_limit, pdf, generic)
        **kwargs: Additional context (backend_url, limit, reset_time, etc.)
    """
    if error_type == "authentication":
        _error_handler.handle_authentication_error(kwargs.get("message"))
    elif error_type == "backend":
        _error_handler.handle_backend_unreachable(kwargs.get("backend_url"))
    elif error_type == "rate_limit":
        _error_handler.handle_rate_limit_error(
            kwargs.get("limit"),
            kwargs.get("reset_time")
        )
    elif error_type == "pdf":
        _error_handler.handle_pdf_library_error()
    else:
        _error_handler.handle_generic_error(error, kwargs.get("context"))
