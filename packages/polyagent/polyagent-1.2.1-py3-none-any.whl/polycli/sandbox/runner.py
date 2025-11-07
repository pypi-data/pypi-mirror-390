"""Sandbox runner for Docker execution."""

import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path


def run(project_dir=".", testcase=None, clean=False, no_cache=False, stream=True, ports=None, image=None):
    """
    Run sandbox tests with persistent workspace.
    
    Args:
        project_dir: Project directory containing workflow and testcases
        testcase: Specific test case to run (or None for all)
        clean: If True, clear workspace and cache before running
        no_cache: If True, disable PolyCLI cache for this run
        stream: If True, stream output in real-time
        ports: Port mappings (e.g., "8000:8000,3000:3000")
        image: Docker image to use (default: from config or 'polycli-sandbox')
    """
    
    base = Path(project_dir).resolve()
    
    # Check .polyconfig exists
    config_file = base / ".polyconfig"
    if not config_file.exists():
        print("❌ No .polyconfig found. Run 'polycli sandbox init' first.")
        return
    
    # Parse config
    config = {}
    for line in config_file.read_text().splitlines():
        # Remove inline comments
        if '#' in line:
            line = line[:line.index('#')]
        if ':' in line and line.strip():
            key, value = line.split(':', 1)
            config[key.strip()] = value.strip()
    
    entry = config.get('entry', 'main.py')
    config_ports = config.get('ports', '')
    claude_token = config.get('claude_token')
    config_image = config.get('image', 'polycli-sandbox')
    
    # Determine test cases to run
    testcases_dir = base / "testcases"
    if not testcases_dir.exists():
        print("❌ No testcases/ directory found")
        return
    
    if testcase:
        # Run specific test case
        cases = [testcases_dir / testcase]
        if not cases[0].exists():
            print(f"❌ Test case '{testcase}' not found")
            return
    else:
        # Run all test cases
        cases = [d for d in testcases_dir.iterdir() if d.is_dir()]
        if not cases:
            print("❌ No test cases found in testcases/")
            return
    
    # Determine which Docker image to use
    docker_image = image or config_image
    
    # Check Docker image exists
    result = subprocess.run(
        ["docker", "images", "-q", docker_image],
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        print(f"❌ Docker image '{docker_image}' not found")
        if docker_image == "polycli-sandbox":
            print("  Build it with: docker build -t polycli-sandbox .")
        else:
            print(f"  Pull it with: docker pull {docker_image}")
            print(f"  Or build it with: docker build -t {docker_image} .")
        return
    
    # Check Claude directory permissions if it exists
    claude_dir = Path.home() / ".claude"
    if claude_dir.exists():
        mode = claude_dir.stat().st_mode & 0o777
        if mode < 0o777:
            print("⚠️  Warning: ~/.claude/ directory needs write permissions for Docker")
            print(f"   Current: {oct(mode)}, needs: 0o777")
            print("   Fix with: chmod -R 777 ~/.claude")
            print("   This allows the container to write cache/session data")
            response = input("Continue anyway? [y/N]: ")
            if response.lower() != 'y':
                return
    
    # Process each test case
    for case_path in cases:
        case_name = case_path.name
        print(f"\n▶ Running test case: {case_name}")
        
        # Setup workspace directory (persistent)
        workspace_dir = base / ".workspaces" / case_name
        
        if clean:
            if workspace_dir.exists():
                print(f"  🧹 Cleaning workspace for {case_name}...")
                shutil.rmtree(workspace_dir)
        
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Set permissions for Docker
        workspace_dir.chmod(0o777)
        
        # Log file for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = base / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"{case_name}_{timestamp}.log"
        
        # Show status
        cache_status = "disabled" if no_cache else "enabled"
        workspace_status = "fresh" if clean else "resumed"
        print(f"  Workspace: {workspace_status}")
        print(f"  Cache: {cache_status}")
        if docker_image != "polycli-sandbox":
            print(f"  Image: {docker_image}")
        
        # Build Docker command
        cmd = [
            "docker", "run", "--rm",
            # Mount workflow as read-only
            "-v", f"{base / 'workflow'}:/app/workflow:ro",
            # Mount test case as read-only
            "-v", f"{case_path}:/app/testcase:ro",
            # Mount persistent workspace
            "-v", f"{workspace_dir}:/app/workspace",
            # Set working directory to workspace
            "-w", "/app/workspace",
        ]
        
        # Mount Claude credentials if available
        if claude_dir.exists():
            cmd.extend(["-v", f"{claude_dir}:/home/node/.claude"])
        
        # Mount models.json if it exists
        models_json = base / "models.json"
        if not models_json.exists():
            # Try parent directory (for when running from project subdirectory)
            models_json = base.parent / "models.json"
        if models_json.exists():
            cmd.extend(["-v", f"{models_json}:/app/models.json:ro"])
        
        # Environment variables
        cmd.extend(["-e", "PYTHONUNBUFFERED=1"])
        
        if not no_cache:
            cmd.extend(["-e", "POLYCLI_CACHE=true"])
        
        if claude_token:
            cmd.extend(["-e", f"CLAUDE_CODE_OAUTH_TOKEN={claude_token}"])
        
        # Port mappings
        port_mappings = ports or config_ports
        if port_mappings:
            for port_map in port_mappings.split(','):
                port_map = port_map.strip()
                if port_map:
                    cmd.extend(["-p", port_map])
        
        # Container and command
        cmd.extend([
            docker_image,
            "python", f"/app/workflow/{entry}"
        ])
        
        # Execute with logging
        print(f"  Logging to: logs/{log_file.name}")
        
        if stream:
            # Real-time streaming with tee to log file
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                print("-" * 60)
                for line in process.stdout:
                    print(line, end='')
                    log.write(line)
                    log.flush()
                
                process.wait()
                print("-" * 60)
                
                if process.returncode != 0:
                    print(f"  ❌ Container exited with code {process.returncode}")
                else:
                    print(f"  ✅ Test case completed successfully")
        else:
            # Capture output without streaming
            print("  Running...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Save to log
            with open(log_file, 'w') as log:
                if result.stdout:
                    log.write(result.stdout)
                if result.stderr:
                    log.write("\n--- STDERR ---\n")
                    log.write(result.stderr)
            
            if result.returncode != 0:
                print(f"  ❌ Container exited with code {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}...")
            else:
                print(f"  ✅ Test case completed")
        
        # Summary
        if workspace_dir.exists():
            workspace_files = list(workspace_dir.rglob("*"))
            file_count = sum(1 for f in workspace_files if f.is_file())
            cache_dir = workspace_dir / ".polycache"
            has_cache = cache_dir.exists() and any(cache_dir.iterdir())
            
            print(f"  Workspace: {file_count} files")
            if has_cache:
                print(f"  Cache: Present (will be reused on next run)")


def list_testcases(project_dir="."):
    """List available test cases and their status."""
    base = Path(project_dir).resolve()
    
    testcases_dir = base / "testcases"
    if not testcases_dir.exists():
        print("❌ No testcases/ directory found")
        return
    
    workspaces_dir = base / ".workspaces"
    
    print("Available test cases:")
    for case_dir in sorted(testcases_dir.iterdir()):
        if case_dir.is_dir():
            case_name = case_dir.name
            workspace = workspaces_dir / case_name
            
            status = ""
            if workspace.exists():
                cache_dir = workspace / ".polycache"
                has_cache = cache_dir.exists() and any(cache_dir.iterdir())
                file_count = sum(1 for f in workspace.rglob("*") if f.is_file())
                status = f" (workspace: {file_count} files"
                if has_cache:
                    status += ", cached"
                status += ")"
            else:
                status = " (not run yet)"
            
            print(f"  • {case_name}{status}")
    
    print("\nRun with: polycli sandbox run --testcase <name>")
    print("Clean run: polycli sandbox run --testcase <name> --clean")