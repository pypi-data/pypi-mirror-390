"""
Image Utilities

Utility functions for handling images in LLM prompts.
"""

import hashlib
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests

from .image_schemas import ImageInput


def download_image_from_url(
    url: str,
    timeout: int = 30,
    max_size_mb: float = 20.0,
    cache_dir: str | None = None
) -> ImageInput:
    """
    Lädt ein Bild von einer URL herunter und erstellt ein ImageInput-Objekt.
    
    Args:
        url: URL des Bildes
        timeout: Timeout für den Download in Sekunden
        max_size_mb: Maximale Dateigröße in MB
        cache_dir: Optionales Cache-Verzeichnis für heruntergeladene Bilder
        
    Returns:
        ImageInput-Objekt mit den heruntergeladenen Bilddaten
        
    Raises:
        requests.RequestException: Bei Netzwerkfehlern
        ValueError: Bei ungültigen URLs oder zu großen Dateien
    """
    # URL validieren
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        raise ValueError(f"Ungültige URL: {url}")
    
    if parsed_url.scheme not in ['http', 'https']:
        raise ValueError(f"Nur HTTP/HTTPS URLs werden unterstützt: {url}")
    
    # Cache-Pfad bestimmen
    if cache_dir:
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        
        # Cache-Dateiname basierend auf URL-Hash
        url_hash = hashlib.md5(url.encode()).hexdigest()
        file_extension = _get_extension_from_url(url) or '.jpg'
        cache_file = cache_path / f"{url_hash}{file_extension}"
        
        # Prüfe ob bereits im Cache
        if cache_file.exists():
            return ImageInput(source=str(cache_file), mime_type=None, description=None, max_size_mb=None)
    
    try:
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        # Direkter GET mit Streaming - KEIN HEAD-Request
        headers = {'User-Agent': user_agents[0]} # Use the first user agent for now
        response = requests.get(url, stream=True, timeout=timeout, headers=headers)
        response.raise_for_status()
        
        # Content-Type sofort prüfen
        content_type = response.headers.get('content-type', '').lower()
        if content_type and not any(img_type in content_type for img_type in
                                  ['image/', 'application/octet-stream']):
            # Warnung, aber kein Fehler - Magic Bytes prüfen später
            pass
        
        # Streaming Download mit Größenüberwachung
        downloaded_size = 0
        max_size_bytes = max_size_mb * 1024 * 1024
        image_data = b''
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                downloaded_size += len(chunk)
                if downloaded_size > max_size_bytes:
                    raise ValueError(f"Bild zu groß: >{max_size_mb}MB")
                image_data += chunk
        
        # Magic Bytes Validierung (robuster als Content-Type)
        if not _validate_image_magic_bytes(image_data):
            raise ValueError("Keine gültigen Bilddaten erkannt")
        
        # In Cache speichern wenn gewünscht
        if cache_dir:
            with open(cache_file, 'wb') as f:
                f.write(image_data)
            return ImageInput(source=str(cache_file), mime_type=content_type, description=None, max_size_mb=None)
        
        return ImageInput(source=image_data, mime_type=content_type, description=None, max_size_mb=None)
        
    except requests.RequestException as e:
        raise requests.RequestException(f"Fehler beim Herunterladen von {url}: {e}") from e


def _get_extension_from_url(url: str) -> str | None:
    """Extrahiert die Dateierweiterung aus einer URL."""
    parsed = urlparse(url)
    path = Path(parsed.path)
    return path.suffix if path.suffix else None


def validate_image_format(image_input: ImageInput) -> bool:
    """
    Validiert das Bildformat durch Überprüfung der Magic Bytes.
    
    Args:
        image_input: ImageInput-Objekt zum Validieren
        
    Returns:
        True wenn das Format gültig ist
        
    Raises:
        ValueError: Wenn das Format nicht unterstützt wird
    """
    try:
        image_bytes = image_input.to_bytes()
    except Exception as e:
        raise ValueError(f"Kann Bilddaten nicht lesen: {e}") from e
    
    if len(image_bytes) < 8:
        raise ValueError("Bilddatei ist zu klein")
    
    # Magic Bytes für verschiedene Bildformate
    magic_bytes = {
        b'\xFF\xD8\xFF': 'image/jpeg',
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'GIF87a': 'image/gif',
        b'GIF89a': 'image/gif',
        b'RIFF': 'image/webp',  # Muss mit WEBP im Header kombiniert werden
        b'BM': 'image/bmp',
        b'II*\x00': 'image/tiff',
        b'MM\x00*': 'image/tiff',
    }
    
    # Prüfe Magic Bytes
    for magic, format_type in magic_bytes.items():
        if image_bytes.startswith(magic):
            # Spezielle Prüfung für WebP
            if format_type == 'image/webp':
                if b'WEBP' in image_bytes[8:12]:
                    return True
                else:
                    continue
            return True
    
    # SVG-Prüfung (textbasiert)
    try:
        text_content = image_bytes.decode('utf-8', errors='ignore')
        if '<svg' in text_content.lower() and 'xmlns' in text_content.lower():
            return True
    except Exception:
        pass
    
    raise ValueError("Nicht unterstütztes Bildformat")


