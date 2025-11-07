"""Sandbox module for safe polycli testing."""

import json
from pathlib import Path


def init(project_dir="."):
    """Initialize a new sandbox project structure."""
    
    base = Path(project_dir)
    
    # Track what was created vs skipped
    created = []
    skipped = []
    
    # Create directories
    for dir_path in [base / "workflow", base / "testcases" / "example", base / "logs"]:
        if dir_path.exists():
            skipped.append(str(dir_path.relative_to(base)))
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            created.append(str(dir_path.relative_to(base)))
    
    # Note: .workspaces/ will be created on first run
    
    # Create minimal .polyconfig
    config_file = base / ".polyconfig"
    if config_file.exists():
        skipped.append(".polyconfig")
    else:
        config_content = """# PolyCLI Sandbox Configuration
# Entry point in workflow directory
entry: main.py
# Port mappings for services
ports: 8765:8765,8766:8766
# Docker image to use (default: polycli-sandbox)
# image: polycli-sandbox
# Add your Claude OAuth token here (run 'claude setup-token' to get one)
# claude_token: sk-ant-oat01-xxxxx
"""
        config_file.write_text(config_content)
        created.append(".polyconfig")
    
    # Create example entry point
    entry_file = base / "workflow" / "main.py"
    if entry_file.exists():
        skipped.append("workflow/main.py")
    else:
        entry_content = '''"""Example PolyCLI sandbox workflow."""

import json
from pathlib import Path
from polycli import PolyAgent

# Read test configuration
# Test data is always at /app/testcase/
with open("/app/testcase/config.json") as f:
    config = json.load(f)

print(f"Running test: {config['name']}")
print(f"Description: {config['description']}")

# Process with agent (cache persists in workspace)
agent = PolyAgent()
result = agent.run(config["prompt"])
print(f"\\nAgent response:\\n{result.content}")

# Save results (workspace is current directory)
output = Path("results.txt")
output.write_text(result.content)
print(f"\\nSaved results to {output}")

# Example of persistent state
counter_file = Path("run_counter.txt")
if counter_file.exists():
    count = int(counter_file.read_text()) + 1
else:
    count = 1
counter_file.write_text(str(count))
print(f"This is run #{count} for this test case")
'''
        entry_file.write_text(entry_content)
        created.append("workflow/main.py")
    
    # Create sample test case configuration
    test_config_file = base / "testcases" / "example" / "config.json"
    if test_config_file.exists():
        skipped.append("testcases/example/config.json")
    else:
        test_config = {
            "name": "example",
            "description": "Example test case for PolyCLI sandbox",
            "prompt": "Write a haiku about testing code in sandboxes"
        }
        test_config_file.write_text(json.dumps(test_config, indent=2))
        created.append("testcases/example/config.json")
    
    # Print results
    if created:
        print("✓ Created:")
        for item in created:
            print(f"  • {item}")
    
    if skipped:
        print("⚠️  Skipped (already exists):")
        for item in skipped:
            print(f"  • {item}")
    
    if not created and skipped:
        print("\nProject already initialized. All files/folders exist.")
    else:
        print("\n📁 Sandbox structure:")
        print("  workflow/    - Your code (read-only in container)")
        print("  testcases/   - Test configurations (read-only in container)")  
        print("  logs/        - Console output from runs")
        print("  .polyconfig  - Configuration")
        print("\nNext steps:")
        print("  1. Run 'polycli sandbox run' to test all cases")
        print("  2. Run 'polycli sandbox run --testcase example' for specific case")
        print("  3. Run 'polycli sandbox run --clean' for fresh start")
        print("\nNote: Workspaces and cache persist between runs (use --clean to reset)")