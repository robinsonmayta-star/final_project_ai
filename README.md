# Proyecto Final: Ecosistema ETL para Workloads de Inteligencia Artificial
**Autor:** Robinson Mayta Calderón
**Programa:** Certificación de Ingeniero de Datos de IA
**Curso:** Procesos ETL para Workloads de AI

---

## 1. Descripción del Proyecto
Este proyecto es una solución técnica avanzada que integra **Deep Learning (YOLOv8)**, **Visión por Computadora (OpenCV)** y **Big Data (Hadoop/Hive)**. El objetivo es procesar flujos de datos no estructurados provenientes de imágenes y videos para convertirlos en activos analíticos estructurados.

La arquitectura se fundamenta en la **separación estricta de dos sistemas independientes**:
*   **Sistema 1 (IA)**: Captura e inferencia en tiempo real, generando una capa de staging local (CSV).
*   **Sistema 2 (ETL)**: Limpieza, transformación y carga batch hacia un ecosistema de Big Data.

---

## 2. Organización y Estructura Detallada del Repositorio
Para mantener el orden de ingeniería, el proyecto sigue esta jerarquía de directorios (Base del Proyecto):

```text
~/final_project_ai/
├── codigo/                 # Carpeta Raíz del Proyecto de Robinson
│   ├── config.env          # Configuración Global (IA, Thresholds, Paths).
│   ├── Makefile            # Orquestador: setup, lint, test, classify, etl.
│   ├── requirements.txt    # Dependencias del Entorno Virtual.
│   ├── README.md           # Documentación Maestra (Este archivo).
│   ├── data/               # Ciclo de vida del dato
│   │   ├── raw/            # Datos de Ingesta (20 fotos y 2 videos propios)
│   │   └── staging/        # Almacenamiento temporal de resultados de IA.
│   ├── src/                # Lógica del Sistema
│   │   ├── classification.py # Sistema 1: Motor de Inferencia IA.
│   │   ├── etl_batch.py      # Sistema 2: Proceso ETL Batch a Hive.
│   │   ├── utils/            # Librerías auxiliares (Cámara, Color, DB).
│   │   └── sql/              # DDL de Hive y Consultas Analíticas.
│   ├── tests/              # Calidad: Pruebas unitarias para scripts .py.
│   └── logs/               # Histórico de logs y base de datos local.
├── ambiente/               # Entorno Virtual Python (venv).
├── hadoopdata/             # Persistencia física de HDFS.
└── logs/                   # Logs generales de servicios de Hadoop/Hive.
```

---

## 3. Requisitos de Infraestructura y Software

### 3.1 Requisitos de Software
*   **Sistema Operativo**: Ubuntu 24.04 en WSL2.
*   **Python**: Versión 3.12 (Se escaló para mejor compatibilidad con YOLOv8 en WSL2).
*   **Servicios Big Data**: Apache HDFS y Apache Hive (Metastore/HiveServer2).

### 3.2 Verificación de Requisitos (Comandos Linux)
Ejecute estos comandos para demostrar que el entorno está correctamente configurado:
```bash
# 1. Verificar Hadoop (Big Data Core)
hadoop version

# 2. Verificar Hive (Data Warehouse)
hive --version

# 3. Verificar Python (Motor de IA)
python3 --version

# 4. Verificar Java (El "corazón" de Hadoop/Hive)
java -version

# 5. Verificar que los servicios están CORRIENDO
jps
```

## 4. Guía de Arranque de Infraestructura (Paso a Paso)

### 4.0 Protocolo de Limpieza y Apagado (Paso 0)
Para garantizar una demostración impecable, siga este orden (los servicios deben estar encendidos para limpiar el clúster):

**1. Limpieza de Datos (Con servicios activos):**
```bash
# Limpieza Local
cd ~/final_project_ai/codigo && make clean

# Purga de Clúster (HDFS y Hive)
/usr/local/hadoop/bin/hdfs dfs -rm -r -f /user/user/final_project/detections/*
/usr/local/hadoop/bin/hdfs dfs -rm -r -f /user/hive/warehouse/ai_data_db.db/detections/*
beeline -u jdbc:hive2:// -n user -e "TRUNCATE TABLE ai_data_db.detections;"
```

