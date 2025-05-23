# Combinatorial Testing Tools - Python Implementation

Source files for basic sequence covering, 3-way and 4-way sequences.  These are simple little greedy algorithm programs in Python.

## Tools Overview

### newseq3.py - 3-Way Sequence Generator

Generates test sequences that cover all 3-way permutations of events. For N events, ensures coverage of N×(N-1)×(N-2) possible 3-sequences.

### newseq4.py - 4-Way Sequence Generator  

Generates test sequences that cover all 4-way permutations of events. For N events, ensures coverage of N×(N-1)×(N-2)×(N-3) possible 4-sequences.

## Key Features

- **Aligned Implementation**: Both tools use identical algorithmic structure based on the original NIST C implementation
- **Consistent Output Format**: Both tools produce CSV-formatted output with identical structure
- **Greedy Algorithm**: Uses randomized candidate generation with greedy selection for optimal coverage
- **Coverage Validation**: Built-in verification that all required t-way sequences are covered
- **Performance Monitoring**: Tracks generation time and coverage statistics

## Installation

No external dependencies required. Python 3.6+ recommended.

```bash
git clone https://github.com/richardnero/combinatorial-testing-tools
cd combinatorial-testing-tools
```

## Usage

### Basic Usage

```bash
# Generate 3-way sequences for 6 events
python newseq3.py 6

# Generate 4-way sequences for 8 events  
python newseq4.py 8
```

### Output Format

Both tools produce identical output format:

```bash
Generating test sequences for N events
new cov X
--- covered Y. -- remain Z. -- expect W.W
==== M TESTS ====
0,1,2,3,4,5,
5,4,3,2,1,0,
...
Tests: M. Seqs covered: Y/NSEQ: TOTAL = 0.XXXXXX
```

Where:

- `N` = Number of events
- `M` = Number of generated test sequences  
- `Y` = Number of covered t-way sequences
- `TOTAL` = Total number of required t-way sequences
- Each test sequence is output as comma-separated values

### Example Usage

```bash
# Test with 5 events (minimum for meaningful 3-way testing)
$ python newseq3.py 5
Generating test sequences for 5 events
new cov 60
--- covered 60. -- remain 0. -- expect 0.0
==== 8 TESTS ====
0,1,2,3,4,
4,3,2,1,0,
1,0,4,2,3,
2,4,0,3,1,
3,4,0,1,2,
2,3,1,4,0,
0,4,2,1,3,
1,3,4,0,2,
Tests: 8. Seqs covered: 60/NSEQ: 60 = 1.000000
```

## Algorithm Details

### Core Components

1. **Coverage Matrix**: Tracks which t-way sequences have been covered
2. **Candidate Generation**: Creates random test sequences using controlled randomization
3. **Greedy Selection**: Chooses candidates that maximize new coverage
4. **Coverage Analysis**: Verifies complete t-way coverage

### Key Parameters

- `MAXT = 10000`: Maximum number of test sequences to generate
- `NTRIALS = 100`: Number of candidate sequences to evaluate per iteration
- Random seed: Based on current time for reproducible randomization

### Performance Characteristics

| Events | 3-Way Tests | 4-Way Tests | 3-Way Time | 4-Way Time |
|--------|-------------|-------------|------------|------------|
| 5      | ~8          | ~29         | <1s        | <1s        |
| 6      | ~10         | ~38         | <1s        | <2s        |
| 7      | ~12         | ~50         | <1s        | <5s        |
| 8      | ~12         | ~56         | <2s        | <10s       |
| 10     | ~14         | ~72         | <5s        | <30s       |

## Testing and Validation

A comprehensive test suite is provided to verify alignment and correctness:

```bash
# Run alignment tests
python test_alignment.py

# Test specific event sizes
python test_alignment.py 5 6 7 8
```

The test suite validates:

- Output format consistency between newseq3.py and newseq4.py
- Sequence validity (no repeated elements, correct range)
- Coverage completeness (all required t-way sequences covered)
- Performance benchmarks

## Alignment Features

This implementation ensures both tools are fully aligned:

### Consistent Algorithm Structure

- Both use identical greedy candidate selection
- Same coverage analysis methods
- Unified random seed handling

### Standardized Output Format  

- CSV format with comma-separated sequences
- Identical progress reporting
- Consistent final statistics format

### Shared Core Functions

- `used()` and `tmpused()` for duplicate checking
- `analyze()` for coverage analysis  
- `allcovered()` for completion checking
- `print_results()` for output formatting

### Parameter Consistency

- Same maximum tests limit (MAXT = 10000)
- Same candidate trials per iteration (NTRIALS = 100)  
- Consistent variable naming convention

## Performance Tips

1. **Event Size Limits**:
   - 3-way: Practical up to ~30 events
   - 4-way: Practical up to ~20 events

2. **Memory Usage**:
   - 3-way: O(N³) for coverage matrix
   - 4-way: O(N⁴) for coverage matrix

3. **Time Complexity**:
   - Generation time grows exponentially with event count
   - 4-way testing requires significantly more time than 3-way

## Applications

- **GUI Testing**: Test sequences of user interface events
- **Protocol Testing**: Validate communication protocol event sequences  
- **Hardware Testing**: Test sequences of hardware state changes
- **Workflow Testing**: Validate business process event sequences
- **API Testing**: Test sequences of API calls

## Comparison with NIST Reference

This Python implementation maintains mathematical equivalence with the original NIST C implementation while providing:

- Modern Python 3 compatibility
- Enhanced error handling and validation
- Improved code readability and maintainability  
- Comprehensive test suite
- Detailed documentation

## Contributing

Contributions are welcome! Please ensure:

1. Both newseq3.py and newseq4.py remain aligned
2. All tests pass: `python test_alignment.py`
3. Code follows Python PEP 8 style guidelines
4. New features are documented

## License

This software is in the public domain as it is based on NIST tools. No license is required and there are no restrictions on distribution or use.

## Troubleshooting

### Common Issues

#### **"Error: Number of events must be >= 3"**

- newseq3.py requires at least 3 events for meaningful 3-way testing

#### **"Error: Number of events must be >= 4"**

- newseq4.py requires at least 4 events for meaningful 4-way testing

#### **Long generation times**

- 4-way testing with >15 events can take significant time
- Consider using 3-way testing for larger event sets
- Generation time grows exponentially with event count

#### **Memory issues with large event sets**

- Coverage matrix size grows as O(N^t) where t is the strength
- For very large event sets, consider distributed approaches

### Validation

To verify your installation and alignment:

```bash
# Quick validation test
python newseq3.py 5
python newseq4.py 5

# Comprehensive validation  
python test_alignment.py 5 6 7

# Check output format consistency
python newseq3.py 6 > test3.out
python newseq4.py 6 > test4.out
# Both should have identical format structure
```

## Version History

### v1.0.0 (Current)

- Initial aligned implementation
- Full compatibility with NIST reference
- Comprehensive test suite
- Complete documentation

### Planned Features

- GUI interface for easier usage
- Batch processing capabilities  
- Integration with popular testing frameworks
- Performance optimizations for large event sets
- Constraint support for restricted event sequences
