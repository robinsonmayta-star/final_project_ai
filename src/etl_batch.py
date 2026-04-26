import os
import glob
import subprocess
from datetime import datetime
import pandas as pd

# Configuración de Rutas de Almacenamiento HDFS/Hive
STAGING_BASE_DIR = "data/staging"
PROCESSED_DIR = "data/staging/processed"
HDFS_PATH = "/user/user/final_project/detections"
HIVE_BIN = "/usr/local/hive/bin/beeline -u jdbc:hive2:// -n user"
HDFS_BIN = "/usr/local/hadoop/bin/hdfs"

def run_command(cmd):
    """Ejecuta un comando de sistema y maneja errores específicos"""
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e: # pylint: disable=broad-exception-caught
        print(f"Error ejecutando comando: {cmd}\n{e}")
        return False

def run_etl():
    """Proceso ETL Batch """
    print("--- Iniciando Pipeline de Procesamiento Batch - Data Engineering ---")
    
    # Asegurar directorios
    run_command(f"{HDFS_BIN} dfs -mkdir -p {HDFS_PATH}")

    today = datetime.now().strftime("%Y%m%d")
    daily_staging = os.path.join(STAGING_BASE_DIR, today)
    
    if not os.path.exists(daily_staging):
        print(f"No hay datos para procesar hoy ({today}).")
        return

    csv_files = glob.glob(os.path.join(daily_staging, "*.csv"))
    for csv_file in csv_files:
        print(f"Procesando: {os.path.basename(csv_file)}")
        
        # 1. Extracción y Limpieza de Duplicados en Python (Sección 7.2)
        df = pd.read_csv(csv_file)
        df = df.drop_duplicates(subset=['detection_id'])
        
        temp_csv = f"/tmp/etl_{os.path.basename(csv_file)}"
        df.to_csv(temp_csv, index=False, header=False)

        # 2. Carga a HDFS
        if run_command(f"{HDFS_BIN} dfs -put -f {temp_csv} {HDFS_PATH}"):
            # 3. Carga a Hive
            hive_cmd = f"{HIVE_BIN} -e \"LOAD DATA INPATH '{HDFS_PATH}/etl_{os.path.basename(csv_file)}' INTO TABLE ai_data_db.detections;\""
            if run_command(hive_cmd):
                print(f"   [OK] {os.path.basename(csv_file)} cargado en Hive.")
                os.makedirs(PROCESSED_DIR, exist_ok=True)
                os.rename(csv_file, os.path.join(PROCESSED_DIR, os.path.basename(csv_file)))
        
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

    print("--- ETL Finalizado con éxito ---")

if __name__ == "__main__":
    run_etl()
