from decouple import config

# Database
DATABASE_URL: str = config("DATABASE_URL", default="postgresql://user:password@localhost:5432/aesi_mrp")

# Escalation timeouts (minutes)
ESCALATION_TIMEOUT_URGENT: int = config("ESCALATION_TIMEOUT_URGENT", default=15, cast=int)
ESCALATION_TIMEOUT_STANDARD: int = config("ESCALATION_TIMEOUT_STANDARD", default=240, cast=int)

# App
APP_ENV: str = config("APP_ENV", default="development")
SECRET_KEY: str = config("SECRET_KEY")
