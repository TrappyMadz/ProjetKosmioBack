from pydantic import BaseModel

class Metadata(BaseModel):
    category: str
    system: str
    type: str
    maturity: str
    cost_scale: str
    complexity: str
    last_update: str
    contributors: list[str]


class JsonSolution1(BaseModel):
        title: str
        metadata: Metadata
        summary: str

class Contexte(BaseModel):
        objective: str
        target_sites: list[str]
        scope_includes: list[str]
        scope_excludes: list[str]
        prerequisites: list[str]

class Mecanism(BaseModel):
        description: str
        variants: list[str]

class Applicability(BaseModel):
        conditions: list[str]
        avoid_if: list[str]
        constraints: list[str]

class Costs(BaseModel):
        capex: str
        opex: str
        roi: str

class Impacts(BaseModel):
        energy: str
        co2: str
        costs: Costs
        co_benefits: list[str]

class JsonSolution2(BaseModel):
        contexte: Contexte
        mecanism: Mecanism
        applicability: Applicability
        impacts: Impacts
        levers: list[str]


class ImplementationPathStep(BaseModel):
        step: str
        details: str

class Risk(BaseModel):
        risk: str
        mitigation: str
class Example(BaseModel):
        secteur: str
        resume: str
        link: str
class Resource(BaseModel):
        title: str
        type: str
        link: str
class JsonSolution3(BaseModel):
        implementation_path: list[ImplementationPathStep]
        risks: list[Risk]
        examples: list[Example]
        resources: list[Resource]
