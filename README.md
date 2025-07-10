# omrevaluationcmr
# OMR Analysis System

This system provides comprehensive analysis of OMR (Optical Mark Recognition) evaluation results, including difficulty level classification and question type analysis.

## Files Structure

```
your_project/
├── main.py                    # Modified main file with analysis integration
├── analyze_omr.py            # Standalone analysis script
├── requirements.txt          # Required packages
├── src/
│   ├── analysis.py           # Main analysis engine
│   ├── result_processor.py   # Results processing utilities
│   ├── entry.py             # Your existing entry point
│   └── logger.py            # Your existing logger
└── outputs/
    └── Analysis/             # Generated analysis reports and charts
```

## Installation

1. **Install required packages:**
```bash
pip install -r requirements.txt
```

2. **Place the new files in your project:**
   - Replace your existing `main.py` with the new version
   - Add `analyze_omr.py` to your project root
   - Create `src/analysis.py` and `src/result_processor.py`

## Usage Options

### Option 1: Integrated Analysis (Recommended)
Run your OMR evaluation with analysis:
```bash
python main.py -i inputs/samplecmr -o outputs --analyze
```

### Option 2: Standalone Analysis
Analyze results after OMR evaluation:

**From console output:**
```bash
# Save your console output to a file first
python main.py -i inputs/samplecmr -o outputs > omr_output.txt

# Then analyze
python analyze_omr.py --sample
python analyze_omr.py --output_dir reports

```

**From CSV files:**
```bash
python analyze_omr.py --output_dir outputs/samplecmr
```

**Analyze specific CSV:**
```bash
python analyze_omr.py --csv_file outputs/samplecmr/Results/Results_07PM.csv
```

### Option 3: Sample Analysis (For Testing)
```bash
python analyze_omr.py --sample
```

## Generated Reports

Output Reports
After running analysis, the following files are generated in outputs/Analysis/:

File	Description
detailed_analysis.txt	Per-question statistics with difficulty, correctness, and answer distribution
statistical_summary.csv	Summary in CSV format (ideal for spreadsheets or dashboards)
summary_statistics.txt	Overall statistics, difficulty breakdown

Sample console output:

yaml
Copy
Edit
OMR BATCH ANALYSIS REPORT
=========================

Total Questions Analyzed: 40
Total OMR Sheets Processed: 6

Question q1:
- Correct Answer: A
- Participation: 100.0% of sheets
- Correctness Rate: 83.3%
- Difficulty: Easy
- Average Delta: 0.00
- Answer Distribution:
  A: 83.3%
  B: 16.7%
...
📌 Answer Key Format
The analyze_omr.py script contains a hardcoded answer key like:

python
Copy
Edit
answer_key = {
    'q1': 'B', 'q2': 'C', ..., 'q40': 'B'
}
To customize, edit the answer_key dictionary in analyze_omr.py > analyze_from_student_csv().

🧪 Testing the Analysis
Use the sample mode to verify everything works:

bash
Copy
Edit
python analyze_omr.py --sample
This mode uses built-in answer keys and picks the latest CSV file from:

bash
Copy
Edit
outputs/samplecmr/Results/
🙋 Support
For help:

Ensure your directory matches the expected structure.

Validate all Python dependencies are installed.

Ensure your result CSVs are properly formatted.

