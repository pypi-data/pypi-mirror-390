"""
Image Input Schemas

Defines Pydantic models for handling image inputs in LLM prompts.
"""

import base64
import mimetypes
import re
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, computed_field, field_validator


class ImageInput(BaseModel):
    """
    Schema für Bild-Inputs in LLM-Prompts.
    
    Unterstützt verschiedene Bildquellen:
    - Lokale Dateipfade
    - URLs zu Remote-Bildern
    - Base64-kodierte Strings
    - Raw bytes
    """

    source: str | bytes = Field(
        ...,
        description="Bildquelle: Dateipfad, URL, Base64-String oder Raw bytes"
    )
    mime_type: str | None = Field(
        None,
        description="MIME-Type des Bildes (wird automatisch erkannt wenn None)"
    )
    description: str | None = Field(
        None,
        description="Optionale Beschreibung des Bildes für besseren Kontext"
    )
    max_size_mb: float | None = Field(
        None,
        description="Maximale Dateigröße in MB (überschreibt globale Einstellung)"
    )

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str | bytes) -> str | bytes:
        """Validiert die Bildquelle."""
        if isinstance(v, bytes):
            if len(v) == 0:
                raise ValueError("Bytes-Daten dürfen nicht leer sein")
            return v

        if isinstance(v, str):
            if len(v.strip()) == 0:
                raise ValueError("String-Quelle darf nicht leer sein")
            return v.strip()

        raise ValueError("Source muss ein String oder bytes sein")

    @field_validator('mime_type')
    @classmethod
    def validate_mime_type(cls, v: str | None) -> str | None:
        """Validiert den MIME-Type."""
        if v is None:
            return v

        # Unterstützte Bildformate
        supported_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'image/webp', 'image/bmp', 'image/tiff', 'image/svg+xml'
        }

        if v.lower() not in supported_types:
            raise ValueError(f"Nicht unterstützter MIME-Type: {v}. Unterstützt: {supported_types}")

        return v.lower()

    @field_validator('max_size_mb')
    @classmethod
    def validate_max_size_mb(cls, v: float | None) -> float | None:
        """Validiert die maximale Dateigröße."""
        if v is None:
            return v

        if v <= 0:
            raise ValueError("max_size_mb muss größer als 0 sein")

        if v > 100:  # 100MB Limit
            raise ValueError("max_size_mb darf nicht größer als 100MB sein")

        return v

    @computed_field
    @property
    def source_type(self) -> Literal["file", "url", "base64", "bytes"]:
        """Erkennt automatisch den Typ der Bildquelle."""
        if isinstance(self.source, bytes):
            return "bytes"

        # Für String-Quellen
        source_str = str(self.source)

        # URL-Erkennung
        if self._is_url(source_str):
            return "url"

        # Base64-Erkennung
        if self._is_base64(source_str):
            return "base64"

        # Ansonsten Dateipfad
        return "file"

    @computed_field
    @property
    def detected_mime_type(self) -> str | None:
        """Erkennt automatisch den MIME-Type basierend auf der Quelle."""
        if self.mime_type:
            return self.mime_type

        if self.source_type == "file":
            return mimetypes.guess_type(str(self.source))[0]
        elif self.source_type == "url":
            # Versuche MIME-Type aus URL-Extension zu erraten
            parsed = urlparse(str(self.source))
            return mimetypes.guess_type(parsed.path)[0]
        elif self.source_type == "base64":
            # Versuche MIME-Type aus Base64-Header zu extrahieren
            return self._extract_mime_from_base64(str(self.source))

        return None

    def _is_url(self, source: str) -> bool:
        """Prüft ob die Quelle eine URL ist."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False

    def _is_base64(self, source: str) -> bool:
        """Prüft ob die Quelle ein Base64-String ist."""
        # Data URL Format: data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...
        if source.startswith('data:'):
            return True

        # Reiner Base64-String (mindestens 20 Zeichen, nur Base64-Zeichen)
        if len(source) >= 20:
            base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
            return bool(base64_pattern.match(source))

        return False

    def _extract_mime_from_base64(self, source: str) -> str | None:
        """Extrahiert MIME-Type aus Base64 Data URL."""
        if source.startswith('data:'):
            try:
                # Format: data:image/jpeg;base64,<data>
                header = source.split(',')[0]
                mime_part = header.split(':')[1].split(';')[0]
                return mime_part
            except (IndexError, ValueError):
                return None
        return None

    def get_file_size_mb(self) -> float | None:
        """Ermittelt die Dateigröße in MB."""
        try:
            if self.source_type == "file":
                file_path = Path(str(self.source))
                if file_path.exists():
                    size_bytes = file_path.stat().st_size
                    return size_bytes / (1024 * 1024)
            elif self.source_type == "bytes":
                size_bytes = len(self.source)
                return size_bytes / (1024 * 1024)
            elif self.source_type == "base64":
                # Schätze Größe basierend auf Base64-String
                base64_data = str(self.source)
                if base64_data.startswith('data:'):
                    base64_data = base64_data.split(',', 1)[1]

                # Base64 ist etwa 33% größer als die ursprünglichen Daten
                estimated_bytes = len(base64_data) * 3 / 4
                return estimated_bytes / (1024 * 1024)
        except Exception:
            pass

        return None

    def validate_size(self, max_size_mb: float | None = None) -> bool:
        """
        Validiert die Dateigröße gegen das Limit.

        Args:
            max_size_mb: Maximale Größe in MB (verwendet self.max_size_mb wenn None)

        Returns:
            True wenn die Größe OK ist
        Raises:
            ValueError: Wenn die Datei zu groß ist
        """
        limit = max_size_mb or self.max_size_mb or 20.0  # Default 20MB
        actual_size = self.get_file_size_mb()

        if actual_size is not None and actual_size > limit:
            raise ValueError(
                f"Bild ist zu groß: {actual_size:.2f}MB > {limit:.2f}MB"
            )

        return True

    def to_bytes(self) -> bytes:
        """
        Konvertiert die Bildquelle zu bytes.

        Returns:
            Raw bytes des Bildes

        Raises:
            ValueError: Wenn die Konvertierung fehlschlägt
            FileNotFoundError: Wenn eine Datei nicht gefunden wird
        """
        if self.source_type == "bytes":
            if isinstance(self.source, bytes):
                return self.source
            else:
                raise ValueError("Source ist nicht vom Typ bytes")

        elif self.source_type == "file":
            file_path = Path(str(self.source))
            if not file_path.exists():
                raise FileNotFoundError(f"Bilddatei nicht gefunden: {file_path}")

            with open(file_path, 'rb') as f:
                return f.read()

        elif self.source_type == "base64":
            source_str = str(self.source)

            # Data URL Format
            if source_str.startswith('data:'):
                base64_data = source_str.split(',', 1)[1]
            else:
                base64_data = source_str

            try:
                return base64.b64decode(base64_data)
            except Exception as e:
                raise ValueError(f"Ungültiger Base64-String: {e}") from e

        elif self.source_type == "url":
            raise ValueError(
                "URL-basierte Bilder müssen extern heruntergeladen werden. "
                "Verwenden Sie image_utils.download_image_from_url()"
            )

        else:
            raise ValueError(f"Unbekannter source_type: {self.source_type}")

    def to_base64(self) -> str:
        """
        Konvertiert das Bild zu einem Base64-String.

        Returns:
            Base64-kodierter String des Bildes
        """
        image_bytes = self.to_bytes()
        return base64.b64encode(image_bytes).decode('utf-8')

    def to_data_url(self) -> str:
        """
        Konvertiert das Bild zu einer Data URL.
        
        Returns:
            Data URL im Format: data:image/jpeg;base64,<data>
        """
        mime_type = self.detected_mime_type or 'image/jpeg'
        base64_data = self.to_base64()
        return f"data:{mime_type};base64,{base64_data}"


# Helper-Funktionen für einfache Erstellung von ImageInput-Objekten

def image_from_file(path: str | Path, description: str | None = None) -> ImageInput:
    """
    Erstellt ein ImageInput-Objekt aus einem Dateipfad.
    
    Args:
        path: Pfad zur Bilddatei
        description: Optionale Beschreibung
        
    Returns:
        ImageInput-Objekt
    """
    return ImageInput(source=str(path), description=description, mime_type=None, max_size_mb=None)


def image_from_url(url: str, description: str | None = None) -> ImageInput:
    """
    Erstellt ein ImageInput-Objekt aus einer URL.
    
    Args:
        url: URL zum Bild
        description: Optionale Beschreibung
        
    Returns:
        ImageInput-Objekt
    """
    return ImageInput(source=url, description=description, mime_type=None, max_size_mb=None)


def image_from_base64(
    data: str,
    mime_type: str | None = None,
    description: str | None = None
) -> ImageInput:
    """
    Erstellt ein ImageInput-Objekt aus Base64-Daten.
    
    Args:
        data: Base64-kodierte Bilddaten
        mime_type: MIME-Type des Bildes
        description: Optionale Beschreibung
        
    Returns:
        ImageInput-Objekt
    """
    return ImageInput(source=data, mime_type=mime_type, description=description, max_size_mb=None)


def image_from_bytes(
    data: bytes,
    mime_type: str,
    description: str | None = None
) -> ImageInput:
    """
    Erstellt ein ImageInput-Objekt aus Raw bytes.
    
    Args:
        data: Raw bytes des Bildes
        mime_type: MIME-Type des Bildes
        description: Optionale Beschreibung
        
    Returns:
        ImageInput-Objekt
    """
    return ImageInput(source=data, mime_type=mime_type, description=description, max_size_mb=None)
