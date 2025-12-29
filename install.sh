#!/bin/bash

# Financial Projections Module - Installation Script
# This script helps install the Financial Projections module into a Frappe/ERPNext site

set -e

echo "======================================"
echo "Financial Projections Module Installer"
echo "======================================"
echo ""

# Check if we're in a Frappe bench directory
if [ ! -f "common_site_config.json" ]; then
    echo "Error: This doesn't appear to be a Frappe bench directory."
    echo "Please run this script from your frappe-bench folder."
    exit 1
fi

# Get site name
echo "Available sites:"
ls -d sites/*/ | cut -d'/' -f2 | grep -v assets
echo ""
read -p "Enter site name: " SITE_NAME

if [ ! -d "sites/$SITE_NAME" ]; then
    echo "Error: Site $SITE_NAME not found."
    exit 1
fi

# Get module path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MODULE_PATH="$SCRIPT_DIR"

echo ""
echo "Installing Financial Projections module..."
echo "Site: $SITE_NAME"
echo "Module path: $MODULE_PATH"
echo ""

# Copy module to apps directory if not already there
if [ ! -d "apps/financial_projections" ]; then
    echo "Copying module to apps directory..."
    cp -r "$MODULE_PATH" apps/financial_projections
else
    echo "Module already exists in apps directory, updating..."
    rm -rf apps/financial_projections
    cp -r "$MODULE_PATH" apps/financial_projections
fi

# Add to apps.txt if not already there
if ! grep -q "financial_projections" "sites/$SITE_NAME/apps.txt"; then
    echo "Adding to site's apps.txt..."
    echo "financial_projections" >> "sites/$SITE_NAME/apps.txt"
fi

# Install the app
echo "Installing app on site..."
bench --site "$SITE_NAME" install-app financial_projections

# Run migrations
echo "Running migrations..."
bench --site "$SITE_NAME" migrate

# Clear cache
echo "Clearing cache..."
bench --site "$SITE_NAME" clear-cache

# Build assets
echo "Building assets..."
bench build --app financial_projections

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Restart your bench: bench restart"
echo "2. Login to your ERPNext site"
echo "3. Search for 'Financial Projection' to start creating projections"
echo ""
echo "For usage instructions, see README.md"
echo ""
