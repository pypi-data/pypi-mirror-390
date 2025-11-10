#!/usr/bin/env python3
"""
Performance test script for DeepSeek R1 Local Web UI
"""
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import ModelManager

def test_performance():
    """Run performance tests"""
    print("=" * 60)
    print("Performance Test Suite")
    print("=" * 60)
    
    # Initialize model
    print("\n[1/5] Loading model...")
    start = time.time()
    manager = ModelManager()
    
    try:
        manager.load_model()
        load_time = time.time() - start
        print(f"✓ Model loaded in {load_time:.2f}s")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return
    
    # Test queries
    test_cases = [
        ("What is 2+2?", 50, 0.1),  # Simple, low temp (greedy)
        ("Explain Python in one sentence.", 100, 0.2),  # Short, low temp
        ("Write a haiku about coding.", 100, 0.7),  # Creative, higher temp
        ("What is 2+2?", 50, 0.1),  # Repeat - should use cache
    ]
    
    results = []
    
    for i, (prompt, max_len, temp) in enumerate(test_cases, 1):
        print(f"\n[{i+1}/5] Testing: '{prompt[:40]}...' (temp={temp})")
        
        start = time.time()
        try:
            response = manager.generate_response(prompt, max_len, temp)
            elapsed = time.time() - start
            
            tokens = len(response.split())
            tokens_per_sec = tokens / elapsed if elapsed > 0 else 0
            
            results.append({
                'prompt': prompt,
                'temp': temp,
                'time': elapsed,
                'tokens': tokens,
                'tps': tokens_per_sec,
                'response': response[:100]
            })
            
            print(f"  Time: {elapsed:.2f}s")
            print(f"  Tokens: {tokens} (~{tokens_per_sec:.1f} tokens/sec)")
            print(f"  Response: {response[:80]}...")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({'error': str(e)})
    
    # Summary
    print("\n" + "=" * 60)
    print("Performance Summary")
    print("=" * 60)
    
    valid_results = [r for r in results if 'error' not in r]
    if valid_results:
        avg_time = sum(r['time'] for r in valid_results) / len(valid_results)
        avg_tps = sum(r['tps'] for r in valid_results) / len(valid_results)
        
        print(f"\nTotal tests: {len(results)}")
        print(f"Successful: {len(valid_results)}")
        print(f"Average response time: {avg_time:.2f}s")
        print(f"Average tokens/sec: {avg_tps:.1f}")
        print(f"Cache size: {len(manager.response_cache.cache)}")
        
        # Check if cache worked
        if len(test_cases) == 4 and test_cases[0][0] == test_cases[3][0]:
            first_time = results[0]['time']
            cached_time = results[3]['time']
            if cached_time < first_time * 0.1:  # Should be much faster
                print(f"\n✓ Cache working! Cached response {(first_time/cached_time):.0f}x faster")
            else:
                print(f"\n⚠ Cache may not be working (cached: {cached_time:.2f}s vs first: {first_time:.2f}s)")
        
        # Performance rating
        if avg_tps > 50:
            rating = "Excellent 🚀"
        elif avg_tps > 20:
            rating = "Good ✓"
        elif avg_tps > 10:
            rating = "Acceptable ⚠"
        else:
            rating = "Slow 🐌"
        
        print(f"\nPerformance Rating: {rating}")
    else:
        print("\n✗ All tests failed")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_performance()
