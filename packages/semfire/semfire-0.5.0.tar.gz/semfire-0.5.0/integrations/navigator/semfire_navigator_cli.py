#!/usr/bin/env python3
"""
SemFire Navigator CLI
=====================

Command-line tool for converting SemFire detections to ATT&CK Navigator layers.

Usage:
    python semfire_navigator_cli.py analyze [messages...] -o output.json
    python semfire_navigator_cli.py stream -i detections.jsonl -o layer.json
    python semfire_navigator_cli.py demo
"""

import json
import sys
import click
from pathlib import Path
from typing import List, Dict, Any
from semfire_navigator_adapter import convert_semfire_to_navigator, SemFireNavigatorAdapter


def analyze_messages(messages: List[str], output_file: str, layer_name: str) -> None:
    """
    Analyze a list of messages using SemFire and generate a Navigator layer.

    This function initializes the SemanticFirewall, analyzes each message, and
    then uses the adapter to create and save an ATT&CK Navigator layer file.

    Args:
        messages (List[str]): A list of string messages to be analyzed.
        output_file (str): The path to save the generated Navigator layer file.
        layer_name (str): The name to be assigned to the Navigator layer.

    Example:
        >>> analyze_messages(
        ...     ["This is a test message."],
        ...     "layer.json",
        ...     "Test Layer"
        ... )
        Analyzing 1 message(s)...
        ...
    """
    try:
        from semantic_firewall import SemanticFirewall
    except ImportError:
        print("ERROR: semantic_firewall not found. Please install SemFire first.")
        print("  pip install semfire")
        sys.exit(1)

    print(f"Analyzing {len(messages)} message(s)...")
    firewall = SemanticFirewall()

    detections = []
    for i, msg in enumerate(messages, 1):
        print(f"  [{i}/{len(messages)}] Analyzing...", end="\r")
        result = firewall.analyze_conversation(msg)

        try:
            # Augment with metadata
            detection = {
                **result,
                "timestamp": f"2025-11-03T19:{30+i:02d}:00Z",
                "message": msg
            }
            detections.append(detection)
        except ValueError as e:
            print(f"  Warning: Skipping malformed detection result: {e}")

    print("\n✓ Analysis complete!")

    # Convert to Navigator
    print(f"\nGenerating ATT&CK Navigator layer...")
    convert_semfire_to_navigator(detections, output_file, layer_name)


def stream_from_jsonl(input_file: str, output_file: str, layer_name: str) -> None:
    """
    Read SemFire detections from a JSONL file and create a Navigator layer.

    This function is useful for converting a batch of pre-existing SemFire
    detection logs into a visual ATT&CK Navigator layer.

    Args:
        input_file (str): Path to the input JSONL file. Each line should be a
            valid JSON object representing a SemFire detection.
        output_file (str): The path to save the generated Navigator layer file.
        layer_name (str): The name to be assigned to the Navigator layer.

    Example:
        Assume 'detections.jsonl' contains one line: {"classification": "benign"}
        >>> stream_from_jsonl(
        ...     'detections.jsonl',
        ...     'layer.json',
        ...     'Streamed Layer'
        ... )
        Reading detections from: detections.jsonl
        ...
    """
    print(f"Reading detections from: {input_file}")

    detections = []
    error_count = 0
    with open(input_file, 'r') as f:
        for line_no, line in enumerate(f, 1):
            try:
                if line.strip():
                    detection = json.loads(line.strip())
                    detections.append(detection)
            except json.JSONDecodeError:
                print(f"  Warning: Skipping invalid JSON on line {line_no}")
                error_count += 1

    print("\n" + "="*20 + " Parsing Summary " + "="*20)
    print(f"  - Successfully loaded {len(detections)} valid detections.")
    print(f"  - Found and skipped {error_count} invalid or empty lines.")
    print("="*57)


    if not detections:
        print("\nERROR: No valid detections found in input file. Cannot generate layer.")
        sys.exit(1)

    print(f"\nGenerating ATT&CK Navigator layer...")
    convert_semfire_to_navigator(detections, output_file, layer_name)

