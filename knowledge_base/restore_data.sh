#!/bin/bash
# This script moves the original data back alongside the new data once ingestion is complete.
cd "/Users/fahadiqbal/Documents/Latest_Codes/Islamic work/Islamic AI Agent/knowledge_base"

if [ -d "data_old" ]; then
    echo "Restoring original data from data_old to data..."
    mv data_old/* data/ 2>/dev/null
    rmdir data_old
    echo "Done! The knowledge base now has all files together."
else
    echo "No data_old folder found. Restoration might have already occurred."
fi
