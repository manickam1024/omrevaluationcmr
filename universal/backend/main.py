import argparse
import sys
from pathlib import Path
from src.entry import entry_point
from src.logger import logger

def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-i", "--inputDir",
        default=["inputs"],
        nargs="*",
        required=False,
        type=str,
        dest="input_paths",
        help="Specify an input directory.",
    )
    argparser.add_argument(
        "-d", "--debug",
        required=False,
        dest="debug",
        action="store_false",
        help="Enables debugging mode for showing detailed errors",
    )
    argparser.add_argument(
        "-o", "--outputDir",
        default="outputs",
        required=False,
        dest="output_dir",
        help="Specify an output directory.",
    )
    argparser.add_argument(
        "-a", "--autoAlign",
        required=False,
        dest="autoAlign",
        action="store_true",
        help="(experimental) Enables automatic template alignment - use if the scans show slight misalignments.",
    )
    argparser.add_argument(
        "-l", "--setLayout",
        required=False,
        dest="setLayout",
        action="store_true",
        help="Set up OMR template layout - modify your json file and run again until the template is set.",
    )
    argparser.add_argument(
        "--analyze",
        required=False,
        dest="analyze",
        action="store_true",
        help="Run detailed analysis on OMR results including difficulty and question type classification.",
    )
    
    args, unknown = argparser.parse_known_args()
    args = vars(args)
    
    if len(unknown) > 0:
        logger.warning(f"\nError: Unknown arguments: {unknown}", unknown)
        argparser.print_help()
        exit(11)
    
    return args

def run_analysis(output_dir: str, results_data: list = None):
    """Run analysis on OMR results"""
    try:
        from analyze_omr import analyze_results
        
        if results_data:
            # Use provided results data
            analyze_results(results_data, output_dir)
        else:
            # Try to find and analyze CSV files
            from analyze_omr import analyze_from_csv_files
            analyze_from_csv_files(output_dir)
            
    except ImportError:
        print("Analysis module not found. Please ensure analyze_omr.py is in the same directory.")
    except Exception as e:
        print(f"Error running analysis: {e}")

def entry_point_for_args(args):
    if args["debug"] is True:
        sys.tracebacklimit = 0
    
    # Store results for analysis
    all_results = []
    
    for root in args["input_paths"]:
        # Get results from entry_point
        results = entry_point(Path(root), args)
        if results:
            all_results.extend(results)
    
    # Run analysis if requested
    if args.get("analyze", False):
        print("\n" + "="*50)
        print("STARTING DETAILED ANALYSIS...")
        print("="*50)
        
        if all_results:
            # Use the results from processing
            run_analysis(args["output_dir"], all_results)
        else:
            # Fallback to CSV analysis
            run_analysis(args["output_dir"])

if __name__ == "__main__":
    args = parse_args()
    entry_point_for_args(args)