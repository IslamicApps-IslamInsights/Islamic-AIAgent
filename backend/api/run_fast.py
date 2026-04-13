import sys
# Bypass crazy iCloud hang on metadata fetch in google.api_core
import importlib.metadata
original_packages_distributions = importlib.metadata.packages_distributions
def fast_packages_distributions(): return {}
importlib.metadata.packages_distributions = fast_packages_distributions

print("Importing genai...")
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
print("Saying hello...")
response = model.generate_content("Say hello in Arabic")
print("Response:", response.text)
