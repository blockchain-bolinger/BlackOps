#!/bin/bash
read -p "Framework komplett deinstallieren? (yes/NO): " confirm
if [ "$confirm" = "yes" ]; then
    rm -rf venv logs/* tmp/* backups/*
    echo "Deinstallation abgeschlossen (Konfigurationsdateien bleiben erhalten)."
else
    echo "Abgebrochen."
fi
