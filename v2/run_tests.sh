#!/bin/bash

echo "Running tests for Any-to-Any Conversion Studio v2..."
echo ""

# Run sources service tests
echo "Testing Sources Service..."
python -m tests.test_sources_service

echo ""
echo "Tests completed!"