#!/bin/bash
# post-create script

# Prepare pre-commit
if [ -d ".git" ]; then
  if [ -f ".pre-commit-config.yaml" ] || [ -f ".pre-commit-config.yml" ]; then
    echo "Setting up pre-commit hooks..."
    prek install --install-hooks
  else
    echo "No .pre-commit-config.yaml found. Skipping pre-commit setup."
  fi
else
  echo "No git repository found. Skipping pre-commit setup."
fi
