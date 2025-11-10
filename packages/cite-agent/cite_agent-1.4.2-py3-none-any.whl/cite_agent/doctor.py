#!/usr/bin/env python3
"""
Health Check Tool - Diagnostic and Troubleshooting

Provides comprehensive diagnostics for cite-agent installation and configuration
"""

import sys
import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
import asyncio

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


class HealthChecker:
    """
    Comprehensive health check for cite-agent

    Checks:
    - Python version
    - Dependencies installed
    - Configuration validity
    - Backend connectivity
    - Local library status
    - Disk space
    - Network connectivity
    """

    def __init__(self):
        self.console = Console()
        self.issues = []
        self.warnings = []
        self.info = []

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:

            # Check 1: Python version
            task = progress.add_task("Checking Python version...", total=None)
            results['python'] = self.check_python_version()
            progress.update(task, completed=True)

            # Check 2: Dependencies
            task = progress.add_task("Checking dependencies...", total=None)
            results['dependencies'] = self.check_dependencies()
            progress.update(task, completed=True)

            # Check 3: Configuration
            task = progress.add_task("Checking configuration...", total=None)
            results['config'] = self.check_configuration()
            progress.update(task, completed=True)

            # Check 4: Backend connectivity
            task = progress.add_task("Checking backend connectivity...", total=None)
            results['backend'] = await self.check_backend()
            progress.update(task, completed=True)

            # Check 5: Local library
            task = progress.add_task("Checking local library...", total=None)
            results['library'] = self.check_local_library()
            progress.update(task, completed=True)

            # Check 6: Disk space
            task = progress.add_task("Checking disk space...", total=None)
            results['disk'] = self.check_disk_space()
            progress.update(task, completed=True)

            # Check 7: Network
            task = progress.add_task("Checking network connectivity...", total=None)
            results['network'] = await self.check_network()
            progress.update(task, completed=True)

        return results

    def check_python_version(self) -> Dict[str, Any]:
        """Check Python version"""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        is_ok = version >= (3, 9)

        if not is_ok:
            self.issues.append(f"Python {version_str} is too old (need 3.9+)")
        else:
            self.info.append(f"Python {version_str} ✅")

        return {
            "version": version_str,
            "major": version.major,
            "minor": version.minor,
            "is_ok": is_ok,
            "required": "3.9+"
        }

    def check_dependencies(self) -> Dict[str, Any]:
        """Check if all required dependencies are installed"""
        required_packages = [
            "aiohttp",
            "groq",
            "openai",
            "requests",
            "pydantic",
            "rich",
            "keyring",
            "pypdf2",
            "pdfplumber",
            "pymupdf"
        ]

        installed = []
        missing = []

        for package in required_packages:
            try:
                __import__(package)
                installed.append(package)
            except ImportError:
                missing.append(package)
                self.issues.append(f"Missing dependency: {package}")

        if missing:
            self.issues.append(f"Run: pip install {' '.join(missing)}")
        else:
            self.info.append(f"All {len(installed)} dependencies installed ✅")

        return {
            "installed": installed,
            "missing": missing,
            "is_ok": len(missing) == 0
        }

    def check_configuration(self) -> Dict[str, Any]:
        """Check configuration files and settings"""
        config_dir = Path.home() / ".nocturnal_archive"
        session_file = config_dir / "session.json"

        config_exists = config_dir.exists()
        session_exists = session_file.exists()

        has_email = bool(os.getenv("NOCTURNAL_ACCOUNT_EMAIL"))
        has_password = bool(os.getenv("NOCTURNAL_ACCOUNT_PASSWORD"))

        is_configured = session_exists or (has_email and has_password)

        if not is_configured:
            self.warnings.append("Not configured. Run 'cite-agent --setup'")
        else:
            self.info.append("Configuration found ✅")

        return {
            "config_dir_exists": config_exists,
            "session_file_exists": session_exists,
            "has_env_email": has_email,
            "has_env_password": has_password,
            "is_ok": is_configured
        }

    async def check_backend(self) -> Dict[str, Any]:
        """Check backend connectivity"""
        backend_url = os.getenv(
            "NOCTURNAL_API_URL",
            "https://cite-agent-api-720dfadd602c.herokuapp.com"
        )

        import aiohttp

        is_reachable = False
        status_code = None
        error = None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{backend_url}/api/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    status_code = response.status
                    is_reachable = status_code < 500
        except asyncio.TimeoutError:
            error = "Timeout (>10s)"
            self.warnings.append(f"Backend timeout: {backend_url}")
        except Exception as e:
            error = str(e)[:100]
            self.warnings.append(f"Backend unreachable: {error}")

        if is_reachable:
            self.info.append(f"Backend reachable ({status_code}) ✅")

        return {
            "url": backend_url,
            "is_reachable": is_reachable,
            "status_code": status_code,
            "error": error,
            "is_ok": is_reachable
        }

    def check_local_library(self) -> Dict[str, Any]:
        """Check local paper library status"""
        library_dir = Path.home() / ".cite_agent" / "papers"

        if not library_dir.exists():
            library_dir = Path.home() / ".nocturnal_archive" / "papers"

        exists = library_dir.exists()
        paper_count = 0
        total_size = 0

        if exists:
            paper_files = list(library_dir.glob("*.json"))
            paper_count = len(paper_files)
            total_size = sum(f.stat().st_size for f in paper_files)

            if paper_count > 0:
                self.info.append(f"Library: {paper_count} papers ({total_size / 1024:.1f} KB) ✅")
            else:
                self.warnings.append("Library empty (save papers with --save)")

        return {
            "exists": exists,
            "path": str(library_dir),
            "paper_count": paper_count,
            "total_size_kb": total_size / 1024,
            "is_ok": True  # Library being empty is not an error
        }

    def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        import shutil

        home_dir = Path.home()
        stats = shutil.disk_usage(home_dir)

        free_gb = stats.free / (1024 ** 3)
        total_gb = stats.total / (1024 ** 3)
        used_percent = (stats.used / stats.total) * 100

        is_ok = free_gb > 1.0  # Need at least 1GB free

        if not is_ok:
            self.warnings.append(f"Low disk space: {free_gb:.1f}GB free")
        else:
            self.info.append(f"Disk space: {free_gb:.1f}GB free ({used_percent:.0f}% used) ✅")

        return {
            "free_gb": free_gb,
            "total_gb": total_gb,
            "used_percent": used_percent,
            "is_ok": is_ok
        }

    async def check_network(self) -> Dict[str, Any]:
        """Check general network connectivity"""
        import aiohttp

        # Test multiple endpoints
        test_urls = [
            ("Google DNS", "http://8.8.8.8"),
            ("Cloudflare", "https://1.1.1.1"),
            ("Google", "https://google.com")
        ]

        results = {}
        any_reachable = False

        for name, url in test_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        results[name] = response.status < 500
                        if results[name]:
                            any_reachable = True
            except:
                results[name] = False

        if any_reachable:
            self.info.append("Network connectivity OK ✅")
        else:
            self.issues.append("No network connectivity detected")

        return {
            "test_results": results,
            "is_ok": any_reachable
        }

    def display_results(self, results: Dict[str, Any]):
        """Display health check results"""
        self.console.print()

        # Summary table
        table = Table(title="Health Check Results", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan", width=25)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Details", style="dim")

        for component, data in results.items():
            is_ok = data.get("is_ok", False)
            status = "✅ PASS" if is_ok else "❌ FAIL"

            # Get details based on component
            if component == "python":
                details = f"Version {data['version']}"
            elif component == "dependencies":
                details = f"{len(data['installed'])} installed, {len(data['missing'])} missing"
            elif component == "backend":
                details = f"{data.get('status_code', 'N/A')} - {data['url']}"
            elif component == "library":
                details = f"{data['paper_count']} papers"
            elif component == "disk":
                details = f"{data['free_gb']:.1f}GB free"
            elif component == "network":
                ok_count = sum(1 for v in data['test_results'].values() if v)
                details = f"{ok_count}/{len(data['test_results'])} endpoints reachable"
            elif component == "config":
                details = "Configured" if data['is_ok'] else "Not configured"
            else:
                details = ""

            table.add_row(component.capitalize(), status, details)

        self.console.print(table)
        self.console.print()

        # Issues
        if self.issues:
            self.console.print(Panel(
                "\n".join(f"❌ {issue}" for issue in self.issues),
                title="[bold red]Issues Found[/]",
                border_style="red"
            ))
            self.console.print()

        # Warnings
        if self.warnings:
            self.console.print(Panel(
                "\n".join(f"⚠️  {warning}" for warning in self.warnings),
                title="[bold yellow]Warnings[/]",
                border_style="yellow"
            ))
            self.console.print()

        # Overall status
        has_critical_issues = len(self.issues) > 0
        if has_critical_issues:
            self.console.print(Panel(
                "[bold red]❌ Some checks failed[/]\n\n"
                "Please address the issues above before using cite-agent.\n"
                "Run [bold]cite-agent --setup[/] to configure.",
                title="Overall Status",
                border_style="red"
            ))
        elif self.warnings:
            self.console.print(Panel(
                "[bold yellow]⚠️  System is functional with warnings[/]\n\n"
                "Cite-agent will work but some features may be limited.\n"
                "Consider addressing the warnings above.",
                title="Overall Status",
                border_style="yellow"
            ))
        else:
            self.console.print(Panel(
                "[bold green]✅ All systems operational![/]\n\n"
                "Cite-agent is ready to use.\n"
                "Try: [bold]cite-agent \"find papers on machine learning\"[/]",
                title="Overall Status",
                border_style="green"
            ))

        self.console.print()

    def show_system_info(self):
        """Display system information"""
        self.console.print("\n[bold cyan]System Information[/]\n")

        info_table = Table(show_header=False, box=None)
        info_table.add_column("Key", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("OS", platform.system())
        info_table.add_row("OS Version", platform.release())
        info_table.add_row("Architecture", platform.machine())
        info_table.add_row("Python", sys.version.split()[0])
        info_table.add_row("Python Executable", sys.executable)

        # Try to get cite-agent version
        try:
            import pkg_resources
            version = pkg_resources.get_distribution('cite-agent').version
            info_table.add_row("Cite-Agent Version", version)
        except:
            info_table.add_row("Cite-Agent Version", "Unknown (not installed)")

        self.console.print(info_table)


async def run_doctor():
    """Run full health check"""
    checker = HealthChecker()

    checker.console.print(Panel.fit(
        "[bold magenta]Cite-Agent Health Check[/]\n"
        "Running diagnostics...",
        border_style="magenta"
    ))

    checker.show_system_info()
    checker.console.print()

    results = await checker.run_all_checks()
    checker.display_results(results)

    # Return exit code based on results
    has_critical = len(checker.issues) > 0
    return 1 if has_critical else 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_doctor())
    sys.exit(exit_code)
