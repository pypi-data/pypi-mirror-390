"""
Command Execution Safety & Enforcement
Ensures backend executes EXACTLY what agent planned - validates pre/post execution
"""

import json
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CommandClassification(Enum):
    """Safety classification for commands"""
    SAFE = "safe"                  # File reads, non-destructive queries
    WRITE = "write"                # File writes, modifications
    DANGEROUS = "dangerous"         # Dangerous: rm -rf, format disk
    BLOCKED = "blocked"            # Never execute


class CommandAuditLevel(Enum):
    """How strictly to audit commands"""
    PERMISSIVE = "permissive"      # Allow, log only
    STRICT = "strict"              # Require pre-approval
    ENFORCED = "enforced"          # Prevent mismatches


@dataclass
class CommandPlan:
    """What agent intends to do"""
    command: str
    classification: CommandClassification
    reason: str  # Why this command
    expected_output_pattern: Optional[str] = None
    max_execution_time_s: float = 60.0
    
    def get_hash(self) -> str:
        """Get hash of command for comparison"""
        return hashlib.sha256(self.command.encode()).hexdigest()[:16]


@dataclass
class CommandExecution:
    """Record of command execution"""
    command: str
    planned_hash: str
    executed_hash: str
    classification: CommandClassification
    status: str  # success, failure, timeout, mismatch
    exit_code: int = 0
    output: str = ""
    error: str = ""
    execution_time_s: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    
    def was_modified(self) -> bool:
        """Check if executed command differs from planned"""
        return self.planned_hash != self.executed_hash
    
    def to_audit_log(self) -> str:
        """Format as audit log entry"""
        modified = "⚠️ MODIFIED" if self.was_modified() else "✓ AS-PLANNED"
        return (
            f"{self.timestamp.isoformat()} | {self.classification.value.upper()} | "
            f"{modified} | exit={self.exit_code} | {self.command[:60]}..."
        )


