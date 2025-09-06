#!/bin/bash

# Script to rename files and update imports for Electric Load Forecasting project

echo "Starting file renaming and import updating process..."

# Create a backup of the original files
echo "Creating backup directory..."
mkdir -p backup_before_rename
cp -r Models/*.py server/*.py server/swag/*.py backup_before_rename/

# Rename mapping
declare -A file_mapping=(
  ["aws_arima.py"]="arima_forecaster.py"
  ["aws_rnn.py"]="rnn_forecaster.py"
  ["aws_smoothing.py"]="smoothing_forecaster.py"
  ["aws.py"]="scheduler.py"
  ["pdq_search.py"]="arima_tuner.py"
)

# Rename files
echo "Renaming files..."
cd Models
for old_name in "${!file_mapping[@]}"; do
  new_name="${file_mapping[$old_name]}"
  if [ -f "$old_name" ]; then
    echo "Renaming $old_name to $new_name"
    git mv "$old_name" "$new_name" 2>/dev/null || mv "$old_name" "$new_name"
  else
    echo "Warning: $old_name not found"
  fi
done
cd ..

# Update imports in Python files
echo "Updating import statements..."

# Function to update imports in a file
update_imports() {
  local file=$1
  
  if [ -f "$file" ]; then
    echo "Checking imports in $file"
    
    # Update each import statement
    for old_name in "${!file_mapping[@]}"; do
      old_module=$(basename "$old_name" .py)
      new_module=$(basename "${file_mapping[$old_name]}" .py)
      
      # Various import patterns to replace
      sed -i "s/from $old_module import/from $new_module import/g" "$file"
      sed -i "s/import $old_module as/import $new_module as/g" "$file"
      sed -i "s/import $old_module$/import $new_module/g" "$file"
      sed -i "s/$old_module\\./$new_module./g" "$file"
    done
  fi
}

# Find and update all Python files in the project
find . -name "*.py" -not -path "./backup_before_rename/*" | while read file; do
  update_imports "$file"
done

# Also check Jupyter notebooks for imports
find . -name "*.ipynb" -not -path "./backup_before_rename/*" | while read notebook; do
  echo "Checking imports in notebook: $notebook"
  
  # For each old module name, update to new module name in notebook
  for old_name in "${!file_mapping[@]}"; do
    old_module=$(basename "$old_name" .py)
    new_module=$(basename "${file_mapping[$old_name]}" .py)
    
    # Use sed to replace in the JSON content of notebooks
    # This is a simple approach and might need adjustments for complex notebooks
    sed -i "s/import $old_module/import $new_module/g" "$notebook"
    sed -i "s/from $old_module import/from $new_module import/g" "$notebook"
    sed -i "s/$old_module\\./$new_module./g" "$notebook"
  done
done

echo "File renaming and import updating completed!"
echo "A backup of the original files has been saved to backup_before_rename/"