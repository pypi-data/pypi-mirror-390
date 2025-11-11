"""
Beispiel für strukturierte Outputs mit Pydantic Modellen

Dieses Beispiel zeigt, wie man strukturierte Outputs mit OpenAI's response_format
und Pydantic Modellen verwendet.
"""

from typing import Optional

from pydantic import BaseModel, Field

from automation_lib.llm_prompt.config.llm_prompt_config import LLMPromptConfig
from automation_lib.llm_prompt.llm_prompt_runner import execute_prompt_detailed


class Task(BaseModel):
    """Ein strukturiertes Task-Objekt."""
    title: str = Field(description="Titel der Aufgabe")
    priority: int = Field(ge=1, le=5, description="Priorität von 1-5")
    tags: list[str] = Field(default_factory=list, description="Tags für die Aufgabe")
    due_date: Optional[str] = Field(None, description="Fälligkeitsdatum im ISO-Format (YYYY-MM-DD)")


class Person(BaseModel):
    """Ein strukturiertes Person-Objekt."""
    name: str = Field(description="Vollständiger Name")
    age: int = Field(description="Alter in Jahren")
    occupation: str = Field(description="Beruf")
    interests: list[str] = Field(default_factory=list, description="Interessen")


def main():
    """Demonstriert strukturierte Outputs."""

    # Konfiguration laden
    config = LLMPromptConfig.default()

    # Beispiel 1: Task erstellen
    print("=== Beispiel 1: Task erstellen ===")
    task_prompt = """
    Erstelle eine neue Aufgabe basierend auf dieser Beschreibung:
    "Rechnungsupload-API Dokumentation schreiben, hohe Priorität, Tags: billing, api, docs, Fällig: 2025-09-30"
    """

    try:
        task_response = execute_prompt_detailed(
            prompt=task_prompt,
            response_model=Task,
            system_prompt="Du bist ein hilfreicher Assistent, der strukturierte Daten erstellt.",
            config=config
        )

        print(f"Response Type: {type(task_response.content)}")
        print(f"Task: {task_response.content}")
        print(f"Model: {task_response.model}")
        print(f"Response Time: {task_response.response_time_ms}ms")

        # Direkter Zugriff auf strukturierte Daten
        if isinstance(task_response.content, Task):
            print(f"Titel: {task_response.content.title}")
            print(f"Priorität: {task_response.content.priority}")
            print(f"Tags: {task_response.content.tags}")
            print(f"Fällig: {task_response.content.due_date}")

    except Exception as e:
        print(f"Fehler bei Task-Erstellung: {e}")

    print("\n" + "="*50 + "\n")

    # Beispiel 2: Person beschreiben
    print("=== Beispiel 2: Person beschreiben ===")
    person_prompt = """
    Erstelle ein Profil für eine fiktive Person:
    "Anna Schmidt, 28 Jahre alt, arbeitet als Data Scientist bei einem Tech-Unternehmen.
    Sie interessiert sich für Machine Learning, Fotografie und Wandern."
    """

    try:
        person_response = runner.execute_prompt_detailed(
            prompt=person_prompt,
            response_model=Person,
            system_prompt="Du bist ein hilfreicher Assistent, der strukturierte Personenprofile erstellt."
        )

        print(f"Response Type: {type(person_response.content)}")
        print(f"Person: {person_response.content}")

        # Direkter Zugriff auf strukturierte Daten
        if isinstance(person_response.content, Person):
            print(f"Name: {person_response.content.name}")
            print(f"Alter: {person_response.content.age}")
            print(f"Beruf: {person_response.content.occupation}")
            print(f"Interessen: {person_response.content.interests}")

    except Exception as e:
        print(f"Fehler bei Personen-Erstellung: {e}")

    print("\n" + "="*50 + "\n")

    # Beispiel 3: Normaler Text-Output (ohne response_model)
    print("=== Beispiel 3: Normaler Text-Output ===")
    text_prompt = "Erkläre kurz, was strukturierte Outputs sind."

    try:
        text_response = runner.execute_prompt_detailed(
            prompt=text_prompt,
            system_prompt="Du bist ein hilfreicher Assistent."
        )

        print(f"Response Type: {type(text_response.content)}")
        print(f"Content: {text_response.content}")

    except Exception as e:
        print(f"Fehler bei Text-Output: {e}")


if __name__ == "__main__":
    main()
