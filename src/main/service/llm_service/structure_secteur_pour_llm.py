from pydantic import BaseModel

     
class Metadata(BaseModel):
    sub_sectors: list[str]
    company_size: str
    last_update: str
    contributors: list[str]


class JsonSecteur1(BaseModel):
        title: str
        metadata: Metadata
        summary: str

class EmissionsProfile(BaseModel):
        process: str
        utilities: str
        building: str
        transport: str
        waste: str

class Challenge(BaseModel):
        title: str
        description: str

class SystemMatrix(BaseModel):
        system: str
        impact: str
        priority: str
        solutions: list[str]

class JsonSecteur2(BaseModel):
        description: str
        emissions_profile: list[EmissionsProfile]
        contexte: list[Challenge]
        regulations: list[str]
        systems_matrix: list[SystemMatrix]


class SectorPath(BaseModel):
        phase: str
        action: str

class UseCase(BaseModel):
        sub_sector: str
        actions: str
        results: str
        link: str

class Resource(BaseModel):
        title: str
        type: str
        link: str
class JsonSecteur3(BaseModel):
        sector_path: list[SectorPath]
        use_cases: list[UseCase]
        resources: list[Resource]
