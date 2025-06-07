import re
import pandas as pd
from pathlib import Path
import csv
from src.logger import logger

class ResultProcessor:
    """Process OMR results and prepare them for analysis"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
    
    def extract_from_console_output(self, console_output):
        """Extract evaluation data from console output"""
        results = []
        
        # Regular expression to match table rows
        table_pattern = r'│\s*(q\d+)\s*│\s*([A-D])\s*│\s*([A-D])\s*│\s*(Correct|Incorrect)\s*│\s*([\d.]+)\s*│\s*([\d.]+)\s*│'
        
        matches = re.findall(table_pattern, console_output)
        
        for match in matches:
            question, marked, correct, verdict, delta, score = match
            results.append({
                'question': question,
                'marked_answer': marked,
                'correct_answer': correct,
                'verdict': verdict,
                'delta': float(delta),
                'cumulative_score': float(score),
                'is_correct': verdict == 'Correct'
            })
        
        return results
    
    def load_from_csv(self, csv_file_path):
        """Load results from CSV file in outputs directory"""
        try:
            df = pd.read_csv(csv_file_path)
            results = []
            
            # Process each row in the CSV
            for index, row in df.iterrows():
                file_name = row.get('file_name', f'file_{index}')
                
                # Extract question columns (assuming they start with 'q' followed by numbers)
                question_cols = [col for col in df.columns if col.startswith('q') and col[1:].isdigit()]
                
                for q_col in question_cols:
                    if pd.notna(row[q_col]):
                        results.append({
                            'file_name': file_name,
                            'question': q_col,
                            'marked_answer': row[q_col],
                            'student_response': row[q_col]
                        })
            
            return results
        
        except Exception as e:
            logger.error(f"Error loading CSV file {csv_file_path}: {e}")
            return []
    
    def find_result_files(self):
        """Find all result CSV files in the output directory"""
        result_files = []
        
        # Look for CSV files in Results directory
        results_dir = self.output_dir / "Results"
        if results_dir.exists():
            result_files.extend(list(results_dir.glob("*.csv")))
        
        # Look for CSV files in the main output directory
        result_files.extend(list(self.output_dir.glob("*.csv")))
        
        return result_files
    
    def process_all_results(self):
        """Process all available result files"""
        all_results = []
        
        # Find and process CSV files
        csv_files = self.find_result_files()
        
        for csv_file in csv_files:
            logger.info(f"Processing results from: {csv_file}")
            results = self.load_from_csv(csv_file)
            all_results.extend(results)
        
        return all_results

def integrate_with_entry_point():
    """
    Integration function to modify your existing entry_point to capture results
    Add this to your existing src/entry.py file
    """
    
    # Sample modification for your entry.py
    sample_code = '''
    # Add this to your existing entry.py file
    
    def entry_point(input_dir, args):
        # Your existing OMR processing code...
        
        # After processing, capture results
        results = []
        
        # Example: Extract from evaluation table output
        # You'll need to modify this based on your actual implementation
        
        # Return results for analysis
        return results
    '''
    
    return sample_code