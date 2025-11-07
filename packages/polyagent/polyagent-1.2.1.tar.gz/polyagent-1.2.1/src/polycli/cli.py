"""CLI for PolyCLI."""

import click
from pathlib import Path


@click.group()
def cli():
    """PolyCLI - Unified AI agent interface."""
    pass


@cli.group()
def sandbox():
    """Sandbox commands for safe testing."""
    pass


@sandbox.command()
@click.option('--dir', '-d', default='.', help='Directory to initialize')
def init(dir):
    """Initialize a new sandbox project."""
    from .sandbox import init as sandbox_init
    sandbox_init(dir)


@sandbox.command()
@click.option('--testcase', '-t', help='Specific test case to run (default: all)')
@click.option('--clean', is_flag=True, help='Start fresh (clear workspace and cache)')
@click.option('--no-cache', is_flag=True, help='Disable PolyCLI cache for this run')
@click.option('--dir', '-d', default='.', help='Project directory')
@click.option('--no-stream', is_flag=True, help='Disable output streaming')
@click.option('--ports', '-p', help='Port mappings (e.g. 8000:8000,5000:5000)')
@click.option('--image', '-i', help='Docker image to use (default: from config or polycli-sandbox)')
def run(testcase, clean, no_cache, dir, no_stream, ports, image):
    """Run sandbox tests (resumes by default, use --clean for fresh start)."""
    from .sandbox.runner import run as sandbox_run
    sandbox_run(dir, testcase=testcase, clean=clean, no_cache=no_cache, 
                stream=not no_stream, ports=ports, image=image)


@sandbox.command('ls')
@click.option('--dir', '-d', default='.', help='Project directory')
def list_cmd(dir):
    """List available test cases and their status."""
    from .sandbox.runner import list_testcases
    list_testcases(dir)


@cli.command()
@click.argument('file')
@click.option('--interval', '-i', default=0.5, help='Check interval in seconds')
def watch(file, interval):
    """Watch a file and auto-run with cache on changes (live coding mode)."""
    from .utils.watcher import watch_file
    watch_file(file, interval)


@cli.group()
def cchook():
    """Manage Claude Code hooks integration."""
    pass


@cchook.command()
@click.option('--scope', '-s', type=click.Choice(['local', 'global']), default='local',
              help='Install hooks locally or globally')
def install(scope):
    """Install PolyCLI bridge hooks for Claude Code."""
    from .scripts.claude_hooks import ClaudeHooksManager
    manager = ClaudeHooksManager(scope=scope)
    
    if manager.is_installed():
        click.echo(f"✓ PolyCLI hooks already installed in {scope} settings")
    elif manager.install_bridge_hooks():
        click.echo(f"✓ Installed PolyCLI hooks in {scope} settings")
        click.echo(f"  Command: {manager._get_hook_command()}")
    else:
        click.echo(f"✗ Failed to install hooks", err=True)
        raise click.Abort()


@cchook.command()
@click.option('--scope', '-s', type=click.Choice(['local', 'global']), default='local',
              help='Uninstall hooks locally or globally')
def uninstall(scope):
    """Remove PolyCLI bridge hooks from Claude Code."""
    from .scripts.claude_hooks import ClaudeHooksManager
    manager = ClaudeHooksManager(scope=scope)
    
    if not manager.is_installed():
        click.echo(f"✓ No PolyCLI hooks found in {scope} settings")
    elif manager.uninstall_bridge_hooks():
        click.echo(f"✓ Uninstalled PolyCLI hooks from {scope} settings")
    else:
        click.echo(f"✗ Failed to uninstall hooks", err=True)
        raise click.Abort()


@cchook.command('list')
@click.option('--scope', '-s', type=click.Choice(['local', 'global']), default='local',
              help='List hooks locally or globally')
def list_hooks(scope):
    """List current Claude Code hooks configuration."""
    from .scripts.claude_hooks import ClaudeHooksManager
    import json
    manager = ClaudeHooksManager(scope=scope)
    
    hooks = manager.list_hooks()
    if hooks:
        click.echo(json.dumps(hooks, indent=2))
    else:
        click.echo(f"No hooks configured in {scope} settings")


@cchook.command()
@click.option('--scope', '-s', type=click.Choice(['local', 'global']), default='local',
              help='Check hooks locally or globally')
def check(scope):
    """Check if PolyCLI hooks are installed."""
    from .scripts.claude_hooks import ClaudeHooksManager
    manager = ClaudeHooksManager(scope=scope)
    
    if manager.is_installed():
        click.echo(f"✓ PolyCLI hooks are installed in {scope} settings")
    else:
        click.echo(f"✗ PolyCLI hooks are not installed in {scope} settings")


@cli.command(hidden=True)  # @@@ Easter egg - resume from Claude Code
def chat():
    """Resume from latest Claude Code session."""
    from .utils.chat import run_chat
    run_chat()


if __name__ == "__main__":
    cli()