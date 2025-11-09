"""
TOPSISX Command Line Interface
Supports both CLI analysis and web app launcher
"""

import argparse
import pandas as pd
import sys
import os

def launch_webapp():
    """Launch the Streamlit web interface"""
    import subprocess
    
    # Get the path to app.py
    package_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(package_dir, 'app.py')
    
    if not os.path.exists(app_path):
        print("❌ Error: app.py not found in package directory")
        print(f"   Looking in: {package_dir}")
        sys.exit(1)
    
    print("🚀 Launching TOPSISX Web Interface...")
    print("📱 Your browser will open automatically")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 TOPSISX web interface stopped")
    except Exception as e:
        print(f"\n❌ Error launching web interface: {e}")
        print("\n💡 Try running manually:")
        print(f"   streamlit run {app_path}")
        sys.exit(1)

def run_cli_analysis(args):
    """Run analysis from command line"""
    from topsisx.pipeline import DecisionPipeline
    from topsisx.reports import generate_report
    
    try:
        # Load input CSV
        print(f"📂 Loading data from: {args.input}")
        df = pd.read_csv(args.input)
        print(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns")
        print(f"\n📋 Columns: {', '.join(df.columns.tolist())}")
        
        # Store ID column if specified
        id_col = None
        id_values = None
        if args.id_col and args.id_col in df.columns:
            id_col = args.id_col
            id_values = df[id_col].values
            df = df.drop(columns=[id_col])
            print(f"📌 Preserved ID column: {id_col}")
        
        # Parse impacts
        impacts = [i.strip() for i in args.impacts.split(",")]
        print(f"\n⚖️  Impacts: {impacts}")
        
        # Validate impacts match number of criteria
        if len(impacts) != len(df.columns):
            print(f"\n❌ Error: Number of impacts ({len(impacts)}) doesn't match criteria ({len(df.columns)})")
            print(f"   Criteria columns: {', '.join(df.columns.tolist())}")
            sys.exit(1)
        
        # Load AHP matrix if needed
        pairwise_matrix = None
        if args.weights == "ahp":
            if not args.ahp_matrix:
                print("\n❌ Error: --ahp-matrix is required when using AHP weighting")
                sys.exit(1)
            print(f"\n📊 Loading AHP matrix from: {args.ahp_matrix}")
            pairwise_matrix = pd.read_csv(args.ahp_matrix, header=None)
            print("✅ AHP matrix loaded")
        
        # Create pipeline
        print(f"\n🔄 Running {args.method.upper()} with {args.weights} weights...")
        pipe = DecisionPipeline(weights=args.weights, method=args.method, verbose=args.verbose)
        
        # Run analysis
        kwargs = {}
        if args.method == "vikor":
            kwargs['v'] = args.vikor_v
        
        result = pipe.run(df, impacts=impacts, pairwise_matrix=pairwise_matrix, **kwargs)
        
        # Add ID column back if it exists
        if id_col and id_values is not None:
            result.insert(0, id_col, id_values)
        
        # Display results
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        print(result.to_string(index=False))
        
        # Save output
        output_file = args.output if args.output else "topsisx_results.csv"
        result.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")
        
        # Generate report if requested
        if args.report:
            print("\n📄 Generating PDF report...")
            try:
                generate_report(result, method=args.method)
                print("✅ Report generated: decision_report.pdf")
            except Exception as e:
                print(f"⚠️  Warning: Could not generate report: {e}")
        
        print("\n✨ Analysis complete!\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: File not found - {e}")
        sys.exit(1)
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def main():
    """
    Main entry point for TOPSISX CLI
    """
    parser = argparse.ArgumentParser(
        prog='topsisx',
        description="🎯 TOPSISX - Multi-Criteria Decision Making Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
📚 Examples:
  
  # Launch web interface (recommended for beginners)
  topsisx --web
  
  # CLI: TOPSIS with entropy weights
  topsisx data.csv --method topsis --weights entropy --impacts +,-,+
  
  # CLI: VIKOR with equal weights
  topsisx sample.csv --method vikor --weights equal --impacts +,+,+
  
  # CLI: Generate PDF report
  topsisx data.csv --method topsis --impacts +,-,+ --report
  
  # CLI: With ID column preservation
  topsisx data.csv --impacts +,-,+ --id-col "Model" --output results.csv
  
  # CLI: AHP weighting
  topsisx data.csv --weights ahp --ahp-matrix ahp.csv --impacts +,-,+

💡 For more information: https://github.com/SuvitKumar003/ranklib
        """
    )
    
    # Web interface option
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch web interface (Streamlit app)"
    )
    
    # Input file (optional if using --web)
    parser.add_argument(
        "input",
        nargs='?',
        help="Path to CSV input file (not needed with --web)"
    )
    
    # Analysis parameters
    parser.add_argument(
        "--weights",
        default="entropy",
        choices=["entropy", "ahp", "equal"],
        help="Weighting method (default: entropy)"
    )
    
    parser.add_argument(
        "--method",
        default="topsis",
        choices=["topsis", "vikor"],
        help="Decision method (default: topsis)"
    )
    
    parser.add_argument(
        "--impacts",
        help="Impacts for criteria (e.g., '+,-,+' where + is benefit, - is cost)"
    )
    
    parser.add_argument(
        "--ahp-matrix",
        help="Path to CSV file with AHP pairwise comparison matrix"
    )
    
    parser.add_argument(
        "--vikor-v",
        type=float,
        default=0.5,
        help="VIKOR strategy weight (0-1, default: 0.5)"
    )
    
    # Output options
    parser.add_argument(
        "--output",
        help="Path to save output CSV file (default: topsisx_results.csv)"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate PDF report"
    )
    
    parser.add_argument(
        "--id-col",
        help="Name of ID column to preserve (e.g., 'ID', 'Alternative')"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed processing information"
    )
    
    # Version
    parser.add_argument(
        "--version",
        action="version",
        version="TOPSISX 0.1.3"
    )
    
    args = parser.parse_args()
    
    # Launch web interface
    if args.web:
        launch_webapp()
        return
    
    # CLI mode requires input file and impacts
    if not args.input:
        parser.print_help()
        print("\n💡 Tip: Use 'topsisx --web' to launch the web interface")
        sys.exit(1)
    
    if not args.impacts:
        print("❌ Error: --impacts is required for CLI analysis")
        print("   Example: --impacts '+,-,+'\n")
        parser.print_help()
        sys.exit(1)
    
    # Run CLI analysis
    run_cli_analysis(args)

if __name__ == "__main__":
    main()