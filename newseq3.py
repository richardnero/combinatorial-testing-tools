#!/usr/bin/env python3
"""
Sequence Generator for Test Coverage

This program generates test sequences that cover all possible 3-element subsequences
from N events. It uses a greedy algorithm to find the minimum number of test sequences
needed to achieve complete coverage.

The algorithm works by:
1. Starting with two initial sequences (ascending and descending)
2. Randomly generating candidate sequences
3. Selecting the candidate that covers the most uncovered 3-element subsequences
4. Optionally creating reversed sequences for additional coverage
5. Repeating until all subsequences are covered or maximum tests reached
"""

import sys
import random
import time
from typing import List, Tuple, Set
import argparse


class SequenceGenerator:
    """
    Generates test sequences to cover all possible 3-element subsequences.
    
    A 3-element subsequence is any ordered triple (i,j,k) where i,j,k are distinct
    elements from the sequence, maintaining their relative order.
    """
    
    def __init__(self, n_events: int, max_tests: int = 10000, n_trials: int = 1000, use_reversal: bool = None):
        """
        Initialize the sequence generator.
        
        Args:
            n_events: Number of distinct events/elements (0 to n_events-1)
            max_tests: Maximum number of test sequences to generate
            n_trials: Number of random candidates to generate each iteration
            use_reversal: Whether to generate reversed sequences (auto-determined if None)
        """
        if n_events < 3:
            raise ValueError("Need at least 3 events to generate 3-element subsequences")
            
        self.n_events = n_events
        self.max_tests = max_tests
        self.n_trials = n_trials
        self.n_sequences = n_events * (n_events - 1) * (n_events - 2)  # Total possible 3-subsequences
        
        # Auto-determine reversal strategy based on problem size
        self.use_reversal = use_reversal if use_reversal is not None else (n_events > 5)
        
        # Track which 3-element subsequences have been covered
        # Using a set for O(1) lookup instead of 3D array
        self.covered_subsequences: Set[Tuple[int, int, int]] = set()
        
        # Store generated test sequences
        self.test_sequences: List[List[int]] = []
        
        # Generate all possible 3-element subsequences for reference
        self.all_subsequences = self._generate_all_subsequences()
        
        print(f"Initializing sequence generator:")
        print(f"  Events: {n_events} (labeled 0 to {n_events-1})")
        print(f"  Total 3-element subsequences to cover: {self.n_sequences}")
        print(f"  Maximum test sequences allowed: {max_tests}")
        print(f"  Random candidates per iteration: {n_trials}")
        print(f"  Using reversal strategy: {self.use_reversal}")
        print()
    
    def _generate_all_subsequences(self) -> Set[Tuple[int, int, int]]:
        """Generate all possible 3-element subsequences."""
        subsequences = set()
        for i in range(self.n_events):
            for j in range(self.n_events):
                for k in range(self.n_events):
                    if i != j and i != k and j != k:
                        subsequences.add((i, j, k))
        return subsequences
    
    def _generate_random_sequence(self) -> List[int]:
        """Generate a random permutation of all events."""
        sequence = list(range(self.n_events))
        random.shuffle(sequence)
        return sequence
    
    def _extract_subsequences(self, sequence: List[int]) -> Set[Tuple[int, int, int]]:
        """
        Extract all 3-element subsequences from a sequence.
        
        For a sequence [a,b,c,d,e], subsequences include:
        (a,b,c), (a,b,d), (a,b,e), (a,c,d), (a,c,e), (a,d,e),
        (b,c,d), (b,c,e), (b,d,e), (c,d,e)
        """
        subsequences = set()
        n = len(sequence)
        
        # Generate all combinations of 3 positions, maintaining order
        for i in range(n - 2):
            for j in range(i + 1, n - 1):
                for k in range(j + 1, n):
                    subseq = (sequence[i], sequence[j], sequence[k])
                    subsequences.add(subseq)
        
        return subsequences
    
    def _count_new_coverage(self, sequence: List[int]) -> int:
        """Count how many uncovered subsequences this sequence would cover."""
        candidate_subsequences = self._extract_subsequences(sequence)
        new_coverage = candidate_subsequences - self.covered_subsequences
        return len(new_coverage)
    
    def _add_sequence(self, sequence: List[int]) -> int:
        """
        Add a sequence to our test set and update coverage.
        
        Returns:
            Number of new subsequences covered by this sequence
        """
        subsequences = self._extract_subsequences(sequence)
        new_subsequences = subsequences - self.covered_subsequences
        
        self.covered_subsequences.update(new_subsequences)
        self.test_sequences.append(sequence.copy())
        
        return len(new_subsequences)
    
    def _is_fully_covered(self) -> bool:
        """Check if all possible subsequences have been covered."""
        return len(self.covered_subsequences) >= self.n_sequences
    
    def _get_coverage_stats(self) -> Tuple[int, float]:
        """Get current coverage statistics."""
        covered_count = len(self.covered_subsequences)
        coverage_percentage = (covered_count / self.n_sequences) * 100
        return covered_count, coverage_percentage
    
    def generate_sequences(self) -> List[List[int]]:
        """
        Generate test sequences using a greedy algorithm.
        
        Returns:
            List of test sequences that cover all 3-element subsequences
        """
        print("Starting sequence generation...")
        
        # Step 1: Initialize with two basic sequences
        print("Step 1: Adding initial sequences")
        ascending_seq = list(range(self.n_events))
        descending_seq = list(range(self.n_events - 1, -1, -1))
        
        new_coverage = self._add_sequence(ascending_seq)
        print(f"  Added ascending sequence {ascending_seq}: +{new_coverage} new subsequences")
        
        new_coverage = self._add_sequence(descending_seq)
        print(f"  Added descending sequence {descending_seq}: +{new_coverage} new subsequences")
        
        covered, percentage = self._get_coverage_stats()
        print(f"  Initial coverage: {covered}/{self.n_sequences} ({percentage:.1f}%)")
        print()
        
        # Step 2: Greedy sequence generation
        print("Step 2: Greedy sequence generation")
        iteration = 0
        
        while not self._is_fully_covered() and len(self.test_sequences) < self.max_tests:
            iteration += 1
            print(f"Iteration {iteration}:", end=" ")
            
            # Generate random candidate sequences
            candidates = [self._generate_random_sequence() for _ in range(self.n_trials)]
            
            # Find the candidate with best coverage improvement
            best_candidate = None
            best_coverage = 0
            
            for candidate in candidates:
                coverage = self._count_new_coverage(candidate)
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_candidate = candidate
            
            if best_candidate is None or best_coverage == 0:
                print("No improvement possible with random candidates")
                break
            
            # Add the best candidate
            actual_coverage = self._add_sequence(best_candidate)
            print(f"Added sequence with +{actual_coverage} new subsequences")
            
            # Optionally add reversed sequence
            if self.use_reversal:
                reversed_seq = best_candidate[::-1]
                reversed_coverage = self._add_sequence(reversed_seq)
                if reversed_coverage > 0:
                    print(f"                    Added reversed sequence with +{reversed_coverage} new subsequences")
            
            # Show progress every 10 iterations or when close to completion
            if iteration % 10 == 0 or self._is_fully_covered():
                covered, percentage = self._get_coverage_stats()
                print(f"                    Progress: {covered}/{self.n_sequences} ({percentage:.1f}%) covered")
        
        # Final results
        print()
        print("Sequence generation complete!")
        covered, percentage = self._get_coverage_stats()
        
        if self._is_fully_covered():
            print(f"✓ Successfully achieved 100% coverage!")
        else:
            print(f"⚠ Partial coverage: {percentage:.1f}%")
        
        print(f"  Total test sequences generated: {len(self.test_sequences)}")
        print(f"  Subsequences covered: {covered}/{self.n_sequences}")
        print()
        
        return self.test_sequences
    
    def print_results(self):
        """Print detailed results of the sequence generation."""
        print("=" * 60)
        print(f"FINAL RESULTS FOR {self.n_events} EVENTS")
        print("=" * 60)
        
        print(f"\nGenerated {len(self.test_sequences)} test sequences:")
        print("-" * 40)
        
        for i, sequence in enumerate(self.test_sequences):
            # Format sequence nicely
            seq_str = ",".join(map(str, sequence))
            print(f"Test {i+1:2d}: [{seq_str}]")
        
        # Coverage analysis
        covered, percentage = self._get_coverage_stats()
        print(f"\nCoverage Analysis:")
        print("-" * 40)
        print(f"Total possible 3-element subsequences: {self.n_sequences}")
        print(f"Subsequences covered: {covered}")
        print(f"Coverage percentage: {percentage:.2f}%")
        
        if not self._is_fully_covered():
            uncovered = self.all_subsequences - self.covered_subsequences
            print(f"Uncovered subsequences: {len(uncovered)}")
            if len(uncovered) <= 10:  # Show uncovered if not too many
                print("Uncovered subsequences:", sorted(uncovered))
        
        print(f"\nAlgorithm Settings:")
        print("-" * 40)
        print(f"Events: {self.n_events}")
        print(f"Max test sequences: {self.max_tests}")
        print(f"Random candidates per iteration: {self.n_trials}")
        print(f"Reversal strategy enabled: {self.use_reversal}")


