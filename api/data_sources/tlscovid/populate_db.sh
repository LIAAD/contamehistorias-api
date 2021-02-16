#!/bin/sh

echo "Inserting publico news"
python populate_db.py -f data/pt/publico/publico_km.json
python populate_db.py -f data/pt/publico/publico_lb.json

echo "Inserting observador news"
python populate_db.py -f data/pt/observador/observador_km.json
python populate_db.py -f data/pt/observador/observador_lb.json

echo "Inserting cnn news"
python populate_db.py -f data/en/cnn/cnn_km.json
python populate_db.py -f data/en/cnn/cnn_lb.json

echo "Inserting guardian news"
python populate_db.py -f data/en/guardian/guardian_km.json
python populate_db.py -f data/en/guardian/guardian_lb.json 

echo "Inserting topics data"
python populate_db.py -f data/topics.json
