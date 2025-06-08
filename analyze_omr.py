#!/usr/bin/env python3
"""
Standalone OMR Analysis Script

This script can analyze your OMR results independently.
Run this after your OMR evaluation is complete.

Usage:
    python analyze_omr.py --output_dir outputs/samplecmr
    python analyze_omr.py --console_output_file omr_output.txt
    python analyze_omr.py --sample  # For testing with sample data
"""

import argparse
import sys
import os
import csv
import re
from pathlib import Path
from typing import List, Dict, Any

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
    
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Run analysis on sample data for demonstration'
    )
    
    return parser.parse_args()

def extract_results_from_console_output(console_output: str) -> List[Dict[str, Any]]:
    """Extract results from console output text"""
    results = []
    
    # Look for the evaluation table in the console output
    lines = console_output.split('\n')
    in_table = False
    
    for line in lines:
        # Skip header and separator lines
        if '┏━━━' in line or '┡━━━' in line or '├──────' in line or '└──────' in line:
            continue
        if 'Question' in line and 'Marked' in line and 'Answer(s)' in line:
            in_table = True
            continue
        
        if in_table and '│' in line:
            # Parse table row
            parts = [part.strip() for part in line.split('│') if part.strip()]
            if len(parts) >= 6:
                try:
                    question = parts[0]
                    marked_answer = parts[1]
                    correct_answer = parts[2]
                    verdict = parts[3]
                    delta = float(parts[4])
                    cumulative_score = float(parts[5])
                    
                    result = {
                        'question': question,
                        'marked_answer': marked_answer,
                        'correct_answer': correct_answer,
                        'verdict': verdict,
                        'delta': delta,
                        'cumulative_score': cumulative_score,
                        'is_correct': verdict == 'Correct'
                    }
                    results.append(result)
                except (ValueError, IndexError) as e:
                    print(f"Error parsing line: {line}")
                    continue
    
    return results

def load_csv_results(csv_file_path: str) -> List[Dict[str, Any]]:
    """Load results from CSV file"""
    results = []
    
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert CSV row to our standard format
                # Adjust these field names based on your CSV structure
                result = {
                    'question': row.get('question', ''),
                    'marked_answer': row.get('marked_answer', ''),
                    'correct_answer': row.get('correct_answer', ''),
                    'verdict': row.get('verdict', ''),
                    'delta': float(row.get('delta', 0)),
                    'cumulative_score': float(row.get('cumulative_score', 0)),
                    'is_correct': row.get('verdict', '').lower() == 'correct'
                }
                results.append(result)
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file_path}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    
    return results

def find_csv_files(output_dir: str) -> List[str]:
    """Find all CSV files in the output directory"""
    csv_files = []
    output_path = Path(output_dir)
    
    if output_path.exists():
        # Look for CSV files in Results subdirectory and main directory
        for pattern in ['**/*.csv', '*.csv']:
            csv_files.extend(list(output_path.glob(pattern)))
    
    return [str(f) for f in csv_files]

