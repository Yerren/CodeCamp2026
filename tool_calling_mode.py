import json

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from just_ask_1 import VALID_APPLICATIONS

load_dotenv()  # loads GEMINI_API_KEY from .env


class Parameter(BaseModel):
    name: str = Field(description="The parameter name, as listed for the chosen action")
    value: str = Field(
        description="The value for the parameter, taken from the transcript"
    )


class ParsedCommand(BaseModel):
    target_application: str = Field(description="The application the user wants to use")
    target_action: str = Field(
        description="The action to perform within that application"
    )
    additional_parameters: list[Parameter] = Field(
        default_factory=list,
        description="Any parameters for the action mentioned in the transcript",
    )


TOOL_NAME = "submit_parsed_command"


def parse_transcript(
    text_in: str, valid_applications: dict[str, dict]
) -> ParsedCommand:
    message = f"""For the following transcript, determine the target action the user wants to take,
    the target application, and any additional parameters.\n
    The target application, action and parameters must be chosen from the following
    valid applications (each lists its actions and the parameters each action accepts):\n
    {json.dumps(valid_applications, indent=2)}\n
    Submit your answer by calling the {TOOL_NAME} tool.

    transcript: {text_in}"""

    # The Pydantic schema becomes the parameters of a "fake" function.
    # The model fills in the arguments, which is our structured output.
    submit_tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=TOOL_NAME,
                description="Submit the parsed command extracted from the transcript.",
                parameters_json_schema=ParsedCommand.model_json_schema(),
            )
        ]
    )

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=message,
        config=types.GenerateContentConfig(
            tools=[submit_tool],
            # Force the model to call our tool (no free-text answer allowed)
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="ANY",
                    allowed_function_names=[TOOL_NAME],
                )
            ),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )

    function_call = response.function_calls[0]
    # Validate the tool-call arguments against the Pydantic model
    return ParsedCommand.model_validate(function_call.args)


if __name__ == "__main__":
    transcript = "Hey Google, navigate to Ara."

    result = parse_transcript(transcript, VALID_APPLICATIONS)
    print(result.model_dump_json(indent=2))
