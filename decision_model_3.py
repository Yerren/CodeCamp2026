import time
from typing import cast

from dotenv import load_dotenv
from typesafe_sdk import Choice, ChoiceAnswer, TypeSafeClient

from just_ask_1 import VALID_APPLICATIONS

load_dotenv()  # loads TYPESAFE_API_KEY from .env

NONE_OPTION = "none"


def number_words(text_in: str) -> tuple[list[str], str]:
    """Split the transcript into words and give each one an ID.
    Returns the words plus a state string showing the transcript and the numbered words."""
    words = text_in.split()
    numbered = "\n".join(f"{i}: {word}" for i, word in enumerate(words))
    state = f"transcript: {text_in}\n\nwords (id: word):\n{numbered}"
    return words, state


def parse_transcript(text_in: str, valid_applications: dict[str, dict]) -> dict:
    words, state = number_words(text_in)

    # Every word ID is a valid choice, plus "none" for parameters not mentioned
    word_criteria: dict[str, str | None] = {str(i): word for i, word in enumerate(words)}
    word_criteria[NONE_OPTION] = "The parameter is not mentioned in the transcript"

    with TypeSafeClient(model="jev-latest") as client:
        # --- Call 1: which application? ---
        start = time.perf_counter()
        app_response = client.system_one(
            state=text_in,
            questions={
                "application": Choice(
                    instructions="Which application does the user want to use?",
                    criteria={
                        name: app["description"]
                        for name, app in valid_applications.items()
                    },
                ),
            },
        )
        elapsed = time.perf_counter() - start
        print(f"Application call took {elapsed:.2f}s")

        app_answer = cast(ChoiceAnswer, app_response.answers["application"])
        app_name = app_answer.choice
        app = valid_applications[app_name]

        # --- Call 2: which action, within the chosen application? ---
        start = time.perf_counter()
        action_response = client.system_one(
            state=text_in,
            questions={
                "action": Choice(
                    instructions=(
                        f"The user is using the {app_name} application "
                        f"({app['description']}). Which action do they want?"
                    ),
                    criteria={
                        action_name: action_name.replace("_", " ")
                        for action_name in app["actions"]
                    },
                ),
            },
        )
        elapsed = time.perf_counter() - start
        print(f"Action call took {elapsed:.2f}s")

        action_answer = cast(ChoiceAnswer, action_response.answers["action"])
        action_name = action_answer.choice
        parameters = app["actions"][action_name]

        # --- Call 3: extract each parameter as a phrase (start word ID, end word ID) ---
        # All the start/end questions go in one call and are answered in parallel.
        extracted: dict[str, str | None] = {}
        if parameters:
            questions = {}
            for param, param_type in parameters.items():
                described = f'the "{param}" parameter ({param_type}) of the {app_name} {action_name} action'
                questions[f"{param}.phrase_start"] = Choice(
                    instructions=(
                        f"Extract {described} as a phrase from the transcript. "
                        "Pick the ID of the FIRST word of the phrase, "
                        f'or "{NONE_OPTION}" if it is not mentioned.'
                    ),
                    criteria=word_criteria,
                )
                questions[f"{param}.phrase_end"] = Choice(
                    instructions=(
                        f"Extract {described} as a phrase from the transcript. "
                        "Pick the ID of the LAST word of the phrase, "
                        f'or "{NONE_OPTION}" if it is not mentioned.'
                    ),
                    criteria=word_criteria,
                )

            start = time.perf_counter()
            param_response = client.system_one(state=state, questions=questions)
            elapsed = time.perf_counter() - start
            print(f"Parameter call took {elapsed:.2f}s")

            for param in parameters:
                start_id = param_response.answers[f"{param}.phrase_start"].choice
                end_id = param_response.answers[f"{param}.phrase_end"].choice
                print(f"  {param}: start={start_id} end={end_id}")
                if NONE_OPTION in (start_id, end_id):
                    extracted[param] = None
                    continue
                first, last = sorted((int(start_id), int(end_id)))
                extracted[param] = " ".join(words[first : last + 1]).strip(".,!?")

    return {
        "target_application": app_name,
        "target_action": action_name,
        "additional_parameters": {k: v for k, v in extracted.items() if v is not None},
    }


if __name__ == "__main__":
    import json

    transcript = "Hey Google, navigate to Ara."

    result = parse_transcript(transcript, VALID_APPLICATIONS)
    print(json.dumps(result, indent=2))
