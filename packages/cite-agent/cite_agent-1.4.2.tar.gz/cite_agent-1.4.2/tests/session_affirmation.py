#!/usr/bin/env python3
"""
Session Affirmation System for Cite-Agent
Handles session detection and user choice for authentication
"""

import json
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

class SessionAffirmation:
    """Handles session detection and user authentication choices"""
    
    def __init__(self):
        self.console = Console()
        self.session_file = Path.home() / ".nocturnal_archive" / "session.json"
        self.config_file = Path.home() / ".nocturnal_archive" / "config.env"
    
    def check_existing_session(self):
        """Check if there's an existing session and return session info"""
        if not self.session_file.exists():
            return None
            
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
                return {
                    'email': session_data.get('email'),
                    'user_id': session_data.get('user_id'),
                    'expires_at': session_data.get('expires_at'),
                    'daily_limit': session_data.get('daily_token_limit', 0)
                }
        except Exception:
            return None
    
    def show_session_info(self, session_info):
        """Display existing session information"""
        self.console.print("\n" + "="*60)
        self.console.print(Panel(
            f"[bold green]🔑 Existing Session Found[/bold green]\n\n"
            f"[bold]Email:[/bold] {session_info['email']}\n"
            f"[bold]User ID:[/bold] {session_info['user_id']}\n"
            f"[bold]Daily Limit:[/bold] {session_info['daily_limit']} queries\n"
            f"[bold]Expires:[/bold] {session_info['expires_at']}",
            title="Session Information",
            border_style="green"
        ))
        self.console.print("="*60 + "\n")
    
    def ask_session_choice(self):
        """Ask user what they want to do with the existing session"""
        self.console.print("[bold cyan]What would you like to do?[/bold cyan]")
        self.console.print("1. [green]Resume[/green] - Use existing session")
        self.console.print("2. [yellow]Switch[/yellow] - Login with different account")
        self.console.print("3. [red]Logout[/red] - Clear session and start fresh")
        
        while True:
            choice = Prompt.ask(
                "Choose an option",
                choices=["1", "2", "3", "resume", "switch", "logout"],
                default="1"
            ).lower()
            
            if choice in ["1", "resume"]:
                return "resume"
            elif choice in ["2", "switch"]:
                return "switch"
            elif choice in ["3", "logout"]:
                return "logout"
            else:
                self.console.print("[red]Invalid choice. Please try again.[/red]")
    
    def clear_session(self):
        """Clear the existing session"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            if self.config_file.exists():
                self.config_file.unlink()
            self.console.print("[green]✅ Session cleared successfully[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]❌ Error clearing session: {e}[/red]")
            return False
    
    def handle_session_affirmation(self):
        """Main function to handle session affirmation"""
        session_info = self.check_existing_session()
        
        if not session_info:
            # No existing session
            self.console.print("[yellow]No existing session found. Starting fresh...[/yellow]")
            return "fresh"
        
        # Show existing session info
        self.show_session_info(session_info)
        
        # Ask user what to do
        choice = self.ask_session_choice()
        
        if choice == "resume":
            self.console.print("[green]✅ Resuming existing session...[/green]")
            return "resume"
        elif choice == "switch":
            self.console.print("[yellow]🔄 Switching to different account...[/yellow]")
            if self.clear_session():
                return "fresh"
            else:
                return "error"
        elif choice == "logout":
            self.console.print("[red]🚪 Logging out...[/red]")
            if self.clear_session():
                return "fresh"
            else:
                return "error"
        
        return "error"
    
    def show_help(self):
        """Show help for session management"""
        self.console.print(Panel(
            "[bold cyan]Session Management Help[/bold cyan]\n\n"
            "[bold]Resume:[/bold] Continue with your existing session\n"
            "[bold]Switch:[/bold] Logout and login with a different account\n"
            "[bold]Logout:[/bold] Clear your session and start fresh\n\n"
            "[bold]Session files are stored in:[/bold]\n"
            f"• {self.session_file}\n"
            f"• {self.config_file}\n\n"
            "[bold]To manually clear your session:[/bold]\n"
            "[dim]rm ~/.nocturnal_archive/session.json[/dim]\n"
            "[dim]rm ~/.nocturnal_archive/config.env[/dim]",
            title="Help",
            border_style="blue"
        ))

def main():
    """Test the session affirmation system"""
    sa = SessionAffirmation()
    result = sa.handle_session_affirmation()
    print(f"Result: {result}")

if __name__ == "__main__":
    main()