def analyze_results(results: List[Dict[str, Any]], output_dir: str):
    """Analyze the OMR results and generate reports"""
    if not results:
        print("No results to analyze")
        return
    
    # Create analysis directory
    analysis_dir = Path(output_dir) / "Analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    
    # Basic statistics
    total_questions = len(results)
    correct_answers = sum(1 for r in results if r['is_correct'])
    incorrect_answers = total_questions - correct_answers
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Final score
    final_score = results[-1]['cumulative_score'] if results else 0
    
    # Answer distribution
    answer_distribution = {}
    for result in results:
        marked = result['marked_answer']
        answer_distribution[marked] = answer_distribution.get(marked, 0) + 1
    
    # Generate analysis report
    report_path = analysis_dir / "analysis_report.txt"
    with open(report_path, 'w') as f:
        f.write("OMR ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("OVERALL STATISTICS:\n")
        f.write(f"Total Questions: {total_questions}\n")
        f.write(f"Correct Answers: {correct_answers}\n")
        f.write(f"Incorrect Answers: {incorrect_answers}\n")
        f.write(f"Accuracy: {accuracy:.2f}%\n")
        f.write(f"Final Score: {final_score}\n\n")
        
        f.write("ANSWER DISTRIBUTION:\n")
        for answer, count in sorted(answer_distribution.items()):
            percentage = (count / total_questions) * 100
            f.write(f"Option {answer}: {count} ({percentage:.1f}%)\n")
        f.write("\n")
        
        f.write("QUESTION-BY-QUESTION ANALYSIS:\n")
        f.write("-" * 50 + "\n")
        for result in results:
            status = "✓" if result['is_correct'] else "✗"
            f.write(f"{status} {result['question']}: "
                   f"Marked {result['marked_answer']}, "
                   f"Correct {result['correct_answer']}, "
                   f"Score: {result['cumulative_score']}\n")
    
    # Generate detailed CSV report
    csv_report_path = analysis_dir / "detailed_analysis.csv"
    with open(csv_report_path, 'w', newline='') as csvfile:
        fieldnames = ['question', 'marked_answer', 'correct_answer', 'verdict', 
                     'delta', 'cumulative_score', 'is_correct']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Analysis complete! Reports saved to:")
    print(f"  - {report_path}")
    print(f"  - {csv_report_path}")
    
    # Print summary to console
    print(f"\nSUMMARY:")
    print(f"Total Questions: {total_questions}")
    print(f"Correct: {correct_answers}, Incorrect: {incorrect_answers}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Final Score: {final_score}")

def analyze_from_console_output(output_file_path: str, output_dir: str):
    """Analyze results from saved console output"""
    try:
        with open(output_file_path, 'r', encoding='utf-8') as f:
            console_output = f.read()
        
        # Extract results from console output
        results = extract_results_from_console_output(console_output)
        
        if not results:
            print("No evaluation data found in console output")
            return
        
        print(f"Found {len(results)} questions in console output")
        analyze_results(results, output_dir)
        
    except FileNotFoundError:
        print(f"Console output file not found: {output_file_path}")
    except Exception as e:
        print(f"Error analyzing console output: {e}")

def analyze_from_csv_files(output_dir: str, specific_csv: str = None):
    """Analyze results from CSV files"""
    if specific_csv:
        if os.path.exists(specific_csv):
            results = load_csv_results(specific_csv)
        else:
            print(f"CSV file not found: {specific_csv}")
            return
    else:
        # Find all CSV files
        csv_files = find_csv_files(output_dir)
        if not csv_files:
            print(f"No CSV files found in {output_dir}")
            print("Available files and directories:")
            output_path = Path(output_dir)
            if output_path.exists():
                for item in output_path.rglob('*'):
                    if item.is_file():
                        print(f"  - {item}")
            return
        
        print(f"Found CSV files: {csv_files}")
        results = []
        for csv_file in csv_files:
            file_results = load_csv_results(csv_file)
            results.extend(file_results)
    
    if not results:
        print("No results found to analyze")
        return
    
    analyze_results(results, output_dir)

def analyze_sample_data():
    """Analyze the sample data for demonstration"""
    # Sample data from your console output
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
        {'question': 'q16', 'marked_answer': 'B', 'correct_answer': 'C', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 6.25, 'is_correct': False},
        {'question': 'q17', 'marked_answer': 'C', 'correct_answer': 'D', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 6.5, 'is_correct': False},
        {'question': 'q18', 'marked_answer': 'B', 'correct_answer': 'A', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 6.75, 'is_correct': False},
        {'question': 'q19', 'marked_answer': 'B', 'correct_answer': 'B', 'verdict': 'Correct', 'delta': 1.0, 'cumulative_score': 7.75, 'is_correct': True},
        {'question': 'q20', 'marked_answer': 'A', 'correct_answer': 'C', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 8.0, 'is_correct': False},
        {'question': 'q21', 'marked_answer': 'C', 'correct_answer': 'A', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 8.25, 'is_correct': False},
        {'question': 'q22', 'marked_answer': 'B', 'correct_answer': 'D', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 8.5, 'is_correct': False},
        {'question': 'q23', 'marked_answer': 'B', 'correct_answer': 'B', 'verdict': 'Correct', 'delta': 1.0, 'cumulative_score': 9.5, 'is_correct': True},
        {'question': 'q24', 'marked_answer': 'A', 'correct_answer': 'C', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 9.75, 'is_correct': False},
        {'question': 'q25', 'marked_answer': 'D', 'correct_answer': 'A', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 10.0, 'is_correct': False},
        {'question': 'q26', 'marked_answer': 'D', 'correct_answer': 'B', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 10.25, 'is_correct': False},
        {'question': 'q27', 'marked_answer': 'A', 'correct_answer': 'D', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 10.5, 'is_correct': False},
        {'question': 'q28', 'marked_answer': 'A', 'correct_answer': 'C', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 10.75, 'is_correct': False},
        {'question': 'q29', 'marked_answer': 'D', 'correct_answer': 'A', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 11.0, 'is_correct': False},
        {'question': 'q30', 'marked_answer': 'D', 'correct_answer': 'B', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 11.25, 'is_correct': False},
        {'question': 'q31', 'marked_answer': 'B', 'correct_answer': 'C', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 11.5, 'is_correct': False},
        {'question': 'q32', 'marked_answer': 'B', 'correct_answer': 'D', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 11.75, 'is_correct': False},
        {'question': 'q33', 'marked_answer': 'A', 'correct_answer': 'B', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 12.0, 'is_correct': False},
        {'question': 'q34', 'marked_answer': 'B', 'correct_answer': 'C', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 12.25, 'is_correct': False},
        {'question': 'q35', 'marked_answer': 'B', 'correct_answer': 'A', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 12.5, 'is_correct': False},
        {'question': 'q36', 'marked_answer': 'B', 'correct_answer': 'D', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 12.75, 'is_correct': False},
        {'question': 'q37', 'marked_answer': 'B', 'correct_answer': 'B', 'verdict': 'Correct', 'delta': 1.0, 'cumulative_score': 13.75, 'is_correct': True},
        {'question': 'q38', 'marked_answer': 'C', 'correct_answer': 'C', 'verdict': 'Correct', 'delta': 1.0, 'cumulative_score': 14.75, 'is_correct': True},
        {'question': 'q39', 'marked_answer': 'B', 'correct_answer': 'A', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 15.0, 'is_correct': False},
        {'question': 'q40', 'marked_answer': 'B', 'correct_answer': 'D', 'verdict': 'Incorrect', 'delta': 0.25, 'cumulative_score': 15.25, 'is_correct': False},
    ]
    
    print("Running sample analysis...")
    analyze_results(sample_results, "sample_analysis")

def main():
    args = parse_arguments()
    
    if args.sample:
        analyze_sample_data()
        return
    
    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    print("Starting OMR Analysis...")
    print(f"Output directory: {args.output_dir}")
    
    # Check what files exist in the output directory
    output_path = Path(args.output_dir)
    if output_path.exists():
        print(f"\nFiles in {args.output_dir}:")
        for item in output_path.rglob('*'):
            if item.is_file():
                print(f"  - {item}")
    
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
    print("4. Use --sample to analyze sample data")

if __name__ == "__main__":
    main()