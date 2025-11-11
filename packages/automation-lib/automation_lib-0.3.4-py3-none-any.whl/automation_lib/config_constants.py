class ModuleConfigConstants:
    """Zentrale Konfigurationskonstanten für automation_lib"""
    
    # Standard .env-Datei Reihenfolge (höchste zu niedrigste Priorität)
    DEFAULT_ENV_FILES = ('.env.local', '.env.test', '.env')
    
    # Weitere modulübergreifende Konstanten können hier hinzugefügt werden
    # DEFAULT_TIMEOUT = 60
    # DEFAULT_RETRY_ATTEMPTS = 3
    
    @classmethod
    def get_env_files_for_context(cls, context: str = 'default') -> tuple:
        """Ermöglicht kontextspezifische .env-Dateien"""
        if context == 'test':
            return ('.env.test', '.env')
        elif context == 'development':
            return ('.env.local', '.env.dev', '.env')
        return cls.DEFAULT_ENV_FILES
