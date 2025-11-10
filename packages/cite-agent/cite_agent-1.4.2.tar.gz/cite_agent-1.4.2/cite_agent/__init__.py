"""
Nocturnal Archive - Beta Agent

A Groq-powered research and finance co-pilot with deterministic tooling and
prior stacks preserved only in Git history, kept out of the runtime footprint.
"""

from .enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest, ChatResponse

__version__ = "1.4.2"
__author__ = "Cite Agent Team"
__email__ = "contact@citeagent.dev"

__all__ = [
    "EnhancedNocturnalAgent",
    "ChatRequest", 
    "ChatResponse"
]

# Package metadata
PACKAGE_NAME = "cite-agent"
PACKAGE_VERSION = __version__
PACKAGE_DESCRIPTION = "Research and finance CLI copilot with shell, Archive, and FinSight tools"
PACKAGE_URL = "https://github.com/Spectating101/cite-agent"

def get_version():
    """Get the package version"""
    return __version__

def quick_start():
    """Print quick start instructions"""
    print("""
🚀 Cite Agent Quick Start
=========================

1. Install the package and CLI:
   pip install cite-agent

2. Configure your account or local keys:
   cite-agent --setup

3. Ask a question:
   cite-agent "Compare Apple and Microsoft net income this quarter"

4. Prefer embedding in code? Minimal example:
   ```python
   import asyncio
   from cite_agent import EnhancedNocturnalAgent, ChatRequest

   async def main():
       agent = EnhancedNocturnalAgent()
       await agent.initialize()

       response = await agent.process_request(ChatRequest(question="List repo workspace files"))
       print(response.response)

       await agent.close()

   asyncio.run(main())
   ```

Full installation instructions live in docs/INSTALL.md.
""")

if __name__ == "__main__":
    quick_start()
