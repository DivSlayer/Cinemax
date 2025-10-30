import environ
import os

# Create env instance
env = environ.Env()

# Explicitly load the .env file
environ.Env.read_env(os.path.join(os.path.dirname(__file__), ".env"))

# Now you can safely access your variable
print(env.list("IMPORT_SITES"))

print(os.getenv("IMPORT_SITES"))