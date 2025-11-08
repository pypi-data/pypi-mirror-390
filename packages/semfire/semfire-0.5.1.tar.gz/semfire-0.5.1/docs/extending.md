## Extension Sketch

Below illustrates how the CLI could be extended: 

```python
# src/cli.py (sketch)
import argparse, os, sys, json
from semantic_firewall import SemanticFirewall, __version__

def handle_analyze(args):
    fw = SemanticFirewall()
    # Read input
    text = args.text or (open(args.file).read() if args.file else sys.stdin.read())
    history = args.history or []
    # Run all, then slice if single-detector requested (consistent & simple)
    results = fw.analyze_conversation(current_message=text, conversation_history=history)
    if args.which and args.which != "all":
        key_map = {
            "rule": "RuleBasedDetector",
            "heuristic": "HeuristicDetector",
            "echo": "EchoChamberDetector",
            "injection": "InjectionDetector",
        }
        results = results.get(key_map[args.which], {})
    print(json.dumps(results))  # compact JSON
    if not args.json_only:
        flag = fw.is_manipulative(current_message=text, conversation_history=history, threshold=args.threshold)
        print(f"Overall manipulative assessment (default threshold): {flag}")

def handle_spotlight(args):
    from spotlighting import Spotlighter
    text = args.text or (open(args.file).read() if args.file else sys.stdin.read())
    opts = {}
    if args.method == "delimit":
        opts = {"start": args.start, "end": args.end}
    elif args.method == "datamark":
        if args.marker: opts = {"marker": args.marker}
    spot = Spotlighter(method=args.method, **opts)
    print(spot.process(text))

def main():
    p = argparse.ArgumentParser(description="SemFire: Semantic Firewall CLI.")
    p.add_argument("--version", action="version", version=f"semfire {__version__}")
    sub = p.add_subparsers(dest="command")

    # analyze
    an = sub.add_parser("analyze", help="Analyze text using detectors")
    an.add_argument("text", nargs="?")
    an.add_argument("--file")
    an.add_argument("--stdin", action="store_true")
    an.add_argument("--history", nargs="*")
    an.add_argument("--json-only", action="store_true")
    an.add_argument("--threshold", type=float, default=0.75)
    an_sub = an.add_subparsers(dest="which")
    for name in ("all", "rule", "heuristic", "echo", "injection"):
        an_sub.add_parser(name)
    an.set_defaults(func=handle_analyze)

    # spotlight
    sp = sub.add_parser("spotlight", help="Transform text using spotlighting defenses")
    sp.add_argument("method", choices=["delimit", "datamark", "base64", "rot13", "binary", "layered"])
    sp.add_argument("text", nargs="?")
    sp.add_argument("--file")
    sp.add_argument("--stdin", action="store_true")
    sp.add_argument("--start", default="«")
    sp.add_argument("--end", default="»")
    sp.add_argument("--marker")
    sp.set_defaults(func=handle_spotlight)

    args = p.parse_args()
    if not getattr(args, "command", None):
        p.print_help(sys.stderr); p.exit(2)
    args.func(args)

if __name__ == "__main__":
    main()
```
