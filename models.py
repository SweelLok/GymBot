from pydantic import BaseModel


class Plan(BaseModel):
    name: str
    split: str
    exercise: str


class Power(BaseModel):
    benchpress: float
    pushups: float
    pullingup: float
    squatting: float
    frechpress: float
    onbiceps: float
