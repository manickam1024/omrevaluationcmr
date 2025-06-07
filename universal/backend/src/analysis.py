import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from collections import defaultdict, Counter
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OMRAnalyzer:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.analysis_dir = self.output_dir / "Analysis"
        self.analysis_dir.mkdir(exist_ok=True)
        
        # Difficulty thresholds (based on percentage of students getting it right)
        self.difficulty_thresholds = {
            'Very Easy': 0.8,    # >80% correct
            'Easy': 0.6,         # 60-80% correct
            'Medium': 0.4,       # 40-60% correct
            'Hard': 0.2,         # 20-40% correct
            'Very Hard': 0.0     # <20% correct
        }
        
        # Question type patterns (can be enhanced based on your specific needs)
        self.question_patterns = {
            'Conceptual': ['concept', 'definition', 'theory', 'principle'],
            'Computational': ['calculate', 'compute', 'solve', 'find'],
            'Analytical': ['analyze', 'compare', 'evaluate', 'assess'],
            'Application': ['apply', 'use', 'implement', 'practical'],
            'Memory': ['recall', 'remember', 'list', 'identify']
        }
    
    def parse_evaluation_table(self, log_content):
        """Parse the evaluation table from OMR log output"""
        results = []
        lines = log_content.split('\n')
        
        # Find the evaluation table
        in_table = False
        for line in lines:
            if 'Question' in line and 'Marked' in line and 'Answer(s)' in line:
                in_table = True
                continue
            
            if in_table and '│' in line and 'q' in line:
                # Parse table row
                parts = [p.strip() for p in line.split('│') if p.strip()]
                if len(parts) >= 6:
                    try:
                        question = parts[0]
                        marked = parts[1]
                        correct_answer = parts[2]
                        verdict = parts[3]
                        delta = float(parts[4])
                        score = float(parts[5])
                        
                        results.append({
                            'question': question,
                            'marked_answer': marked,
                            'correct_answer': correct_answer,
                            'verdict': verdict,
                            'delta': delta,
                            'cumulative_score': score,
                            'is_correct': verdict == 'Correct'
                        })
                    except (ValueError, IndexError):
                        continue
            
            if in_table and '└' in line:
                break
        
        return results
    
    def load_results_from_csv(self, csv_path):
        """Load results from CSV file if available"""
        try:
            df = pd.read_csv(csv_path)
            results = []
            
            for _, row in df.iterrows():
                # Assuming CSV has columns for questions and answers
                for col in df.columns:
                    if col.startswith('q') and col.replace('q', '').isdigit():
                        question_num = col
                        marked_answer = row[col] if pd.notna(row[col]) else 'Not Marked'
                        
                        results.append({
                            'question': question_num,
                            'marked_answer': marked_answer,
                            'student_id': row.get('student_id', 'Unknown'),
                            'file_name': row.get('file_name', 'Unknown')
                        })
            
            return results
        except Exception as e:
            logger.warning(f"Could not load CSV: {e}")
            return []
    
    def classify_difficulty(self, correct_percentage):
        """Classify question difficulty based on correct percentage"""
        for difficulty, threshold in self.difficulty_thresholds.items():
            if correct_percentage >= threshold:
                return difficulty
        return 'Very Hard'
    
    def classify_question_type(self, question_text="", answer_pattern=""):
        """Classify question type based on available information"""
        # This is a basic implementation - you can enhance it based on your needs
        question_text = question_text.lower()
        
        for q_type, keywords in self.question_patterns.items():
            if any(keyword in question_text for keyword in keywords):
                return q_type
        
        # Default classification based on answer patterns
        if answer_pattern in ['A', 'B', 'C', 'D']:
            return 'Multiple Choice'
        
        return 'General'
    
    def analyze_results(self, results_data):
        """Main analysis function"""
        logger.info("Starting OMR Analysis...")
        
        # Convert results to DataFrame
        df = pd.DataFrame(results_data)
        
        if df.empty:
            logger.warning("No data to analyze")
            return
        
        # Basic statistics
        total_questions = len(df)
        if 'is_correct' in df.columns:
            total_correct = df['is_correct'].sum()
            overall_accuracy = total_correct / total_questions * 100
        else:
            overall_accuracy = 0
        
        # Question-wise analysis
        question_stats = self.analyze_questions(df)
        
        # Generate reports
        self.generate_analysis_report(df, question_stats, overall_accuracy)
        self.create_visualizations(df, question_stats)
        
        logger.info(f"Analysis complete! Results saved to {self.analysis_dir}")
    
    def analyze_questions(self, df):
        """Analyze individual questions"""
        question_stats = {}
        
        for question in df['question'].unique():
            q_data = df[df['question'] == question]
            
            if 'is_correct' in df.columns:
                correct_count = q_data['is_correct'].sum()
                total_attempts = len(q_data)
                correct_percentage = correct_count / total_attempts if total_attempts > 0 else 0
                
                difficulty = self.classify_difficulty(correct_percentage)
            else:
                correct_percentage = 0
                difficulty = 'Unknown'
            
            # Analyze answer distribution
            answer_dist = q_data['marked_answer'].value_counts().to_dict()
            
            # Classify question type
            question_type = self.classify_question_type()
            
            question_stats[question] = {
                'correct_percentage': correct_percentage * 100,
                'difficulty': difficulty,
                'question_type': question_type,
                'answer_distribution': answer_dist,
                'total_attempts': len(q_data),
                'correct_answer': q_data['correct_answer'].iloc[0] if 'correct_answer' in q_data.columns else 'Unknown'
            }
        
        return question_stats
    
    def generate_analysis_report(self, df, question_stats, overall_accuracy):
        """Generate comprehensive analysis report"""
        report_path = self.analysis_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w') as f:
            f.write("OMR ANALYSIS REPORT\n")
            f.write("="*50 + "\n\n")
            
            # Overall statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-"*20 + "\n")
            f.write(f"Total Questions: {len(question_stats)}\n")
            f.write(f"Overall Accuracy: {overall_accuracy:.2f}%\n\n")
            
            # Difficulty distribution
            difficulty_dist = Counter([stats['difficulty'] for stats in question_stats.values()])
            f.write("DIFFICULTY DISTRIBUTION\n")
            f.write("-"*25 + "\n")
            for difficulty, count in difficulty_dist.items():
                percentage = count / len(question_stats) * 100
                f.write(f"{difficulty}: {count} questions ({percentage:.1f}%)\n")
            f.write("\n")
            
            # Question type distribution
            type_dist = Counter([stats['question_type'] for stats in question_stats.values()])
            f.write("QUESTION TYPE DISTRIBUTION\n")
            f.write("-"*30 + "\n")
            for q_type, count in type_dist.items():
                percentage = count / len(question_stats) * 100
                f.write(f"{q_type}: {count} questions ({percentage:.1f}%)\n")
            f.write("\n")
            
            # Detailed question analysis
            f.write("DETAILED QUESTION ANALYSIS\n")
            f.write("-"*30 + "\n")
            
            for question, stats in sorted(question_stats.items()):
                f.write(f"\n{question.upper()}:\n")
                f.write(f"  Correct Percentage: {stats['correct_percentage']:.1f}%\n")
                f.write(f"  Difficulty Level: {stats['difficulty']}\n")
                f.write(f"  Question Type: {stats['question_type']}\n")
                f.write(f"  Correct Answer: {stats['correct_answer']}\n")
                f.write(f"  Answer Distribution: {stats['answer_distribution']}\n")
        
        logger.info(f"Analysis report saved to: {report_path}")
        
        # Also create JSON version for programmatic access
        json_path = self.analysis_dir / f"analysis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analysis_data = {
            'overall_accuracy': overall_accuracy,
            'total_questions': len(question_stats),
            'question_stats': question_stats,
            'difficulty_distribution': dict(difficulty_dist),
            'question_type_distribution': dict(type_dist)
        }
        
        with open(json_path, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        logger.info(f"Analysis data saved to: {json_path}")
    
    def create_visualizations(self, df, question_stats):
        """Create visualization charts"""
        plt.style.use('seaborn-v0_8')
        
        # 1. Difficulty Distribution Pie Chart
        difficulty_counts = Counter([stats['difficulty'] for stats in question_stats.values()])
        
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        plt.pie(difficulty_counts.values(), labels=difficulty_counts.keys(), autopct='%1.1f%%')
        plt.title('Question Difficulty Distribution')
        
        # 2. Question Type Distribution
        type_counts = Counter([stats['question_type'] for stats in question_stats.values()])
        
        plt.subplot(2, 2, 2)
        plt.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%')
        plt.title('Question Type Distribution')
        
        # 3. Accuracy by Question
        questions = list(question_stats.keys())
        accuracies = [question_stats[q]['correct_percentage'] for q in questions]
        
        plt.subplot(2, 2, 3)
        plt.bar(range(len(questions)), accuracies)
        plt.title('Accuracy by Question')
        plt.xlabel('Question Number')
        plt.ylabel('Accuracy (%)')
        plt.xticks(range(len(questions)), [q.replace('q', '') for q in questions], rotation=45)
        
        # 4. Difficulty vs Accuracy Scatter
        difficulties = [question_stats[q]['difficulty'] for q in questions]
        difficulty_map = {'Very Easy': 5, 'Easy': 4, 'Medium': 3, 'Hard': 2, 'Very Hard': 1}
        difficulty_scores = [difficulty_map.get(d, 3) for d in difficulties]
        
        plt.subplot(2, 2, 4)
        plt.scatter(difficulty_scores, accuracies, alpha=0.6)
        plt.title('Difficulty Level vs Accuracy')
        plt.xlabel('Difficulty Score')
        plt.ylabel('Accuracy (%)')
        
        plt.tight_layout()
        chart_path = self.analysis_dir / f"analysis_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualization charts saved to: {chart_path}")
        
        # Create detailed heatmap for answer patterns
        self.create_answer_pattern_heatmap(question_stats)
    
    def create_answer_pattern_heatmap(self, question_stats):
        """Create heatmap showing answer distribution patterns"""
        # Prepare data for heatmap
        questions = sorted(question_stats.keys(), key=lambda x: int(x.replace('q', '')))
        options = ['A', 'B', 'C', 'D']
        
        heatmap_data = []
        for question in questions:
            row = []
            answer_dist = question_stats[question]['answer_distribution']
            total = sum(answer_dist.values())
            
            for option in options:
                percentage = (answer_dist.get(option, 0) / total * 100) if total > 0 else 0
                row.append(percentage)
            heatmap_data.append(row)
        
        # Create heatmap
        plt.figure(figsize=(10, max(8, len(questions) * 0.3)))
        sns.heatmap(heatmap_data, 
                   xticklabels=options,
                   yticklabels=[q.replace('q', 'Q') for q in questions],
                   annot=True, 
                   fmt='.1f',
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Percentage of Students'})
        
        plt.title('Answer Distribution Heatmap\n(Percentage of students choosing each option)')
        plt.xlabel('Answer Options')
        plt.ylabel('Questions')
        
        heatmap_path = self.analysis_dir / f"answer_distribution_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Answer distribution heatmap saved to: {heatmap_path}")

# Utility function to extract results from OMR output
def extract_results_from_output(output_text):
    """Extract results from OMR console output"""
    analyzer = OMRAnalyzer("temp")
    return analyzer.parse_evaluation_table(output_text)