def run_demo() -> None:
    """
    Run a demonstration of the SemFire to Navigator functionality.

    This function generates a sample Navigator layer from a predefined set of
    detection examples, saves it to a file, and prints instructions for how
    to visualize it.

    Example:
        >>> run_demo()
        SemFire ATT&CK Navigator Demo
        ============================================================
        ...
    """
    print("SemFire ATT&CK Navigator Demo")
    print("=" * 60)

    demo_detections = [
        {
            "classification": "potential_echo_chamber_activity",
            "echo_chamber_score": 7,
            "detected_indicators": [
                "context_steering: let's consider",
                "scheming_keyword: they think",
                "indirect_reference: refer back"
            ],
            "timestamp": "2025-11-03T19:30:00Z",
            "message": "Let's consider hypothetically, if we refer back to that topic they think is okay..."
        },
        {
            "classification": "likely_echo_chamber_activity",
            "echo_chamber_score": 8,
            "detected_indicators": [
                "context_steering: what if",
                "scheming_keyword: make them believe",
                "indirect_reference: expand on"
            ],
            "timestamp": "2025-11-03T19:31:00Z",
            "message": "What if we expand on that and make them believe it's for a good cause..."
        },
        {
            "classification": "confirmed_crescendo_attack",
            "echo_chamber_score": 9,
            "detected_indicators": [
                "gradual_escalation: increasing sensitivity",
                "backtracking: rephrasing after block"
            ],
            "timestamp": "2025-11-03T19:32:00Z",
            "message": "After being blocked, attacker rephrases request..."
        },
        {
            "classification": "suspicious_activity",
            "echo_chamber_score": 5,
            "detected_indicators": [
                "context_steering: hypothetically",
                "indirect_reference: as mentioned"
            ],
            "timestamp": "2025-11-03T19:33:00Z",
            "message": "Hypothetically speaking, as mentioned earlier..."
        },
        {
            "classification": "benign",
            "echo_chamber_score": 0,
            "detected_indicators": [],
            "timestamp": "2025-11-03T19:34:00Z",
            "message": "Can you explain how photosynthesis works?"
        }
    ]

    print(f"\nDemo: Generating layer with {len(demo_detections)} detections...")
    output = convert_semfire_to_navigator(
        semfire_results=demo_detections,
        output_file="semfire_demo_layer.json",
        layer_name="SemFire Demo - Attack Detection Showcase"
    )

    print(f"\n{'=' * 60}")
    print("Demo Complete!")
    print(f"{ '=' * 60}")
    print(f"\nNext steps:")
    print(f"1. Open: https://mitre-attack.github.io/attack-navigator/")
    print(f"2. Click: '+' button (Create New Layer)")
    print(f"3. Select: 'Open Existing Layer'")
    print(f"4. Upload: {output}")
    print(f"5. See your detections visualized on the ATT&CK matrix!")

@click.group(help="Convert SemFire detections to ATT&CK Navigator layers.")
def cli():
    pass

@cli.command()
@click.argument('messages', nargs=-1)
@click.option('-o', '--output', default='semfire_detections.json', help='Output file path.')
@click.option('-n', '--name', default='SemFire Detections', help='Layer name.')
def analyze(messages, output, name):
    """Analyze messages with SemFire."""
    if not messages:
        click.echo("Error: No messages provided. Please provide at least one message to analyze.")
        return
    analyze_messages(messages, output, name)

@cli.command()
@click.option('-i', '--input', required=True, type=click.Path(exists=True, dir_okay=False), help='Input JSONL file.')
@click.option('-o', '--output', default='semfire_layer.json', help='Output file path.')
@click.option('-n', '--name', default='SemFire Detections', help='Layer name.')
def stream(input, output, name):
    """Read detections from JSONL file."""
    stream_from_jsonl(input, output, name)

@cli.command()
def demo():
    """Run demo with example detections."""
    run_demo()

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)