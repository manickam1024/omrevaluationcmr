#main.py

import argparse
import sys
from pathlib import Path
from src.entry import entry_point
from src.logger import logger
from typing import List, Dict, Any
import json

def parse_args():
    argparser = argparse.ArgumentParser(description="OMR Processing System")

    argparser.add_argument(
        "-i", "--inputDir",
        default=["inputs"],
        nargs="+",
        required=False,
        type=str,
        dest="input_paths",
        help="Specify one or more input directories containing OMR sheets",
    )

    argparser.add_argument(
        "-d", "--debug",
        required=False,
        dest="debug",
        action="store_true",
        help="Enable debugging mode for detailed errors",
    )

    argparser.add_argument(
        "-o", "--outputDir",
        default="outputs",
        required=False,
        dest="output_dir",
        help="Specify an output directory for results",
    )

    argparser.add_argument(
        "-a", "--autoAlign",
        required=False,
        dest="autoAlign",
        action="store_true",
        help="(experimental) Enable automatic template alignment",
    )

    argparser.add_argument(
        "-l", "--setLayout",
        required=False,
        dest="setLayout",
        action="store_true",
        help="Set up OMR template layout",
    )

    argparser.add_argument(
        "--analyze",
        required=False,
        dest="analyze",
        action="store_true",
        help="Run detailed analysis on OMR results",
    )

    argparser.add_argument(
        "--batch",
        required=False,
        dest="batch_mode",
        action="store_true",
        help="Process multiple OMR sheets in batch mode",
    )

    args, unknown = argparser.parse_known_args()
    args = vars(args)

    if unknown:
        logger.warning(f"\nWarning: Unknown arguments: {unknown}")
        argparser.print_help()
        sys.exit(11)

    return args

def run_analysis(output_dir: str, all_results: List[Dict[str, Any]]):
    """Run comprehensive analysis on multiple OMR results"""
    try:
        from analyze_omr import analyze_batch_results

        if not all_results:
            logger.error("No results available for analysis")
            return

        # Ensure output directory exists
        analysis_dir = Path(output_dir) / "Analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)

        # Run batch analysis
        analyze_batch_results(all_results, str(analysis_dir))

    except ImportError as e:
        logger.error(f"Analysis module not found: {e}")
    except Exception as e:
        logger.error(f"Error running analysis: {e}")

def process_single_omr(input_path: Path, args: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process a single OMR sheet"""
    try:
        if not input_path.exists():
            logger.error(f"Input path does not exist: {input_path}")
            return []

        logger.info(f"Processing OMR: {input_path.name}")
        return entry_point(input_path, args)

    except Exception as e:
        logger.error(f"Error processing {input_path}: {e}")
        return []

def entry_point_for_args(args):
    if not args.get("debug", False):
        sys.tracebacklimit = 0

    all_results = []

    for input_path in args["input_paths"]:
        root_path = Path(input_path)

        if args.get("batch_mode", False) and root_path.is_dir():
            # Batch process all image/pdf files in the directory
            logger.info(f"Batch processing OMR sheets in: {root_path}")
            for omr_file in root_path.glob("*"):
                if omr_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.pdf']:
                    results = process_single_omr(omr_file, args)
                    if results:
                        all_results.append({
                            'omr_file': str(omr_file),
                            'results': results
                        })
        else:
            # Process a single OMR sheet or directory
            results = process_single_omr(root_path, args)
            if results:
                all_results.append({
                    'omr_file': str(root_path),
                    'results': results
                })

    # Save raw results
    Path(args["output_dir"]).mkdir(parents=True, exist_ok=True)
    with open(Path(args["output_dir"]) / "raw_results.json", 'w') as f:
        json.dump(all_results, f, indent=2)

    # Run analysis if enabled
    if args.get("analyze", False) and all_results:
        print("\n" + "=" * 50)
        print("STARTING BATCH ANALYSIS...")
        print("=" * 50)
        run_analysis(args["output_dir"], all_results)

if __name__ == "__main__":
    args = parse_args()
    entry_point_for_args(args)