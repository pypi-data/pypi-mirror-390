#!/usr/bin/env python3
"""
Test cache validation and rollback functionality.

This demonstrates the optimistic caching with rollback pattern:
1. Results are cached immediately on success
2. Validation can invalidate/remove bad caches
3. Context manager provides automatic rollback on validation failure
"""

import os
import tempfile
import shutil
from pathlib import Path
from polycli import PolyAgent


def validate_positive(content: str) -> bool:
    """Validation function - only accept positive numbers."""
    try:
        num = int(content.strip())
        return num > 0
    except:
        return False


def test_manual_invalidation():
    """Test manual cache invalidation."""
    print("\n=== Test Manual Cache Invalidation ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['POLYCLI_CACHE'] = 'true'
        
        agent1 = PolyAgent(debug=True, cwd=tmpdir)
        
        # First run - should cache
        print("\nFirst run (will be cached):")
        result1 = agent1.run("Say exactly '-5'", cli="no-tools")
        print(f"Result: {result1.content}")
        print(f"From cache: {result1.from_cache}")
        
        # Validate and invalidate if bad
        if not validate_positive(result1.content):
            print("Validation failed - invalidating cache")
            result1.invalidate_cache()
        
        # Fresh agent to simulate new session
        agent2 = PolyAgent(debug=True, cwd=tmpdir)
        
        # Second run - should NOT use cache (was invalidated)
        print("\nSecond run with fresh agent (cache was invalidated):")
        result2 = agent2.run("Say exactly '-5'", cli="no-tools")
        print(f"Result: {result2.content}")
        print(f"From cache: {result2.from_cache}")
        assert not result2.from_cache, "Should not be from cache after invalidation"


def test_context_manager_rollback():
    """Test automatic cache rollback with context manager."""
    print("\n=== Test Context Manager Rollback ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['POLYCLI_CACHE'] = 'true'
        
        agent1 = PolyAgent(debug=True, cwd=tmpdir)
        
        # Run with validation that will fail
        print("\nFirst run with failing validation:")
        try:
            with agent1.run("Say exactly '-10'", cli="no-tools") as result:
                print(f"Result: {result.content}")
                print(f"From cache: {result.from_cache}")
                
                # This validation will fail and raise
                if not validate_positive(result.content):
                    raise ValueError("Negative number not allowed")
        except ValueError as e:
            print(f"Validation error: {e}")
        
        # Fresh agent to simulate new session
        agent2 = PolyAgent(debug=True, cwd=tmpdir)
        
        # Second run - should NOT use cache (was rolled back)
        print("\nSecond run with fresh agent (cache should have been rolled back):")
        result2 = agent2.run("Say exactly '-10'", cli="no-tools")
        print(f"Result: {result2.content}")
        print(f"From cache: {result2.from_cache}")
        assert not result2.from_cache, "Should not be from cache after rollback"


def test_successful_validation():
    """Test that successful validation keeps cache."""
    print("\n=== Test Successful Validation ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['POLYCLI_CACHE'] = 'true'
        
        # First agent for initial run
        agent1 = PolyAgent(debug=True, cwd=tmpdir)
        
        # Run with validation that will pass
        print("\nFirst run with passing validation:")
        with agent1.run("Say exactly '42'", cli="no-tools") as result:
            print(f"Result: {result.content}")
            print(f"From cache: {result.from_cache}")
            
            # This validation will pass
            if not validate_positive(result.content):
                raise ValueError("Not positive")
            print("Validation passed")
        
        # Create fresh agent with same cache dir - simulates new session
        agent2 = PolyAgent(debug=True, cwd=tmpdir)
        
        # Second run - SHOULD use cache (validation passed)
        print("\nSecond run with fresh agent (should use cache):")
        result2 = agent2.run("Say exactly '42'", cli="no-tools")
        print(f"Result: {result2.content}")
        print(f"From cache: {result2.from_cache}")
        assert result2.from_cache, "Should be from cache after successful validation"


def test_no_context_manager():
    """Test that caching still works without context manager."""
    print("\n=== Test Without Context Manager ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['POLYCLI_CACHE'] = 'true'
        
        agent1 = PolyAgent(debug=True, cwd=tmpdir)
        
        # First run - should cache immediately
        print("\nFirst run:")
        result1 = agent1.run("Say exactly 'hello'", cli="no-tools")
        print(f"Result: {result1.content}")
        print(f"From cache: {result1.from_cache}")
        
        # Fresh agent to simulate new session
        agent2 = PolyAgent(debug=True, cwd=tmpdir)
        
        # Second run - should use cache
        print("\nSecond run with fresh agent:")
        result2 = agent2.run("Say exactly 'hello'", cli="no-tools")
        print(f"Result: {result2.content}")
        print(f"From cache: {result2.from_cache}")
        assert result2.from_cache, "Should be from cache"


if __name__ == "__main__":
    test_manual_invalidation()
    test_context_manager_rollback()
    test_successful_validation()
    test_no_context_manager()
    print("\n✅ All tests passed!")