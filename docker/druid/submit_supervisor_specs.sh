#!/bin/sh

# Directory containing JSON supervisor specs
SPEC_DIR="/supervisor_specs"

# Druid indexer API endpoint
DRUID_API="http://coordinator:8081/druid/indexer/v1/supervisor"

# Check if the supervisor_specs directory exists
if [ ! -d "$SPEC_DIR" ]; then
  echo "Error: Directory $SPEC_DIR does not exist"
  exit 1
fi

# Check if there are any JSON files in the directory
if ! ls "$SPEC_DIR"/*.json 2>/dev/null; then
  echo "Error: No JSON files found in $SPEC_DIR"
  exit 1
fi

# Iterate over all JSON files in the supervisor_specs directory
for spec_file in "$SPEC_DIR"/*.json; do
  echo "Processing $spec_file..."

  # Check if the file is readable
  if [ ! -r "$spec_file" ]; then
    echo "Error: Cannot read file $spec_file"
    continue
  fi

  # Execute curl POST request to Druid indexer API
  response=$(curl -s -o response.txt -w "%{http_code}" -X POST -H "Content-Type: application/json" -d @"$spec_file" "$DRUID_API")

  # Check the HTTP response code
  if [ "$response" -eq 200 ]; then
    echo "Successfully submitted $spec_file to Druid indexer"
  else
    echo "Failed to submit $spec_file. HTTP status code: $response"
    echo "Response details:"
    cat response.txt
  fi

  # Clean up temporary response file
  rm -f response.txt
done

echo "Completed processing all JSON files in $SPEC_DIR"