-- Esquema de Tabla Final - Proyecto Robinson Mayta Calderón
-- Alineado con la Sección 8 de los requerimientos

CREATE DATABASE IF NOT EXISTS ai_data_db;
USE ai_data_db;

CREATE TABLE IF NOT EXISTS detections (
  source_type           STRING,
  source_id             STRING,
  frame_number          INT,
  class_id              INT,
  class_name            STRING,
  confidence            DOUBLE,
  x_min                 DOUBLE,
  y_min                 DOUBLE,
  x_max                 DOUBLE,
  y_max                 DOUBLE,
  width                 DOUBLE,
  height                DOUBLE,
  area_pixels           DOUBLE,
  frame_width           INT,
  frame_height          INT,
  bbox_area_ratio       DOUBLE,
  center_x              DOUBLE,
  center_y              DOUBLE,
  center_x_norm         DOUBLE,
  center_y_norm         DOUBLE,
  position_region       STRING,
  dominant_color_name   STRING,
  dom_r                 INT,
  dom_g                 INT,
  dom_b                 INT,
  timestamp_sec         DOUBLE,
  ingestion_date        STRING,
  detection_id          STRING
)
STORED AS PARQUET;
