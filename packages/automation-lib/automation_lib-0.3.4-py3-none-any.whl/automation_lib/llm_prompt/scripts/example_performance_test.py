#!/usr/bin/env python3
"""
Beispiel für die programmatische Verwendung des LLM Performance Test Scripts

Dieses Skript zeigt, wie man die LLMPerformanceTester Klasse direkt verwenden kann,
um Performance-Tests in eigenen Anwendungen zu integrieren.
"""

import os
import sys

# Füge das automation_lib Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from automation_lib.llm_prompt.models import GeminiModel
from scripts.llm_performance_test import LLMPerformanceTester


def beispiel_einfacher_test():
    """Einfacher Performance-Test mit zwei Modellen."""
    print("🔬 Beispiel: Einfacher Performance-Test")
    print("=" * 50)
    
    tester = LLMPerformanceTester()
    
    # Test mit nur zwei schnellen Modellen
    modelle = ["gpt-4o-mini", "gemini-1.5-flash"]
    prompt = "Was ist 2+2?"
    
    results = tester.run_performance_test(
        models=modelle,
        prompt=prompt,
        iterations=3,
        max_tokens=50,
        temperature=0.1
    )
    
    tester.print_results_table()
    return results


def beispiel_vergleichstest():
    """Vergleichstest zwischen verschiedenen Modell-Kategorien."""
    print("\n\n🏆 Beispiel: Modell-Kategorien Vergleich")
    print("=" * 50)
    
    tester = LLMPerformanceTester()
    
    # Teste verschiedene Modell-Kategorien
    modelle = [
        "gpt-4o-mini",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        GeminiModel.GEMINI_2_5_FLASH,
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite"
    ]
    
    prompt = "Erkläre den Unterschied zwischen Machine Learning und Deep Learning in einem Satz."
    
    results = tester.run_performance_test(
        models=modelle,
        prompt=prompt,
        iterations=3,
        max_tokens=100,
        system_prompt="Du bist ein KI-Experte, der komplexe Themen einfach erklärt.",
        temperature=0.3
    )
    
    tester.print_results_table()
    return results


def beispiel_custom_analyse():
    """Beispiel für eine benutzerdefinierte Analyse der Ergebnisse."""
    print("\n\n📊 Beispiel: Benutzerdefinierte Analyse")
    print("=" * 50)
    
    tester = LLMPerformanceTester()
    
    # Führe Test durch
    results = tester.run_performance_test(
        models=["gpt-4o-mini", "gemini-1.5-flash"],
        prompt="Nenne drei Vorteile von erneuerbaren Energien.",
        iterations=4,
        max_tokens=80
    )
    
    # Benutzerdefinierte Analyse
    print("\n🔍 BENUTZERDEFINIERTE ANALYSE:")
    
    successful_results = [r for r in results if r.successful_requests > 0]
    
    if successful_results:
        # Berechne Gesamtstatistiken
        total_requests = sum(r.successful_requests for r in successful_results)
        total_time = sum(r.total_time for r in successful_results)
        overall_avg_time = sum(r.average_time * r.successful_requests for r in successful_results) / total_requests
        
        print(f"📈 Gesamt-Requests: {total_requests}")
        print(f"⏱️  Gesamt-Zeit: {total_time:.2f}s")
        print(f"📊 Durchschnittliche Antwortzeit: {overall_avg_time:.3f}s")
        
        # Finde Extremwerte
        fastest_response = min(r.min_time for r in successful_results)
        slowest_response = max(r.max_time for r in successful_results)
        
        print(f"⚡ Schnellste Antwort: {fastest_response:.3f}s")
        print(f"🐌 Langsamste Antwort: {slowest_response:.3f}s")
        
        # Berechne Effizienz-Score (Requests pro Sekunde pro erfolgreichen Request)
        print("\n🏅 EFFIZIENZ-RANKING:")
        efficiency_ranking = sorted(successful_results, key=lambda x: x.requests_per_second, reverse=True)
        
        for i, result in enumerate(efficiency_ranking, 1):
            print(f"  {i}. {result.model_name}: {result.requests_per_second:.2f} req/s")


def main():
    """Hauptfunktion mit verschiedenen Beispielen."""
    print("🎯 LLM Performance Test - Programmatische Beispiele")
    print("=" * 60)
    
    try:
        # Beispiel 1: Einfacher Test
        # beispiel_einfacher_test()
        
        # Beispiel 2: Vergleichstest
        beispiel_vergleichstest()
        
        # Beispiel 3: Benutzerdefinierte Analyse
        # beispiel_custom_analyse()
        
        print("\n✅ Alle Beispiele erfolgreich ausgeführt!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests durch Benutzer abgebrochen.")
    
    except Exception as e:
        print(f"\n❌ Fehler bei der Ausführung: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
