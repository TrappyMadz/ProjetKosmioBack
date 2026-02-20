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


class Json1(BaseModel):
        title: str
        metadata: Metadata
        summary: str

        def to_json(self):
            return {
                "title": self.title,
                "metadata": self.metadata.dict(),
                "summary": self.summary
            }
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

class Costs(BaseModel):
        capex: str
        opex: str
        def to_json(self):
            return {
                "capex": self.capex,
                "opex": self.opex
            }
class Impacts(BaseModel):
        energy: str
        co2: str
        costs: Costs
        co_benefits: list[str]
        def to_json(self):
            return {
                "energy": self.energy,
                "co2": self.co2,
                "costs": self.costs.to_json(),
                "co_benefits": self.co_benefits
            }

class Json2(BaseModel):
        contexte: Contexte
        mecanism: Mecanism
        applicability: Applicability
        impacts: Impacts
        levers: list[str]

        def to_json(self):
            return {
                "contexte": self.contexte.dict(),
                "mecanism": self.mecanism.dict(),
                "applicability": self.applicability.dict(),
                "impacts": self.impacts.to_json(),
                "levers": self.levers
            }
       


class ImplementationPathStep(BaseModel):
        step: str
        details: str

class Risk(BaseModel):
        risk: str
class Example(BaseModel):
        secteur: str
        resume: str
        link: str
class Resource(BaseModel):
        title: str
        type: str
        link: str
class Json3(BaseModel):
        implementation_path: list[ImplementationPathStep]
        risks: list[Risk]
        examples: list[Example]
        resources: list[Resource]
        
        def to_json(self):
            return {
                "implementation_path": [step.dict() for step in self.implementation_path],
                "risks": [risk.dict() for risk in self.risks],
                "examples": [example.dict() for example in self.examples],
                "resources": [resource.dict() for resource in self.resources]
            }