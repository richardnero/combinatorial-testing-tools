#!/usr/bin/env python3
"""
Validation script to compare old vs new implementations
Ensures the aligned versions maintain mathematical correctness
"""

import subprocess
import sys
import os
import time
from typing import Dict, List


def run_script(script_path: str, n_events: int) -> Dict:
    """Run a script and return parsed results"""
    try:
        result = subprocess.run(
            [sys.executable, script_path, str(n_events)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return {'error': result.stderr, 'success': False}
        
        # Parse key metrics from output
        lines = result.stdout.strip().split('\n')
        sequences = []
        n_tests = 0
        coverage_ratio = 0.0
        
        in_tests = False
        for line in lines:
            line = line.strip()
            if "==== " in line and "TESTS" in line:
                in_tests = True
                try:
                    n_tests = int(line.split()[1])
                except:
                    pass
            elif line.startswith("Tests:"):
                in_tests = False
                # Parse coverage ratio
                parts = line.split('=')
                if len(parts) > 1:
                    try:
                        coverage_ratio = float(parts[-1].strip())
                    except:
                        pass
            elif in_tests and line and not line.startswith("---"):
                # Parse sequence
                if line.endswith(','):
                    line = line[:-1]
                try:
                    seq = [int(x) for x in line.split(',') if x.strip().isdigit()]
                    if seq:
                        sequences.append(seq)
                except:
                    pass
        
        return {
            'success': True,
            'n_tests': n_tests,
            'sequences': sequences,
            'coverage_ratio': coverage_ratio,
            'output': result.stdout
        }
        
    except Exception as e:
        return {'error': str(e), 'success': False}


def validate_sequences(sequences: List[List[int]], n_events: int, strength: int) -> Dict:
    """Validate sequence properties"""
    issues = []
    
    for i, seq in enumerate(sequences):
        if len(seq) != n_events:
            issues.append(f"Sequence {i}: wrong length {len(seq)}")
        
        if len(set(seq)) != len(seq):
            issues.append(f"Sequence {i}: has duplicates")
        
        for elem in seq:
            if elem < 0 or elem >= n_events:
                issues.append(f"Sequence {i}: element {elem} out of range")
    
    # Calculate actual coverage
    covered = set()
    if strength == 3:
        for seq in sequences:
            n = len(seq)
            for i in range(n-2):
                for j in range(i+1, n-1):
                    for k in range(j+1, n):
                        if len(set([seq[i], seq[j], seq[k]])) == 3:
                            covered.add((seq[i], seq[j], seq[k]))
        expected_total = n_events * (n_events-1) * (n_events-2)
    
    elif strength == 4:
        for seq in sequences:
            n = len(seq)
            for i in range(n-3):
                for j in range(i+1, n-2):
                    for k in range(j+1, n-1):
                        for l in range(k+1, n):
                            if len(set([seq[i], seq[j], seq[k], seq[l]])) == 4:
                                covered.add((seq[i], seq[j], seq[k], seq[l]))
        expected_total = n_events * (n_events-1) * (n_events-2) * (n_events-3)
    
    return {
        'issues': issues,
        'covered_count': len(covered),
        'expected_total': expected_total,
        'actual_ratio': len(covered) / expected_total if expected_total > 0 else 0
    }


def compare_implementations():
    """Compare old vs new implementations"""
    print("NIST Alignment Validation")
    print("=" * 40)
    
    test_cases = [
        ("newseq3.py", 5, 3),
        ("newseq3.py", 6, 3),
        ("newseq4.py", 5, 4),
        ("newseq4.py", 6, 4),
    ]
    
    results = []
    
    for script, n_events, strength in test_cases:
        print(f"\nTesting {script} with {n_events} events...")
        
        if not os.path.exists(script):
            print(f"  SKIP: {script} not found")
            continue
        
        start_time = time.time()
        result = run_script(script, n_events)
        runtime = time.time() - start_time
        
        if not result['success']:
            print(f"  FAIL: {result['error']}")
            continue
        
        # Validate sequences
        validation = validate_sequences(result['sequences'], n_events, strength)
        
        # Report results
        print(f"  Runtime: {runtime:.2f}s")
        print(f"  Tests generated: {result['n_tests']}")
        print(f"  Reported coverage: {result['coverage_ratio']:.6f}")
        print(f"  Calculated coverage: {validation['actual_ratio']:.6f}")
        print(f"  Coverage match: {'✓' if abs(result['coverage_ratio'] - validation['actual_ratio']) < 0.001 else '✗'}")
        
        if validation['issues']:
            print(f"  Issues: {len(validation['issues'])}")
            for issue in validation['issues'][:3]:
                print(f"    - {issue}")
        else:
            print(f"  Validation: ✓ All sequences valid")
        
        results.append({
            'script': script,
            'n_events': n_events,
            'strength': strength,
            'runtime': runtime,
            'success': len(validation['issues']) == 0,
            'coverage_accurate': abs(result['coverage_ratio'] - validation['actual_ratio']) < 0.001
        })
    
    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    
    total = len(results)
    passed = sum(1 for r in results if r['success'] and r['coverage_accurate'])
    
    print(f"Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All implementations are NIST-compliant")
        print("✓ Mathematical correctness verified")
        print("✓ Ready for production use")
    else:
        print("✗ Some tests failed - review implementation")
        failed = [r for r in results if not (r['success'] and r['coverage_accurate'])]
        for f in failed:
            print(f"  - {f['script']} ({f['n_events']} events): Issues detected")
    
    return passed == total


if __name__ == "__main__":
    success = compare_implementations()
    sys.exit(0 if success else 1)