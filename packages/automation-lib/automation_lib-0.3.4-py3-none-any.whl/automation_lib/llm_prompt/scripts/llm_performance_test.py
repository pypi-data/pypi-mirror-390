#!/usr/bin/env python3
"""
LLM Performance Test Script

Dieses Skript führt Performance-Tests für verschiedene LLM-Modelle durch.
Es misst die Antwortzeit für eine definierte Anzahl von Wiederholungen
und stellt die Ergebnisse tabellarisch dar.
"""

import argparse
import os
import statistics
import sys
import time
from dataclasses import dataclass

from tabulate import tabulate

# Füge das automation_lib Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from automation_lib.llm_prompt.llm_prompt_runner import execute_prompt


@dataclass
class PerformanceResult:
    """Datenklasse für Performance-Ergebnisse eines Modells."""
    model_name: str
    successful_requests: int
    failed_requests: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    median_time: float
    std_deviation: float
    requests_per_second: float


class LLMPerformanceTester:
    """Klasse für die Durchführung von LLM-Performance-Tests."""
    
    def __init__(self):
        self.results: list[PerformanceResult] = []
    
    def get_default_models(self) -> list[str]:
        """Gibt eine Liste der Standard-Testmodelle zurück."""
        return [
            "gpt-4o-mini",
            "gemini-2.5-flash",
        ]
    
    def test_model_performance(
        self,
        model_name: str,
        prompt: str,
        iterations: int,
        system_prompt: str | None = None,
        **kwargs
    ) -> PerformanceResult:
        """
        Testet die Performance eines einzelnen Modells.
        
        Args:
            model_name: Name des zu testenden Modells
            prompt: Der zu sendende Prompt
            iterations: Anzahl der Wiederholungen
            system_prompt: Optionaler System-Prompt
            **kwargs: Zusätzliche Parameter für das Modell
            
        Returns:
            PerformanceResult: Ergebnisse des Performance-Tests
        """
        print(f"\n🔄 Teste Modell: {model_name} ({iterations} Wiederholungen)")
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        start_total_time = time.time()
        
        for i in range(iterations):
            print(f"  Request {i+1}/{iterations}...", end=" ", flush=True)
            
            try:
                start_time = time.time()
                
                execute_prompt(
                    prompt=prompt,
                    model=model_name,
                    system_prompt=system_prompt,
                    **kwargs
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                successful_requests += 1
                
                print(f"✅ {response_time:.2f}s")
                
            except Exception as e:
                failed_requests += 1
                print(f"❌ Fehler: {str(e)[:50]}...")
        
        total_time = time.time() - start_total_time
        
        # Berechne Statistiken nur wenn erfolgreiche Requests vorhanden sind
        if response_times:
            average_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            median_time = statistics.median(response_times)
            std_deviation = statistics.stdev(response_times) if len(response_times) > 1 else 0.0
            requests_per_second = successful_requests / total_time if total_time > 0 else 0.0
        else:
            average_time = min_time = max_time = median_time = std_deviation = requests_per_second = 0.0
        
        return PerformanceResult(
            model_name=model_name,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            average_time=average_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            std_deviation=std_deviation,
            requests_per_second=requests_per_second
        )
    
    def run_performance_test(
        self,
        models: list[str],
        prompt: str,
        iterations: int,
        system_prompt: str | None = None,
        **kwargs
    ) -> list[PerformanceResult]:
        """
        Führt Performance-Tests für mehrere Modelle durch.
        
        Args:
            models: Liste der zu testenden Modelle
            prompt: Der zu sendende Prompt
            iterations: Anzahl der Wiederholungen pro Modell
            system_prompt: Optionaler System-Prompt
            **kwargs: Zusätzliche Parameter für die Modelle
            
        Returns:
            List[PerformanceResult]: Liste der Testergebnisse
        """
        print(f"🚀 Starte Performance-Test mit {len(models)} Modellen")
        print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print(f"🔄 Wiederholungen pro Modell: {iterations}")
        
        if system_prompt:
            print(f"🎯 System-Prompt: {system_prompt[:100]}{'...' if len(system_prompt) > 100 else ''}")
        
        self.results = []
        
        for model in models:
            try:
                result = self.test_model_performance(
                    model_name=model,
                    prompt=prompt,
                    iterations=iterations,
                    system_prompt=system_prompt,
                    **kwargs
                )
                self.results.append(result)
                
            except Exception as e:
                print(f"❌ Fehler beim Testen von Modell {model}: {e}")
                # Erstelle ein Ergebnis mit allen fehlgeschlagenen Requests
                error_result = PerformanceResult(
                    model_name=model,
                    successful_requests=0,
                    failed_requests=iterations,
                    total_time=0.0,
                    average_time=0.0,
                    min_time=0.0,
                    max_time=0.0,
                    median_time=0.0,
                    std_deviation=0.0,
                    requests_per_second=0.0
                )
                self.results.append(error_result)
        
        return self.results
    
    def print_results_table(self) -> None:
        """Gibt die Ergebnisse in tabellarischer Form aus."""
        if not self.results:
            print("❌ Keine Ergebnisse zum Anzeigen vorhanden.")
            return
        
        print("\n" + "="*100)
        print("📊 PERFORMANCE-TEST ERGEBNISSE")
        print("="*100)
        
        # Erstelle Tabellendaten
        table_data = []
        headers = [
            "Modell",
            "Erfolg",
            "Fehler",
            "Durchschn. Zeit (s)",
            "Min Zeit (s)",
            "Max Zeit (s)",
            "Median (s)",
            "Std.abw. (s)",
            "Req/s"
        ]
        
        for result in self.results:
            table_data.append([
                result.model_name,
                result.successful_requests,
                result.failed_requests,
                f"{result.average_time:.3f}" if result.average_time > 0 else "N/A",
                f"{result.min_time:.3f}" if result.min_time > 0 else "N/A",
                f"{result.max_time:.3f}" if result.max_time > 0 else "N/A",
                f"{result.median_time:.3f}" if result.median_time > 0 else "N/A",
                f"{result.std_deviation:.3f}" if result.std_deviation > 0 else "N/A",
                f"{result.requests_per_second:.2f}" if result.requests_per_second > 0 else "N/A"
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Zusätzliche Zusammenfassung
        print("\n📈 ZUSAMMENFASSUNG:")
        
        successful_results = [r for r in self.results if r.successful_requests > 0]
        
        if successful_results:
            fastest_model = min(successful_results, key=lambda x: x.average_time)
            most_reliable = max(self.results, key=lambda x: x.successful_requests)
            highest_throughput = max(successful_results, key=lambda x: x.requests_per_second)
            
            print(f"⚡ Schnellstes Modell: {fastest_model.model_name} ({fastest_model.average_time:.3f}s)")
            print(f"🛡️  Zuverlässigstes Modell: {most_reliable.model_name} ({most_reliable.successful_requests}/{most_reliable.successful_requests + most_reliable.failed_requests} erfolgreich)")
            print(f"🚀 Höchster Durchsatz: {highest_throughput.model_name} ({highest_throughput.requests_per_second:.2f} req/s)")
        else:
            print("❌ Keine erfolgreichen Requests für Zusammenfassung verfügbar.")


def main():
    """Hauptfunktion für das Performance-Test-Skript."""
    parser = argparse.ArgumentParser(
        description="LLM Performance Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Standard-Test mit allen verfügbaren Modellen
  python llm_performance_test.py
  
  # Test mit spezifischen Modellen
  python llm_performance_test.py --models gpt-4o-mini gemini-1.5-flash
  
  # Test mit eigenem Prompt und mehr Wiederholungen
  python llm_performance_test.py --prompt "Erkläre Quantencomputing" --iterations 10
  
  # Test mit System-Prompt
  python llm_performance_test.py --system-prompt "Du bist ein Experte für KI"
        """
    )
    
    parser.add_argument(
        "--models",
        nargs="+",
        help="Liste der zu testenden Modelle (Standard: alle verfügbaren)"
    )
    
    parser.add_argument(
        "--prompt",
        default="Was ist künstliche Intelligenz? Erkläre es in 2-3 Sätzen.",
        help="Der zu testende Prompt (Standard: KI-Erklärung)"
    )
    
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Anzahl der Wiederholungen pro Modell (Standard: 5)"
    )
    
    parser.add_argument(
        "--system-prompt",
        help="Optionaler System-Prompt"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature-Parameter für die Modelle (Standard: 0.7)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=150,
        help="Maximale Anzahl von Tokens (Standard: 150)"
    )
    
    args = parser.parse_args()
    
    # Erstelle Tester-Instanz
    tester = LLMPerformanceTester()
    
    # Bestimme zu testende Modelle
    if args.models:
        models_to_test = args.models
    else:
        models_to_test = tester.get_default_models()
    
    print("🎯 LLM Performance Test")
    print("=" * 50)
    
    # Führe Tests durch
    try:
        tester.run_performance_test(
            models=models_to_test,
            prompt=args.prompt,
            iterations=args.iterations,
            system_prompt=args.system_prompt,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
        
        # Zeige Ergebnisse an
        tester.print_results_table()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test durch Benutzer abgebrochen.")
        if tester.results:
            print("Zeige bisherige Ergebnisse:")
            tester.print_results_table()
    
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