**2. Apagado Seguro y Liberación de Recursos:**
```bash
/usr/local/hadoop/sbin/stop-yarn.sh
/usr/local/hadoop/sbin/stop-dfs.sh
pkill -f HiveMetaStore
killall -9 java
# Eliminar bloqueos de base de datos
find /home/user -name "*.lck" -delete
```

### 4.1 Encendido de Servicios
1.  **Iniciar Hadoop (HDFS)**: `/usr/local/hadoop/sbin/start-dfs.sh`
2.  **Iniciar YARN (Procesamiento)**: `/usr/local/hadoop/sbin/start-yarn.sh`
3.  **Iniciar Hive Metastore**:
    ```bash
    # IMPORTANTE: Usar Java 8 para estabilidad en Hive 4.0.1
    export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
    hive --service metastore &
    ```
4.  **Verificación**: Espere 15 segundos y ejecute `jps`. Debe ver: *NameNode, DataNode, ResourceManager, NodeManager, RunJar*.

---

---

## 5. Guía de Ejecución del Pipeline (Escenarios de Uso)
Primero, diríjase a la carpeta raíz del código:
```bash
cd ~/final_project_ai/codigo
```

### Escenario A: Entrega Final / Reinicio Total (Recomendado para Sustentación)
Utilice este comando si desea limpiar todo el historial de staging y ejecutar el pipeline desde cero para demostrar el flujo completo.
*   **Comando**: `make all`
*   **Efecto**: Procesa el dataset y carga la data limpia a Hive.

### Escenario B: Modo Producción (Escalabilidad / Agregar Nuevos Datos)
Utilice esta lógica si ya tiene datos en Hive y desea **agregar nuevas imágenes o videos** a la carpeta `data/raw/` sin borrar lo que ya existe.
*   **Comando**: `make classify && make etl`
*   **Efecto**: El sistema detectará los nuevos archivos. El motor ETL aplicará el **filtro de duplicados** por `detection_id`, cargando a Hive únicamente los registros nuevos.

### Opción C: Auditoría Paso a Paso
Si desea ejecutar cada fase del Makefile de forma individual:
1.  **`make setup`**: Configuración de entorno.
2.  **`make lint`**: Validación de calidad (Pylint 10/10).
3.  **`make test`**: Ejecución de pruebas unitarias.
4.  **`make classify`**: Inferencia de IA.
5.  **`make etl`**: Procesamiento Batch y carga a Hive.

---

## 5. Lógica de Ingeniería y Valor Agregado

### 5.1 Estrategia Contra Datos Duplicados (Requisito Imperativo)
El sistema emplea un mecanismo de sincronización de dos niveles:
*   **Detection ID Único**: Filtrado en el DataFrame de Python antes de la carga a Hive.
*   **Mecanismo de Checkpoints**: Los archivos CSV procesados se mueven de `staging/` a `processed/`, garantizando que cada registro entre al clúster una sola vez.

### 5.2 Aportes
*   **Configuración Desacoplada (`config.env`)**: Parametrización dinámica del modelo y umbrales sin modificar código.
*   **Orquestación End-to-End**: Se extendió el Makefile base para gestionar el flujo completo de datos.

---

## 6. Cumplimiento de Rúbrica Técnica
*   **Documentación de Código (Sección 3)**: Todo el código fuente (`.py`) utiliza **Docstrings** y comentarios lógicos descriptivos.
*   **Extracción Enriquecida (Sección 6)**: Extracción de 25+ atributos incluyendo geometría, regiones y colores RGB (OpenCV).
*   **Consultas Analíticas (Sección 9)**: Se incluyen las 5 consultas obligatorias en la carpeta `src/sql/`.

---

---

## 7. Guía de Validación Analítica para Sustentación (Paso a Paso)

Esta sección documenta el procedimiento oficial para demostrar los resultados del pipeline ETL.

### Paso 1: Confirmar datos en el Warehouse de Hadoop (HDFS)
```bash
/usr/local/hadoop/bin/hdfs dfs -ls /user/hive/warehouse/ai_data_db.db/detections/
```
> Nota: Apache Hive gestiona el ciclo de vida del dato moviendo los archivos procesados a su Warehouse interno.

### Paso 1.1: Verificar estructura de la tabla (28 Atributos)
Demuestre el esquema técnico diseñado para la analítica:
```bash
beeline -u jdbc:hive2:// -n user -e "DESCRIBE ai_data_db.detections;"
```

