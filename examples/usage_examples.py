#!/usr/bin/env python3
"""
Usage Examples and Demonstration Script
for Combinatorial Testing Tools

This script demonstrates how to use the aligned newseq3.py and newseq4.py
generators and provides practical examples of their application.
"""

import os
import sys
import subprocess
import time
from typing import List, Dict, Tuple


class SequenceDemo:
    """Demonstration class for sequence covering array generators"""
    
    def __init__(self):
        self.examples = []
    
    def run_example(self, title: str, description: str, n_events: int, 
                   strength: int = 3, show_sequences: bool = True):
        """Run a single demonstration example"""
        print("\n" + "="*60)
        print(f"EXAMPLE: {title}")
        print("="*60)
        print(f"Description: {description}")
        print(f"Events: {n_events}, Strength: {strength}-way")
        print("-"*40)
        
        # Select appropriate script
        script = f"newseq{strength}.py"
        
        if not os.path.exists(script):
            print(f"ERROR: {script} not found!")
            return
        
        # Run the generator
        start_time = time.time()
        try:
            result = subprocess.run(
                [sys.executable, script, str(n_events)],
                capture_output=True,
                text=True,
                timeout=60
            )
            end_time = time.time()
            
            if result.returncode != 0:
                print(f"ERROR: {result.stderr}")
                return
            
            # Parse and display results
            lines = result.stdout.strip().split('\n')
            sequences = []
            
            in_tests_section = False
            for line in lines:
                line = line.strip()
                if line.startswith("====") and "TESTS" in line:
                    in_tests_section = True
                    print(line)
                    continue
                elif line.startswith("Tests:"):
                    in_tests_section = False
                    print(line)
                    print(f"Generation Time: {end_time - start_time:.2f} seconds")
                    continue
                elif in_tests_section and line and not line.startswith("---"):
                    sequences.append(line)
                    if show_sequences:
                        print(line)
                elif not in_tests_section:
                    print(line)
            
            # Store example results
            self.examples.append({
                'title': title,
                'n_events': n_events,
                'strength': strength,
                'n_sequences': len(sequences),
                'generation_time': end_time - start_time
            })
            
        except subprocess.TimeoutExpired:
            print("ERROR: Generation timed out (>60 seconds)")
        except Exception as e:
            print(f"ERROR: {e}")
    
    def demo_basic_usage(self):
        """Demonstrate basic usage of both generators"""
        print("\n" + "#"*80)
        print("BASIC USAGE DEMONSTRATIONS")
        print("#"*80)
        
        self.run_example(
            "Small GUI Event Testing",
            "Testing 5 GUI events: Click, Double-click, Right-click, Hover, Key-press",
            n_events=5,
            strength=3
        )
        
        self.run_example(
            "Protocol State Testing", 
            "Testing 6 protocol states: Init, Connect, Auth, Send, Receive, Close",
            n_events=6,
            strength=3
        )
        
        self.run_example(
            "Hardware Control Testing",
            "Testing 4 hardware controls: Power, Reset, Configure, Monitor",
            n_events=4,
            strength=4
        )
    
    def demo_comparison(self):
        """Demonstrate comparison between 3-way and 4-way testing"""
        print("\n" + "#"*80)
        print("3-WAY vs 4-WAY COMPARISON")
        print("#"*80)
        
        n_events = 6
        
        print(f"\nComparing 3-way vs 4-way testing for {n_events} events:")
        print("(Sequences hidden for brevity)")
        
        self.run_example(
            "6 Events - 3-Way Coverage",
            f"3-way testing covers {n_events}×{n_events-1}×{n_events-2} = {n_events*(n_events-1)*(n_events-2)} sequences",
            n_events=n_events,
            strength=3,
            show_sequences=False
        )
        
        self.run_example(
            "6 Events - 4-Way Coverage", 
            f"4-way testing covers {n_events}×{n_events-1}×{n_events-2}×{n_events-3} = {n_events*(n_events-1)*(n_events-2)*(n_events-3)} sequences",
            n_events=n_events,
            strength=4,
            show_sequences=False
        )
    
    def demo_scalability(self):
        """Demonstrate scalability characteristics"""
        print("\n" + "#"*80)
        print("SCALABILITY DEMONSTRATION")
        print("#"*80)
        
        test_sizes = [5, 6, 7, 8]
        
        print("Testing scalability with increasing event counts:")
        print("(Sequences hidden for performance)")
        
        for size in test_sizes:
            self.run_example(
                f"Scalability Test - {size} Events",
                f"Performance test with {size} events using 3-way coverage",
                n_events=size,
                strength=3,
                show_sequences=False
            )
    
    def demo_practical_applications(self):
        """Demonstrate practical testing applications"""
        print("\n" + "#"*80)
        print("PRACTICAL APPLICATION EXAMPLES")
        print("#"*80)
        
        # Web application testing
        print("\n" + "-"*50)
        print("WEB APPLICATION TESTING SCENARIO")
        print("-"*50)
        print("Events: Login, Navigate, Search, Filter, Sort, Logout")
        print("Goal: Test all 3-way combinations of user actions")
        
        self.run_example(
            "Web App User Flow Testing",
            "Testing user interaction sequences in a web application",
            n_events=6,
            strength=3,
            show_sequences=True
        )
        
        # API testing
        print("\n" + "-"*50)
        print("API TESTING SCENARIO")  
        print("-"*50)
        print("Events: GET, POST, PUT, DELETE, PATCH")
        print("Goal: Test all 4-way combinations of API operations")
        
        self.run_example(
            "REST API Operation Testing",
            "Testing sequences of REST API operations",
            n_events=5,
            strength=4,
            show_sequences=True
        )
    
    def generate_summary_report(self):
        """Generate a summary report of all examples"""
        print("\n" + "#"*80)
        print("DEMONSTRATION SUMMARY REPORT")
        print("#"*80)
        
        if not self.examples:
            print("No examples were run successfully.")
            return
        
        print(f"{'Example':<30} {'Events':<8} {'Strength':<8} {'Tests':<8} {'Time(s)':<8}")
        print("-" * 70)
        
        total_time = 0
        for example in self.examples:
            print(f"{example['title'][:29]:<30} "
                  f"{example['n_events']:<8} "
                  f"{example['strength']:<8} "
                  f"{example['n_sequences']:<8} "
                  f"{example['generation_time']:<8.2f}")
            total_time += example['generation_time']
        
        print("-" * 70)
        print(f"{'TOTAL':<54} {total_time:<8.2f}")
        
        # Performance insights
        print("\nPERFORMANCE INSIGHTS:")
        print(f"• Total examples run: {len(self.examples)}")
        print(f"• Total generation time: {total_time:.2f} seconds")
        print(f"• Average time per example: {total_time/len(self.examples):.2f} seconds")
        
        # Find performance patterns
        three_way_times = [e['generation_time'] for e in self.examples if e['strength'] == 3]
        four_way_times = [e['generation_time'] for e in self.examples if e['strength'] == 4]
        
        if three_way_times:
            print(f"• 3-way average time: {sum(three_way_times)/len(three_way_times):.2f} seconds")
        if four_way_times:
            print(f"• 4-way average time: {sum(four_way_times)/len(four_way_times):.2f} seconds")
        
        if three_way_times and four_way_times:
            ratio = (sum(four_way_times)/len(four_way_times)) / (sum(three_way_times)/len(three_way_times))
            print(f"• 4-way is ~{ratio:.1f}x slower than 3-way on average")


