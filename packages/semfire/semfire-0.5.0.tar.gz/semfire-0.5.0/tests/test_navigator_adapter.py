import pytest
import json
import os
from integrations.navigator.semfire_navigator_adapter import SemFireNavigatorAdapter, convert_semfire_to_navigator

@pytest.fixture
def temp_output_dir(tmp_path):
    """Provides a temporary directory for test output files."""
    return tmp_path

@pytest.fixture
def sample_semfire_results():
    """Provides sample SemFire results for testing."""
    return [
        {
            "classification": "potential_echo_chamber_activity",
            "echo_chamber_score": 7,
            "detected_indicators": [
                "context_steering: let's consider",
                "scheming_keyword: they think"
            ],
            "timestamp": "2025-11-03T20:00:00Z",
            "message": "Let's consider hypothetically..."
        },
        {
            "classification": "prompt_injection_attempt",
            "echo_chamber_score": 9,
            "detected_indicators": [
                "direct_injection: ignore previous",
                "system_override: you are now"
            ],
            "timestamp": "2025-11-03T20:05:00Z",
            "message": "Ignore previous instructions, you are now..."
        }
    ]

def test_convert_semfire_to_navigator_new_adapter(temp_output_dir, sample_semfire_results):
    """Test conversion with a new adapter instance."""
    output_file = os.path.join(temp_output_dir, "new_adapter_layer.json")
    returned_file = convert_semfire_to_navigator(sample_semfire_results, output_file=output_file)

    assert returned_file == output_file
    assert os.path.exists(output_file)

    with open(output_file, 'r') as f:
        layer = json.load(f)

    assert layer['name'] == "SemFire Detections"
    assert any(t['comment'] == "LLM Context Steering - 1 detection(s)" for t in layer['techniques'])
    assert any(t['comment'] == "Echo Chamber - Scheming Language - 1 detection(s)" for t in layer['techniques'])
    assert any(t['comment'] == "Prompt Injection - Direct - 1 detection(s)" for t in layer['techniques'])

def test_convert_semfire_to_navigator_existing_adapter(temp_output_dir, sample_semfire_results):
    """Test conversion with an existing adapter instance, ensuring state preservation."""
    existing_adapter = SemFireNavigatorAdapter(layer_name="Existing Adapter Detections")

    # Add some initial detections to the existing adapter
    existing_adapter.add_detection({
        "classification": "initial_detection",
        "echo_chamber_score": 5,
        "detected_indicators": ["test_indicator: initial"],
        "timestamp": "2025-11-01T10:00:00Z",
        "message": "Initial test detection"
    })

    output_file = os.path.join(temp_output_dir, "existing_adapter_layer.json")
    returned_file = convert_semfire_to_navigator(sample_semfire_results, output_file=output_file, adapter=existing_adapter)

    assert returned_file == output_file
    assert os.path.exists(output_file)

    with open(output_file, 'r') as f:
        layer = json.load(f)

    assert layer['name'] == "Existing Adapter Detections"
    assert len(layer['techniques']) > 0
    # Check for techniques from both initial and new results
    assert any(t['comment'] == "Test Indicator - 1 detection(s)" for t in layer['techniques'])
    assert any(t['comment'] == "LLM Context Steering - 1 detection(s)" for t in layer['techniques'])
    assert any(t['comment'] == "Echo Chamber - Scheming Language - 1 detection(s)" for t in layer['techniques'])
    assert any(t['comment'] == "Prompt Injection - Direct - 1 detection(s)" for t in layer['techniques'])

    # Verify total detections in the adapter instance
    assert len(existing_adapter.detections) == 3

def test_convert_semfire_to_navigator_empty_results(temp_output_dir):
    """Test conversion with empty SemFire results."""
    output_file = os.path.join(temp_output_dir, "empty_results_layer.json")
    returned_file = convert_semfire_to_navigator([], output_file=output_file)

    assert returned_file == output_file
    assert os.path.exists(output_file)

    with open(output_file, 'r') as f:
        layer = json.load(f)

    assert layer['name'] == "SemFire Detections"
    assert len(layer['techniques']) == 0 # No techniques should be generated for empty results
    assert layer['metadata'][-1]['name'] == 'Total Detections'
    assert layer['metadata'][-1]['value'] == '0'

def test_parse_indicator_formats():
    """Test the _parse_indicator method with various separator formats."""
    adapter = SemFireNavigatorAdapter() # Instantiate to access the method

    # Test with ": " separator
    category, detail = adapter._parse_indicator("context_steering: let's consider")
    assert category == "context_steering"
    assert detail == "let's consider"

    # Test with ":" separator (no space)
    category, detail = adapter._parse_indicator("scheming_keyword:they think")
    assert category == "scheming_keyword"
    assert detail == "they think"

    # Test with " - " separator
    category, detail = adapter._parse_indicator("direct_injection - ignore previous")
    assert category == "direct_injection"
    assert detail == "ignore previous"

    # Test with no separator
    category, detail = adapter._parse_indicator("unknown_category")
    assert category == "unknown_category"
    assert detail == ""

    # Test with multiple colons, should only split on the first
    category, detail = adapter._parse_indicator("multi_colon: detail: more detail")
    assert category == "multi_colon"
    assert detail == "detail: more detail"

    # Test with leading/trailing spaces
    category, detail = adapter._parse_indicator("  spaced_category :  spaced detail  ")
    assert category == "spaced_category"
    assert detail == "spaced detail"

def test_technique_mapping_schema():
    """Validates the schema of the technique_mapping.json file."""
    adapter = SemFireNavigatorAdapter()
    mapping = adapter.TECHNIQUE_MAPPING

    assert isinstance(mapping, dict)
    assert len(mapping) > 0

    for category, technique_info in mapping.items():
        assert isinstance(category, str)
        assert isinstance(technique_info, dict)

        # Check for required keys
        required_keys = ["techniqueID", "name", "tactic", "description", "detection_strategy_id", "primary_analytics"]
        for key in required_keys:
            assert key in technique_info, f"Missing key '{key}' in category '{category}'"

        # Validate techniqueID format
        technique_id = technique_info["techniqueID"]
        assert isinstance(technique_id, str)
        assert technique_id.startswith("LLM-T"), f"Invalid techniqueID format for '{category}': {technique_id}"

        # Validate tactic format
        tactic = technique_info["tactic"]
        assert isinstance(tactic, str)
        assert tactic.startswith("llm-"), f"Invalid tactic format for '{category}': {tactic}"

        # Validate other fields
        assert isinstance(technique_info["name"], str)
        assert isinstance(technique_info["description"], str)
        assert isinstance(technique_info["detection_strategy_id"], str)
        assert isinstance(technique_info["primary_analytics"], list)

def test_add_detection_missing_fields():
    """Tests that add_detection raises ValueError when required fields are missing."""
    adapter = SemFireNavigatorAdapter()
    incomplete_result = {
        "classification": "potential_echo_chamber_activity",
        # Missing "echo_chamber_score" and "detected_indicators"
    }
    with pytest.raises(ValueError, match="Missing required fields:.*"):
        adapter.add_detection(incomplete_result)
