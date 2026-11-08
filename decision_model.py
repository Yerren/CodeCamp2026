import json
from typing import cast

from dotenv import load_dotenv
from typesafe_sdk import Choice, ChoiceAnswer, TypeSafeClient

from just_ask_1 import VALID_APPLICATIONS

load_dotenv()  # loads TYPESAFE_API_KEY from .env


def build_criteria(valid_applications: dict[str, dict]) -> dict[str, str]:
    """Flatten every application/action pair into one option, e.g. "maps.navigate".
    The description helps the model tell similar options apart."""
    criteria = {}
    for app_name, app in valid_applications.items():
        for action_name in app["actions"]:
            criteria[f"{app_name}.{action_name}"] = (
                f"{app['description']}: {action_name.replace('_', ' ')}"
            )
    return criteria


def parse_transcript(text_in: str, valid_applications: dict[str, dict]):
    # A decision model can only choose between options, it can't extract text,
    # so there are no additional parameters here: just the application + action.
    with TypeSafeClient(model="jev-latest") as client:
        response = client.system_one(
            state=text_in,
            questions={
                "command": Choice(
                    instructions="Which application and action does the user want?",
                    criteria=build_criteria(valid_applications),
                ),
            },
        )

    print(response)
    return response.answers["command"]


if __name__ == "__main__":
    transcript = "Hey Google, navigate to Ara."

    answer = cast(ChoiceAnswer, parse_transcript(transcript, VALID_APPLICATIONS))
    print(answer.model_dump_json(indent=2))
