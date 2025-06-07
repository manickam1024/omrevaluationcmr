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

### 1. Text Report (`analysis_report_YYYYMMDD_HHMMSS.txt`)
- Overall statistics
- Difficulty distribution
- Question type distribution
- Detailed question-by-question analysis

### 2. JSON Data (`analysis_data_YYYYMMDD_HHMMSS.json`)
- Machine-readable analysis results
- Can be used for further processing

### 3. Visualization Charts (`analysis_charts_YYYYMMDD_HHMMSS.png`)
- Difficulty distribution pie chart
- Question type distribution
- Accuracy by question bar chart
- Difficulty vs accuracy scatter plot

### 4. Answer Pattern Heatmap (`answer_distribution_heatmap_YYYYMMDD_HHMMSS.png`)
- Visual representation of student answer choices
- Helps identify patterns and common mistakes

## Analysis Features

### Difficulty Classification
Questions are classified into 5 difficulty levels based on student success rate:
- **Very Easy**: >80% students correct
- **Easy**: 60-80% students correct
- **Medium**: 40-60% students correct
- **Hard**: 20-40% students correct
- **Very Hard**: <20% students correct

### Question Type Classification
Basic classification includes:
- **Multiple Choice**: Standard A/B/C/D questions
- **Conceptual**: Theory and definition based
- **Computational**: Calculation based
- **Analytical**: Analysis and comparison
- **Application**: Practical application
- **Memory**: Recall and identification

## Customization

### Modifying Difficulty Thresholds
Edit the `difficulty_thresholds` in `src/analysis.py`:
```python
self.difficulty_thresholds = {
    'Very Easy': 0.8,    # Change these values
    'Easy': 0.6,
    'Medium': 0.4,
    'Hard': 0.2,
    'Very Hard': 0.0
}
```

### Adding Question Type Patterns
Enhance question type detection in `src/analysis.py`:
```python
self.question_patterns = {
    'Your_Type': ['keyword1', 'keyword2'],
    # Add more patterns
}
```

## Integration with Existing Code

### Minimal Integration
If you prefer minimal changes to your existing code, just use the standalone analyzer:

1. Run your existing OMR system
2. Save console output to file
3. Run `python analyze_omr.py --console_output_file your_output.txt`

### Full Integration
For full integration, modify your `src/entry.py` to return results data that can be analyzed.

## Troubleshooting

### Common Issues

1. **No data found**: Ensure your CSV files or console output contain the evaluation table
2. **Import errors**: Make sure all required packages are installed
3. **File not found**: Check that output directories and files exist

### Debug Mode
Run with debug information:
```bash
python analyze_omr.py --output_dir outputs/samplecmr --verbose
```

## Sample Output

```
OMR ANALYSIS REPORT
==================================================

OVERALL STATISTICS
--------------------
Total Questions: 40
Overall Accuracy: 38.13%

DIFFICULTY DISTRIBUTION
-------------------------
Very Hard: 32 questions (80.0%)
Hard: 5 questions (12.5%)
Medium: 3 questions (7.5%)

QUESTION TYPE DISTRIBUTION
------------------------------
Multiple Choice: 40 questions (100.0%)

DETAILED QUESTION ANALYSIS
------------------------------

Q1:
  Correct Percentage: 0.0%
  Difficulty Level: Very Hard
  Question Type: Multiple Choice
  Correct Answer: B
  Answer Distribution: {'A': 1}
```

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