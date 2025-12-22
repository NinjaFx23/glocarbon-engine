# File: models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal

# --- 1. Define Specific Rules for Each Ecosystem ---

class GrasslandSpecs(BaseModel):
    """
    Rules for Grassland Projects (Verra VM0042)
    """
    area_hectares: float = Field(..., gt=0, description="Size of the land in hectares")
    health_index: float = Field(..., ge=0, le=1.0, description="Satellite health score (0.0 to 1.0)")
    livestock_density: float = Field(0.0, ge=0, description="Animals per hectare (creates methane penalty)")

class WetlandSpecs(BaseModel):
    """
    Rules for Wetland Projects (Verra VM0033)
    """
    area_hectares: float = Field(..., gt=0)
    water_level: Literal['stable', 'rising', 'declining'] # Must be one of these three

class ForestSpecs(BaseModel):
    """
    Rules for Forestry (Verra VM0007)
    """
    area_hectares: float = Field(..., gt=0)
    tree_density: int = Field(..., gt=0, description="Number of trees per hectare")

# --- 2. Define the General Structure ---

class EcosystemZone(BaseModel):
    """
    Represents one 'zone' of land (e.g., The swampy part of the ranch)
    """
    type: Literal['grassland', 'wetland', 'forest']
    # We use a generic dict here, and will validate specific details in the engine
    specs: dict 

class ProjectRequest(BaseModel):
    """
    The Master Blueprint for an incoming API request
    """
    project_name: str
    project_owner: str
    ecosystems: List[EcosystemZone]

    # Example of an automatic check
    @validator('project_name')
    def name_must_be_long_enough(cls, v):
        if len(v) < 5:
            raise ValueError('Project name is too short! Must be 5+ characters.')
        return v