#!/usr/bin/env python3
"""
4-Way Sequence Covering Array Generator
Fixed version with proper candidate generation

Usage: python newseq4_fixed.py <number_of_events>
"""

import sys
import random
import time


class NewSeq4Generator:
    """4-way sequence covering array generator - NIST C equivalent with fixed candidates"""
    
    def __init__(self, n_events):
        # NIST C variable naming convention
        self.N = n_events
        self.NSEQ = n_events * (n_events - 1) * (n_events - 2) * (n_events - 3)
        self.MAXT = 10000
        self.NTRIALS = 1000  # Match NIST C exactly
        
        # Initialize data structures matching NIST C
        # chk[N][N][N][N] equivalent using dictionary
        self.chk = self._initialize_check_matrix()
        
        # test[MAXT][N] equivalent
        self.test = []
        
        # tmptest[NTRIALS][N] equivalent
        self.tmptest = []
        
        # Statistics matching NIST C
        self.nt = 0  # number of tests generated
        
        # Reversal logic matching NIST C
        self.reversal = 1 if n_events > 5 else 0
        
        # Random seed matching NIST C approach
        random.seed(int(time.time()))
    
    def _initialize_check_matrix(self):
        """Initialize 4D check matrix exactly like NIST chk[N][N][N][N]"""
        chk = {}
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    for l in range(self.N):
                        if i != j and i != k and i != l and j != k and j != l and k != l:
                            chk[(i, j, k, l)] = 0
        return chk
    
    def used(self, test_idx, digit, length):
        """Check if digit is already used in test up to given length - NIST C equivalent"""
        if test_idx >= len(self.test):
            return False
        for i in range(length):
            if i < len(self.test[test_idx]) and self.test[test_idx][i] == digit:
                return True
        return False
    
    def analyze(self, tst):
        """Analyze tests and mark covered sequences - NIST C equivalent"""
        ncov = 0
        
        # Analyze all complete tests exactly like NIST C
        for m in range(tst):
            if m < len(self.test):
                for i in range(self.N - 3):
                    for j in range(i + 1, self.N - 2):
                        for k in range(j + 1, self.N - 1):
                            for l in range(k + 1, self.N):
                                if (i < len(self.test[m]) and 
                                    j < len(self.test[m]) and 
                                    k < len(self.test[m]) and
                                    l < len(self.test[m])):
                                    seq = (self.test[m][i], self.test[m][j], self.test[m][k], self.test[m][l])
                                    if seq in self.chk and self.chk[seq] == 0:
                                        ncov += 1
                                        self.chk[seq] = 1
        
        print(f"new cov {ncov}")
        return ncov
    
    def allcovered(self):
        """Check if all sequences are covered - NIST C equivalent"""
        cnt = 0
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    for l in range(self.N):
                        if (i != j and i != k and i != l and j != k and j != l and k != l and 
                            (i, j, k, l) in self.chk and self.chk[(i, j, k, l)] == 1):
                            cnt += 1
        
        remaining = self.NSEQ - cnt
        expected = remaining / 24.0  # 4! = 24 for 4-way
        print(f"--- covered {cnt}. -- remain {remaining}. -- expect {expected:.1f}")
        
        return cnt >= self.NSEQ
    
    def generate_valid_candidate(self):
        """Generate a valid permutation candidate (fixed version)"""
        # Start with a valid permutation
        candidate = list(range(self.N))
        
        # Fisher-Yates shuffle to create random permutation
        for i in range(self.N):
            j = random.randint(i, self.N - 1)
            candidate[i], candidate[j] = candidate[j], candidate[i]
        
        return candidate
    
    def generate(self):
        """Main generation algorithm - NIST C structure with fixed candidate generation"""
        print(f"Generating test sequences for {self.N} events")
        
        # Initialize with TWO tests exactly like NIST C
        # test[0][i] = i; test[1][i] = N-1-i; nt=2;
        test0 = list(range(self.N))                    # [0,1,2,3,4]
        test1 = [self.N-1-i for i in range(self.N)]   # [4,3,2,1,0]
        self.test = [test0, test1]
        self.nt = 2
        
        # Analyze initial coverage
        self.analyze(self.nt)
        
        # Main generation loop matching NIST C: while (!allcovered() && nt < MAXT)
        while not self.allcovered() and self.nt < self.MAXT:
            
            # Generate NTRIALS candidates - FIXED to ensure valid permutations
            self.tmptest = []
            for i in range(self.NTRIALS):
                # Generate valid permutation candidate
                candidate = self.generate_valid_candidate()
                self.tmptest.append(candidate)
            
            # Find best candidate using NIST C greedy selection
            bestidx = 0
            bestcov = 0
            
            for m in range(self.NTRIALS):
                cnt = 0
                # Count new coverage exactly like NIST C
                for i in range(self.N - 3):
                    for j in range(i + 1, self.N - 2):
                        for k in range(j + 1, self.N - 1):
                            for l in range(k + 1, self.N):
                                i1 = self.tmptest[m][i]
                                j1 = self.tmptest[m][j] 
                                k1 = self.tmptest[m][k]
                                l1 = self.tmptest[m][l]
                                # Match NIST C condition exactly
                                if ((i1, j1, k1, l1) in self.chk and self.chk[(i1, j1, k1, l1)] == 0 and 
                                    i != j and i != k and i != l and j != k and j != l and k != l):
                                    cnt += 1
                
                if cnt > bestcov:
                    bestcov = cnt
                    bestidx = m
            
            # Add the best candidate
            if bestcov > 0:
                best_test = self.tmptest[bestidx][:]
                self.test.append(best_test)
                self.nt += 1
                self.analyze(self.nt)
                
                # Add reversal logic exactly like NIST C
                if self.reversal:
                    # Create reversed test: test[nt][i] = test[nt-1][N-1-i]
                    reversed_test = [best_test[self.N-1-i] for i in range(self.N)]
                    self.test.append(reversed_test)
                    self.nt += 1
                    self.analyze(self.nt)
            else:
                # No improvement possible, break like NIST C would
                break
        
        return self.test
    
    def print_results(self):
        """Print results in exact NIST C format"""
        print(f"==== {self.nt} TESTS ====")
        
        # Print to stderr like NIST C: fprintf(stderr,"%d,", test[m][j]);
        import sys
        for m in range(self.nt):
            if m < len(self.test):
                for j in range(self.N):
                    sys.stderr.write(f"{self.test[m][j]},")
                sys.stderr.write("\n")
        
        # Final statistics exactly like NIST C
        cnt = 0
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    for l in range(self.N):
                        if (i != j and i != k and i != l and j != k and j != l and k != l and 
                            (i, j, k, l) in self.chk and self.chk[(i, j, k, l)] == 1):
                            cnt += 1
        
        coverage_ratio = cnt / self.NSEQ if self.NSEQ > 0 else 0
        print(f"Tests: {self.nt}. Seqs covered: {cnt}/NSEQ: {self.NSEQ} = {coverage_ratio:.6f}")
        sys.stderr.flush()  # Ensure stderr output is flushed


def main():
    """Main entry point - NIST C equivalent"""
    if len(sys.argv) < 2:
        print("Usage: <number of events>")
        sys.exit(1)
    
    try:
        n_events = int(sys.argv[1])
        if n_events < 4:
            print("Error: Number of events must be >= 4")
            sys.exit(1)
    except ValueError:
        print("Error: Number of events must be an integer")
        sys.exit(1)
    
    # Create generator with NIST C parameters
    generator = NewSeq4Generator(n_events)
    
    # Generate sequences
    sequences = generator.generate()
    
    # Print results in NIST C format
    generator.print_results()


if __name__ == "__main__":
    main()