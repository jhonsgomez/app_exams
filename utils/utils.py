from django.utils.crypto import get_random_string
from datetime import datetime


def generate_unique_filename(file):
    # Obtener la extensión del archivo original
    ext = file.name.split(".")[-1]  # Obtener la extensión del archivo

    # Generar un nombre único basado en el tiempo actual y una cadena aleatoria
    random_str = get_random_string(10)  # 10 caracteres aleatorios
    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )  # Usamos el timestamp como base para asegurar unicidad

    # Crear el nombre único combinando los elementos
    unique_filename = f"{timestamp}_{random_str}.{ext}"

    return unique_filename
