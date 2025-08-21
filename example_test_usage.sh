#!/bin/bash

# Example script showing how to run the Docker test container

echo "🐳 Monopoly Deal Docker Test Container Examples"
echo "================================================"

echo ""
echo "1. Run tests using Docker Compose (recommended):"
echo "   docker compose --profile test run --rm test"

echo ""
echo "2. Run tests with database support:"
echo "   docker compose up --build -d db"
echo "   docker compose --profile test run --rm test"
echo "   docker compose down"

echo ""
echo "3. Build and run test container manually:"
echo "   docker build -f Dockerfile.test -t monopoly-test ."
echo "   docker run --rm monopoly-test"

echo ""
echo "4. Run tests locally (no Docker):"
echo "   ./run_tests.sh"

echo ""
echo "5. Use minimal test container (if networking issues):"
echo "   docker compose --profile test-minimal run --rm test-minimal"

echo ""
echo "For more details, see DOCKER_TESTING.md"