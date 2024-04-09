#!/bin/bash

# Check if the APK file path is provided as a command-line argument
if [ $# -ne 1 ]; then
  echo "Usage: $0 <APK_FILE>"
  exit 1
fi

APK_FILE="$1"
APK_NAME=$(basename -- "$APK_FILE")
APK_NAME_NO_EXT="${APK_NAME%.*}"
OUTPUT_DIR="out"
PERMISSIONS_FILE="$APK_NAME_NO_EXT"_permissions.txt

# Step 1: Ensure the output directory exists and is empty
if [ -d "$OUTPUT_DIR" ]; then
  rm -r "$OUTPUT_DIR"
fi

# Step 2: Decompile the APK using apktool
apktool d -o "$OUTPUT_DIR" "$APK_FILE"

# Check if apktool decompilation was successful
if [ $? -ne 0 ]; then
  echo "Error decompiling APK."
  exit 1
fi

# Step 3: Extract and save permissions to a file
MANIFEST_FILE="$OUTPUT_DIR/AndroidManifest.xml"

# Use awk to extract permissions and save to the file
awk '/android.permission/ {gsub(/.*android.permission./, "", $0); gsub(/".*/, "", $0); print $0}' "$MANIFEST_FILE" > "$PERMISSIONS_FILE"

# Display the permissions
echo "Permissions: $PERMISSIONS_FILE"
cat "$PERMISSIONS_FILE"

# Step 4: Clean up the temporary directory
rm -r "$OUTPUT_DIR"

# Exit successfully
exit 0

