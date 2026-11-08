import time
from typing import cast

from dotenv import load_dotenv
from typesafe_sdk import Choice, ChoiceAnswer, TypeSafeClient

from just_ask_1 import VALID_APPLICATIONS

load_dotenv()  # loads TYPESAFE_API_KEY from .env


def parse_transcript(
    text_in: str, valid_applications: dict[str, dict]
) -> tuple[ChoiceAnswer, ChoiceAnswer]:
    # Two-step decision: first pick the application, then pick an action
    # from only that application's actions.
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
        app = valid_applications[app_answer.choice]

        # --- Call 2: which action, within the chosen application? ---
        start = time.perf_counter()
        action_response = client.system_one(
            state=text_in,
            questions={
                "action": Choice(
                    instructions=(
                        f"The user is using the {app_answer.choice} application "
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

    return app_answer, action_answer


if __name__ == "__main__":
    transcript = "Hey Google, navigate to Ara."

    app_answer, action_answer = parse_transcript(transcript, VALID_APPLICATIONS)

    print("\nApplication answer:")
    print(app_answer.model_dump_json(indent=2))
    print("\nAction answer:")
    print(action_answer.model_dump_json(indent=2))

    print(f"\ntarget_application: {app_answer.choice} ({app_answer.confidence:.2f})")
    print(
        f"target_action:      {action_answer.choice} ({action_answer.confidence:.2f})"
    )
