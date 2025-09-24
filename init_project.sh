#!/bin/bash

# Script to initialize a Python project with custom parameters
# Usage: ./init_project.sh "project-name" "Project description" "3.11" ["3.12"] ["topic1 topic2 topic3"]

set -e  # Exit on any error

# Function to display usage
usage() {
    echo "Usage: $0 <project-name> <description> <min-python-version> [max-python-version] [keywords]"
    echo ""
    echo "Arguments:"
    echo "  project-name         : Name of the project (e.g., 'my-awesome-project')"
    echo "  description          : Description of the project"
    echo "  min-python-version   : Minimum Python version (e.g., '3.11')"
    echo "  max-python-version   : Optional maximum Python version (not included, e.g., '3.12')"
    echo "  keywords             : Optional space-separated list of keywords/topics (e.g., 'python automation testing')"
    echo ""
    echo "Examples:"
    echo "  $0 'my-data-analyzer' 'A tool for analyzing data' '3.9'"
    echo "  $0 'web-scraper' 'A web scraping utility' '3.10' '3.12'"
    echo "  $0 'ml-toolkit' 'Machine learning toolkit' '3.11' '' 'machine-learning python ai'"
    exit 1
}

# Function to convert name to snake_case
to_snake_case() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | tr '-' '_'
}

# Function to find and replace in files
find_and_replace() {
    local find_pattern="$1"
    local replace_with="$2"
    local file_patterns=("*.py" "*.toml" "*.rst" "*.md" "*.txt" "*.ini" "*.yaml" "*.yml" "*.json")

    echo "  Replacing '$find_pattern' with '$replace_with'"

    # Find all relevant files and replace content
    for pattern in "${file_patterns[@]}"; do
        find . -name "$pattern" -type f -exec sed -i "s|$find_pattern|$replace_with|g" {} + 2>/dev/null || true
    done
}

# Function to rename directories recursively
rename_directories() {
    local old_name="$1"
    local new_name="$2"

    if [[ "$old_name" == "$new_name" ]]; then
        return 0
    fi

    echo "  Looking for directories named '$old_name' to rename to '$new_name'"

    # Find and rename directories from deepest to shallowest to avoid conflicts
    find . -name "$old_name" -type d | sort -r | while IFS= read -r dir; do
        parent_dir=$(dirname "$dir")
        new_path="$parent_dir/$new_name"

        if [[ ! -e "$new_path" ]]; then
            mv "$dir" "$new_path"
            echo "    ✓ Renamed $dir to $new_path"
        else
            echo "    ⚠ Warning: Cannot rename $dir - $new_path already exists"
        fi
    done
}

# Function to update keywords in pyproject.toml
update_keywords() {
    local keywords_string="$1"

    if [[ -z "$keywords_string" ]]; then
        echo "  No keywords provided, keeping existing keywords"
        return 0
    fi

    echo "  Updating keywords with: $keywords_string"

    # Convert space-separated keywords to TOML array format
    local keywords_array=""
    IFS=' ' read -ra KEYWORDS_ARRAY <<< "$keywords_string"

    for i in "${!KEYWORDS_ARRAY[@]}"; do
        if [[ $i -eq 0 ]]; then
            keywords_array="\"${KEYWORDS_ARRAY[i]}\""
        else
            keywords_array="$keywords_array, \"${KEYWORDS_ARRAY[i]}\""
        fi
    done

    # Update keywords line in pyproject.toml
    if [[ -f "pyproject.toml" ]]; then
        sed -i "s|^keywords = \[.*\]|keywords = [$keywords_array]|" pyproject.toml
        echo "  ✓ Keywords updated to: [$keywords_array]"
    else
        echo "  ⚠ Warning: pyproject.toml not found"
    fi
}

