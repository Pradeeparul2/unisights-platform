#!/bin/sh

# Directory containing JSON supervisor specs
SPEC_DIR="/supervisor_specs"

# Druid indexer API endpoint
DRUID_API="http://unisights-druid-coordinator:8081/druid/indexer/v1/supervisor"

if [ ! -d "$SPEC_DIR" ]; then
  echo "Error: Directory $SPEC_DIR does not exist"
  exit 1
fi

if ! ls "$SPEC_DIR"/*.json 2>/dev/null; then
  echo "Error: No JSON files found in $SPEC_DIR"
  exit 1
fi

for spec_file in "$SPEC_DIR"/*.json; do
  echo "Processing $spec_file..."

  if [ ! -r "$spec_file" ]; then
    echo "Error: Cannot read file $spec_file"
    continue
  fi

  response=$(curl --connect-timeout 10 --max-time 30 -s -o /tmp/response.txt -w "%{http_code}" -X POST -H "Content-Type: application/json" -d @"$spec_file" "$DRUID_API" || true)

  if [ "$response" -eq 200 ]; then
    echo "Successfully submitted $spec_file to Druid indexer"
  else
    echo "Failed to submit $spec_file. HTTP status code: $response"
    echo "Response details:"
    cat /tmp/response.txt
    rm -f /tmp/response.txt
    exit 1
  fi

  rm -f /tmp/response.txt
done

echo "Completed processing all JSON files in $SPEC_DIR"
