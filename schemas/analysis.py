from pydantic import BaseModel

class AnalysisPlan(BaseModel):
    goal: str
    inputs: list[str]
    outputs: list[str]
    libraries: list[str]
