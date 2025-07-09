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
python analyze_omr.py --output_dir outputs/samplecmr --console_output_file omr_output.txt
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

The analysis creates several outputs in the `outputs/Analysis/` directory:

1. Console Output
plaintext
Copy
Download
Loaded 50 questions from omr_sheet1.csv
Loaded 50 questions from omr_sheet2.csv
Loaded 50 questions from omr_sheet3.csv

Analyzing 3 OMR sheets...

Analysis complete!
Reports saved to: outputs/Analysis
2. Generated Files
text
Copy
Download
outputs/
└── Analysis/
    ├── difficulty_report.csv
    ├── individual_reports/
    │   ├── sheet_1.csv
    │   ├── sheet_2.csv
    │   └── sheet_3.csv
    └── summary.txt
3. Sample Report Contents
A. difficulty_report.csv
Question	Difficulty	Accuracy (%)	Attempts	Correct	Incorrect	Correct Answer	Most Common Wrong	Wrong Answer Distribution
Q12	Hard	28.6%	3	1	2	C	B	B(2)
Q05	Medium	58.3%	3	2	1	A	C	C(1)
Q01	Easy	100%	3	3	0	D	None	None
Key Features:

Sorted by difficulty (hardest first)

Shows wrong answer patterns

Includes attempt statistics across all sheets

B. individual_reports/sheet_1.csv
Question	Marked	Correct	Verdict
Q01	D	D	Correct
Q05	A	A	Correct
Q12	B	C	Incorrect
Note: Generated for each OMR sheet separately

C. summary.txt
plaintext
Copy
Download
OMR Analysis Summary
===================

Difficulty Distribution:
Easy: 38 questions
Medium: 9 questions
Hard: 3 questions

Top 5 Most Difficult Questions:
Q12: 28.6% correct (Common wrong: B)
Q17: 33.3% correct (Common wrong: A)
Q23: 42.9% correct (Common wrong: D)
4. Key Metrics Provided
Question-Level Analysis:

Difficulty classification (Easy/Medium/Hard)

Accuracy percentage across all students

Most frequently selected wrong answer

Aggregate Statistics:

Total sheets processed

Questions sorted by difficulty

Wrong answer distribution patterns

Per-Sheet Verification:

Individual OMR sheet results

Marked vs correct answers

Question-by-question verdicts

5. Special Cases Handled
Perfect Scores:

Shows "None" for wrong answers if all attempts were correct

Unattempted Questions:

Excluded from reports (only shows attempted questions)

Tie Situations:

When multiple wrong answers are equally common, selects alphabetically first

6. Example Scenario
For 3 students answering 50 questions each:

Q12 was missed by 2/3 students (66% incorrect)

Q01 was answered correctly by all students

Q05 showed a strong bias toward option C when incorrect

The reports help identify:

Which questions need review (Hard ones)

Common misconceptions (frequent wrong answers)

Overall class performance trends

## Advanced Features

### Batch Processing
Process multiple OMR result sets:
```bash
for dir in outputs/*/; do
    python analyze_omr.py --output_dir "$dir"
done
```

### Custom Analysis Scripts
Use the analysis engine in your own scripts:
```python
from src.analysis import OMRAnalyzer

analyzer = OMRAnalyzer("output_directory")
results = [...]  # Your results data
analyzer.analyze_results(results)
```

## Contributing

To extend the analysis system:
1. Add new analysis methods to `OMRAnalyzer` class
2. Enhance question type detection algorithms
3. Add new visualization types
4. Improve result parsing for different OMR formats

## Support

For issues or questions:
1. Check that all files are in correct locations
2. Verify required packages are installed
3. Ensure your OMR output format matches expected structure