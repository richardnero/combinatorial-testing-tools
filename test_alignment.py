#!/usr/bin/env python3
"""
Test Suite for Sequence Covering Array Generator Alignment
Validates that newseq3.py and newseq4.py produce consistent results
"""

import sys
import os
import subprocess
import time
from typing import List, Tuple, Dict
import tempfile


class SequenceGeneratorTester:
    """Test harness for sequence covering array generators"""
    
    def __init__(self, newseq3_path: str = "newseq3.py", newseq4_path: str = "newseq4.py"):
        self.newseq3_path = newseq3_path
        self.newseq4_path = newseq4_path
        self.test_results = []
    
    def run_generator(self, script_path: str, n_events: int) -> Tuple[List[List[int]], Dict]:
        """Run a sequence generator and parse its output"""
        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, script_path, str(n_events)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Script failed: {result.stderr}")
            
            # Parse output
            lines = result.stdout.strip().split('\n')
            sequences = []
            stats = {}
            
            in_tests_section = False
            for line in lines:
                line = line.strip()
                
                if line.startswith("====") and "TESTS" in line:
                    in_tests_section = True
                    # Extract number of tests
                    parts = line.split()
                    stats['n_tests'] = int(parts[1])
                    continue
                
                if line.startswith("Tests:"):
                    in_tests_section = False
                    # Parse final statistics
                    # Format: "Tests: X. Seqs covered: Y/NSEQ: Z = ratio"
                    parts = line.replace(".", " ").replace(":", " ").replace("=", " ").split()
                    stats['final_tests'] = int(parts[1])
                    stats['covered'] = int(parts[4].split('/')[0])
                    stats['total_sequences'] = int(parts[4].split('/')[1].replace('NSEQ', ''))
                    stats['coverage_ratio'] = float(parts[-1])
                    continue
                
                if in_tests_section and line and not line.startswith("---"):
                    # Parse sequence line
                    if line.endswith(','):
                        line = line[:-1]  # Remove trailing comma
                    sequence = [int(x) for x in line.split(',') if x.strip().isdigit()]
                    if sequence:  # Only add non-empty sequences
                        sequences.append(sequence)
            
            return sequences, stats
            
        except Exception as e:
            print(f"Error running {script_path} with {n_events} events: {e}")
            return [], {}
    
    def validate_sequence_coverage(self, sequences: List[List[int]], n_events: int, strength: int) -> Dict:
        """Validate that sequences provide proper t-way coverage"""
        if strength == 3:
            return self._validate_3way_coverage(sequences, n_events)
        elif strength == 4:
            return self._validate_4way_coverage(sequences, n_events)
        else:
            raise ValueError(f"Unsupported strength: {strength}")
    
    def _validate_3way_coverage(self, sequences: List[List[int]], n_events: int) -> Dict:
        """Validate 3-way sequence coverage"""
        covered_sequences = set()
        expected_total = n_events * (n_events - 1) * (n_events - 2)
        
        for sequence in sequences:
            n = len(sequence)
            for i in range(n - 2):
                for j in range(i + 1, n - 1):
                    for k in range(j + 1, n):
                        if (sequence[i] != sequence[j] and 
                            sequence[i] != sequence[k] and 
                            sequence[j] != sequence[k]):
                            covered_sequences.add((sequence[i], sequence[j], sequence[k]))
        
        return {
            'covered_count': len(covered_sequences),
            'expected_total': expected_total,
            'coverage_ratio': len(covered_sequences) / expected_total,
            'is_complete': len(covered_sequences) >= expected_total
        }
    
    def _validate_4way_coverage(self, sequences: List[List[int]], n_events: int) -> Dict:
        """Validate 4-way sequence coverage"""
        covered_sequences = set()
        expected_total = n_events * (n_events - 1) * (n_events - 2) * (n_events - 3)
        
        for sequence in sequences:
            n = len(sequence)
            for i in range(n - 3):
                for j in range(i + 1, n - 2):
                    for k in range(j + 1, n - 1):
                        for l in range(k + 1, n):
                            elements = [sequence[i], sequence[j], sequence[k], sequence[l]]
                            if len(set(elements)) == 4:  # All different
                                covered_sequences.add(tuple(elements))
        
        return {
            'covered_count': len(covered_sequences),
            'expected_total': expected_total,
            'coverage_ratio': len(covered_sequences) / expected_total,
            'is_complete': len(covered_sequences) >= expected_total
        }
    
    def test_output_format_consistency(self, n_events_list: List[int]) -> Dict:
        """Test that both generators produce consistent output formats"""
        results = {}
        
        for n_events in n_events_list:
            print(f"\nTesting output format consistency for {n_events} events...")
            
            # Test newseq3
            if n_events >= 3:
                seq3, stats3 = self.run_generator(self.newseq3_path, n_events)
                coverage3 = self.validate_sequence_coverage(seq3, n_events, 3)
            else:
                seq3, stats3, coverage3 = [], {}, {}
            
            # Test newseq4
            if n_events >= 4:
                seq4, stats4 = self.run_generator(self.newseq4_path, n_events)
                coverage4 = self.validate_sequence_coverage(seq4, n_events, 4)
            else:
                seq4, stats4, coverage4 = [], {}, {}
            
            results[n_events] = {
                'newseq3': {
                    'sequences': seq3,
                    'stats': stats3,
                    'coverage': coverage3
                },
                'newseq4': {
                    'sequences': seq4,
                    'stats': stats4,
                    'coverage': coverage4
                }
            }
        
        return results
    
    def test_sequence_validity(self, sequences: List[List[int]], n_events: int) -> List[str]:
        """Test that sequences are valid (no repeated elements)"""
        issues = []
        
        for i, sequence in enumerate(sequences):
            # Check length
            if len(sequence) != n_events:
                issues.append(f"Sequence {i}: Wrong length {len(sequence)}, expected {n_events}")
            
            # Check for repeated elements
            if len(set(sequence)) != len(sequence):
                issues.append(f"Sequence {i}: Contains repeated elements: {sequence}")
            
            # Check element range
            for elem in sequence:
                if elem < 0 or elem >= n_events:
                    issues.append(f"Sequence {i}: Element {elem} out of range [0, {n_events-1}]")
        
        return issues
    
    def generate_test_report(self, results: Dict) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("SEQUENCE COVERING ARRAY GENERATOR ALIGNMENT TEST REPORT")
        report.append("=" * 60)
        report.append(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for n_events, data in results.items():
            report.append(f"TEST RESULTS FOR {n_events} EVENTS")
            report.append("-" * 40)
            
            # newseq3 results
            if data['newseq3']['sequences']:
                seq3 = data['newseq3']['sequences']
                stats3 = data['newseq3']['stats']
                coverage3 = data['newseq3']['coverage']
                
                report.append(f"newseq3.py:")
                report.append(f"  Generated {len(seq3)} test sequences")
                report.append(f"  Reported {stats3.get('final_tests', 'N/A')} tests")
                report.append(f"  Coverage: {coverage3.get('covered_count', 0)}/{coverage3.get('expected_total', 0)} "
                            f"({coverage3.get('coverage_ratio', 0):.4f})")
                
                validity_issues = self.test_sequence_validity(seq3, n_events)
                if validity_issues:
                    report.append(f"  VALIDITY ISSUES:")
                    for issue in validity_issues[:5]:  # Limit to first 5 issues
                        report.append(f"    - {issue}")
                else:
                    report.append(f"  All sequences are valid")
            else:
                report.append(f"newseq3.py: No sequences generated (n_events < 3)")
            
            # newseq4 results
            if data['newseq4']['sequences']:
                seq4 = data['newseq4']['sequences']
                stats4 = data['newseq4']['stats']
                coverage4 = data['newseq4']['coverage']
                
                report.append(f"newseq4.py:")
                report.append(f"  Generated {len(seq4)} test sequences")
                report.append(f"  Reported {stats4.get('final_tests', 'N/A')} tests")
                report.append(f"  Coverage: {coverage4.get('covered_count', 0)}/{coverage4.get('expected_total', 0)} "
                            f"({coverage4.get('coverage_ratio', 0):.4f})")
                
                validity_issues = self.test_sequence_validity(seq4, n_events)
                if validity_issues:
                    report.append(f"  VALIDITY ISSUES:")
                    for issue in validity_issues[:5]:
                        report.append(f"    - {issue}")
                else:
                    report.append(f"  All sequences are valid")
            else:
                report.append(f"newseq4.py: No sequences generated (n_events < 4)")
            
            report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 20)
        
        total_tests = len(results)
        successful_tests = 0
        
        for n_events, data in results.items():
            newseq3_ok = (data['newseq3']['coverage'].get('is_complete', False) or 
                         data['newseq3']['coverage'].get('coverage_ratio', 0) > 0.95)
            newseq4_ok = (data['newseq4']['coverage'].get('is_complete', False) or 
                         data['newseq4']['coverage'].get('coverage_ratio', 0) > 0.95)
            
            if (n_events < 3 or newseq3_ok) and (n_events < 4 or newseq4_ok):
                successful_tests += 1
        
        report.append(f"Tests passed: {successful_tests}/{total_tests}")
        
        if successful_tests == total_tests:
            report.append("✓ ALL TESTS PASSED - Generators are properly aligned")
        else:
            report.append("✗ SOME TESTS FAILED - Review alignment implementation")
        
        return "\n".join(report)
    
    def run_alignment_tests(self, test_sizes: List[int] = None) -> str:
        """Run complete alignment test suite"""
        if test_sizes is None:
            test_sizes = [5, 6, 7, 8, 10]
        
        print("Running Sequence Generator Alignment Tests...")
        print(f"Testing with event sizes: {test_sizes}")
        
        results = self.test_output_format_consistency(test_sizes)
        report = self.generate_test_report(results)
        
        return report


def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        test_sizes = [int(x) for x in sys.argv[1:]]
    else:
        test_sizes = [5, 6, 7, 8]  # Default test sizes
    
    # Check if generator files exist
    if not os.path.exists("newseq3.py"):
        print("Error: newseq3.py not found in current directory")
        sys.exit(1)
    
    if not os.path.exists("newseq4.py"):
        print("Error: newseq4.py not found in current directory")
        sys.exit(1)
    
    # Run tests
    tester = SequenceGeneratorTester()
    report = tester.run_alignment_tests(test_sizes)
    
    print(report)
    
    # Save report to file
    with open("alignment_test_report.txt", "w") as f:
        f.write(report)
    
    print(f"\nTest report saved to: alignment_test_report.txt")


if __name__ == "__main__":
    main()