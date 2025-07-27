# analyze_omr.py (full updated code)

import csv
import statistics
import argparse
import re
import json
from pathlib import Path
from typing import List, Dict, Any

# Difficulty level thresholds
DIFFICULTY_THRESHOLDS = {
    'Easy': 0.7,
    'Medium': 0.4,
    'Hard': 0.0
}

def analyze_batch_results(all_results: List[Dict[str, Any]], output_dir: str):
    if not all_results:
        print("No results to analyze")
        return

    total_sheets = len(all_results)
    analysis_dir = Path(output_dir)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    question_stats = aggregate_question_stats(all_results, total_sheets)
    student_results = extract_student_results(all_results)
    
    generate_text_report(question_stats, analysis_dir, total_sheets)
    generate_csv_report(question_stats, analysis_dir)
    generate_summary_report(question_stats, analysis_dir)
    generate_student_report(student_results, analysis_dir)
    print("\nBatch analysis complete!")
    print(f"Reports saved to: {analysis_dir}")

def extract_student_results(all_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    student_results = []
    for result in all_results:
        usn = result.get('usn', 'Unknown')
        total_score = 0
        total_questions = 0
        correct_answers = 0
        
        # Extract from detailed results
        for q in result['results']:
            total_questions += 1
            if q.get('is_correct', False):
                correct_answers += 1
                total_score += q.get('score', 1)  # Use actual score if available
        
        # Calculate pass/fail (50% threshold)
        pass_fail = "Pass" if (total_score / total_questions) >= 0.5 else "Fail"
        
        student_results.append({
            'usn': usn,
            'score': total_score,
            'pass_fail': pass_fail,
            'total_questions': total_questions,
            'correct_answers': correct_answers
        })
    
    return student_results

def aggregate_question_stats(all_results: List[Dict[str, Any]], total_sheets: int) -> Dict[str, Dict[str, Any]]:
    question_stats = {}
    for result in all_results:
        for q in result['results']:
            qid = q.get('question', '')
            if not qid:
                continue
                
            if qid not in question_stats:
                question_stats[qid] = {
                    'total_attempts': 0,
                    'correct_attempts': 0,
                    'marked_answers': {},
                    'correct_answer': q.get('correct_answer', ''),
                }
            stats = question_stats[qid]
            stats['total_attempts'] += 1
            marked = q.get('marked_answer', '')
            if marked:
                stats['marked_answers'][marked] = stats['marked_answers'].get(marked, 0) + 1
            if q.get('is_correct', False):
                stats['correct_attempts'] += 1

    for qid, stats in question_stats.items():
        stats['participation_rate'] = stats['total_attempts'] / total_sheets
        stats['correctness_rate'] = stats['correct_attempts'] / stats['total_attempts'] if stats['total_attempts'] > 0 else 0
        stats['difficulty'] = calculate_difficulty(stats['correctness_rate'])
        stats['answer_distribution'] = normalize_distribution(stats['marked_answers'])
    return question_stats

def calculate_difficulty(correctness_rate: float) -> str:
    if correctness_rate >= DIFFICULTY_THRESHOLDS['Easy']:
        return 'Easy'
    elif correctness_rate >= DIFFICULTY_THRESHOLDS['Medium']:
        return 'Medium'
    else:
        return 'Hard'

def normalize_distribution(dist: Dict[str, int]) -> Dict[str, float]:
    total = sum(dist.values()) or 1
    return {k: v / total for k, v in dist.items()}

def generate_text_report(question_stats: Dict[str, Dict[str, Any]], output_dir: Path, total_sheets: int):
    report_path = output_dir / "detailed_analysis.txt"
    with report_path.open('w') as f:
        f.write("OMR BATCH ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Questions Analyzed: {len(question_stats)}\n")
        f.write(f"Total OMR Sheets Processed: {total_sheets}\n\n")
        f.write("QUESTION STATISTICS:\n")
        f.write("=" * 50 + "\n")
        for qid, stats in sorted(question_stats.items(), key=lambda x: natural_sort_key(x[0])):
            f.write(f"\nQuestion {qid}:\n")
            f.write(f"- Correct Answer: {stats['correct_answer']}\n")
            f.write(f"- Participation: {stats['participation_rate']:.1%} of sheets\n")
            f.write(f"- Correctness Rate: {stats['correctness_rate']:.1%}\n")
            f.write(f"- Difficulty: {stats['difficulty']}\n")
            f.write("- Answer Distribution:\n")
            for opt, perc in stats['answer_distribution'].items():
                f.write(f"  {opt}: {perc:.1%}\n")
    print(f"Generated text report: {report_path}")

def generate_csv_report(question_stats: Dict[str, Dict[str, Any]], output_dir: Path):
    report_path = output_dir / "statistical_summary.csv"
    fieldnames = ['question', 'correct_answer', 'participation_rate', 'correctness_rate', 'difficulty']
    with report_path.open('w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for qid, stats in sorted(question_stats.items(), key=lambda x: natural_sort_key(x[0])):
            writer.writerow({
                'question': qid,
                'correct_answer': stats['correct_answer'],
                'participation_rate': stats['participation_rate'],
                'correctness_rate': stats['correctness_rate'],
                'difficulty': stats['difficulty'],
            })
    print(f"Generated CSV report: {report_path}")

def generate_summary_report(question_stats: Dict[str, Dict[str, Any]], output_dir: Path):
    report_path = output_dir / "summary_statistics.txt"
    total_questions = len(question_stats)
    participation_rates = [s['participation_rate'] for s in question_stats.values()]
    correctness_rates = [s['correctness_rate'] for s in question_stats.values()]
    difficulties = [s['difficulty'] for s in question_stats.values()]
    with report_path.open('w') as f:
        f.write("SUMMARY STATISTICS\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Questions: {total_questions}\n")
        f.write(f"Average Participation Rate: {statistics.mean(participation_rates):.1%}\n")
        f.write(f"Average Correctness Rate: {statistics.mean(correctness_rates):.1%}\n\n")
        for level in ['Easy', 'Medium', 'Hard']:
            count = difficulties.count(level)
            f.write(f"- {level}: {count} questions ({count / total_questions:.1%})\n")
    print(f"Generated summary report: {report_path}")

def generate_student_report(student_results: List[Dict[str, Any]], output_dir: Path):
    report_path = output_dir / "student_results.csv"
    with report_path.open('w', newline='') as csvfile:
        fieldnames = ['USN', 'Score', 'Total Questions', 'Correct Answers', 'Percentage', 'Pass/Fail']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for student in student_results:
            percentage = (student['score'] / student['total_questions']) * 100
            writer.writerow({
                'USN': student['usn'],
                'Score': student['score'],
                'Total Questions': student['total_questions'],
                'Correct Answers': student['correct_answers'],
                'Percentage': f"{percentage:.2f}%",
                'Pass/Fail': student['pass_fail']
            })
    print(f"Generated student report: {report_path}")
    
    # Create summary
    pass_count = sum(1 for s in student_results if s['pass_fail'] == 'Pass')
    fail_count = len(student_results) - pass_count
    pass_rate = (pass_count / len(student_results)) * 100 if student_results else 0
    
    summary_path = output_dir / "student_summary.txt"
    with summary_path.open('w') as f:
        f.write("STUDENT RESULTS SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Students: {len(student_results)}\n")
        f.write(f"Passed: {pass_count} students ({pass_rate:.2f}%)\n")
        f.write(f"Failed: {fail_count} students\n")
        f.write("\nPassing Threshold: 50% of total marks\n")
        
        # Top performers
        if student_results:
            f.write("\nTOP PERFORMERS:\n")
            top_students = sorted(student_results, key=lambda x: x['score'], reverse=True)[:5]
            for i, student in enumerate(top_students, 1):
                percentage = (student['score'] / student['total_questions']) * 100
                f.write(f"{i}. {student['usn']}: {student['score']}/{student['total_questions']} ({percentage:.2f}%)\n")
    print(f"Generated student summary: {summary_path}")

def natural_sort_key(s: str) -> List[Any]:
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def parse_arguments():
    parser = argparse.ArgumentParser(description="OMR Batch Analysis Tool")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for reports")
    return parser.parse_args()

def analyze_from_raw_json(output_dir: str):
    raw_results_path = Path("outputs/raw_results.json")
    if not raw_results_path.exists():
        print(f"❌ Raw results not found at {raw_results_path}")
        return
    
    try:
        with raw_results_path.open() as f:
            all_results = json.load(f)
    except Exception as e:
        print(f"❌ Error loading raw results: {e}")
        return
    
    if not all_results:
        print("❌ No results in raw_results.json")
        return
    
    # Convert to analysis format
    processed_results = []
    for result in all_results:
        processed = {
            'usn': result.get('usn', 'Unknown'),
            'results': []
        }
        
        # Extract detailed results
        for q_result in result.get('results', []):
            responses = q_result.get('responses', {})
            for qid, marked in responses.items():
                # Skip non-question fields
                if not qid.startswith('q'):
                    continue
                
                # Get correct answer from evaluation (if available)
                correct = q_result.get('evaluation', {}).get(qid, {}).get('correct', '')
                is_correct = marked == correct
                
                processed['results'].append({
                    'question': qid,
                    'marked_answer': marked,
                    'correct_answer': correct,
                    'is_correct': is_correct,
                    'score': 1 if is_correct else 0  # Assuming 1 point per question
                })
        
        processed_results.append(processed)
    
    analyze_batch_results(processed_results, output_dir)

def main():
    args = parse_arguments()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    print("Starting OMR Analysis...")
    print(f"Output directory: {args.output_dir}")
    print("\nAnalyzing from raw_results.json")
    analyze_from_raw_json(args.output_dir)
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()