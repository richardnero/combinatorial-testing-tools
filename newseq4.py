#!/usr/bin/env python3
"""
Combinatorial Test Sequence Generator

This program generates minimal test sequences that cover all possible 4-tuples
of N events. This is useful for combinatorial testing where you want to ensure
every combination of 4 different events appears in at least one test sequence.

The algorithm uses a greedy approach:
1. Start with two initial sequences (ascending and descending)
2. Generate random candidate sequences
3. Pick the candidate that covers the most uncovered 4-tuples
4. Optionally create reversed sequences for additional coverage
5. Repeat until all 4-tuples are covered

This Python implementation replicates the logic of the original C program
while providing better readability, error handling, and progress reporting.

Author: Converted and improved from C implementation
"""

import sys
import random
import time
from typing import List, Set, Tuple


class CombinatorialTestGenerator:
    """
    Generates test sequences to achieve complete 4-way combinatorial coverage.
    
    This class replicates the behavior of the original C program but with
    improved structure, documentation, and user feedback.
    """
    
    def __init__(self, n_events: int, max_tests: int = 10000, n_trials: int = 1000):
        """
        Initialize the test generator.
        
        Args:
            n_events: Number of different events (N in the original C code)
            max_tests: Maximum number of test sequences to generate (MAXT)
            n_trials: Number of random candidates to evaluate per iteration (NTRIALS)
        """
        if n_events < 4:
            raise ValueError("Number of events must be at least 4 for 4-way testing")
            
        self.n_events = n_events
        self.max_tests = max_tests
        self.n_trials = n_trials
        
        # Calculate total number of 4-tuples to cover (NSEQ in C code)
        # This is the number of ways to choose 4 different elements from N elements
        # where order matters: N * (N-1) * (N-2) * (N-3)
        self.total_sequences = n_events * (n_events - 1) * (n_events - 2) * (n_events - 3)
        
        # Enable reversal optimization for larger problems (matches C code logic)
        self.use_reversal = n_events > 5
        
        # Track which 4-tuples have been covered
        # Using a set for O(1) lookup instead of the C code's 4D array
        self.covered_sequences: Set[Tuple[int, int, int, int]] = set()
        
        # Store generated test sequences
        self.test_sequences: List[List[int]] = []
        
        print(f"Combinatorial Test Generator initialized for {n_events} events")
        print(f"Total 4-tuples to cover: {self.total_sequences:,}")
        print(f"Using reversal optimization: {'Yes' if self.use_reversal else 'No'}")
        print(f"Maximum test sequences allowed: {max_tests:,}")
        print(f"Candidates evaluated per iteration: {n_trials:,}")
        print("-" * 70)
    
    def extract_4tuples_from_sequence(self, sequence: List[int]) -> Set[Tuple[int, int, int, int]]:
        """
        Extract all 4-tuples from a test sequence.
        
        This exactly replicates the C code's nested loop structure in the analyze() function:
        for (i=0; i<N-3; i++)
        for (j=i+1; j<N-2; j++)  
        for (k=j+1; k<N-1; k++)
        for (r=k+1; r<N; r++)
        
        Args:
            sequence: A test sequence (permutation of 0 to n_events-1)
            
        Returns:
            Set of all 4-tuples found in the sequence
        """
        tuples_found = set()
        n = len(sequence)
        
        # Match the C code's nested loop structure exactly
        for i in range(n - 3):
            for j in range(i + 1, n - 2):
                for k in range(j + 1, n - 1):
                    for r in range(k + 1, n):
                        # Extract the values at these positions to form a 4-tuple
                        tuple_values = (sequence[i], sequence[j], sequence[k], sequence[r])
                        tuples_found.add(tuple_values)
        
        return tuples_found
    
    def count_new_coverage(self, candidate_sequence: List[int]) -> int:
        """
        Count how many new 4-tuples would be covered by a candidate sequence.
        
        This implements the coverage counting logic from the C code's main loop
        where it evaluates tmptest[m] candidates.
        
        Args:
            candidate_sequence: A candidate test sequence
            
        Returns:
            Number of previously uncovered 4-tuples this sequence would cover
        """
        candidate_tuples = self.extract_4tuples_from_sequence(candidate_sequence)
        new_tuples = candidate_tuples - self.covered_sequences
        return len(new_tuples)
    
    def generate_random_sequence(self) -> List[int]:
        """
        Generate a random permutation of events.
        
        This replicates the C code's candidate generation in the main loop:
        tmptest[i][0] = rand()%N;
        for (j=1; j<N; j++) {
            n=rand()%N; while (tmpused(i,n,j)) n=rand()%N;
            tmptest[i][j] = n;   
        }
        
        Returns:
            Random sequence containing each event exactly once
        """
        sequence = []
        available = set(range(self.n_events))
        
        # Build sequence one element at a time, ensuring no duplicates
        # This matches the C code's approach of checking tmpused()
        for _ in range(self.n_events):
            element = random.choice(list(available))
            sequence.append(element)
            available.remove(element)
        
        return sequence
    
    def add_sequence_coverage(self, sequence: List[int]) -> int:
        """
        Add a sequence to our test set and update coverage tracking.
        
        This implements the functionality of the C code's analyze() function
        which marks covered 4-tuples in the chk array.
        
        Args:
            sequence: Test sequence to add
            
        Returns:
            Number of new 4-tuples covered by this sequence
        """
        sequence_tuples = self.extract_4tuples_from_sequence(sequence)
        new_tuples = sequence_tuples - self.covered_sequences
        
        # Update coverage (equivalent to setting chk[i][j][k][r] = 1 in C)
        self.covered_sequences.update(sequence_tuples)
        self.test_sequences.append(sequence.copy())
        
        return len(new_tuples)
    
    def is_fully_covered(self) -> bool:
        """
        Check if all required 4-tuples have been covered.
        
        This implements the C code's allcovered() function logic.
        
        Returns:
            True if all 4-tuples are covered, False otherwise
        """
        return len(self.covered_sequences) >= self.total_sequences
    
    def generate_test_suite(self) -> List[List[int]]:
        """
        Generate a complete test suite with full 4-way coverage.
        
        This implements the main algorithm from the C code:
        1. Initialize with ascending and descending sequences
        2. Generate and evaluate random candidates
        3. Pick the best candidate and optionally add its reverse
        4. Repeat until coverage is complete
        
        Returns:
            List of test sequences that provide complete coverage
        """
        print("Starting test sequence generation...")
        print()
        
        # Initialize with two sequences (matches C code initialization)
        # test[0][i] = i;           // ascending: [0, 1, 2, 3, ...]
        # test[1][i] = N-1-i;       // descending: [N-1, N-2, ..., 1, 0]
        ascending_seq = list(range(self.n_events))
        descending_seq = list(reversed(range(self.n_events)))
        
        print(f"Test sequence 1 (ascending):  {ascending_seq}")
        new_coverage = self.add_sequence_coverage(ascending_seq)
        print(f"  → Covers {new_coverage:,} new 4-tuples")
        
        print(f"Test sequence 2 (descending): {descending_seq}")
        new_coverage = self.add_sequence_coverage(descending_seq)
        print(f"  → Covers {new_coverage:,} new 4-tuples")
        
        current_coverage = len(self.covered_sequences)
        coverage_percent = 100 * current_coverage / self.total_sequences
        
        print(f"Initial coverage: {current_coverage:,}/{self.total_sequences:,} "
              f"({coverage_percent:.1f}%)")
        print("-" * 50)
        
        iteration = 0
        
        # Main generation loop (matches C code's while (!allcovered() && nt < MAXT))
        while not self.is_fully_covered() and len(self.test_sequences) < self.max_tests:
            iteration += 1
            
            print(f"Iteration {iteration}: Evaluating {self.n_trials:,} candidate sequences...")
            
            # Generate and evaluate candidates (matches C code's NTRIALS loop)
            best_sequence = None
            best_score = 0
            
            for trial in range(self.n_trials):
                candidate = self.generate_random_sequence()
                score = self.count_new_coverage(candidate)
                
                if score > best_score:
                    best_score = score
                    best_sequence = candidate
                
                # Progress indicator for long evaluations
                if trial > 0 and trial % 100 == 0:
                    print(f"  Evaluated {trial:,} candidates... (best score so far: {best_score})")
            
            # Check if we found a useful candidate
            if best_score == 0:
                print("  No candidates provide new coverage. Generation complete.")
                break
            
            print(f"  Best candidate covers {best_score:,} new 4-tuples")
            print(f"  Adding sequence: {best_sequence}")
            
            # Add the best sequence
            self.add_sequence_coverage(best_sequence)
            sequence_count = len(self.test_sequences)
            
            # Optionally add reversed sequence (matches C code's reversal logic)
            if self.use_reversal:
                reversed_seq = list(reversed(best_sequence))
                reversed_coverage = self.count_new_coverage(reversed_seq)
                
                if reversed_coverage > 0:
                    print(f"  Adding reversed sequence: {reversed_seq}")
                    print(f"  → Covers {reversed_coverage:,} additional new 4-tuples")
                    self.add_sequence_coverage(reversed_seq)
            
            # Progress update
            current_coverage = len(self.covered_sequences)
            coverage_percent = 100 * current_coverage / self.total_sequences
            total_sequences = len(self.test_sequences)
            
            print(f"  Progress: {current_coverage:,}/{self.total_sequences:,} 4-tuples covered "
                  f"({coverage_percent:.2f}%)")
            print(f"  Total test sequences: {total_sequences}")
            print()
            
            # Milestone progress reports
            if iteration % 5 == 0:
                print(f"=== Milestone: Iteration {iteration} ===")
                print(f"Coverage: {coverage_percent:.2f}% complete")
                print(f"Sequences: {total_sequences}")
                remaining = self.total_sequences - current_coverage
                print(f"Remaining: {remaining:,} 4-tuples")
                print()
        
        # Final results summary
        final_coverage = len(self.covered_sequences)
        coverage_percent = 100 * final_coverage / self.total_sequences
        
        print("=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print(f"Total test sequences generated: {len(self.test_sequences)}")
        print(f"4-tuples covered: {final_coverage:,} out of {self.total_sequences:,}")
        print(f"Coverage percentage: {coverage_percent:.3f}%")
        print(f"Iterations completed: {iteration}")
        
        if self.is_fully_covered():
            print("SUCCESS: Complete 4-way combinatorial coverage achieved!")
        else:
            missing = self.total_sequences - final_coverage
            print(f"INCOMPLETE: Missing {missing:,} 4-tuples")
            print("  Consider increasing max_tests or n_trials for better coverage")
        
        return self.test_sequences
    
    def print_test_sequences(self):
        """
        Print all generated test sequences in a format matching the C program output.
        
        The C code outputs: "==== N TESTS ====" followed by comma-separated sequences.
        """
        print()
        print("=" * 70)
        print(f"GENERATED TEST SEQUENCES ({len(self.test_sequences)} tests)")
        print("=" * 70)
        
        for i, sequence in enumerate(self.test_sequences, 1):
            # Format matches C code: "1,2,3,4," with trailing comma
            sequence_str = ",".join(map(str, sequence)) + ","
            print(f"Test {i:3d}: {sequence_str}")
    
    def print_coverage_analysis(self):
        """
        Print detailed coverage analysis matching the C program's final output.
        
        The C code prints coverage statistics and the ratio of covered sequences.
        """
        print()
        print("=" * 70)
        print("COVERAGE ANALYSIS")
        print("=" * 70)
        
        total_tests = len(self.test_sequences)
        covered_count = len(self.covered_sequences)
        coverage_ratio = covered_count / self.total_sequences if self.total_sequences > 0 else 0
        
        # Match C code output format
        print(f"Tests: {total_tests}")
        print(f"Sequences covered: {covered_count}")
        print(f"Total sequences (NSEQ): {self.total_sequences}")
        print(f"Coverage ratio: {coverage_ratio:.6f}")
        print(f"Coverage percentage: {100 * coverage_ratio:.3f}%")
        
        if coverage_ratio >= 1.0:
            print("Complete coverage achieved - all 4-tuples are covered!")
        else:
            missing = self.total_sequences - covered_count
            print(f"Incomplete coverage - {missing:,} 4-tuples still missing")
    
    def verify_coverage(self) -> bool:
        """
        Verify that the generated test suite provides the claimed coverage.
        
        This double-checks our coverage calculation by re-analyzing all sequences
        from scratch, similar to the C code's verification logic.
        
        Returns:
            True if coverage calculation is correct
        """
        print()
        print("=" * 70)
        print("VERIFYING COVERAGE")
        print("=" * 70)
        
        # Recalculate coverage from scratch
        verification_coverage = set()
        
        for i, sequence in enumerate(self.test_sequences, 1):
            sequence_tuples = self.extract_4tuples_from_sequence(sequence)
            new_tuples = sequence_tuples - verification_coverage
            verification_coverage.update(sequence_tuples)
            
            print(f"Sequence {i:2d}: {len(sequence_tuples):3d} total 4-tuples, "
                  f"{len(new_tuples):3d} new → cumulative: {len(verification_coverage):,}")
        
        # Compare with our tracking
        tracked_coverage = len(self.covered_sequences)
        verified_coverage = len(verification_coverage)
        
        print(f"\nCoverage verification:")
        print(f"  Tracked during generation: {tracked_coverage:,}")
        print(f"  Verified by re-analysis:   {verified_coverage:,}")
        print(f"  Expected total:            {self.total_sequences:,}")
        
        tracking_correct = tracked_coverage == verified_coverage
        coverage_complete = verified_coverage == self.total_sequences
        
        if tracking_correct:
            print("Coverage tracking is accurate")
        else:  
            print("Coverage tracking error detected!")
            
        if coverage_complete:
            print("Complete coverage verified")
        else:
            missing = self.total_sequences - verified_coverage
            print(f"Coverage incomplete - {missing:,} 4-tuples missing")
        
        return tracking_correct and coverage_complete


def main():
    """
    Main function that replicates the C program's behavior.
    
    Parses command line arguments, creates the generator, runs the algorithm,
    and outputs results in the same format as the original C code.
    """
    
    # Parse command line arguments (matches C code's argc/argv handling)
    if len(sys.argv) < 2:
        print("Usage: python newseq4.py <number_of_events>")
        print("Example: python newseq4.py 6")
        print()
        print("This generates test sequences for N-way combinatorial testing")
        print("where N is the number of different events to be tested.")
        sys.exit(1)
    
    try:
        n_events = int(sys.argv[1])
        if n_events < 4:
            print("Error: Number of events must be at least 4 for 4-way combinatorial testing")
            sys.exit(1)
    except ValueError:
        print("Error: Number of events must be a valid integer")
        sys.exit(1)
    
    # Set random seed for reproducible results (C code uses srand(time(0)))
    # We could make this configurable, but for now we'll use current time
    random.seed(int(time.time()))
    
    print("Combinatorial Test Sequence Generator")
    print("Converted from C implementation with improvements")
    print("=" * 70)
    print(f"Number of events to test: {n_events}")
    print(f"Target: Complete 4-way combinatorial coverage")
    print()
    
    # Create and run the generator
    try:
        generator = CombinatorialTestGenerator(n_events)
        
        start_time = time.time()
        test_sequences = generator.generate_test_suite()
        end_time = time.time()
        
        # Display results in C program format
        generator.print_test_sequences()
        generator.print_coverage_analysis()
        
        print()
        print(f"Generation completed in {end_time - start_time:.2f} seconds")
               
    except KeyboardInterrupt:
        print("\nGeneration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()