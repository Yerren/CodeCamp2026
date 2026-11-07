from typing import Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()  # loads GEMINI_API_KEY from .env


# --- maps ---
class Navigate(BaseModel):
    action: Literal["navigate"]
    destination: str
    mode: Literal["driving", "walking", "cycling", "transit"] | None = None


class SearchNearby(BaseModel):
    action: Literal["search_nearby"]
    query: str
    radius_km: float | None = None


class ShowTraffic(BaseModel):
    action: Literal["show_traffic"]


class Maps(BaseModel):
    """Navigation and location search"""

    application: Literal["maps"]
    command: Navigate | SearchNearby | ShowTraffic


# --- music ---
class Play(BaseModel):
    action: Literal["play"]
    song: str | None = None
    artist: str | None = None
    playlist: str | None = None


class Pause(BaseModel):
    action: Literal["pause"]


class Skip(BaseModel):
    action: Literal["skip"]


class SetVolume(BaseModel):
    action: Literal["set_volume"]
    level: int = Field(ge=0, le=100)


class Music(BaseModel):
    """Music streaming and playback"""

    application: Literal["music"]
    command: Play | Pause | Skip | SetVolume


# --- messages ---
class SendMessage(BaseModel):
    action: Literal["send_message"]
    recipient: str
    body: str


class ReadLatest(BaseModel):
    action: Literal["read_latest"]
    sender: str | None = None


class Messages(BaseModel):
    """Send and read text messages"""

    application: Literal["messages"]
    command: SendMessage | ReadLatest


# --- calendar ---
class CreateEvent(BaseModel):
    action: Literal["create_event"]
    title: str
    date: str = Field(description="YYYY-MM-DD")
    time: str | None = Field(default=None, description="HH:MM")
    duration_minutes: int | None = None


class ListEvents(BaseModel):
    action: Literal["list_events"]
    date: str = Field(description="YYYY-MM-DD")


class SetReminder(BaseModel):
    action: Literal["set_reminder"]
    text: str
    time: str = Field(description="HH:MM")


class Calendar(BaseModel):
    """Manage events and reminders"""

    application: Literal["calendar"]
    command: CreateEvent | ListEvents | SetReminder


# --- weather ---
class CurrentConditions(BaseModel):
    action: Literal["current_conditions"]
    location: str | None = None


class Forecast(BaseModel):
    action: Literal["forecast"]
    location: str | None = None
    days: int | None = None


class Weather(BaseModel):
    """Weather forecasts and conditions"""

    application: Literal["weather"]
    command: CurrentConditions | Forecast


class ParsedCommand(BaseModel):
    target: Maps | Music | Messages | Calendar | Weather


def const_to_enum(schema):
    """Pydantic renders single-value Literals as {"const": x}, which Gemini doesn't
    enforce. Rewrite them as {"enum": [x]} so the choice is actually constrained."""
    if isinstance(schema, dict):
        if "const" in schema:
            schema["enum"] = [schema.pop("const")]
        for value in schema.values():
            const_to_enum(value)
    elif isinstance(schema, list):
        for item in schema:
            const_to_enum(item)
    return schema


def parse_transcript(text_in: str) -> ParsedCommand:
    message = f"""For the following transcript, determine the target application the user
    wants to use, the action to take, and any parameters for that action.

    transcript: {text_in}"""

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=message,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=const_to_enum(ParsedCommand.model_json_schema()),
        ),
    )

    print(response)
    return ParsedCommand.model_validate(response.parsed)


if __name__ == "__main__":
    transcript = "Hey Google, navigate to Ara."

    result = parse_transcript(transcript)
    print(result.model_dump_json(indent=2, exclude_none=True))
