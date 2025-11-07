"""File watcher for live coding with PolyCLI."""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime


def watch_file(filepath, interval=0.5):
    """
    Watch a file and execute it with cache enabled when it changes.
    
    Perfect for live coding with PolyCLI - just save your file and see results instantly.
    """
    filepath = Path(filepath).resolve()
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return
    
    print(f"👁️  Watching: {filepath}")
    print(f"💾 Cache: ENABLED (.polycache/)")
    print(f"⚡ Save file to run | Ctrl+C to stop")
    print("-" * 50)
    
    last_mtime = 0
    run_count = 0
    
    # Set cache environment variable
    env = os.environ.copy()
    env['POLYCLI_CACHE'] = 'true'
    
    try:
        while True:
            try:
                current_mtime = filepath.stat().st_mtime
                
                if current_mtime > last_mtime:
                    if last_mtime > 0:  # Skip first run
                        run_count += 1
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        
                        print(f"\n🔄 [{timestamp}] Run #{run_count}")
                        print("=" * 50)
                        
                        # Run the file with cache enabled
                        start_time = time.time()
                        result = subprocess.run(
                            [sys.executable, str(filepath)],
                            env=env,
                            capture_output=False,
                            text=True
                        )
                        
                        elapsed = time.time() - start_time
                        
                        print("=" * 50)
                        if result.returncode == 0:
                            print(f"✅ Completed in {elapsed:.2f}s (cache enabled)")
                        else:
                            print(f"❌ Failed with code {result.returncode}")
                        print()
                    
                    last_mtime = current_mtime
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"⚠️  Error: {e}")
                time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n\n👋 Stopped watching (ran {run_count} times)")
        
        # Show cache stats
        cache_dir = filepath.parent / '.polycache'
        if cache_dir.exists():
            cache_files = list(cache_dir.rglob('*.json'))
            if cache_files:
                total_size = sum(f.stat().st_size for f in cache_files)
                print(f"💾 Cache: {len(cache_files)} entries, {total_size/1024:.1f}KB")