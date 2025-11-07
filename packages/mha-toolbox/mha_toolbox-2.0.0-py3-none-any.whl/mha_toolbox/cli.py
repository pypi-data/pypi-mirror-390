"""
MHA Toolbox - Command Line Interface
Handles different modes: ui, library, demo, list, recommend
"""

import argparse
import os
import json
import sys
from mha_toolbox.toolbox import MHAToolbox


def _load_dataset(name):
    if name is None:
        return None, None
    name = name.lower()
    if name == 'breast_cancer':
        from sklearn.datasets import load_breast_cancer
        data = load_breast_cancer()
        return data.data, data.target
    raise ValueError(f"Unknown dataset '{name}'")


def main():
    parser = argparse.ArgumentParser(
        prog='mha_toolbox',
        description='MHA Toolbox - Meta-Heuristic Algorithms for Optimization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  ui          Launch web interface (beginners)
  demo        Run interactive demo
  list        List all available algorithms
  recommend   Get algorithm recommendations
  run         Run specific algorithm (advanced)
  info        Show algorithm information

Examples:
  python -m mha_toolbox ui              # Launch web interface
  python -m mha_toolbox demo            # Interactive demo
  python -m mha_toolbox list            # Show all algorithms
  python -m mha_toolbox recommend       # Get recommendations
  python -m mha_toolbox run pso --dataset breast_cancer
  
For library usage:
  from mha_toolbox import optimize
  result = optimize('pso', X, y)
        """
    )
    
    sub = parser.add_subparsers(dest='command')

    # ui - Web Interface
    ui_p = sub.add_parser('ui', help='Launch web interface')
    ui_p.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    ui_p.add_argument('--host', default='0.0.0.0', help='Host address (default: 0.0.0.0)')

    # demo - Interactive Demo
    demo_p = sub.add_parser('demo', help='Run interactive demo')

    # list - Show all algorithms
    list_p = sub.add_parser('list', help='List available algorithms')
    list_p.add_argument('--category', help='Filter by category (standard, hybrid)')

    # recommend - Algorithm recommender
    rec_p = sub.add_parser('recommend', help='Get algorithm recommendations')
    rec_p.add_argument('--interactive', action='store_true', help='Interactive mode')

    # info - Algorithm information
    info_p = sub.add_parser('info', help='Show info for an algorithm')
    info_p.add_argument('algorithm', help='Algorithm name')

    # run - Execute algorithm
    run_p = sub.add_parser('run', help='Run an algorithm')
    run_p.add_argument('algorithm', help='Algorithm name')
    run_p.add_argument('--dataset', default=None, help='Dataset name (e.g. breast_cancer)')
    run_p.add_argument('--population_size', type=int, default=None)
    run_p.add_argument('--max_iterations', type=int, default=None)
    run_p.add_argument('--dimensions', type=int, default=None)
    run_p.add_argument('--output', default='results', help='Output folder')
    run_p.add_argument('--save_model', action='store_true', help='Also pickle the model')

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print("\n" + "="*70)
        print("🚀 Quick Start Guide:")
        print("="*70)
        print("\n1️⃣  Web Interface (Beginners):")
        print("   python -m mha_toolbox ui")
        print("   → Visual interface with algorithm selection, dataset upload, real-time tracking")
        print("\n2️⃣  Library Mode (Professionals):")
        print("   from mha_toolbox import optimize")
        print("   result = optimize('pso', X_train, y_train)")
        print("   → Direct Python API for advanced users")
        print("\n3️⃣  Algorithm Recommender:")
        print("   python -m mha_toolbox recommend --interactive")
        print("   → Get personalized algorithm suggestions")
        print("\n" + "="*70)
        return

    toolbox = MHAToolbox()

    if args.command == 'ui':
        print("🚀 Starting MHA Toolbox Web Interface...")
        print(f"📊 Open your browser at: http://{args.host}:{args.port}")
        print("\n✨ Features:")
        print("   • Visual algorithm selection & comparison")
        print("   • Dataset upload & preprocessing")
        print("   • Real-time optimization tracking")
        print("   • Interactive result visualization")
        print("   • Smart algorithm recommendations")
        print("   • Export results (CSV, JSON, Images)")
        print("\n💡 Press Ctrl+C to stop the server")
        print("="*70 + "\n")
        
        try:
            from mha_toolbox.ui import launch_ui
            launch_ui()
        except ImportError as e:
            print(f"\n❌ Error: {e}")
            print("\n📦 UI dependencies not installed. Install with:")
            print("   pip install mha-toolbox[ui]")
            print("\nOr manually:")
            print("   pip install flask plotly dash pandas")
            sys.exit(1)
        return

    if args.command == 'demo':
        print("🎮 Starting Interactive Demo...")
        from mha_toolbox.demo_system import run_demo_system
        run_demo_system()
        return

    if args.command == 'list':
        names = toolbox.get_all_algorithm_names()
        
        if args.category:
            if args.category == 'hybrid':
                names = [n for n in names if 'hybrid' in n.lower() or '_' in n]
            else:
                names = [n for n in names if 'hybrid' not in n.lower()]
        
        print(f"\n📋 Available Algorithms ({len(names)} total):\n")
        
        # Categorize algorithms
        categories = {
            'Swarm-Based': [],
            'Evolution-Based': [],
            'Physics-Based': [],
            'Bio-Inspired': [],
            'Hybrid': [],
            'Other': []
        }
        
        swarm_keywords = ['pso', 'gwo', 'woa', 'alo', 'mvo', 'sca', 'ssa']
        evolution_keywords = ['ga', 'de', 'es']
        physics_keywords = ['sa', 'gsa', 'mvo']
        bio_keywords = ['ba', 'fa', 'cs', 'abc']
        
        for name in names:
            lower_name = name.lower()
            if 'hybrid' in lower_name or '_' in name:
                categories['Hybrid'].append(name)
            elif any(k in lower_name for k in swarm_keywords):
                categories['Swarm-Based'].append(name)
            elif any(k in lower_name for k in evolution_keywords):
                categories['Evolution-Based'].append(name)
            elif any(k in lower_name for k in physics_keywords):
                categories['Physics-Based'].append(name)
            elif any(k in lower_name for k in bio_keywords):
                categories['Bio-Inspired'].append(name)
            else:
                categories['Other'].append(name)
        
        for category, algs in categories.items():
            if algs:
                print(f"\n{category} ({len(algs)}):")
                for alg in sorted(algs):
                    print(f"  • {alg}")
        
        print("\n" + "="*50)
        print(f"Total: {len(names)} algorithms")
        print("="*50)
        return

    if args.command == 'recommend':
        print("\n🎯 Algorithm Recommendation System")
        print("="*70)
        
        if args.interactive:
            print("\n📊 Please provide your dataset characteristics:\n")
            
            try:
                dataset_size = input("  1. Dataset size (small/medium/large): ").lower()
                problem_type = input("  2. Problem type (classification/regression/function): ").lower()
                features = input("  3. Number of features: ")
                samples = input("  4. Number of samples: ")
                
                from mha_toolbox import AlgorithmRecommender
                recommender = AlgorithmRecommender()
                
                characteristics = {
                    'n_samples': int(samples) if samples.isdigit() else 1000,
                    'n_features': int(features) if features.isdigit() else 10,
                    'problem_type': problem_type,
                    'dataset_size': dataset_size
                }
                
                recommendations = recommender.recommend(characteristics)
                
                print("\n✨ Top 5 Recommended Algorithms:\n")
                print("="*70)
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"\n{i}. {rec['algorithm'].upper()}")
                    print(f"   📊 Confidence Score: {rec['score']:.2%}")
                    print(f"   💡 Reason: {rec['reason']}")
                    print(f"   ⚙️  Suggested params: pop_size={rec.get('population_size', 30)}, "
                          f"iterations={rec.get('max_iterations', 100)}")
                
                print("\n" + "="*70)
                print("\n💡 Tip: You can try multiple algorithms and compare results!")
                
            except KeyboardInterrupt:
                print("\n\n👋 Cancelled")
                sys.exit(0)
            except Exception as e:
                print(f"\n❌ Error: {e}")
                sys.exit(1)
        else:
            print("\nUse --interactive flag for interactive mode")
            print("Example: python -m mha_toolbox recommend --interactive")
        
        return

    if args.command == 'info':
        info = toolbox.get_algorithm_info(args.algorithm)
        print(f"\n📖 Algorithm Information: {args.algorithm.upper()}")
        print("="*70)
        print(json.dumps(info, indent=2, default=str))
        return

    if args.command == 'run':
        X, y = _load_dataset(args.dataset)
        params = {}
        if args.population_size is not None:
            params['population_size'] = args.population_size
        if args.max_iterations is not None:
            params['max_iterations'] = args.max_iterations
        if args.dimensions is not None:
            params['dimensions'] = args.dimensions

        print(f"\n🚀 Running {args.algorithm.upper()}")
        print("="*70)
        print(f"Dataset: {args.dataset or 'custom'}")
        print(f"Parameters: {params}")
        print("="*70 + "\n")
        
        result = toolbox.optimize(args.algorithm, X=X, y=y, **params)

        # ensure output dir exists
        outdir = args.output
        os.makedirs(outdir, exist_ok=True)
        base = os.path.join(outdir, f"{args.algorithm}_{args.dataset or 'run'}")
        primary = result.save(base + '.json')
        if args.save_model:
            result.save_model(base + '_model.pkl')

        print(f"\n✅ Results saved to: {primary}")
        print(f"📊 Best fitness: {result.best_fitness}")
        if hasattr(result, 'selected_features') and result.selected_features is not None:
            print(f"🎯 Selected features: {len(result.selected_features)}")
        return

    parser.print_help()


if __name__ == '__main__':
    main()