### Paso 1.2: Vista Previa de Datos (Primeros 10 registros)
Muestre la data real ya procesada en el clúster:
```bash
beeline -u jdbc:hive2:// -n user -e "SELECT label, confidence, dominant_color_name, ingestion_date FROM ai_data_db.detections LIMIT 10;"
```

### Paso 2: Ejecutar consultas analíticas vía Beeline
Debido a una limitación conocida del entorno, todas las consultas deben ejecutarse utilizando el modo embebido de Beeline. A continuación, se presentan las consultas analíticas obligatorias.

### Paso 3: Las 5 Consultas Obligatorias de la Rúbrica

**Consulta 1: Conteo de objetos por clase**
```bash
beeline -u jdbc:hive2:// -n user -e "SELECT label, COUNT(*) as total FROM ai_data_db.detections GROUP BY label ORDER BY total DESC;"
```

**Consulta 2: Análisis de personas por fuente de video**
```bash
beeline -u jdbc:hive2:// -n user -e "SELECT source_id, COUNT(*) as total FROM ai_data_db.detections WHERE label='person' AND source_type='video' GROUP BY source_id;"
```

**Consulta 3: Ventanas temporales de 10 segundos**
```bash
beeline -u jdbc:hive2:// -n user -e "SELECT source_id, FLOOR(timestamp_sec/10) as lote, COUNT(*) as total FROM ai_data_db.detections WHERE source_type='video' GROUP BY source_id, FLOOR(timestamp_sec/10);"
```

**Consulta 4: Objetos con mayor confianza promedio**
```bash
beeline -u jdbc:hive2:// -n user -e "SELECT label, ROUND(AVG(confidence),3) as conf_promedio FROM ai_data_db.detections GROUP BY label ORDER BY conf_promedio DESC;"
```

**Consulta 5: Total de registros procesados**
```bash
beeline -u jdbc:hive2:// -n user -e "SELECT COUNT(*) as total_registros, COUNT(DISTINCT source_id) as total_fuentes FROM ai_data_db.detections;"
```

---

---

## 8. Nota Técnica: HiveServer2 en WSL2 (Comportamiento Documentado)

### 9.1 Bloqueo del Puerto TCP 10000
En entornos WSL2 con **Hadoop 3.4.2** y **Hive 4.0.1**, el servicio `HiveServer2` puede iniciar correctamente (generando *Hive Session ID*) pero **no llegar a abrir el puerto TCP 10000** para conexiones externas. Este comportamiento se manifiesta como:
```
Error: java.net.ConnectException: Connection refused (state=08S01,code=0)
```

**Causa Técnica Identificada**: El proceso de inicialización del servidor Thrift se bloquea internamente durante la fase de configuración del `ConfigurationScheduler` de Log4j2, impidiendo que el listener TCP se active. Este es un comportamiento conocido en la capa de virtualización de red de Windows.

### 9.2 Dependencia Crítica de YARN
Para que las consultas que utilizan funciones de agregación (`GROUP BY`, `COUNT`, `AVG`) funcionen, es **obligatorio** que el motor YARN esté activo (`start-yarn.sh`). Sin YARN, los jobs de MapReduce se quedarán en estado *PENDING* indefinidamente, ya que no habrá un ResourceManager para asignar los recursos del clúster.

### 9.3 Solución Implementada (Beeline Embedded)
Se utiliza el **modo de conexión embebida de Beeline** (`jdbc:hive2://` sin host ni puerto), que conecta directamente al Metastore Derby sin depender del puerto 10000. Esto garantiza estabilidad total mediante Java 8.

```bash
# Asegurar que NO haya ningún proceso HiveServer2 corriendo
killall -9 java
/usr/local/hadoop/sbin/start-dfs.sh
/usr/local/hadoop/sbin/start-yarn.sh # Motor de procesamiento de Big Data (Obligatorio)

---

## 9. Material de Sustentación y Entregables
*   **Video Explicativo**: [Enlace aquí]
*   **Dataset Propio**: 20 imágenes y 2 videos capturados por el autor en `data/raw/`.
*   **Guía Base**: `GUIA_PROYECTO_FINAL_ES.md` adjunta en la raíz.

---
**Robinson Mayta Calderón - Ingeniero de Datos de IA**