def main():
    """Main function to run the sequence generator."""
    parser = argparse.ArgumentParser(
        description="Generate test sequences covering all 3-element subsequences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sequence_generator.py 4      # Generate sequences for 4 events
  python sequence_generator.py 5 --no-reversal  # Disable reversal strategy
  python sequence_generator.py 6 --max-tests 5000 --trials 500  # Custom limits
        """
    )
    
    parser.add_argument("n_events", type=int, 
                       help="Number of events (must be >= 3)")
    parser.add_argument("--max-tests", type=int, default=10000,
                       help="Maximum number of test sequences (default: 10000)")
    parser.add_argument("--trials", type=int, default=1000,
                       help="Number of random candidates per iteration (default: 1000)")
    parser.add_argument("--reversal", action="store_true", default=None,
                       help="Force enable reversal strategy")
    parser.add_argument("--no-reversal", action="store_true", default=None,
                       help="Force disable reversal strategy")
    parser.add_argument("--seed", type=int, 
                       help="Random seed for reproducible results")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.n_events < 3:
        print("Error: Need at least 3 events to generate 3-element subsequences")
        return 1
    
    if args.reversal and args.no_reversal:
        print("Error: Cannot specify both --reversal and --no-reversal")
        return 1
    
    # Determine reversal setting
    use_reversal = None
    if args.reversal:
        use_reversal = True
    elif args.no_reversal:
        use_reversal = False
    
    # Set random seed for reproducibility
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    else:
        random.seed(int(time.time()))
    
    try:
        # Create and run generator
        generator = SequenceGenerator(
            n_events=args.n_events,
            max_tests=args.max_tests,
            n_trials=args.trials,
            use_reversal=use_reversal
        )
        
        start_time = time.time()
        sequences = generator.generate_sequences()
        end_time = time.time()
        
        generator.print_results()
        
        print(f"\nExecution time: {end_time - start_time:.2f} seconds")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())