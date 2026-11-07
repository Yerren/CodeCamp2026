from dotenv import load_dotenv
from google import genai

load_dotenv()  # loads GEMINI_API_KEY from .env


def parse_transcript(text_in: str):
    message = f"""For the following transcript, determine the target action the user wants to take, 
    the target application, and any additional parameters.\n transcript: {text_in}"""

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=message,
    )

    return interaction.output_text


if __name__ == "__main__":
    transcript = "Hey Google, navigate to Ara."

    print(parse_transcript(transcript))
