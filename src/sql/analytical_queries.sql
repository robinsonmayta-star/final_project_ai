-- Consultas Analíticas para Validación de Datos
-- Autor: Robinson Mayta Calderón

USE ai_data_db;

-- 1. Conteo total de detecciones por etiqueta (Traducción aplicada)
SELECT label, COUNT(*) as total 
FROM detections 
GROUP BY label 
ORDER BY total DESC;

-- 2. Distribución de detecciones por tipo de fuente (Foto vs Video)
SELECT source_type, COUNT(*) as total 
FROM detections 
GROUP BY source_type;

-- 3. Análisis de confianza promedio por objeto detectado
SELECT label, AVG(confidence) as avg_conf 
FROM detections 
GROUP BY label 
HAVING avg_conf > 0.5;

-- 4. Conteo de objetos detectados en el video de alta confianza (2.mp4)
SELECT label, COUNT(*) as total 
FROM detections 
WHERE frame_id LIKE '%2.mp4%' OR source_type = 'local_video'
GROUP BY label;

-- 5. Identificación de colores predominantes en las personas detectadas
SELECT dominant_color, COUNT(*) as total 
FROM detections 
WHERE label = 'Persona' 
GROUP BY dominant_color;
