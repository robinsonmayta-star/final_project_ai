# Makefile - Proyecto Final Robinson Mayta Calderón
# Automatización de Ecosistema IA + ETL

PYTHON = ../ambiente/etl_ai_lab/bin/python
PIP = ../ambiente/etl_ai_lab/bin/pip
SRC_DIR = src
TEST_DIR = tests

setup:
	@echo "--- Preparando Entorno de Ingeniería ---"
	@mkdir -p data/raw/images data/raw/videos data/staging/processed logs
	@$(PIP) install pylint pytest pandas ultralytics opencv-python
	@echo "[OK] Dependencias de calidad instaladas."

lint:
	@echo "--- Ejecutando Análisis Estático (Pylint) ---"
	@$(PYTHON) -m pylint $(SRC_DIR)/*.py --disable=C,R

test:
	@echo "--- Ejecutando Pruebas Unitarias (Pytest) ---"
	@$(PYTHON) -m pytest $(TEST_DIR)/

classify:
	@echo "--- Ejecutando Sistema de Clasificación (IA) ---"
	@$(PYTHON) $(SRC_DIR)/classification.py

etl:
	@echo "--- Ejecutando Sistema Batch / ETL (Hive) ---"
	@$(PYTHON) $(SRC_DIR)/etl_batch.py

all: setup lint test classify etl
	@echo "Pipeline completo ejecutado exitosamente."

clean:
	@echo "--- Limpiando Staging y Logs ---"
	@rm -rf data/staging/*
	@rm -f logs/*.log
	@mkdir -p data/staging/processed
