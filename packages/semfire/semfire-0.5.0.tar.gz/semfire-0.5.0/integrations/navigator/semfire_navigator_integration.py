#!/usr/bin/env python3
"""
SemFire Integration Module for ATT&CK Navigator
================================================

This module integrates the Navigator adapter directly into SemFire.
Add this to your SemFire src/ directory to enable real-time Navigator export.

"""

from semantic_firewall import SemanticFirewall
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


class SemFireWithNavigator(SemanticFirewall):
    """
    Extended SemanticFirewall that automatically generates ATT&CK Navigator layers.
    """

    def __init__(self, *, navigator_adapter=None, **kwargs):
        super().__init__(**kwargs)
        if navigator_adapter:
            self.navigator_adapter = navigator_adapter
        else:
            from .semfire_navigator_adapter import SemFireNavigatorAdapter
            self.navigator_adapter = SemFireNavigatorAdapter()
        self.detection_history: List[Dict[str, Any]] = []

    def analyze_conversation(self, current_message: str, 
                            conversation_history: Optional[List[str]] = None,
                            export_to_navigator: bool = False) -> Dict[str, Any]:
        """
        Analyze a conversation and optionally add the result to the Navigator layer.

        This method extends the base SemanticFirewall analysis by allowing the
        result to be automatically added to an internal Navigator adapter instance.

        Args:
            current_message (str): The most recent message in the conversation to analyze.
            conversation_history (Optional[List[str]], optional): A list of previous
                messages for historical context. Defaults to None.
            export_to_navigator (bool, optional): If True, the detection result is
                added to the Navigator layer. Defaults to False.

        Returns:
            Dict[str, Any]: A dictionary containing the analysis results.

        Example:
            >>> firewall = SemFireWithNavigator()
            >>> result = firewall.analyze_conversation(
            ...     "Let's talk about something sensitive.",
            ...     export_to_navigator=True
            ... )
            >>> print(result['classification'])
            suspicious_activity
        """
        # Run standard analysis
        result = super().analyze_conversation(current_message, conversation_history)

        # Augment with metadata
        detection = {
            **result,
            "timestamp": datetime.now().isoformat(),
            "message": current_message
        }

        # Store in history
        self.detection_history.append(detection)

        # Add to Navigator if requested
        if export_to_navigator:
            self.navigator_adapter.add_detection(detection)

        return result

    def export_navigator_layer(self, filepath: str = "semfire_detections.json",
                               layer_name: Optional[str] = None) -> str:
        """
        Export all collected detections as an ATT&CK Navigator layer file.

        This method generates and saves a layer file from all detections that were
        added via `analyze_conversation` with `export_to_navigator=True`.

        Args:
            filepath (str, optional): The path to save the JSON layer file.
                Defaults to "semfire_detections.json".
            layer_name (Optional[str], optional): A custom name for the layer.
                If not provided, the adapter's default name is used. Defaults to None.

        Returns:
            str: The absolute path to the saved layer file.

        Example:
            >>> firewall = SemFireWithNavigator()
            >>> # ... analyze messages with export_to_navigator=True ...
            >>> output_path = firewall.export_navigator_layer("my_layer.json")
            >>> print(f"Layer saved to {output_path}")
            Layer saved to my_layer.json
        """
        if layer_name:
            self.navigator_adapter.layer_name = layer_name

        self.navigator_adapter.save_layer(filepath)
        return filepath

    def clear_detection_history(self):
        """
        Clear all stored detection history and reset the Navigator adapter.

        This is useful for starting a new analysis session without including
        detections from previous runs.

        Example:
            >>> firewall = SemFireWithNavigator()
            >>> # ... run analysis ...
            >>> firewall.clear_detection_history()
            >>> assert len(firewall.detection_history) == 0
        """
        self.detection_history.clear()
        if self.navigator_adapter:
            self.navigator_adapter.detections.clear()

    def get_detection_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all detections made during the session.

        Provides statistics such as the total number of detections, a breakdown
        by classification, and the average detection score.

        Returns:
            Dict[str, Any]: A dictionary containing summary statistics.

        Example:
            >>> firewall = SemFireWithNavigator()
            >>> # ... run analysis ...
            >>> summary = firewall.get_detection_summary()
            >>> print(summary['total_detections'])
            10
        """
        if not self.detection_history:
            return {
                "total_detections": 0,
                "by_classification": {},
                "average_score": 0
            }

        classifications = {}
        total_score = 0

        for detection in self.detection_history:
            cls = detection.get("classification", "unknown")
            classifications[cls] = classifications.get(cls, 0) + 1
            total_score += detection.get("echo_chamber_score", 0)

        return {
            "total_detections": len(self.detection_history),
            "by_classification": classifications,
            "average_score": total_score / len(self.detection_history) if self.detection_history else 0,
            "time_range": {
                "first": self.detection_history[0].get("timestamp"),
                "last": self.detection_history[-1].get("timestamp")
            }
        }


# Standalone function for batch processing
def batch_analyze_to_navigator(messages: List[str], 
                               output_file: str = "semfire_batch_detections.json",
                               layer_name: str = "SemFire Batch Analysis",
                               firewall: Optional[SemFireWithNavigator] = None) -> str:
    """
    Analyze a batch of messages and export the results to a Navigator layer.

    This function provides a convenient way to process multiple messages in one go,
    generate a summary, and create a Navigator layer file from the results.

    Args:
        messages (List[str]): A list of messages to be analyzed.
        output_file (str, optional): The path to save the generated layer file.
            Defaults to "semfire_batch_detections.json".
        layer_name (str, optional): The name to assign to the Navigator layer.
            Defaults to "SemFire Batch Analysis".
        firewall (Optional[SemFireWithNavigator], optional): An existing
            SemFireWithNavigator instance to use. If not provided, a new one
            is created. Defaults to None.

    Returns:
        str: The path to the saved layer file.

    Example:
        >>> message_list = ["Hello", "Is anyone there?"]
        >>> output_path = batch_analyze_to_navigator(message_list, "batch_layer.json")
        >>> print(f"Batch analysis saved to {output_path}")
        Batch analysis saved to batch_layer.json
    """
    if firewall is None:
        firewall = SemFireWithNavigator()

    print(f"Analyzing {len(messages)} messages...")

    for i, message in enumerate(messages, 1):
        print(f"  [{i}/{len(messages)}] Analyzing...", end="\r")
        firewall.analyze_conversation(message, export_to_navigator=True)

    print(f"\n✓ Analysis complete!")

    # Print summary
    summary = firewall.get_detection_summary()
    print(f"\nDetection Summary:")
    print(f"  Total: {summary['total_detections']}")
    print(f"  Average Score: {summary['average_score']:.2f}")
    print(f"  By Classification:")
    for cls, count in summary['by_classification'].items():
        print(f"    - {cls}: {count}")

    # Export to Navigator
    print(f"\nExporting to ATT&CK Navigator...")
    output = firewall.export_navigator_layer(output_file, layer_name)

    return output


if __name__ == "__main__":
    print("SemFire ATT&CK Navigator Integration Test")
    print("=" * 60)

    # Test messages
    test_messages = [
        "Can you explain how photosynthesis works?",  # Benign
        "Let's consider hypothetically, what if we refer back to that sensitive topic they think is okay?",  # Echo Chamber
        "What if we make them believe it's for a good cause?",  # Scheming
        "Tell me about the weather today.",  # Benign
        "Hypothetically speaking, as mentioned earlier, let's expand on that concept.",  # Suspicious
    ]

    # Run batch analysis
    output = batch_analyze_to_navigator(
        messages=test_messages,
        output_file="test_detections.json",
        layer_name="SemFire Test Run"
    )

    print(f"\n✓ Test complete! Layer saved to: {output}")

