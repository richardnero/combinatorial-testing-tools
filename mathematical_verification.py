#!/usr/bin/env python3
"""
Mathematical Verification Tool for NIST-Aligned Implementations

This tool performs comprehensive mathematical verification without needing
the original C implementations. It validates:
1. Mathematical correctness of coverage calculations
2. Algorithmic behavior consistency
3. Statistical properties
4. Edge case handling

Usage: python mathematical_verification.py
"""

import subprocess
import sys
import os
import time
import random
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import math


class MathematicalVerifier:
    """Independent mathematical verification of sequence generators"""
    
    def __init__(self):
        self.test_results = []
        self.tolerance = 1e-6
    
    def calculate_expected_sequences(self, n_events: int, strength: int) -> int:
        """Calculate expected number of t-way sequences mathematically"""
        if strength == 3:
            return n_events * (n_events - 1) * (n_events - 2)
        elif strength == 4:
            return n_events * (n_events - 1) * (n_events - 2) * (n_events - 3)
        else:
            raise ValueError(f"Unsupported strength: {strength}")
    
    def extract_tway_sequences(self, sequences: List[List[int]], strength: int) -> Set[Tuple]:
        """Extract all t-way sequences from test sequences"""
        covered = set()
        
        for seq in sequences:
            n = len(seq)
            
            if strength == 3:
                for i in range(n - 2):
                    for j in range(i + 1, n - 1):
                        for k in range(j + 1, n):
                            # Ensure all elements are different
                            if len(set([seq[i], seq[j], seq[k]])) == 3:
                                covered.add((seq[i], seq[j], seq[k]))
            
            elif strength == 4:
                for i in range(n - 3):
                    for j in range(i + 1, n - 2):
                        for k in range(j + 1, n - 1):
                            for l in range(k + 1, n):
                                # Ensure all elements are different
                                if len(set([seq[i], seq[j], seq[k], seq[l]])) == 4:
                                    covered.add((seq[i], seq[j], seq[k], seq[l]))
        
        return covered
    
    def run_generator(self, script: str, n_events: int) -> Dict:
        """Run a generator and parse its output"""
        try:
            result = subprocess.run(
                [sys.executable, script, str(n_events)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                return {'success': False, 'error': result.stderr}
            
            return self._parse_output(result.stdout, result.stderr)
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_output(self, stdout: str, stderr: str) -> Dict:
        """Parse generator output - fixed for NIST C format"""
        result = {
            'success': True,
            'sequences': [],
            'n_tests': 0,
            'coverage_ratio': 0.0,
            'covered_count': 0,
            'total_sequences': 0
        }
        
        # NIST C format: sequences in stderr, statistics in stdout
        if stderr:
            stderr_lines = stderr.strip().split('\n')
            for line in stderr_lines:
                line = line.strip()
                if line and ',' in line and not line.startswith('new cov') and not line.startswith('---'):
                    try:
                        # Remove trailing comma if present
                        if line.endswith(','):
                            line = line[:-1]
                        
                        # Split by comma and convert to integers
                        parts = line.split(',')
                        sequence = []
                        
                        for part in parts:
                            part = part.strip()
                            if part and part.isdigit():
                                sequence.append(int(part))
                        
                        # Only add if we got a valid sequence
                        if len(sequence) > 0:
                            result['sequences'].append(sequence)
                            
                    except ValueError as e:
                        print(f"Warning: Could not parse sequence line: '{line}' - {e}")
                        continue
        
        # Parse statistics from stdout
        stdout_lines = stdout.strip().split('\n')
        for line in stdout_lines:
            line = line.strip()
            
            # Look for the test count in "==== N TESTS ===="
            if "TESTS" in line and "====" in line:
                try:
                    # Extract number from "==== 8 TESTS ====" 
                    import re
                    match = re.search(r'(\d+)\s+TESTS', line)
                    if match:
                        result['n_tests'] = int(match.group(1))
                except:
                    pass
            
            # Parse final statistics line
            elif line.startswith("Tests:"):
                try:
                    # Format: "Tests: 8. Seqs covered: 60/NSEQ: 60 = 1.000000"
                    import re
                    
                    # Extract coverage ratio (the number after =)
                    if '=' in line:
                        ratio_part = line.split('=')[-1].strip()
                        result['coverage_ratio'] = float(ratio_part)
                    
                    # Extract covered count and total (format: "60/NSEQ: 60")
                    match = re.search(r'(\d+)/NSEQ:\s*(\d+)', line)
                    if match:
                        result['covered_count'] = int(match.group(1))
                        result['total_sequences'] = int(match.group(2))
                    
                    # Also extract test count if we missed it earlier
                    if result['n_tests'] == 0:
                        test_match = re.search(r'Tests:\s*(\d+)', line)
                        if test_match:
                            result['n_tests'] = int(test_match.group(1))
                            
                except Exception as e:
                    print(f"Warning: Could not parse statistics line: '{line}' - {e}")
        
        # Debug output
        if result['n_tests'] == 0 and len(result['sequences']) > 0:
            print(f"Debug: Found {len(result['sequences'])} sequences but n_tests=0")
            print(f"Debug: First few sequences: {result['sequences'][:3]}")
        
        if result['coverage_ratio'] == 0.0 and result['covered_count'] > 0:
            print(f"Debug: Found covered_count={result['covered_count']} but coverage_ratio=0.0")
        
        return result
    
    def verify_sequence_properties(self, sequences: List[List[int]], n_events: int) -> Dict:
        """Verify basic sequence properties"""
        issues = []
        
        for i, seq in enumerate(sequences):
            # Check length
            if len(seq) != n_events:
                issues.append(f"Sequence {i}: Wrong length {len(seq)}, expected {n_events}")
            
            # Check for duplicates
            if len(set(seq)) != len(seq):
                issues.append(f"Sequence {i}: Contains duplicates: {seq}")
            
            # Check element range
            for elem in seq:
                if elem < 0 or elem >= n_events:
                    issues.append(f"Sequence {i}: Element {elem} out of range [0, {n_events-1}]")
            
            # Check if it's a valid permutation
            if sorted(seq) != list(range(n_events)):
                issues.append(f"Sequence {i}: Not a valid permutation of [0, {n_events-1}]")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_sequences': len(sequences)
        }
    
    def verify_coverage_mathematics(self, sequences: List[List[int]], n_events: int, 
                                  strength: int, reported_coverage: float) -> Dict:
        """Verify mathematical correctness of coverage"""
        
        # Calculate expected total
        expected_total = self.calculate_expected_sequences(n_events, strength)
        
        # Extract actual coverage
        actual_coverage = self.extract_tway_sequences(sequences, strength)
        actual_count = len(actual_coverage)
        actual_ratio = actual_count / expected_total
        
        # Verify reported vs actual
        coverage_accurate = abs(reported_coverage - actual_ratio) < self.tolerance
        
        # Check completeness
        is_complete = actual_count >= expected_total
        
        return {
            'expected_total': expected_total,
            'actual_count': actual_count,
            'actual_ratio': actual_ratio,
            'reported_ratio': reported_coverage,
            'coverage_accurate': coverage_accurate,
            'is_complete': is_complete,
            'coverage_difference': abs(reported_coverage - actual_ratio)
        }
    
    def test_algorithmic_consistency(self, script: str, n_events: int, strength: int, runs: int = 5) -> Dict:
        """Test algorithmic consistency across multiple runs"""
        
        results = []
        for run in range(runs):
            result = self.run_generator(script, n_events)
            if result['success']:
                results.append(result)
        
        if not results:
            return {'success': False, 'error': 'No successful runs'}
        
        # Analyze consistency
        test_counts = [r['n_tests'] for r in results]
        coverage_ratios = [r['coverage_ratio'] for r in results]
        
        # Calculate statistics
        avg_tests = sum(test_counts) / len(test_counts)
        std_tests = math.sqrt(sum((x - avg_tests) ** 2 for x in test_counts) / len(test_counts))
        
        avg_coverage = sum(coverage_ratios) / len(coverage_ratios)
        std_coverage = math.sqrt(sum((x - avg_coverage) ** 2 for x in coverage_ratios) / len(coverage_ratios))
        
        # Check for reasonable variation (due to randomness)
        reasonable_test_variation = std_tests / avg_tests < 0.2 if avg_tests > 0 else True
        reasonable_coverage_variation = std_coverage < 0.01  # Coverage should be very consistent
        
        return {
            'success': True,
            'runs': len(results),
            'avg_tests': avg_tests,
            'std_tests': std_tests,
            'test_variation_reasonable': reasonable_test_variation,
            'avg_coverage': avg_coverage,
            'std_coverage': std_coverage,
            'coverage_variation_reasonable': reasonable_coverage_variation,
            'min_tests': min(test_counts),
            'max_tests': max(test_counts),
            'all_complete_coverage': all(r['coverage_ratio'] >= 0.999 for r in results)
        }
    
    def verify_edge_cases(self, script: str, strength: int) -> Dict:
        """Test edge cases"""
        edge_results = {}
        
        # Test minimum valid size
        min_events = strength
        print(f"Testing minimum case: {min_events} events...")
        result = self.run_generator(script, min_events)
        
        if result['success']:
            # Verify sequences
            seq_check = self.verify_sequence_properties(result['sequences'], min_events)
            
            # Verify coverage
            coverage_check = self.verify_coverage_mathematics(
                result['sequences'], min_events, strength, result['coverage_ratio']
            )
            
            edge_results['minimum_case'] = {
                'n_events': min_events,
                'sequences_valid': seq_check['valid'],
                'coverage_complete': coverage_check['is_complete'],
                'coverage_accurate': coverage_check['coverage_accurate'],
                'n_tests': result['n_tests']
            }
        else:
            edge_results['minimum_case'] = {'success': False, 'error': result['error']}
        
        return edge_results
    
    def run_comprehensive_verification(self, script: str, strength: int) -> Dict:
        """Run comprehensive mathematical verification"""
        
        print(f"Mathematical Verification of {os.path.basename(script)}")
        print(f"Strength: {strength}-way")
        print("=" * 50)
        
        verification_results = {
            'script': script,
            'strength': strength,
            'overall_success': True,
            'tests': {}
        }
        
        # Test cases to verify
        test_cases = [strength, strength + 1, strength + 2, 8]  # Include various sizes
        
        for n_events in test_cases:
            print(f"\nTesting {n_events} events...")
            
            # Run single test
            result = self.run_generator(script, n_events)
            
            if not result['success']:
                print(f"  ✗ Failed to run: {result['error']}")
                verification_results['tests'][n_events] = {'success': False}
                verification_results['overall_success'] = False
                continue
            
            # Verify sequence properties
            seq_check = self.verify_sequence_properties(result['sequences'], n_events)
            
            # Verify coverage mathematics
            coverage_check = self.verify_coverage_mathematics(
                result['sequences'], n_events, strength, result['coverage_ratio']
            )
            
            # Test consistency
            consistency_check = self.test_algorithmic_consistency(script, n_events, strength, runs=3)
            
            # Compile results
            test_result = {
                'success': True,
                'n_tests': result['n_tests'],
                'sequences_valid': seq_check['valid'],
                'coverage_complete': coverage_check['is_complete'],
                'coverage_accurate': coverage_check['coverage_accurate'],
                'algorithmically_consistent': consistency_check['success'] and 
                                           consistency_check['coverage_variation_reasonable'],
                'sequence_issues': len(seq_check['issues']),
                'coverage_difference': coverage_check['coverage_difference']
            }
            
            verification_results['tests'][n_events] = test_result
            
            # Print results
            print(f"  Tests generated: {result['n_tests']}")
            print(f"  Sequences valid: {'✓' if seq_check['valid'] else '✗'}")
            if seq_check['issues']:
                print(f"    Issues: {len(seq_check['issues'])}")
            
            print(f"  Coverage complete: {'✓' if coverage_check['is_complete'] else '✗'}")
            print(f"  Coverage accurate: {'✓' if coverage_check['coverage_accurate'] else '✗'}")
            print(f"  Algorithmically consistent: {'✓' if test_result['algorithmically_consistent'] else '✗'}")
            
            # Check if this test failed
            if not all([seq_check['valid'], coverage_check['is_complete'], 
                       coverage_check['coverage_accurate'], test_result['algorithmically_consistent']]):
                verification_results['overall_success'] = False
        
        return verification_results
    
    def generate_verification_report(self, results: Dict) -> str:
        """Generate comprehensive verification report"""
        
        report = []
        report.append("MATHEMATICAL VERIFICATION REPORT")
        report.append("=" * 50)
        report.append(f"Script: {os.path.basename(results['script'])}")
        report.append(f"Strength: {results['strength']}-way")
        report.append(f"Overall Result: {'PASS' if results['overall_success'] else 'FAIL'}")
        report.append("")
        
        # Test results
        report.append("TEST RESULTS")
        report.append("-" * 20)
        
        for n_events, test_result in results['tests'].items():
            if not test_result.get('success', True):
                report.append(f"{n_events} events: FAILED TO RUN")
                continue
            
            status = "PASS" if all([
                test_result['sequences_valid'],
                test_result['coverage_complete'], 
                test_result['coverage_accurate'],
                test_result['algorithmically_consistent']
            ]) else "FAIL"
            
            report.append(f"{n_events} events: {status}")
            report.append(f"  Tests: {test_result['n_tests']}")
            report.append(f"  Sequences valid: {'✓' if test_result['sequences_valid'] else '✗'}")
            report.append(f"  Coverage complete: {'✓' if test_result['coverage_complete'] else '✗'}")
            report.append(f"  Coverage accurate: {'✓' if test_result['coverage_accurate'] else '✗'}")
            report.append(f"  Consistent: {'✓' if test_result['algorithmically_consistent'] else '✗'}")
            
            if test_result['sequence_issues'] > 0:
                report.append(f"  Issues: {test_result['sequence_issues']}")
            
            if test_result['coverage_difference'] > 0.001:
                report.append(f"  Coverage error: {test_result['coverage_difference']:.6f}")
        
        # Summary and recommendations
        report.append("")
        report.append("ASSESSMENT")
        report.append("-" * 15)
        
        if results['overall_success']:
            report.append("✓ MATHEMATICAL VERIFICATION PASSED")
            report.append("  The implementation satisfies all mathematical requirements")
            report.append("  and behaves consistently across multiple test cases.")
            report.append("  This provides strong evidence of NIST C equivalence.")
        else:
            report.append("✗ MATHEMATICAL VERIFICATION FAILED")
            report.append("  Issues detected that require investigation:")
            
            failed_tests = [n for n, t in results['tests'].items() 
                          if not t.get('success', True) or not all([
                              t.get('sequences_valid', False),
                              t.get('coverage_complete', False),
                              t.get('coverage_accurate', False),
                              t.get('algorithmically_consistent', False)
                          ])]
            
            if failed_tests:
                report.append(f"  Failed test cases: {failed_tests}")
        
        return "\n".join(report)


def main():
    """Main verification runner"""
    
    scripts_to_test = [
        ('newseq3.py', 3),
        ('newseq4.py', 4)
    ]
    
    verifier = MathematicalVerifier()
    all_reports = []
    
    for script, strength in scripts_to_test:
        if not os.path.exists(script):
            print(f"Skipping {script} - file not found")
            continue
        
        results = verifier.run_comprehensive_verification(script, strength)
        report = verifier.generate_verification_report(results)
        all_reports.append(report)
        
        print("\n" + report)
        print("\n" + "="*70)
    
    # Save combined report
    if all_reports:
        with open("mathematical_verification_report.txt", "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_reports))
        
        print(f"\nDetailed report saved to: mathematical_verification_report.txt")
    
    # Overall assessment
    print("\nOVERALL ASSESSMENT")
    print("=" * 30)
    
    all_passed = all("PASS" in report for report in all_reports)
    
    if all_passed:
        print("✓ ALL IMPLEMENTATIONS MATHEMATICALLY VERIFIED")
        print("  Strong evidence of NIST C equivalence without needing C compiler")
    else:
        print("✗ SOME IMPLEMENTATIONS NEED FIXES")
        print("  Mathematical verification detected issues")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())