def get_image_dimensions(image_input: ImageInput) -> tuple[int, int] | None:
    """
    Ermittelt die Bildabmessungen ohne externe Dependencies.
    
    Args:
        image_input: ImageInput-Objekt
        
    Returns:
        Tuple (width, height) oder None wenn nicht ermittelbar
    """
    try:
        image_bytes = image_input.to_bytes()
    except Exception:
        return None
    
    # Einfache Dimensionserkennung für gängige Formate
    if len(image_bytes) < 24:
        return None
    
    # PNG
    if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        if len(image_bytes) >= 24:
            width = int.from_bytes(image_bytes[16:20], 'big')
            height = int.from_bytes(image_bytes[20:24], 'big')
            return (width, height)
    
    # JPEG - vereinfachte Erkennung
    elif image_bytes.startswith(b'\xFF\xD8\xFF'):
        # JPEG ist komplexer, hier nur eine grundlegende Implementierung
        # Für vollständige JPEG-Unterstützung wäre Pillow besser
        return _parse_jpeg_dimensions(image_bytes)
    
    # GIF
    elif image_bytes.startswith((b'GIF87a', b'GIF89a')):
        if len(image_bytes) >= 10:
            width = int.from_bytes(image_bytes[6:8], 'little')
            height = int.from_bytes(image_bytes[8:10], 'little')
            return (width, height)
    
    # BMP
    elif image_bytes.startswith(b'BM'):
        if len(image_bytes) >= 26:
            width = int.from_bytes(image_bytes[18:22], 'little')
            height = int.from_bytes(image_bytes[22:26], 'little')
            return (width, height)
    
    return None


def _parse_jpeg_dimensions(image_bytes: bytes) -> tuple[int, int] | None:
    """Vereinfachte JPEG-Dimensionserkennung."""
    try:
        # Suche nach SOF (Start of Frame) Markern
        i = 2  # Skip initial FF D8
        while i < len(image_bytes) - 8:
            if image_bytes[i] == 0xFF:
                marker = image_bytes[i + 1]
                # SOF0, SOF1, SOF2 Marker
                if marker in [0xC0, 0xC1, 0xC2]:
                    if i + 9 < len(image_bytes):
                        height = int.from_bytes(image_bytes[i + 5:i + 7], 'big')
                        width = int.from_bytes(image_bytes[i + 7:i + 9], 'big')
                        return (width, height)
                
                # Springe zum nächsten Segment
                if i + 3 < len(image_bytes):
                    length = int.from_bytes(image_bytes[i + 2:i + 4], 'big')
                    i += 2 + length
                else:
                    break
            else:
                i += 1
    except Exception:
        pass
    
    return None


def create_temp_image_file(image_input: ImageInput, suffix: str | None = None) -> str:
    """
    Erstellt eine temporäre Datei für ein ImageInput-Objekt.
    
    Args:
        image_input: ImageInput-Objekt
        suffix: Optionale Dateierweiterung (wird automatisch erkannt wenn None)
        
    Returns:
        Pfad zur temporären Datei
        
    Note:
        Die temporäre Datei muss manuell gelöscht werden!
    """
    if suffix is None:
        # Versuche Suffix aus MIME-Type zu ermitteln
        mime_type = image_input.detected_mime_type
        if mime_type:
            suffix_map = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/webp': '.webp',
                'image/bmp': '.bmp',
                'image/tiff': '.tiff',
                'image/svg+xml': '.svg'
            }
            suffix = suffix_map.get(mime_type, '.jpg')
        else:
            suffix = '.jpg'
    
    # Temporäre Datei erstellen
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        image_bytes = image_input.to_bytes()
        temp_file.write(image_bytes)
        return temp_file.name


def cleanup_temp_file(file_path: str) -> bool:
    """
    Löscht eine temporäre Datei sicher.
    
    Args:
        file_path: Pfad zur zu löschenden Datei
        
    Returns:
        True wenn erfolgreich gelöscht
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            return True
    except Exception:
        pass
    return False


def _validate_image_magic_bytes(image_bytes: bytes) -> bool:
    """
    Validiert das Bildformat durch Überprüfung der Magic Bytes.
    
    Args:
        image_bytes: Bilddaten als Bytes
        
    Returns:
        True wenn das Format gültig ist
    """
    if len(image_bytes) < 8:
        return False
    
    magic_bytes = {
        b'\xFF\xD8\xFF': 'image/jpeg',
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'GIF87a': 'image/gif',
        b'GIF89a': 'image/gif',
        b'RIFF': 'image/webp',
        b'BM': 'image/bmp',
        b'II*\x00': 'image/tiff',
        b'MM\x00*': 'image/tiff',
    }
    
    for magic, format_type in magic_bytes.items():
        if image_bytes.startswith(magic):
            if format_type == 'image/webp':
                if b'WEBP' in image_bytes[8:12]:
                    return True
                else:
                    continue
            return True
    
    try:
        text_content = image_bytes.decode('utf-8', errors='ignore')
        if '<svg' in text_content.lower() and 'xmlns' in text_content.lower():
            return True
    except Exception:
        pass
    
    return False
