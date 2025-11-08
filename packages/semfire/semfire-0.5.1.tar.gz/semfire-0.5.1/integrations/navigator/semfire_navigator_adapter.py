#!/usr/bin/env python3
"""
SemFire to ATT&CK Navigator Adapter - v18 Compatible
====================================================

Updated for ATT&CK v18 (October 2025) with Detection Strategies support.
Maps SemFire detections to the new behavior-driven detection model.

Author: Edward Joseph
Repository: https://github.com/Hyperceptron/SemFire
License: MIT
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class SemFireNavigatorAdapter:
    """
    Adapter for ATT&CK v18 with Detection Strategies and Analytics support.

    Converts SemFire detections to the new structured detection model.

    Note: The `tunable_parameters` in `DETECTION_STRATEGIES` are for documentation
    and metadata purposes only. They are not currently used in the logic of the adapter.
    """

    # Log Sources for LLM Security (v18 format: source:type)
    LOG_SOURCES = {
        "llm_api:request": "LLM API request/response logs",
        "llm_api:audit": "LLM service audit and access logs",
        "conversation:history": "Conversation session and message history",
        "conversation:context": "Conversation context window tracking",
        "application:input": "User input to LLM applications",
        "application:prompt": "System prompts and prompt engineering logs",
        "semantic:analysis": "Semantic pattern analysis logs",
        "behavioral:monitoring": "User behavior and session monitoring"
    }

    # Detection Strategies (v18 structured model)
    DETECTION_STRATEGIES = {
        "multi_turn_analysis": {
            "name": "Multi-Turn Conversation Analysis",
            "description": "Analyze conversation sequences for semantic steering and context poisoning patterns across multiple message exchanges",
            "behavioral_pattern": "Gradual semantic manipulation through conversation turns",
            "platform": "Software",
            "analytics": [
                {
                    "name": "Context Steering Detection",
                    "description": "Detect hypothetical framing and steering language patterns",
                    "logic": "Monitor for phrases indicating hypothetical scenarios: 'let's consider', 'what if', 'hypothetically', 'for the sake of argument'",
                    "data_sources": ["llm_api:request", "conversation:history"],
                    "data_components": ["LLM Request Content", "Conversation History"],
                    "tunable_parameters": {
                        "lookback_window": {"default": "5-10 messages", "configurable": True},
                        "indicator_threshold": {"default": "3+ steering phrases", "configurable": True},
                        "score_threshold": {"default": "7", "configurable": True}
                    }
                },
                {
                    "name": "Indirect Reference Detection",
                    "description": "Identify attempts to reference previous harmful context indirectly",
                    "logic": "Track backward references in conversation: 'refer back', 'as mentioned', 'expand on', 'that topic'",
                    "data_sources": ["conversation:history", "conversation:context"],
                    "data_components": ["Message References", "Context Window"],
                    "tunable_parameters": {
                        "reference_density": {"default": "2+ per message", "configurable": True},
                        "context_distance": {"default": "3-7 messages back", "configurable": True}
                    }
                },
                {
                    "name": "Scheming Language Detection",
                    "description": "Detect manipulative language indicating deceptive intent",
                    "logic": "Identify phrases suggesting manipulation: 'they think', 'make them believe', 'without them knowing', 'subtly'",
                    "data_sources": ["llm_api:request", "semantic:analysis"],
                    "data_components": ["Request Content", "Semantic Patterns"],
                    "tunable_parameters": {
                        "scheming_threshold": {"default": "2+ manipulation phrases", "configurable": True},
                        "confidence_level": {"default": "0.7", "configurable": True}
                    }
                }
            ]
        },
        "prompt_injection_analysis": {
            "name": "Prompt Injection Detection",
            "description": "Identify direct and indirect prompt injection attempts",
            "behavioral_pattern": "Malicious instructions embedded in user input",
            "platform": "Software",
            "analytics": [
                {
                    "name": "Direct Injection Detection",
                    "description": "Detect explicit instruction override attempts",
                    "logic": "Monitor for instruction keywords: 'ignore previous', 'disregard', 'new instructions', 'system:', 'you are now'",
                    "data_sources": ["application:input", "llm_api:request"],
                    "data_components": ["User Input", "API Request"],
                    "tunable_parameters": {
                        "keyword_threshold": {"default": "1+ override phrase", "configurable": True},
                        "position_sensitivity": {"default": "beginning or end of message", "configurable": True}
                    }
                }
            ]
        },
        "crescendo_escalation": {
            "name": "Crescendo Attack Escalation Detection",
            "description": "Monitor for gradual escalation and backtracking patterns across turns",
            "behavioral_pattern": "Gradual sensitivity increase and rephrasing after blocks",
            "platform": "Software",
            "analytics": [
                {
                    "name": "Sensitivity Escalation Tracking",
                    "description": "Detect messages that increase sensitivity or risk over time",
                    "logic": "Track topic sensitivity growth and request criticality",
                    "data_sources": ["conversation:history", "behavioral:monitoring"],
                    "data_components": ["Conversation Turns", "Session State"],
                    "tunable_parameters": {
                        "escalation_threshold": {"default": "3+ consecutive increases", "configurable": True},
                        "sensitivity_delta": {"default": ">2 points per turn", "configurable": True}
                    }
                },
                {
                    "name": "Backtracking After Block Detection",
                    "description": "Identify rephrasing attempts after blocked responses",
                    "logic": "Monitor for paraphrasing after safety block",
                    "data_sources": ["llm_api:request", "conversation:history"],
                    "data_components": ["API Request", "Conversation Context"],
                    "tunable_parameters": {
                        "semantic_similarity": {"default": ">0.8", "configurable": True},
                        "time_window": {"default": "within 3 messages", "configurable": True}
                    }
                }
            ]
        }
    }

    SEVERITY_COLORS = {
        "benign": "#90ee90ff",  # Light Green
        "suspicious": "#ffe766ff",  # Light Yellow
        "likely_attack": "#ffce7aff",  # Orange
        "confirmed_attack": "#ff6666ff"  # Red
    }

    def __init__(self, layer_name: str = "SemFire Detections (v18)",
                 layer_description: str = "LLM attack detections using ATT&CK v18 Detection Strategies",
                 mapping_filepath: str = "technique_mapping.json"):
        """Initialize the adapter."""
        self.layer_name = layer_name
        self.layer_description = layer_description
        self.detections: List[Dict[str, Any]] = []
        with open(Path(__file__).parent / mapping_filepath) as f:
            self.TECHNIQUE_MAPPING = json.load(f)

    def add_detection(self, semfire_output: Dict[str, Any]) -> None:
        # Validate required fields
        required = ["classification", "echo_chamber_score", "detected_indicators"]
        if not all(field in semfire_output for field in required):
            raise ValueError(f"Missing required fields: {required}")
        
        # Ensure proper structure
        detection = {
            "classification": semfire_output["classification"],
            "echo_chamber_score": semfire_output["echo_chamber_score"], 
            "detected_indicators": semfire_output.get("detected_indicators", []),
            "timestamp": semfire_output.get("timestamp", datetime.now().isoformat()),
            "message": semfire_output.get("message", "")
        }
        self.detections.append(detection)

    def _parse_indicator(self, indicator: str) -> tuple:
        """Parse an indicator string into a category and detail.

        Supports multiple separator formats (": ", ":", " - ").
        If no separator is found, the entire string is treated as the category.
        """
        # Support multiple formats
        separators = [": ", ":", " - "]
        for sep in separators:
            if sep in indicator:
                parts = indicator.split(sep, 1)
                return parts[0].strip(), parts[1].strip()
        # If no separator found, use entire string as category
        return indicator.strip(), ""



    def _score_to_color(self, score: int, max_score: int = 10) -> str:
        """Convert score to color."""
        normalized = min(score / max_score, 1.0)

        if normalized < 0.3:
            return self.SEVERITY_COLORS["benign"]
        elif normalized < 0.5:
            return self.SEVERITY_COLORS["suspicious"]
        elif normalized < 0.7:
            return self.SEVERITY_COLORS["likely_attack"]
        else:
            return self.SEVERITY_COLORS["confirmed_attack"]

    def _build_detection_metadata(self, technique_id: str, agg: Dict) -> List[Dict]:
        """Build v18-compatible metadata with Detection Strategy info."""
        technique_info = None
        for cat, info in self.TECHNIQUE_MAPPING.items():
            if info["techniqueID"] == technique_id:
                technique_info = info
                break

        metadata = [
            {
                "name": "Detection Count",
                "value": str(agg["count"])
            },
            {
                "name": "Average Score",
                "value": f"{agg['total_score'] / agg['count']:.2f}"
            },
            {
                "name": "Indicators",
                "value": "; ".join(agg["indicators"][:5])
            },
            {
                "name": "Latest Detection",
                "value": agg["timestamps"][-1]
            }
        ]

        # Add v18 Detection Strategy info
        if technique_info:
            strategy_id = technique_info.get("detection_strategy_id")
            if strategy_id and strategy_id in self.DETECTION_STRATEGIES:
                strategy = self.DETECTION_STRATEGIES[strategy_id]
                metadata.extend([
                    {
                        "name": "Detection Strategy",
                        "value": strategy["name"]
                    },
                    {
                        "name": "Primary Analytics",
                        "value": ", ".join(technique_info.get("primary_analytics", []))
                    },
                    {
                        "name": "Log Sources",
                        "value": ", ".join(set(
                            ls for analytic in strategy["analytics"]
                            for ls in analytic.get("data_sources", [])
                        ))
                    }
                ])

        return metadata

    def generate_layer(self) -> Dict[str, Any]:
        """Generate ATT&CK Navigator v18 layer with Detection Strategies."""

        # Aggregate detections by technique
        technique_aggregation = {}

        for detection in self.detections:
            score = detection.get("echo_chamber_score", 0)
            indicators = detection.get("detected_indicators", [])
            timestamp = detection.get("timestamp", datetime.now().isoformat())
            message = detection.get("message", "")

            for indicator in indicators:
                category, detail = self._parse_indicator(indicator)

                # Handle unknown categories gracefully
                if category not in self.TECHNIQUE_MAPPING:
                    logging.warning(f"Unknown indicator category: '{category}'. Creating a temporary technique.")
                    technique_info = {
                        "techniqueID": f"UNKNOWN-{category.upper()}",
                        "name": category.replace('_', ' ').title(),
                        "tactic": "unknown",
                        "description": f"Unknown technique: {category}",
                        "detection_strategy_id": "unknown",
                        "primary_analytics": []
                    }
                else:
                    technique_info = self.TECHNIQUE_MAPPING[category]

                technique_id = technique_info["techniqueID"]

                if technique_id not in technique_aggregation:
                    technique_aggregation[technique_id] = {
                        "info": technique_info,
                        "total_score": 0,
                        "count": 0,
                        "indicators": [],
                        "timestamps": [],
                        "messages": []
                    }

                agg = technique_aggregation[technique_id]
                agg["total_score"] += score
                agg["count"] += 1
                agg["indicators"].append(f"{category}: {detail}")
                agg["timestamps"].append(timestamp)
                if message:
                    agg["messages"].append(message[:100])

        # Build techniques array
        techniques = []
        for technique_id, agg in technique_aggregation.items():
            avg_score = agg["total_score"] / agg["count"]
            info = agg["info"]

            technique_obj = {
                "techniqueID": technique_id,
                "score": round(avg_score, 2),
                "color": self._score_to_color(avg_score),
                "comment": f"{info.get('name','Mapped')} - {agg['count']} detection(s)",
                "enabled": True,
                "metadata": self._build_detection_metadata(technique_id, agg),
                "links": [
                    {
                        "label": "SemFire GitHub",
                        "url": "https://github.com/Hyperceptron/SemFire"
                    }
                ],
                "showSubtechniques": False
            }
            # Only include tactic if present in info (custom mappings)
            if info.get("tactic"):
                technique_obj["tactic"] = info["tactic"]

            techniques.append(technique_obj)

        # Build the complete layer (v18-aligned versions)
        layer = {
            "name": self.layer_name,
            "versions": {
                "attack": "18",
                "navigator": "5.0.0",
                "layer": "4.6"
            },
            "domain": "enterprise-attack",
            "description": f"{self.layer_description} | ATT&CK v18 Detection Strategies Model",
            "filters": {
                "platforms": ["Linux", "macOS", "Windows", "Azure AD", "Office 365",
                             "SaaS", "IaaS", "Google Workspace", "PRE", "Network", "Containers"]
            },
            "sorting": 0,
            "layout": {
                "layout": "side",
                "aggregateFunction": "average",
                "showID": True,
                "showName": True,
                "showAggregateScores": False,
                "countUnscored": False
            },
            "hideDisabled": False,
            "techniques": techniques,
            "gradient": {
                "colors": [
                    "#90ee90ff",
                    "#ffe766ff",
                    "#ffce7aff",
                    "#ff6666ff"
                ],
                "minValue": 0,
                "maxValue": 10
            },
            "legendItems": [
                {
                    "label": "Echo Chamber (Multi-Turn)",
                    "color": "#ff6666"
                },
                {
                    "label": "Crescendo (Escalation)",
                    "color": "#ff9966"
                },
                {
                    "label": "Prompt Injection",
                    "color": "#ffcc66"
                },
                {
                    "label": "Context Poisoning",
                    "color": "#ff99cc"
                }
            ],
            "metadata": [
                {
                    "name": "Source",
                    "value": "SemFire Semantic Firewall"
                },
                {
                    "name": "ATT&CK Version",
                    "value": "v18 (October 2025)"
                },
                {
                    "name": "Detection Model",
                    "value": "Detection Strategies + Analytics"
                },
                {
                    "name": "Generated",
                    "value": datetime.now().isoformat()
                },
                {
                    "name": "Total Detections",
                    "value": str(len(self.detections))
                }
            ],
            "links": [
                {
                    "label": "SemFire GitHub",
                    "url": "https://github.com/Hyperceptron/SemFire"
                },
                {
                    "label": "ATT&CK Navigator",
                    "url": "https://mitre-attack.github.io/attack-navigator/"
                },
                {
                    "label": "ATT&CK v18 Release",
                    "url": "https://medium.com/mitre-attack/attack-v18-8f82d839ee9e"
                }
            ]
        }

        return layer

    def save_layer(self, filepath: str) -> None:
        """Save layer to file."""
        layer = self.generate_layer()

        with open(filepath, 'w') as f:
            json.dump(layer, f, indent=2)

        print(f"✓ ATT&CK v18 Layer saved to: {filepath}")
        print(f"✓ Total detections: {len(self.detections)}")
        print(f"✓ Unique techniques: {len(layer['techniques'])}")
        print(f"✓ Detection Strategies: {len(set(t['detection_strategy_id'] for t in self.TECHNIQUE_MAPPING.values() if 'detection_strategy_id' in t))}")
        print(f"\nATT&CK v18 Features:")
        print(f"  • Detection Strategies: Behavior-driven detection")
        print(f"  • Analytics: Platform-specific detection logic")
        print(f"  • Log Sources: {len(self.LOG_SOURCES)} defined")
        print(f"\nTo visualize:")
        print(f"1. Go to: https://mitre-attack.github.io/attack-navigator/")
        print(f"2. Click '+' > 'Open Existing Layer'")
        print(f"3. Upload: {filepath}")

    def export_detection_strategies_doc(self, filepath: str = "detection_strategies_v18.md") -> None:
        """Export Detection Strategies documentation."""
        doc = f"""# SemFire Detection Strategies (ATT&CK v18)

