import csv
import statistics
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any

# Difficulty level thresholds
DIFFICULTY_THRESHOLDS = {
    'Easy': 0.7,
    'Medium': 0.4,
    'Hard': 0.0
}

def load_answer_key_from_csv(answer_key_path: Path) -> Dict[str, str]:
    answer_key = {}
    with answer_key_path.open('r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            qid = row['question'].strip().lower()
            correct = row['correct_answer'].strip().upper()
            answer_key[qid] = correct
    return answer_key

def convert_student_csv_to_analysis_format(input_csv: Path, output_csv: Path, answer_key: Dict[str, str]):
    with input_csv.open('r') as infile, output_csv.open('w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=['question', 'correct_answer', 'marked_answer', 'is_correct', 'delta'])
        writer.writeheader()
        for row in reader:
            for i in range(1, 41):
                qid = f'q{i}'
                marked = row[qid].strip().upper()
                correct = answer_key.get(qid, '')
                is_correct = marked == correct
                writer.writerow({
                    'question': qid,
                    'correct_answer': correct,
                    'marked_answer': marked,
                    'is_correct': str(is_correct).lower(),
                    'delta': 0.0
                })

def analyze_batch_results(all_results: List[Dict[str, Any]], output_dir: str):
    if not all_results:
        print("No results to analyze")
        return

    total_sheets = len(all_results)
    analysis_dir = Path(output_dir)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    question_stats = aggregate_question_stats(all_results, total_sheets)
    generate_text_report(question_stats, analysis_dir, total_sheets)
    generate_csv_report(question_stats, analysis_dir)
    generate_summary_report(question_stats, analysis_dir)
    print("\nBatch analysis complete!")
    print(f"Reports saved to: {analysis_dir}")

def aggregate_question_stats(all_results: List[Dict[str, Any]], total_sheets: int) -> Dict[str, Dict[str, Any]]:
    question_stats = {}
    for result in all_results:
        for q in result['results']:
            qid = q['question']
            if qid not in question_stats:
                question_stats[qid] = {
                    'total_attempts': 0,
                    'correct_attempts': 0,
                    'marked_answers': {},
                    'correct_answer': q['correct_answer'],
                    'deltas': []
                }
            stats = question_stats[qid]
            stats['total_attempts'] += 1
            marked = q['marked_answer']
            if marked:
                stats['marked_answers'][marked] = stats['marked_answers'].get(marked, 0) + 1
            if q['is_correct']:
                stats['correct_attempts'] += 1
            stats['deltas'].append(q['delta'])

    for qid, stats in question_stats.items():
        stats['participation_rate'] = stats['total_attempts'] / total_sheets
        stats['correctness_rate'] = stats['correct_attempts'] / stats['total_attempts']
        stats['difficulty'] = calculate_difficulty(stats['correctness_rate'])
        stats['answer_distribution'] = normalize_distribution(stats['marked_answers'])
        stats['delta_avg'] = statistics.mean(stats['deltas']) if stats['deltas'] else 0
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
            f.write(f"- Average Delta: {stats['delta_avg']:.2f}\n")
            f.write("- Answer Distribution:\n")
            for opt, perc in stats['answer_distribution'].items():
                f.write(f"  {opt}: {perc:.1%}\n")
    print(f"Generated text report: {report_path}")

def generate_csv_report(question_stats: Dict[str, Dict[str, Any]], output_dir: Path):
    report_path = output_dir / "statistical_summary.csv"
    fieldnames = ['question', 'correct_answer', 'participation_rate', 'correctness_rate', 'difficulty', 'delta_avg']
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
                'delta_avg': stats['delta_avg']
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

def natural_sort_key(s: str) -> List[Any]:
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def parse_arguments():
    parser = argparse.ArgumentParser(description="OMR Batch Analysis Tool")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for reports")
    return parser.parse_args()

def analyze_from_student_csv(output_dir: str):
    results_dir = Path("outputs/samplecmr/Results")
    answer_key_path = Path("outputs/samplecmr/answer_key.csv")

    if not answer_key_path.exists():
        print(f"❌ Answer key not found at {answer_key_path}")
        return

    csv_files = list(results_dir.glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files found in outputs/samplecmr/Results/")
        return

    latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
    print(f"📄 Automatically picked latest CSV: {latest_file.name}")

    converted_csv = results_dir / "converted_results.csv"
    answer_key = load_answer_key_from_csv(answer_key_path)
    convert_student_csv_to_analysis_format(latest_file, converted_csv, answer_key)

    results = []
    with converted_csv.open('r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                'question': row['question'],
                'correct_answer': row['correct_answer'],
                'marked_answer': row['marked_answer'],
                'is_correct': row['is_correct'].lower() == 'true',
                'delta': float(row['delta'])
            })

    analyze_batch_results([{'results': results}], output_dir)

def main():
    args = parse_arguments()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    print("Starting OMR Analysis...")
    print(f"Output directory: {args.output_dir}")
    print("\nAnalyzing latest file in: outputs/samplecmr/Results/")
    analyze_from_student_csv(args.output_dir)
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