# Check arguments
if [[ $# -lt 3 || $# -gt 5 ]]; then
    echo "Error: Invalid number of arguments"
    usage
fi

PROJECT_NAME="$1"
DESCRIPTION="$2"
MIN_PYTHON="$3"
MAX_PYTHON="$4"
KEYWORDS="$5"

# Validate project name
if [[ ! "$PROJECT_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Error: Project name can only contain letters, numbers, hyphens, and underscores"
    exit 1
fi

# Validate Python versions
if [[ ! "$MIN_PYTHON" =~ ^[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Minimum Python version must be in format 'X.Y' (e.g., '3.11')"
    exit 1
fi

if [[ -n "$MAX_PYTHON" && ! "$MAX_PYTHON" =~ ^[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Maximum Python version must be in format 'X.Y' (e.g., '3.12')"
    exit 1
fi

# Convert project name to snake_case
SNAKE_CASE_NAME=$(to_snake_case "$PROJECT_NAME")

echo "=== Initializing Python Project ==="
echo "Project Name: $PROJECT_NAME"
echo "Snake Case Name: $SNAKE_CASE_NAME"
echo "Description: $DESCRIPTION"
echo "Min Python Version: $MIN_PYTHON"
echo "Max Python Version: ${MAX_PYTHON:-'Not specified'}"
echo "Keywords: ${KEYWORDS:-'Not specified'}"
echo ""

# Step 1: Update pyproject.toml description
echo "Step 1: Updating project description in pyproject.toml..."
if [[ -f "pyproject.toml" ]]; then
    # Update the description field
    sed -i "s|^description = .*|description = \"$DESCRIPTION\"|" pyproject.toml
    echo "  ✓ Description updated"
else
    echo "  ⚠ Warning: pyproject.toml not found"
fi

# Step 1b: Update keywords in pyproject.toml
echo ""
echo "Step 1b: Updating keywords in pyproject.toml..."
update_keywords "$KEYWORDS"

# Step 2: Replace Python version references
echo ""
echo "Step 2: Replacing Python version references..."
find_and_replace "3.x" "$MIN_PYTHON"
echo "  ✓ Python version references updated"

# Step 3: Update requires-python in pyproject.toml
echo ""
echo "Step 3: Updating requires-python in pyproject.toml..."
if [[ -f "pyproject.toml" ]]; then
    if [[ -n "$MAX_PYTHON" ]]; then
        # Set range with maximum version (not included)
        REQUIRES_PYTHON=">=$MIN_PYTHON, <$MAX_PYTHON"
    else
        # Set only minimum version
        REQUIRES_PYTHON=">=$MIN_PYTHON"
    fi

    sed -i "s|^requires-python = .*|requires-python = \"$REQUIRES_PYTHON\"|" pyproject.toml
    echo "  ✓ requires-python set to: $REQUIRES_PYTHON"
else
    echo "  ⚠ Warning: pyproject.toml not found"
fi

# Step 4: Get current project name from pyproject.toml
echo ""
echo "Step 4: Replacing project name references..."
CURRENT_PROJECT_NAME=""
CURRENT_SNAKE_NAME=""

if [[ -f "pyproject.toml" ]]; then
    CURRENT_PROJECT_NAME=$(grep '^name = ' pyproject.toml | sed 's/^name = "\([^"]*\)".*/\1/')
    CURRENT_SNAKE_NAME=$(to_snake_case "$CURRENT_PROJECT_NAME")
    echo "  Current project name: $CURRENT_PROJECT_NAME"
    echo "  Current snake case name: $CURRENT_SNAKE_NAME"
fi

# Replace project names throughout the project
if [[ -n "$CURRENT_PROJECT_NAME" && "$CURRENT_PROJECT_NAME" != "$PROJECT_NAME" ]]; then
    find_and_replace "$CURRENT_PROJECT_NAME" "$PROJECT_NAME"
fi

if [[ -n "$CURRENT_SNAKE_NAME" && "$CURRENT_SNAKE_NAME" != "$SNAKE_CASE_NAME" ]]; then
    find_and_replace "$CURRENT_SNAKE_NAME" "$SNAKE_CASE_NAME"
fi

# Also replace any generic placeholders if they exist
find_and_replace "my-package" "$PROJECT_NAME"
find_and_replace "my_package" "$SNAKE_CASE_NAME"

echo "  ✓ Project name references updated"

# Step 5: Update pyproject.toml project name
echo ""
echo "Step 5: Updating project name in pyproject.toml..."
if [[ -f "pyproject.toml" ]]; then
    sed -i "s|^name = .*|name = \"$PROJECT_NAME\"|" pyproject.toml
    echo "  ✓ Project name in pyproject.toml updated"
fi

# Step 6: Rename directories throughout the project
echo ""
echo "Step 6: Renaming directories throughout the project..."

# Rename directories based on the current project name
if [[ -n "$CURRENT_SNAKE_NAME" && "$CURRENT_SNAKE_NAME" != "$SNAKE_CASE_NAME" ]]; then
    rename_directories "$CURRENT_SNAKE_NAME" "$SNAKE_CASE_NAME"
fi

# Also handle common placeholder directory names
rename_directories "package_name" "$SNAKE_CASE_NAME"
rename_directories "my_package" "$SNAKE_CASE_NAME"
rename_directories "test_package" "$SNAKE_CASE_NAME"

# Handle specific common patterns for source and test directories
if [[ -d "src/package_name" ]]; then
    mv "src/package_name" "src/$SNAKE_CASE_NAME"
    echo "  ✓ Renamed src/package_name to src/$SNAKE_CASE_NAME"
fi

if [[ -d "tests/test_package_name" ]]; then
    mv "tests/test_package_name" "tests/$SNAKE_CASE_NAME"
    echo "  ✓ Renamed tests/test_package_name to tests/$SNAKE_CASE_NAME"
fi

echo "  ✓ Directory renaming complete"

# Step 7: Update setuptools_scm write_to path
echo ""
echo "Step 7: Updating setuptools_scm configuration..."
if [[ -f "pyproject.toml" ]]; then
    sed -i "s|write_to = \"src/.*/|write_to = \"src/$SNAKE_CASE_NAME/|" pyproject.toml
    echo "  ✓ setuptools_scm write_to path updated"
fi

echo ""
echo "=== Project Initialization Complete! ==="
echo ""
echo "Summary of changes:"
echo "  • Project name: $PROJECT_NAME"
echo "  • Package name: $SNAKE_CASE_NAME"
echo "  • Description: $DESCRIPTION"
echo "  • Python version: $MIN_PYTHON$([ -n "$MAX_PYTHON" ] && echo " (max: $MAX_PYTHON)")"
echo "  • requires-python: $REQUIRES_PYTHON"
echo "  • Keywords: ${KEYWORDS:-'None specified'}"
echo "  • Renamed directories to match new package name"
echo ""
echo "Next steps:"
echo "  1. Review the changes made to your files and directories"
echo "  2. Update any URLs, author information, and other project-specific details"
echo "  3. Install dependencies: pip install -e .[dev]"
echo "  4. Run tests: pytest"
echo ""
