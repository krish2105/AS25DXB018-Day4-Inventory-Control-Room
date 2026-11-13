#!/usr/bin/env bash
# Copy the executed notebook's results from build/ into the repository folders and the web app.
set -euo pipefail
cd "$(dirname "$0")/.."
NB="AS25DXB018_Krishna_Mathur_Day4_Inventory_Management.ipynb"
mkdir -p notebook data outputs summary web/public/data
cp "build/$NB" notebook/
cp build/data/inventory_synthetic_data.csv data/
cp build/data/dashboard_data.json data/
rm -rf outputs && mkdir -p outputs && cp build/outputs/* outputs/
cp build/data/dashboard_data.json web/public/data/dashboard_data.json
[ -f build/AS25DXB018_Krishna_Mathur_Day4_Summary.pdf ] && cp build/AS25DXB018_Krishna_Mathur_Day4_Summary.pdf summary/ || true
echo "synced: notebook/ data/ outputs/ summary/ web/public/data/"