def print_usage():
    """Print usage instructions"""
    print("Combinatorial Testing Tools - Usage Examples")
    print("=" * 50)
    print()
    print("This script demonstrates the aligned newseq3.py and newseq4.py tools.")
    print()
    print("Usage:")
    print("  python usage_examples.py [demo_type]")
    print()
    print("Demo types:")
    print("  basic      - Basic usage demonstrations (default)")
    print("  comparison - 3-way vs 4-way comparison") 
    print("  scale      - Scalability testing")
    print("  apps       - Practical application examples")
    print("  all        - Run all demonstrations")
    print()
    print("Examples:")
    print("  python usage_examples.py")
    print("  python usage_examples.py basic")
    print("  python usage_examples.py all")


def main():
    """Main demonstration runner"""
    
    # Check if required files exist
    if not os.path.exists("newseq3.py"):
        print("ERROR: newseq3.py not found in current directory")
        print("Please ensure the sequence generator files are present.")
        sys.exit(1)
    
    if not os.path.exists("newseq4.py"):
        print("ERROR: newseq4.py not found in current directory")
        print("Please ensure the sequence generator files are present.")
        sys.exit(1)
    
    # Parse command line arguments
    demo_type = "basic"
    if len(sys.argv) > 1:
        demo_type = sys.argv[1].lower()
    
    if demo_type in ["help", "-h", "--help"]:
        print_usage()
        return
    
    # Create demo instance
    demo = SequenceDemo()
    
    print("COMBINATORIAL TESTING TOOLS - DEMONSTRATION")
    print("=" * 60)
    print("This demonstration shows the aligned newseq3.py and newseq4.py tools")
    print("generating sequence covering arrays for various testing scenarios.")
    
    # Run requested demonstrations
    if demo_type == "basic":
        demo.demo_basic_usage()
    elif demo_type == "comparison":
        demo.demo_comparison()
    elif demo_type == "scale":
        demo.demo_scalability()
    elif demo_type == "apps":
        demo.demo_practical_applications()
    elif demo_type == "all":
        demo.demo_basic_usage()
        demo.demo_comparison()
        demo.demo_scalability() 
        demo.demo_practical_applications()
    else:
        print(f"Unknown demo type: {demo_type}")
        print_usage()
        return
    
    # Generate summary
    demo.generate_summary_report()
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("For more information, see README.md or run the test suite:")
    print("  python test_alignment.py")


if __name__ == "__main__":
    main()