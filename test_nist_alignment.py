#!/usr/bin/env python3
"""
NIST C Compliance Test Suite
Validates mathematical correctness and algorithmic alignment with NIST reference implementations
"""

import sys
import os
import subprocess
import time
import re
from typing import List, Tuple, Dict, Set


class NistComplianceValidator:
    """Validates NIST C compliance for sequence covering array generators"""
    
    def __init__(self):
        self.test_results = []
        self.tolerance = 1e-6  # Floating point comparison tolerance
    
    def parse_nist_output(self, output: str) -> Dict:
        """Parse NIST-compliant output format and extract key metrics"""
        lines = output.strip().split('\n')
        
        result = {
            'n_events': None,
            'sequences': [],
            'n_tests': None,
            'covered': None,
            'total_sequences': None,
            'coverage_ratio': None,
            'new_cov_values': [],
            'progress_reports': []
        }
        
        in_tests_section = False
        
        for line in lines:
            line = line.strip()
            
            # Extract number of events from first line
            if line.startswith("Generating test sequences for"):
                match = re.search(r'for (\d+) events', line)
                if match:
                    result['n_events'] = int(match.group(1))
            
            # Track "new cov" values
            if line.startswith("new cov"):
                match = re.search(r'new cov (\d+)', line)
                if match:
                    result['new_cov_values'].append(int(match.group(1)))
            
            # Track progress reports
            if line.startswith("--- covered"):
                result['progress_reports'].append(line)
            
            # Detect test section
            if line.startswith("====") and "TESTS" in line:
                in_tests_section = True
                match = re.search(r'(\d+) TESTS', line)
                if match:
                    result['n_tests'] = int(match.group(1))
                continue
            
            # Parse test sequences
            if in_tests_section and line and not line.startswith("Tests:"):
                if line.endswith(','):
                    line = line[:-1]
                try:
                    sequence = [int(x) for x in line.split(',') if x.strip().isdigit()]
                    if sequence:
                        result['sequences'].append(sequence)
                except ValueError:
                    pass
            
            # Parse final statistics
            if line.startswith("Tests:"):
                in_tests_section = False
                # Format: "Tests: X. Seqs covered: Y/NSEQ: Z = ratio"
                match = re.search(r'Tests: (\d+)\. Seqs covered: (\d+)/NSEQ: (\d+) = ([\d.]+)', line)
                if match:
                    result['covered'] = int(match.group(2))
                    result['total_sequences'] = int(match.group(3))
                    result['coverage_ratio'] = float(match.group(4))
        
        return result
    
    def validate_mathematical_correctness(self, result: Dict, strength: int) -> List[str]:
        """Validate mathematical properties of the results"""
        issues = []
        
        n_events = result['n_events']
        if not n_events:
            issues.append("Could not determine number of events")
            return issues
        
        # Validate expected total sequences calculation
        if strength == 3:
            expected_total = n_events * (n_events - 1) * (n_events - 2)
        elif strength == 4:
            expected_total = n_events * (n_events - 1) * (n_events - 2) * (n_events - 3)
        else:
            issues.append(f"Unsupported strength: {strength}")
            return issues
        
        if result['total_sequences'] != expected_total:
            issues.append(f"Total sequences mismatch: got {result['total_sequences']}, expected {expected_total}")
        
        # Validate sequence properties
        for i, sequence in enumerate(result['sequences']):
            # Check length
            if len(sequence) != n_events:
                issues.append(f"Sequence {i}: wrong length {len(sequence)}, expected {n_events}")
            
            # Check for duplicates
            if len(set(sequence)) != len(sequence):
                issues.append(f"Sequence {i}: contains duplicates: {sequence}")
            
            # Check element range
            for elem in sequence:
                if elem < 0 or elem >= n_events:
                    issues.append(f"Sequence {i}: element {elem} out of range [0, {n_events-1}]")
        
        # Validate coverage calculation
        if result['coverage_ratio'] is not None:
            expected_ratio = result['covered'] / result['total_sequences']
            if abs(result['coverage_ratio'] - expected_ratio) > self.tolerance:
                issues.append(f"Coverage ratio mismatch: got {result['coverage_ratio']}, expected {expected_ratio}")
        
        return issues
    
    def validate_coverage_completeness(self, sequences: List[List[int]], n_events: int, strength: int) -> Dict:
        """Independently validate t-way coverage completeness"""
        if strength == 3:
            return self._validate_3way_completeness(sequences, n_events)
        elif strength == 4:
            return self._validate_4way_completeness(sequences, n_events)
        else:
            raise ValueError(f"Unsupported strength: {strength}")
    
    def _validate_3way_completeness(self, sequences: List[List[int]], n_events: int) -> Dict:
        """Validate 3-way coverage completeness using independent calculation"""
        covered = set()
        expected_total = n_events * (n_events - 1) * (n_events - 2)
        
        for sequence in sequences:
            n = len(sequence)
            # Use same nested loop structure as NIST C
            for i in range(n - 2):
                for j in range(i + 1, n - 1):
                    for k in range(j + 1, n):
                        if (sequence[i] != sequence[j] and 
                            sequence[i] != sequence[k] and 
                            sequence[j] != sequence[k]):
                            covered.add((sequence[i], sequence[j], sequence[k]))
        
        return {
            'covered_count': len(covered),
            'expected_total': expected_total,
            'coverage_ratio': len(covered) / expected_total,
            'is_complete': len(covered) >= expected_total,
            'missing_count': max(0, expected_total - len(covered))
        }
    
    def _validate_4way_completeness(self, sequences: List[List[int]], n_events: int) -> Dict:
        """Validate 4-way coverage completeness using independent calculation"""
        covered = set()
        expected_total = n_events * (n_events - 1) * (n_events - 2) * (n_events - 3)
        
        for sequence in sequences:
            n = len(sequence)
            # Use same nested loop structure as NIST C
            for i in range(n - 3):
                for j in range(i + 1, n - 2):
                    for k in range(j + 1, n - 1):
                        for l in range(k + 1, n):
                            elements = [sequence[i], sequence[j], sequence[k], sequence[l]]
                            if len(set(elements)) == 4:  # All different
                                covered.add(tuple(elements))
        
        return {
            'covered_count': len(covered),
            'expected_total': expected_total,
            'coverage_ratio': len(covered) / expected_total,
            'is_complete': len(covered) >= expected_total,
            'missing_count': max(0, expected_total - len(covered))
        }
    
    def test_nist_compliance(self, script_path: str, n_events: int, strength: int) -> Dict:
        """Test a single script for NIST compliance"""
        test_result = {
            'script': script_path,
            'n_events': n_events,
            'strength': strength,
            'success': False,
            'runtime': 0,
            'issues': [],
            'coverage_validation': {},
            'nist_output': {}
        }
        
        try:
            start_time = time.time()
            
            # Run the script
            result = subprocess.run(
                [sys.executable, script_path, str(n_events)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            end_time = time.time()
            test_result['runtime'] = end_time - start_time
            
            if result.returncode != 0:
                test_result['issues'].append(f"Script failed with return code {result.returncode}")
                test_result['issues'].append(f"Error: {result.stderr}")
                return test_result
            
            # Parse NIST output
            nist_output = self.parse_nist_output(result.stdout)
            test_result['nist_output'] = nist_output
            
            # Validate mathematical correctness
            math_issues = self.validate_mathematical_correctness(nist_output, strength)
            test_result['issues'].extend(math_issues)
            
            # Independent coverage validation
            if nist_output['sequences']:
                coverage_validation = self.validate_coverage_completeness(
                    nist_output['sequences'], n_events, strength
                )
                test_result['coverage_validation'] = coverage_validation
                
                # Compare reported vs calculated coverage
                if nist_output['covered'] != coverage_validation['covered_count']:
                    test_result['issues'].append(
                        f"Coverage mismatch: reported {nist_output['covered']}, "
                        f"calculated {coverage_validation['covered_count']}"
                    )
            
            # Check if test was successful
            test_result['success'] = len(test_result['issues']) == 0
            
        except subprocess.TimeoutExpired:
            test_result['issues'].append("Script execution timed out (>120s)")
        except Exception as e:
            test_result['issues'].append(f"Execution error: {e}")
        
        return test_result
    
    def run_compliance_suite(self, test_cases: List[Tuple[str, int, int]]) -> str:
        """Run complete NIST compliance test suite"""
        print("NIST C Compliance Validation Suite")
        print("=" * 50)
        print()
        
        results = []
        
        for script_path, n_events, strength in test_cases:
            if not os.path.exists(script_path):
                print(f"SKIP: {script_path} not found")
                continue
            
            print(f"Testing {script_path} with {n_events} events ({strength}-way)...")
            
            result = self.test_nist_compliance(script_path, n_events, strength)
            results.append(result)
            
            if result['success']:
                print(f"  ✓ PASS ({result['runtime']:.2f}s)")
                coverage = result['coverage_validation']
                if coverage:
                    print(f"    Coverage: {coverage['covered_count']}/{coverage['expected_total']} ({coverage['coverage_ratio']:.4f})")
                    if coverage['is_complete']:
                        print(f"    ✓ Complete coverage achieved")
                    else:
                        print(f"    ⚠ Incomplete: {coverage['missing_count']} sequences missing")
            else:
                print(f"  ✗ FAIL ({result['runtime']:.2f}s)")
                for issue in result['issues'][:3]:  # Show first 3 issues
                    print(f"    - {issue}")
                if len(result['issues']) > 3:
                    print(f"    ... and {len(result['issues']) - 3} more issues")
            print()
        
        # Generate comprehensive report
        return self.generate_compliance_report(results)
    
    def generate_compliance_report(self, results: List[Dict]) -> str:
        """Generate detailed compliance report"""
        report = []
        report.append("NIST C COMPLIANCE TEST REPORT")
        report.append("=" * 60)
        report.append(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(results)}")
        report.append("")
        
        # Summary statistics
        passed = sum(1 for r in results if r['success'])
        failed = len(results) - passed
        total_runtime = sum(r['runtime'] for r in results)
        
        report.append("SUMMARY")
        report.append("-" * 20)
        report.append(f"Tests Passed: {passed}/{len(results)}")
        report.append(f"Tests Failed: {failed}/{len(results)}")
        report.append(f"Total Runtime: {total_runtime:.2f} seconds")
        report.append(f"Average Runtime: {total_runtime/len(results):.2f} seconds")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS")
        report.append("-" * 30)
        
        for result in results:
            script_name = os.path.basename(result['script'])
            status = "PASS" if result['success'] else "FAIL"
            
            report.append(f"{script_name} - {result['n_events']} events ({result['strength']}-way): {status}")
            report.append(f"  Runtime: {result['runtime']:.2f}s")
            
            if result['nist_output']:
                output = result['nist_output']
                report.append(f"  Generated: {output.get('n_tests', 'N/A')} test sequences")
                if output.get('coverage_ratio') is not None:
                    report.append(f"  Coverage: {output['coverage_ratio']:.6f}")
            
            if result['coverage_validation']:
                cv = result['coverage_validation']
                report.append(f"  Validated Coverage: {cv['covered_count']}/{cv['expected_total']} ({cv['coverage_ratio']:.4f})")
                report.append(f"  Complete: {'Yes' if cv['is_complete'] else 'No'}")
            
            if result['issues']:
                report.append(f"  Issues:")
                for issue in result['issues'][:5]:  # Limit to 5 issues per test
                    report.append(f"    - {issue}")
                if len(result['issues']) > 5:
                    report.append(f"    ... and {len(result['issues']) - 5} more")
            
            report.append("")
        
        # Alignment assessment
        report.append("ALIGNMENT ASSESSMENT")
        report.append("-" * 25)
        
        newseq3_results = [r for r in results if 'newseq3' in r['script']]
        newseq4_results = [r for r in results if 'newseq4' in r['script']]
        
        if newseq3_results and newseq4_results:
            newseq3_passed = sum(1 for r in newseq3_results if r['success'])
            newseq4_passed = sum(1 for r in newseq4_results if r['success'])
            
            report.append(f"newseq3.py: {newseq3_passed}/{len(newseq3_results)} tests passed")
            report.append(f"newseq4.py: {newseq4_passed}/{len(newseq4_results)} tests passed")
            
            if newseq3_passed == len(newseq3_results) and newseq4_passed == len(newseq4_results):
                report.append("✓ Both generators are NIST C compliant")
            else:
                report.append("✗ Generators need alignment fixes")
        
        # Recommendations
        report.append("")
        report.append("RECOMMENDATIONS")
        report.append("-" * 20)
        
        if failed == 0:
            report.append("✓ All tests passed - generators are properly aligned with NIST C")
        else:
            common_issues = {}
            for result in results:
                for issue in result['issues']:
                    common_issues[issue] = common_issues.get(issue, 0) + 1
            
            if common_issues:
                report.append("Most common issues:")
                for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:3]:
                    report.append(f"  - {issue} ({count} occurrences)")
            
            report.append("Recommended fixes:")
            report.append("  1. Ensure identical NIST C algorithm implementation")
            report.append("  2. Verify mathematical correctness of coverage calculations")
            report.append("  3. Standardize output format to match NIST reference")
            report.append("  4. Test with known reference outputs")
        
        return "\n".join(report)


def main():
    """Main test runner for NIST compliance validation"""
    
    # Define comprehensive test cases: (script_path, n_events, strength)
    test_cases = [
        # newseq3.py tests
        ("newseq3.py", 5, 3),
        ("newseq3.py", 6, 3),
        ("newseq3.py", 7, 3),
        ("newseq3.py", 8, 3),
        
        # newseq4.py tests  
        ("newseq4.py", 5, 4),
        ("newseq4.py", 6, 4),
        ("newseq4.py", 7, 4),
        ("newseq4.py", 8, 4),
    ]
    
    # Allow custom test cases from command line
    if len(sys.argv) > 1:
        custom_cases = []
        i = 1
        while i < len(sys.argv):
            if sys.argv[i] in ["newseq3.py", "newseq4.py"]:
                script = sys.argv[i]
                if i + 1 < len(sys.argv):
                    try:
                        n_events = int(sys.argv[i + 1])
                        strength = 3 if "newseq3" in script else 4
                        custom_cases.append((script, n_events, strength))
                        i += 2
                    except ValueError:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
        
        if custom_cases:
            test_cases = custom_cases
    
    # Run compliance validation
    validator = NistComplianceValidator()
    report = validator.run_compliance_suite(test_cases)
    
    print(report)
    
    # Save report
    with open("nist_compliance_report.txt", "w") as f:
        f.write(report)
    
    print(f"\nDetailed report saved to: nist_compliance_report.txt")
    
    # Exit with appropriate code
    all_passed = all(result['success'] for result in validator.test_results if hasattr(validator, 'test_results'))
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()