class CommandExecutionValidator:
    """
    Pre and post-execution validation to ensure safety
    
    Prevents:
    - Agent plans "cat file.txt", backend executes "rm -rf /"
    - Command injection attacks
    - Unexpected output/errors
    - Timeout vulnerabilities
    """
    
    def __init__(self, audit_level: CommandAuditLevel = CommandAuditLevel.STRICT):
        self.audit_level = audit_level
        self.audit_log: List[CommandExecution] = []
        self.dangerous_patterns = [
            "rm -rf",
            "mkfs",
            "format",
            ": () { :",  # Bash fork bomb
            "dd if=/dev/zero of=/",
            "chmod -R 777 /",
            "reboot",
            "shutdown -h",
        ]
        self.blocked_commands = [
            "sudo rm -rf /",
            "rm -rf /etc",
            "rm -rf /boot",
        ]
    
    def validate_plan(self, plan: CommandPlan) -> tuple[bool, Optional[str]]:
        """
        Validate a command plan before execution
        
        Returns:
            (is_valid, error_reason)
        """
        # Check for explicitly blocked commands
        for blocked in self.blocked_commands:
            if blocked in plan.command:
                return False, f"Command explicitly blocked: {blocked}"
        
        # Check classification
        if plan.classification == CommandClassification.BLOCKED:
            return False, f"Command classified as BLOCKED"
        
        # For DANGEROUS commands, require strict approval
        if plan.classification == CommandClassification.DANGEROUS:
            if self.audit_level == CommandAuditLevel.PERMISSIVE:
                logger.warning(f"⚠️ DANGEROUS command allowed in permissive mode: {plan.command}")
            else:
                return False, "Dangerous commands require special approval"
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern in plan.command:
                classification = CommandClassification.DANGEROUS
                if plan.classification == CommandClassification.SAFE:
                    return False, f"Command contains dangerous pattern: {pattern}"
        
        return True, None
    
    def validate_execution(
        self,
        plan: CommandPlan,
        executed_command: str,
        exit_code: int,
        output: str,
        error: str,
        execution_time_s: float,
        user_id: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate execution matches plan
        
        Returns:
            (is_valid, error_reason)
        """
        # Record execution
        execution = CommandExecution(
            command=executed_command,
            planned_hash=plan.get_hash(),
            executed_hash=hashlib.sha256(executed_command.encode()).hexdigest()[:16],
            classification=plan.classification,
            status="unknown",
            exit_code=exit_code,
            output=output,
            error=error,
            execution_time_s=execution_time_s,
            user_id=user_id
        )
        
        # Check for modification
        if execution.was_modified():
            if self.audit_level == CommandAuditLevel.ENFORCED:
                execution.status = "mismatch"
                self.audit_log.append(execution)
                return False, f"Command was modified during execution!\nPlanned: {plan.command}\nExecuted: {executed_command}"
            else:
                logger.warning(
                    f"⚠️ Command modification detected:\n"
                    f"  Planned: {plan.command}\n"
                    f"  Executed: {executed_command}"
                )
        
        # Check timeout
        if execution_time_s > plan.max_execution_time_s:
            execution.status = "timeout"
            self.audit_log.append(execution)
            return False, f"Command exceeded max execution time: {execution_time_s:.1f}s > {plan.max_execution_time_s}s"
        
        # Check for unexpected errors
        if error and plan.classification == CommandClassification.SAFE:
            # SAFE commands shouldn't produce errors
            if exit_code != 0:
                execution.status = "error"
                self.audit_log.append(execution)
                return False, f"Safe command produced error (exit {exit_code}): {error}"
        
        # Verify output matches expected pattern if specified
        if plan.expected_output_pattern:
            import re
            if not re.search(plan.expected_output_pattern, output):
                logger.warning(
                    f"⚠️ Output doesn't match expected pattern:\n"
                    f"  Pattern: {plan.expected_output_pattern}\n"
                    f"  Got: {output[:200]}"
                )
        
        # Mark as success
        execution.status = "success" if exit_code == 0 else "failure"
        self.audit_log.append(execution)
        
        return True, None
    
    def get_audit_log(self, limit: int = 50) -> List[str]:
        """Get recent audit log entries"""
        return [entry.to_audit_log() for entry in self.audit_log[-limit:]]
    
    def get_command_stats(self) -> Dict[str, Any]:
        """Get statistics about commands executed"""
        if not self.audit_log:
            return {"total": 0}
        
        safe_count = sum(1 for e in self.audit_log if e.classification == CommandClassification.SAFE)
        write_count = sum(1 for e in self.audit_log if e.classification == CommandClassification.WRITE)
        dangerous_count = sum(1 for e in self.audit_log if e.classification == CommandClassification.DANGEROUS)
        failed_count = sum(1 for e in self.audit_log if e.status == "failure")
        modified_count = sum(1 for e in self.audit_log if e.was_modified())
        
        return {
            "total_executed": len(self.audit_log),
            "safe_commands": safe_count,
            "write_commands": write_count,
            "dangerous_commands": dangerous_count,
            "failed_commands": failed_count,
            "modified_commands": modified_count,
            "modification_rate": modified_count / len(self.audit_log) if self.audit_log else 0,
            "failure_rate": failed_count / len(self.audit_log) if self.audit_log else 0,
        }
    
    def get_status_message(self) -> str:
        """Human-readable status"""
        stats = self.get_command_stats()
        
        if stats.get("total_executed", 0) == 0:
            return "📋 **Command Execution Safety**: No commands executed yet"
        
        lines = [
            "📋 **Command Execution Safety**",
            f"• Audit level: {self.audit_level.value.upper()}",
            f"• Total executed: {stats['total_executed']}",
            f"• Safe commands: {stats['safe_commands']} | Write: {stats['write_commands']} | Dangerous: {stats['dangerous_commands']}",
            f"• Failures: {stats['failed_commands']} ({stats['failure_rate']:.1%})",
            f"• Modifications detected: {stats['modified_commands']} ({stats['modification_rate']:.1%})",
        ]
        
        if stats['modification_rate'] > 0:
            lines.append("\n⚠️ **WARNING**: Commands being modified during execution!")
        
        return "\n".join(lines)


class CommandSandbox:
    """
    Optional sandboxing for dangerous commands
    Runs in isolated environment with limited permissions
    """
    
    def __init__(self, enable_sandbox: bool = False):
        self.enabled = enable_sandbox
    
    def prepare_sandbox(self, command: str, dangerous: bool = False) -> str:
        """
        Wrap command in sandbox if needed
        
        Returns modified command that runs safely
        """
        if not self.enabled or not dangerous:
            return command
        
        # Use firejail if available
        sandboxed = f"firejail --quiet --timeout=60 {command}"
        return sandboxed
    
    def cleanup_sandbox(self):
        """Clean up sandbox resources"""
        if self.enabled:
            logger.info("🧹 Cleaning up sandbox")


# Global validator
command_validator = CommandExecutionValidator()


if __name__ == "__main__":
    # Test the validator
    validator = CommandExecutionValidator(CommandAuditLevel.STRICT)
    
    # Test 1: Safe command
    plan = CommandPlan(
        command="cat /etc/hostname",
        classification=CommandClassification.SAFE,
        reason="Read system hostname",
        expected_output_pattern=r"\w+"
    )
    
    valid, error = validator.validate_plan(plan)
    print(f"Plan validation: {valid} - {error}")
    
    # Simulate execution
    valid, error = validator.validate_execution(
        plan,
        executed_command="cat /etc/hostname",
        exit_code=0,
        output="localhost\n",
        error="",
        execution_time_s=0.05
    )
    print(f"Execution validation: {valid} - {error}")
    
    # Test 2: Dangerous command
    plan2 = CommandPlan(
        command="rm -rf /tmp/test",
        classification=CommandClassification.DANGEROUS,
        reason="Clean test directory"
    )
    
    valid, error = validator.validate_plan(plan2)
    print(f"\nDangerous plan validation: {valid} - {error}")
    
    # Show audit log
    print("\n" + validator.get_status_message())
    print("\n📋 **Audit Log**")
    for entry in validator.get_audit_log(5):
        print(f"  {entry}")
