#!/bin/sh

echo "Inserting publico news"
python3 populate_db.py -f data/pt/publico/publico_km.json
python3 populate_db.py -f data/pt/publico/publico_lb.json

echo "Inserting observador news"
python3 populate_db.py -f data/pt/observador/observador_km.json
python3 populate_db.py -f data/pt/observador/observador_lb.json

echo "Inserting cnn news"
python3 populate_db.py -f data/en/cnn/cnn_km.json
python3 populate_db.py -f data/en/cnn/cnn_lb.json

echo "Inserting guardian news"
python3 populate_db.py -f data/en/guardian/guardian_km.json
python3 populate_db.py -f data/en/guardian/guardian_lb.json 

echo "Inserting topics data"
python3 populate_db.py -f data/topics.json
