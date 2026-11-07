from dotenv import load_dotenv
from google import genai

load_dotenv()  # loads GEMINI_API_KEY from .env

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="Explain how AI works in a few words",
)

print(interaction.output_text)
