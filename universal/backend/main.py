#!/usr/bin/env python3
"""
OMR Processing and Analysis Tool

Processes multiple OMR sheets from inputs/samplecmr
Performs detailed analysis including question difficulty
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
from src.entry import entry_point
from src.logger import logger

def parse_args():
    """Parse command line arguments"""
    argparser = argparse.ArgumentParser(description='OMR Processing Tool')
    
    # Input/output arguments
    argparser.add_argument(
        "-i", "--inputDir",
        default="inputs/samplecmr",
        type=str,
        dest="input_dir",
        help="Directory containing OMR sheets (default: inputs/samplecmr)",
    )
    argparser.add_argument(
        "-o", "--outputDir",
        default="outputs",
        type=str,
        dest="output_dir",
        help="Output directory for results (default: outputs)",
    )
    argparser.add_argument(
        "--pattern",
        default="*.jpg",
        help="File pattern for OMR sheets (e.g., '*.jpg', 'scan_*.png')"
    )

    # Processing options
    argparser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug mode with detailed errors",
    )
    argparser.add_argument(
        "-a", "--autoAlign",
        action="store_true",
        help="Enable automatic template alignment",
    )
    argparser.add_argument(
        "-l", "--setLayout",
        action="store_true",
        help="Set up OMR template layout",
    )

    # Analysis options
    argparser.add_argument(
        "--analyze",
        action="store_true",
        help="Run detailed analysis on OMR results",
    )
    argparser.add_argument(
        "--difficulty",
        action="store_true",
        help="Include question difficulty analysis",
    )

    args, unknown = argparser.parse_known_args()
    
    if unknown:
        logger.warning(f"Unknown arguments: {unknown}")
        argparser.print_help()
        sys.exit(1)
        
    return vars(args)

def process_omr_sheets(input_dir: Path, pattern: str, args: Dict) -> List[List[Dict]]:
    """Process all OMR sheets matching pattern in input directory"""
    all_results = []
    
    for img_path in sorted(input_dir.glob(pattern)):
        try:
            logger.info(f"Processing {img_path.name}...")
            sheet_results = entry_point(img_path, args)
            if sheet_results:
                all_results.append(sheet_results)
        except Exception as e:
            logger.error(f"Failed to process {img_path.name}: {str(e)}")
            if args.get("debug"):
                raise
            continue
    
    return all_results

def run_analysis(output_dir: str, all_results: List[List[Dict]], difficulty: bool = False):
    """Run analysis on collected OMR results"""
    try:
        # Import analysis functions
        from analyze_omr import (
            analyze_results,
            analyze_difficulty,
            generate_difficulty_report,
            generate_individual_reports
        )
        
        # Create output directory
        analysis_dir = Path(output_dir) / "Analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Standard analysis
        analyze_results(all_results, output_dir)
        
        # Difficulty analysis if requested
        if difficulty:
            logger.info("Running difficulty analysis...")
            difficulty_stats = analyze_difficulty(all_results)
            generate_difficulty_report(difficulty_stats, output_dir)
        
        # Generate individual reports
        generate_individual_reports(all_results, output_dir)
        
    except ImportError as e:
        logger.error(f"Analysis module error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        if args.get("debug"):
            raise
        sys.exit(1)

def main():
    """Main processing pipeline"""
    args = parse_args()
    
    try:
        # Setup input directory
        input_dir = Path(args["input_dir"])
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            sys.exit(1)
        
        # Process all OMR sheets
        all_results = process_omr_sheets(
            input_dir,
            args["pattern"],
            args
        )
        
        if not all_results:
            logger.error("No valid OMR sheets processed")
            sys.exit(1)
        
        # Run analysis if requested
        if args.get("analyze"):
            logger.info("Starting analysis...")
            run_analysis(
                args["output_dir"],
                all_results,
                args.get("difficulty", False)
            )
            
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        if args.get("debug"):
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()