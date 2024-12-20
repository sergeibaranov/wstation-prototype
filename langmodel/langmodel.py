import vertexai
import models
from .functions import add_proposal_to_database
from pydantic import BaseModel
from typing import Literal

from vertexai.preview.generative_models import (
    Content,
    FunctionCall,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
    ToolConfig,
)

MODEL = "gemini-1.5-flash-002"


class Config(BaseModel):
    version: Literal[MODEL]


class LangModelClient:
    model: GenerativeModel

    def __init__(self, model: GenerativeModel):
        self.model = model

    @classmethod
    async def create(cls, config: Config) -> "LangModel":
        proposal_tool = Tool(
            function_declarations=[
                FunctionDeclaration.from_func(add_proposal_to_database),
            ],
        )

        proposal_tool_config = ToolConfig(
            function_calling_config=ToolConfig.FunctionCallingConfig(
                mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
            )
        )

        model = GenerativeModel(
            model_name=config.version,
            tools=[proposal_tool],
            tool_config=proposal_tool_config,
        )

        return cls(model)

    async def ingest_proposal(self, proposal_email: str) -> models.Proposal:
        response = self.model.generate_content(
            f"""
            {proposal_email}

            Please add the proposal from this email to the database.
            """,
        )
        function_call = response.candidates[0].content.parts[0].function_call
        return models.Proposal(**FunctionCall.to_dict(function_call)["args"])
