#!/usr/bin/env python3
"""
Standalone OMR Analysis Script

This script can analyze your OMR results independently.
Run this after your OMR evaluation is complete.

Usage:
    python analyze_omr.py --output_dir outputs/samplecmr
    python analyze_omr.py --console_output_file omr_output.txt
"""

import argparse
import sys
from pathlib import Path
from src.analysis import OMRAnalyzer, extract_results_from_output
from src.result_processor import ResultProcessor

def parse_arguments():
    parser = argparse.ArgumentParser(description='Analyze OMR results for difficulty and question types')
    
    parser.add_argument(
        '--output_dir', 
        type=str, 
        default='outputs',
        help='Directory containing OMR output files'
    )
    
    parser.add_argument(
        '--console_output_file',
        type=str,
        help='File containing console output from OMR evaluation'
    )
    
    parser.add_argument(
        '--csv_file',
        type=str,
        help='Specific CSV file to analyze'
    )
    
    return parser.parse_args()

def analyze_from_console_output(output_file_path, output_dir):
    """Analyze results from saved console output"""
    try:
        with open(output_file_path, 'r') as f:
            console_output = f.read()
        
        # Extract results from console output
        results = extract_results_from_output(console_output)
        
        if not results:
            print("No evaluation data found in console output")
            return
        
        # Run analysis
        analyzer = OMRAnalyzer(output_dir)
        analyzer.analyze_results(results)
        
        print(f"Analysis complete! Check {output_dir}/Analysis/ for results.")
        
    except FileNotFoundError:
        print(f"Console output file not found: {output_file_path}")
    except Exception as e:
        print(f"Error analyzing console output: {e}")

def analyze_from_csv_files(output_dir, specific_csv=None):
    """Analyze results from CSV files"""
    processor = ResultProcessor(output_dir)
    
    if specific_csv:
        results = processor.load_from_csv(specific_csv)
    else:
        results = processor.process_all_results()
    
    if not results:
        print("No results found to analyze")
        return
    
    # Run analysis
    analyzer = OMRAnalyzer(output_dir)
    analyzer.analyze_results(results)
    
    print(f"Analysis complete! Check {output_dir}/Analysis/ for results.")

def analyze_sample_data():
    """Analyze the sample data you provided"""
    # Sample data from your output
    sample_results = [
        {'question': 'q1', 'marked_answer': 'A', 'correct_answer': 'B', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 0.25, 'is_correct': False},
        {'question': 'q2', 'marked_answer': 'C', 'correct_answer': 'D', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 0.5, 'is_correct': False},
        {'question': 'q3', 'marked_answer': 'B', 'correct_answer': 'C', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 0.75, 'is_correct': False},
        {'question': 'q4', 'marked_answer': 'A', 'correct_answer': 'B', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 1.0, 'is_correct': False},
        {'question': 'q5', 'marked_answer': 'A', 'correct_answer': 'D', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 1.25, 'is_correct': False},
        {'question': 'q6', 'marked_answer': 'B', 'correct_answer': 'C', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 1.5, 'is_correct': False},
        {'question': 'q7', 'marked_answer': 'C', 'correct_answer': 'A', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 1.75, 'is_correct': False},
        {'question': 'q8', 'marked_answer': 'B', 'correct_answer': 'C', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 2.0, 'is_correct': False},
        {'question': 'q9', 'marked_answer': 'C', 'correct_answer': 'A', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 2.25, 'is_correct': False},
        {'question': 'q10', 'marked_answer': 'A', 'correct_answer': 'D', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 2.5, 'is_correct': False},
        {'question': 'q11', 'marked_answer': 'C', 'correct_answer': 'C', 'verdict': 'Correct', 'delta': 1.0, 'cumulative_score': 3.5, 'is_correct': True},
        {'question': 'q12', 'marked_answer': 'C', 'correct_answer': 'B', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 3.75, 'is_correct': False},
        {'question': 'q13', 'marked_answer': 'C', 'correct_answer': 'A', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 4.0, 'is_correct': False},
        {'question': 'q14', 'marked_answer': 'D', 'correct_answer': 'D', 'verdict': 'Correct', 'delta': 1.0, 'cumulative_score': 5.0, 'is_correct': True},
        {'question': 'q15', 'marked_answer': 'B', 'correct_answer': 'B', 'verdict': 'Correct', 'delta': 1.0, 'cumulative_score': 6.0, 'is_correct': True},
        # Add more sample data...
    ]
    
    analyzer = OMRAnalyzer("sample_analysis")
    analyzer.analyze_results(sample_results)
    
    print("Sample analysis complete! Check sample_analysis/Analysis/ for results.")

def main():
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    print("Starting OMR Analysis...")
    print(f"Output directory: {args.output_dir}")
    
    # Determine analysis method based on provided arguments
    if args.console_output_file:
        print(f"Analyzing from console output file: {args.console_output_file}")
        analyze_from_console_output(args.console_output_file, args.output_dir)
    
    elif args.csv_file:
        print(f"Analyzing from CSV file: {args.csv_file}")
        analyze_from_csv_files(args.output_dir, args.csv_file)
    
    else:
        print("Analyzing from all CSV files in output directory...")
        analyze_from_csv_files(args.output_dir)
        
    print("\nAnalysis methods:")
    print("1. Save your console output to a file and use --console_output_file")
    print("2. Use --csv_file to analyze a specific CSV")
    print("3. Run without arguments to analyze all CSV files in output directory")
    print("4. Run with --sample to analyze sample data")

def run_sample_analysis():
    """Run analysis on sample data for demonstration"""
    print("Running sample analysis...")
    analyze_sample_data()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        run_sample_analysis()
    else:
        main()