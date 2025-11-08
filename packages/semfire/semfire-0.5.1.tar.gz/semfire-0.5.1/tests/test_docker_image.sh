#!/bin/bash

# Test script for the SemFire CLI Docker image.
# This script builds the image and runs a series of functional tests against it.

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the image name and tag for testing
IMAGE_NAME="semfire-cli"
TAG="ci-test"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo "--- Building Docker image: ${FULL_IMAGE_NAME} ---"
docker build -t "${FULL_IMAGE_NAME}" .

echo -e "\n--- Running Docker Image Tests ---"

# Test 1: Default command (--help)
# The default CMD is to show the help message.
echo "Test 1: Running default command (should display help)..."
if docker run --rm "${FULL_IMAGE_NAME}" | grep -q "usage: cli.py"; then
    echo "✅ Test 1 PASSED"
else
    echo "❌ Test 1 FAILED"
    exit 1
fi

# Test 2: Analyze command with direct argument
# This tests the basic analysis functionality.
echo "\nTest 2: Running 'analyze' command with a string argument..."
if docker run --rm "${FULL_IMAGE_NAME}" python -m src.cli analyze "this is a test" | grep -q "HeuristicDetector"; then
    echo "✅ Test 2 PASSED"
else
    echo "❌ Test 2 FAILED"
    exit 1
fi

# Test 3: Analyze command with piped input (stdin)
# This tests the container's ability to handle piped input.
echo "\nTest 3: Running 'analyze' command with piped input..."
if echo "this is a piped test" | docker run --rm -i "${FULL_IMAGE_NAME}" python -m src.cli analyze --stdin | grep -q "HeuristicDetector"; then
    echo "✅ Test 3 PASSED"
else
    echo "❌ Test 3 FAILED"
    exit 1
fi

echo -e "\n--- All Docker Image Tests Passed Successfully ---"

# Optional: Cleanup the test image
# echo "\n--- Cleaning up test image ---"
# docker rmi "${FULL_IMAGE_NAME}"
