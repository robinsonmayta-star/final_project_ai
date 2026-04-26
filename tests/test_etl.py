import pytest
import pandas as pd
import os

# Mapeo de etiquetas para validación de traducción
LABEL_MAP = {"person": "Persona", "car": "Vehiculo"}

def test_label_translation():
    """Valida que el diccionario de traducción funcione correctamente"""
    test_labels = ["person", "car", "unknown"]
    translated = [LABEL_MAP.get(l, l.capitalize()) for l in test_labels]
    assert translated == ["Persona", "Vehiculo", "Unknown"]

def test_confidence_filtering():
    """Valida la lógica de filtrado por umbral de confianza"""
    data = {'confidence': [0.1, 0.5, 0.9]}
    df = pd.DataFrame(data)
    filtered_df = df[df['confidence'] > 0.4]
    assert len(filtered_df) == 2
    assert filtered_df['confidence'].min() > 0.4

def test_staging_directory_structure():
    """Verifica la integridad de la estructura de carpetas del proyecto"""
    base_path = "/home/user/final_project_ai/codigo/data"
    assert os.path.exists(base_path), "La carpeta de datos no existe en la ruta raíz"
    assert os.path.exists(os.path.join(base_path, "raw")), "La carpeta raw no existe"
