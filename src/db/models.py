from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    responsibilities: List[str]

class WorkExperience(BaseModel):
    company: str
    location: str
    duration: str
    position: str
    projects: List[Project]

class Education(BaseModel):
    university: str
    year: str

class Candidate(BaseModel):
    name: str
    location: str
    contact_information: dict = Field(default_factory=dict)
    experience: str
    skills: List[str]
    work_experience: List[WorkExperience]
    education: List[Education]
    additional_skills: List[str]
    additional_information: List[str]