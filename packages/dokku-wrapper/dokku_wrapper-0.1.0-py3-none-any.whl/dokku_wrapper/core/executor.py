import subprocess
from typing import List
from .exceptions import DokkuCommandError


def run_command(command: List[str], capture_output: bool = True) -> str:
    """Executa um comando Dokku com segurança."""
    result = subprocess.run(
        command,
        capture_output=capture_output,
        text=True
    )
    if result.returncode != 0:
        raise DokkuCommandError(command, result.stderr.strip())
    return result.stdout.strip()
