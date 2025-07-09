#!/usr/bin/env python3
"""
Enhanced OMR Analysis Script for samplecmr folder
- Processes multiple OMR sheets
- Calculates question difficulty
- Generates comprehensive reports
"""

import csv
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any

# Difficulty thresholds
DIFFICULTY_LEVELS = {
    'Easy': 70,    # >=70% correct
    'Medium': 40,  # 40-69% correct 
    'Hard': 0      # <40% correct
}

def load_omr_data(file_path: str) -> List[Dict[str, Any]]:
    """Load OMR data from CSV file"""
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append({
                    'question': row.get('question', ''),
                    'marked_answer': row.get('marked_answer', ''),
                    'correct_answer': row.get('correct_answer', ''),
                    'is_correct': row.get('verdict', '').lower() == 'correct'
                })
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return results

def analyze_multiple_sheets(all_sheets: List[List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    """Analyze difficulty across multiple OMR sheets"""
    question_stats = defaultdict(lambda: {
        'total_attempts': 0,
        'correct_attempts': 0,
        'incorrect_attempts': 0,
        'correct_answer': None,
        'wrong_answers': defaultdict(int),
        'sheets_attempted': set()
    })

    # Process all sheets
    for sheet_idx, sheet_results in enumerate(all_sheets):
        for result in sheet_results:
            q = result['question']
            stats = question_stats[q]
            
            stats['total_attempts'] += 1
            stats['sheets_attempted'].add(sheet_idx)
            
            if result['is_correct']:
                stats['correct_attempts'] += 1
            else:
                stats['incorrect_attempts'] += 1
                marked = result['marked_answer']
                stats['wrong_answers'][marked] += 1
            
            if not stats['correct_answer']:
                stats['correct_answer'] = result['correct_answer']

    # Calculate difficulty
    for q, stats in question_stats.items():
        if stats['total_attempts'] > 0:
            stats['accuracy'] = (stats['correct_attempts'] / stats['total_attempts']) * 100
            stats['difficulty'] = get_difficulty_level(stats['accuracy'])
            
            # Find most common wrong answer
            if stats['wrong_answers']:
                stats['most_common_wrong'] = max(
                    stats['wrong_answers'].items(),
                    key=lambda x: x[1]
                )[0]
            else:
                stats['most_common_wrong'] = None
    
    return question_stats

def get_difficulty_level(accuracy: float) -> str:
    """Classify question difficulty"""
    for level, threshold in DIFFICULTY_LEVELS.items():
        if accuracy >= threshold:
            return level
    return 'Hard'

def generate_difficulty_report(stats: Dict[str, Dict[str, Any]], output_dir: str):
    """Generate CSV report of question difficulties"""
    report_path = Path(output_dir) / "Analysis" / "difficulty_report.csv"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Question', 'Difficulty', 'Accuracy (%)', 
            'Attempts', 'Correct', 'Incorrect',
            'Correct Answer', 'Most Common Wrong', 
            'Wrong Answer Distribution'
        ])
        
        for q, data in sorted(stats.items(), key=lambda x: x[1]['accuracy']):
            wrong_dist = ', '.join(
                f"{ans}({count})" for ans, count in data['wrong_answers'].items()
            ) if data['wrong_answers'] else 'None'
            
            writer.writerow([
                q,
                data['difficulty'],
                f"{data['accuracy']:.1f}",
                data['total_attempts'],
                data['correct_attempts'],
                data['incorrect_attempts'],
                data['correct_answer'],
                data['most_common_wrong'] or 'None',
                wrong_dist
            ])

def generate_individual_reports(all_sheets: List[List[Dict[str, Any]]], output_dir: str):
    """Generate reports for each OMR sheet"""
    report_dir = Path(output_dir) / "Analysis" / "individual_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    for i, sheet in enumerate(all_sheets):
        report_path = report_dir / f"sheet_{i+1}.csv"
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Question', 'Marked', 'Correct', 'Verdict'])
            
            for q in sheet:
                writer.writerow([
                    q['question'],
                    q['marked_answer'],
                    q['correct_answer'],
                    'Correct' if q['is_correct'] else 'Incorrect'
                ])

def generate_summary(stats: Dict[str, Dict[str, Any]], output_dir: str):
    """Generate summary text report"""
    summary_path = Path(output_dir) / "Analysis" / "summary.txt"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("OMR Analysis Summary\n")
        f.write("===================\n\n")
        
        # Difficulty distribution
        diff_counts = defaultdict(int)
        for q in stats.values():
            diff_counts[q['difficulty']] += 1
        
        f.write("Difficulty Distribution:\n")
        for level in ['Easy', 'Medium', 'Hard']:
            f.write(f"{level}: {diff_counts.get(level, 0)} questions\n")
        
        # Top difficult questions
        f.write("\nTop 5 Most Difficult Questions:\n")
        difficult = sorted(
            stats.items(),
            key=lambda x: x[1]['accuracy']
        )[:5]
        
        for q, data in difficult:
            f.write(f"{q}: {data['accuracy']:.1f}% correct")
            if data['most_common_wrong']:
                f.write(f" (Common wrong: {data['most_common_wrong']})")
            f.write("\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input-dir",
        default="outputs",  # Assuming CSVs are in outputs/
        help="Directory containing OMR result CSVs"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="outputs",
        help="Output directory for reports"
    )
    args = parser.parse_args()
    
    # Find all CSV files in samplecmr results
    csv_files = list(Path(args.input_dir).glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {args.input_dir}")
        return
    
    # Load all sheets
    all_sheets = []
    for csv_file in csv_files:
        sheet = load_omr_data(str(csv_file))
        if sheet:
            all_sheets.append(sheet)
            print(f"Loaded {len(sheet)} questions from {csv_file.name}")
    
    if not all_sheets:
        print("No valid OMR data found")
        return
    
    # Analyze and generate reports
    print(f"\nAnalyzing {len(all_sheets)} OMR sheets...")
    stats = analyze_multiple_sheets(all_sheets)
    
    generate_difficulty_report(stats, args.output_dir)
    generate_individual_reports(all_sheets, args.output_dir)
    generate_summary(stats, args.output_dir)
    
    print("\nAnalysis complete!")
    print(f"Reports saved to: {Path(args.output_dir)/'Analysis'}")

if __name__ == "__main__":
    main()