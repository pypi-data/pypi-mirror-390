#!/usr/bin/env python3
"""
User Onboarding - First-run Experience

Provides a friendly onboarding flow for new users
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm


class OnboardingFlow:
    """Handles first-time user onboarding"""

    def __init__(self):
        self.console = Console()

    def show_welcome(self):
        """Show welcome message"""
        welcome_text = """
# Welcome to Cite-Agent! 🎉

**Cite-Agent** is your AI-powered research assistant that helps you:

✨ **Search** 200M+ academic papers across multiple databases
📄 **Read** full PDFs and get AI-powered summaries
💰 **Access** real-time financial data and SEC filings
✅ **Verify** facts with source citations
📚 **Export** citations to BibTeX for your papers
🔍 **Track** your research with local library management

Let's get you set up in 2 minutes!
"""
        self.console.print(Panel(
            Markdown(welcome_text),
            title="[bold magenta]Cite-Agent Setup[/]",
            border_style="magenta"
        ))

    def show_quick_start(self):
        """Show quick start guide after setup"""
        quickstart = """
# Quick Start Guide 🚀

## Try These Example Queries:

### Academic Research
```bash
cite-agent "Find recent papers on transformer architecture"
cite-agent "What is the BERT paper about?"
```

### Financial Data
```bash
cite-agent "What is Apple's latest revenue?"
cite-agent "Compare TSLA and GM profit margins"
```

### Fact Checking
```bash
cite-agent "Is the speed of light 299,792,458 m/s?"
cite-agent "Did Einstein win the Nobel Prize for relativity?"
```

### Research Workflow
```bash
cite-agent "Find transformer papers" --save --format bibtex
cite-agent --library                    # View saved papers
cite-agent --export-bibtex              # Export to .bib file
```

## Tips & Tricks:

- 💡 Use `--save` to save papers to your local library
- 📚 Use `--export-bibtex` to export citations
- 🔄 Use `--history` to see previous queries
- ⚡ Press `Ctrl+C` to interrupt long operations
- 🔧 Use `cite-agent --help` to see all options

## Interactive Mode:

Just type `cite-agent` (no arguments) to start a conversation!

---

**Ready to start?** Try: `cite-agent "Find papers on machine learning"`
"""
        self.console.print(Panel(
            Markdown(quickstart),
            title="[bold green]You're All Set![/]",
            border_style="green"
        ))

    def show_examples(self):
        """Show example usage"""
        examples = """
## Example Workflows

### 📚 Literature Review
1. Search for papers: `cite-agent "deep learning for medical imaging"`
2. Save interesting papers: Add `--save` flag
3. Export citations: `cite-agent --export-bibtex`
4. Import into Zotero/Mendeley

### 📊 Financial Analysis
1. Get company data: `cite-agent "AAPL revenue trends"`
2. Compare companies: `cite-agent "Compare MSFT and GOOGL margins"`
3. Track metrics over time

### ✅ Research Verification
1. Fact check: `cite-agent "Verify this claim: ..."`
2. Get sources: AI provides citations
3. Cross-reference: Check multiple sources

### 🔬 Deep Research
1. Search papers: `cite-agent "quantum computing applications"`
2. Read full PDFs (NEW!): Papers automatically summarized
3. Synthesize findings: Get key takeaways across papers
4. Export results: BibTeX, Markdown, or JSON
"""
        self.console.print(Markdown(examples))

    def check_first_run(self) -> bool:
        """Check if this is the first time user is running the CLI"""
        from pathlib import Path
        config_file = Path.home() / ".nocturnal_archive" / "session.json"
        return not config_file.exists()

    def run_onboarding(self):
        """Run full onboarding flow"""
        self.show_welcome()

        # Ask if user wants to see quick start
        if Confirm.ask("\n[bold cyan]Would you like to see the quick start guide?[/]", default=True):
            self.show_quick_start()

        # Ask if user wants to see examples
        if Confirm.ask("\n[bold cyan]Would you like to see example workflows?[/]", default=False):
            self.show_examples()

        self.console.print("\n[bold green]✅ Onboarding complete! Let's start researching![/]\n")

    def show_first_run_tips(self):
        """Show tips for first-time users"""
        tips = """
## 💡 Pro Tips

1. **Save Everything**: Use `--save` to build your research library
2. **Export Often**: Export to BibTeX regularly for backup
3. **Use History**: `--history` shows all your previous queries
4. **Keyboard Shortcuts**: `Ctrl+C` to interrupt, `Ctrl+D` to exit
5. **Get Help**: `cite-agent --help` shows all commands

## Common Issues

**Problem**: "Not authenticated"
**Solution**: Run `cite-agent --setup` to configure credentials

**Problem**: "Backend unreachable"
**Solution**: Check internet connection, try again in a moment

**Problem**: "Command not found"
**Solution**: Make sure `~/.local/bin` is in your PATH
"""
        self.console.print(Markdown(tips))


def show_onboarding_if_first_run():
    """Show onboarding flow if this is the first run"""
    onboarding = OnboardingFlow()

    if onboarding.check_first_run():
        onboarding.run_onboarding()
        return True

    return False
