#!/usr/bin/env python3
"""
3-Way Sequence Covering Array Generator
Aligned with NIST newseq3.c implementation

Usage: python newseq3.py <number_of_events>
"""

import sys
import random
import time


class NewSeq3Generator:
    """3-way sequence covering array generator"""
    
    def __init__(self, n_events, max_tests=10000, n_trials=100, reversal=False):
        self.N = n_events  # Match NIST variable naming
        self.NSEQ = n_events * (n_events - 1) * (n_events - 2)
        self.MAXT = max_tests
        self.NTRIALS = n_trials
        self.reversal = reversal
        
        # Initialize data structures - match NIST structure
        self.chk = self._initialize_check_matrix()
        self.test = []
        self.tmptest = []
        
        # Statistics
        self.nt = 0  # number of tests
        self.all_covered = False
        
        # Random seed
        random.seed(int(time.time()))
    
    def _initialize_check_matrix(self):
        """Initialize 3D check matrix like NIST chk[N][N][N]"""
        chk = {}
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    if i != j and i != k and j != k:
                        chk[(i, j, k)] = 0
        return chk
    
    def used(self, test_idx, digit, length):
        """Check if digit is already used in test up to given length"""
        if test_idx >= len(self.test):
            return False
        for i in range(length):
            if i < len(self.test[test_idx]) and self.test[test_idx][i] == digit:
                return True
        return False
    
    def tmpused(self, test_idx, digit, length):
        """Check if digit is already used in tmptest up to given length"""
        if test_idx >= len(self.tmptest):
            return False
        for i in range(length):
            if i < len(self.tmptest[test_idx]) and self.tmptest[test_idx][i] == digit:
                return True
        return False
    
    def analyze(self, tst, length=0):
        """Analyze tests and mark covered sequences"""
        ncov = 0
        
        # Analyze complete tests
        for m in range(tst):
            if m < len(self.test):
                for i in range(self.N - 2):
                    for j in range(i + 1, self.N - 1):
                        for k in range(j + 1, self.N):
                            if (i < len(self.test[m]) and 
                                j < len(self.test[m]) and 
                                k < len(self.test[m])):
                                seq = (self.test[m][i], self.test[m][j], self.test[m][k])
                                if seq in self.chk and self.chk[seq] == 0:
                                    ncov += 1
                                    self.chk[seq] = 1
        
        # Analyze partial test if specified
        if length > 0 and tst < len(self.test) and length >= 3:
            m = tst
            for i in range(length - 2):
                for j in range(i + 1, length - 1):
                    for k in range(j + 1, length):
                        if (i < len(self.test[m]) and 
                            j < len(self.test[m]) and 
                            k < len(self.test[m])):
                            seq = (self.test[m][i], self.test[m][j], self.test[m][k])
                            if seq in self.chk:
                                self.chk[seq] = 1
        
        print(f"new cov {ncov}")
    
    def allcovered(self):
        """Check if all sequences are covered"""
        cnt = 0
        for key, value in self.chk.items():
            if value == 1:
                cnt += 1
        
        remaining = self.NSEQ - cnt
        expected = remaining / 6.0
        print(f"--- covered {cnt}. -- remain {remaining}. -- expect {expected:.1f}")
        
        return cnt >= self.NSEQ
    
    def generate_candidate(self):
        """Generate a random candidate test sequence"""
        candidate = [0] * self.N
        candidate[0] = random.randint(0, self.N - 1)
        
        for j in range(1, self.N):
            n = random.randint(0, self.N - 1)
            while self.tmpused(len(self.tmptest) - 1, n, j):
                n = random.randint(0, self.N - 1)
            candidate[j] = n
        
        return candidate
    
    def count_new_coverage(self, candidate):
        """Count how many new 3-sequences this candidate would cover"""
        cnt = 0
        for i in range(self.N - 2):
            for j in range(i + 1, self.N - 1):
                for k in range(j + 1, self.N):
                    seq = (candidate[i], candidate[j], candidate[k])
                    if seq in self.chk and self.chk[seq] == 0:
                        cnt += 1
        return cnt
    
    def generate(self):
        """Main generation algorithm - matches NIST structure"""
        print(f"Generating test sequences for {self.N} events")
        
        # Initialize with first test (0,1,2,...,N-1)
        initial_test = list(range(self.N))
        self.test = [initial_test]
        self.nt = 1
        
        self.analyze(self.nt, 0)
        
        # Main generation loop
        while not self.allcovered() and self.nt < self.MAXT:
            # Generate NTRIALS candidates
            self.tmptest = []
            for i in range(self.NTRIALS):
                self.tmptest.append([0] * self.N)
                # Generate random sequence
                self.tmptest[i][0] = random.randint(0, self.N - 1)
                for j in range(1, self.N):
                    n = random.randint(0, self.N - 1)
                    while self.tmpused(i, n, j):
                        n = random.randint(0, self.N - 1)
                    self.tmptest[i][j] = n
            
            # Pick the best candidate
            bestidx = 0
            bestcov = 0
            
            for m in range(self.NTRIALS):
                cnt = 0
                for i in range(self.N - 2):
                    for j in range(i + 1, self.N - 1):
                        for k in range(j + 1, self.N):
                            seq = (self.tmptest[m][i], self.tmptest[m][j], self.tmptest[m][k])
                            if seq in self.chk and self.chk[seq] == 0:
                                cnt += 1
                
                if cnt > bestcov:
                    bestcov = cnt
                    bestidx = m
            
            # Add the best candidate
            best_test = self.tmptest[bestidx][:]
            self.test.append(best_test)
            self.nt += 1
            
            self.analyze(self.nt, 0)
            
            # Optional reversal
            if self.reversal:
                reversed_test = best_test[::-1]
                self.test.append(reversed_test)
                self.nt += 1
                self.analyze(self.nt, 0)
        
        return self.test
    
    def print_results(self):
        """Print results in NIST format"""
        print(f"==== {self.nt} TESTS ====")
        
        for m in range(self.nt):
            if m < len(self.test):
                sequence_str = ",".join(str(x) for x in self.test[m])
                print(f"{sequence_str},")
        
        # Count final coverage
        cnt = sum(1 for value in self.chk.values() if value == 1)
        coverage_ratio = cnt / self.NSEQ
        
        print(f"Tests: {self.nt}. Seqs covered: {cnt}/NSEQ: {self.NSEQ} = {coverage_ratio:.6f}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: <number of events>")
        sys.exit(1)
    
    try:
        n_events = int(sys.argv[1])
        if n_events < 3:
            print("Error: Number of events must be >= 3")
            sys.exit(1)
    except ValueError:
        print("Error: Number of events must be an integer")
        sys.exit(1)
    
    # Create generator
    generator = NewSeq3Generator(n_events)
    
    # Generate sequences
    start_time = time.time()
    sequences = generator.generate()
    end_time = time.time()
    
    # Print results
    generator.print_results()
    
    # Optional: print timing
    if len(sys.argv) > 2 and sys.argv[2] == "--timing":
        print(f"Generation time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()