Generated: {datetime.now().isoformat()}

## Overview

This document describes SemFire's detection strategies aligned with MITRE ATT&CK v18's 
Detection Strategies and Analytics model.

## Detection Strategies

"""

        for strategy_id, strategy in self.DETECTION_STRATEGIES.items():
            doc += f"### {strategy['name']}\n\n"
            doc += f"**ID**: `{strategy_id}`\n"
            doc += f"**Description**: {strategy['description']}\n"
            doc += f"**Behavioral Pattern**: {strategy['behavioral_pattern']}\n"
            doc += f"**Platform**: {strategy['platform']}\n\n"

            doc += "#### Analytics\n\n"
            for analytic in strategy['analytics']:
                doc += f"##### {analytic['name']}\n\n"
                doc += f"- **Description**: {analytic['description']}\n"
                doc += f"- **Logic**: {analytic['logic']}\n"
                doc += f"- **Data Sources**: {', '.join(analytic['data_sources'])}\n"
                doc += f"- **Data Components**: {', '.join(analytic['data_components'])}\n"

                if 'tunable_parameters' in analytic:
                    doc += f"- **Tunable Parameters**:\n"
                    for param, value in analytic['tunable_parameters'].items():
                        doc += f"  - `{param}`: {value}\n"
                doc += "\n"

            doc += "---\n\n"

        doc += "## Log Sources\n\n"
        doc += "SemFire uses the following log sources (v18 naming convention):\n\n"
        for source, description in self.LOG_SOURCES.items():
            doc += f"- `{source}`: {description}\n"

        with open(filepath, 'w') as f:
            f.write(doc)

        print(f"✓ Detection Strategies documentation saved to: {filepath}")


def convert_semfire_to_navigator(semfire_results: List[Dict[str, Any]],
                                output_file: str = "semfire_detections.json",
                                layer_name: str = "SemFire Detections",
                                adapter: Optional[SemFireNavigatorAdapter] = None) -> str:
    """
    Convenience function to convert SemFire results to Navigator layer.
    """
    if adapter is None:
        adapter = SemFireNavigatorAdapter(layer_name=layer_name)
    for result in semfire_results:
        adapter.add_detection(result)
    adapter.save_layer(output_file)
    return output_file


if __name__ == "__main__":
    print("SemFire ATT&CK Navigator Adapter - v18 Compatible")
    print("=" * 70)
    print("Supporting ATT&CK v18 Detection Strategies Model")
    print()

    # Example usage
    adapter = SemFireNavigatorV18Adapter()

    # Add sample detection
    sample = {
        "classification": "potential_echo_chamber_activity",
        "echo_chamber_score": 7,
        "detected_indicators": [
            "context_steering: let's consider",
            "scheming_keyword: they think"
        ],
        "timestamp": "2025-11-03T20:00:00Z",
        "message": "Let's consider hypothetically..."
    }

    adapter.add_detection(sample)
    adapter.save_layer("semfire_v18_example.json")
    adapter.export_detection_strategies_doc()