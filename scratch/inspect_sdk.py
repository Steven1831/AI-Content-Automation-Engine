import os
from google.genai import Client
from google.genai import types
import inspect

api_key = os.getenv("GEMINI_API_KEY")
client = Client(api_key=api_key)

print("generate_videos signature:")
print(inspect.signature(client.models.generate_videos))

print("\ntypes.Image.from_file signature:")
print(inspect.signature(types.Image.from_file))
