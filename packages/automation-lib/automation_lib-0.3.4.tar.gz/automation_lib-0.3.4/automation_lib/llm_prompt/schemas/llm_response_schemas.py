"""
LLM Response Schemas - Pydantic-Modelle für einheitliche LLM-Provider-Responses

Dieses Modul definiert die Datenstrukturen für einheitliche Responses aller LLM-Provider.
"""

from datetime import datetime
from typing import Any, Union

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Token-Verbrauchsinformationen für LLM-Requests."""
    prompt_tokens: int | None = Field(None, description="Anzahl der Tokens im Input-Prompt")
    completion_tokens: int | None = Field(None, description="Anzahl der generierten Tokens")
    total_tokens: int | None = Field(None, description="Gesamtanzahl der verwendeten Tokens")


class RateLimitInfo(BaseModel):
    """Rate Limit Informationen des LLM-Providers."""
    requests_remaining: int | None = Field(None, description="Verbleibende Requests bis Rate Limit")
    requests_reset_time: datetime | None = Field(None, description="Zeitpunkt der Rate Limit Reset")
    tokens_remaining: int | None = Field(None, description="Verbleibende Tokens bis Rate Limit")
    tokens_reset_time: datetime | None = Field(None, description="Zeitpunkt der Token Rate Limit Reset")
    requests_per_minute: int | None = Field(None, description="Maximale Requests pro Minute")
    tokens_per_minute: int | None = Field(None, description="Maximale Tokens pro Minute")


class LLMResponse(BaseModel):
    """
    Einheitlicher Response-Type für alle LLM-Provider.

    Dieser Type stellt eine konsistente Schnittstelle für alle Provider bereit
    und enthält sowohl den generierten Content als auch wichtige Metadaten.
    """
    content: str | dict[str, Any] | BaseModel = Field(..., description="Der generierte Content vom LLM - String, Dict oder Pydantic Model")
    model: str = Field(..., description="Name des verwendeten LLM-Modells")
    provider: str = Field(..., description="Name des LLM-Providers (openai, gemini, etc.)")
    token_usage: TokenUsage | None = Field(None, description="Token-Verbrauchsinformationen")
    rate_limit_info: RateLimitInfo | None = Field(None, description="Rate Limit Informationen")
    response_time_ms: int | None = Field(None, description="Response-Zeit in Millisekunden")
    finish_reason: str | None = Field(None, description="Grund für das Ende der Generierung")
    request_id: str | None = Field(None, description="Eindeutige Request-ID vom Provider")
    created_at: datetime | None = Field(None, description="Zeitstempel der Response-Erstellung")
    raw_response: dict[str, Any] | None = Field(None, description="Vollständige Raw-Response für Debug-Zwecke")
    
    def __str__(self) -> str:
        """String-Repräsentation gibt den Content zurück für einfache Verwendung."""
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, BaseModel):
            return str(self.content)
        elif isinstance(self.content, dict):
            return str(self.content)
        else:
            return str(self.content)
    
    def get_cost_estimate(self) -> float | None:
        """
        Schätzt die Kosten des Requests basierend auf Token-Usage.
        
        Returns:
            Geschätzte Kosten in USD oder None wenn nicht berechenbar
        """
        if not self.token_usage or not self.token_usage.total_tokens:
            return None
        
        # Vereinfachte Kostenschätzung - kann provider-spezifisch erweitert werden
        cost_per_1k_tokens = {
            "gpt-4o": 0.005,
            "gpt-4o-mini": 0.00015,
            "gpt-4-turbo": 0.01,
            "gpt-4": 0.03,
            "gemini-1.5-pro": 0.0035,
            "gemini-1.5-flash": 0.00035,
        }
        
        base_model = self.model.lower()
        for model_key, cost in cost_per_1k_tokens.items():
            if model_key == base_model:
                return (self.token_usage.total_tokens / 1000) * cost
        
        return None
    
    def is_rate_limited(self) -> bool:
        """
        Prüft ob der Request nahe am Rate Limit ist.
        
        Returns:
            True wenn weniger als 10% der Rate Limits verfügbar sind
        """
        if not self.rate_limit_info:
            return False
        
        # Prüfe Request Rate Limit
        if (self.rate_limit_info.requests_remaining is not None and
            self.rate_limit_info.requests_per_minute is not None):
            request_usage_percent = (
                (self.rate_limit_info.requests_per_minute - self.rate_limit_info.requests_remaining)
                / self.rate_limit_info.requests_per_minute
            )
            if request_usage_percent > 0.9:  # Mehr als 90% verwendet
                return True
        
        # Prüfe Token Rate Limit
        if (self.rate_limit_info.tokens_remaining is not None and
            self.rate_limit_info.tokens_per_minute is not None):
            token_usage_percent = (
                (self.rate_limit_info.tokens_per_minute - self.rate_limit_info.tokens_remaining)
                / self.rate_limit_info.tokens_per_minute
            )
            if token_usage_percent > 0.9:  # Mehr als 90% verwendet
                return True
        
        return False
