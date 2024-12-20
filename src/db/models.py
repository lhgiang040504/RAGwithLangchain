from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
import uuid

class DesiredJob(BaseModel):
    name: str = Field(..., description="The name or title of the candidate's desired job (e.g., Software Engineer).")
    skill_requirements: List[str] = Field(..., description="List of skills required for the desired job.")
    experience_requirements: str = Field(..., description="Description of the experience requirements for the desired job.")
    additional_details: Optional[str] = Field(None, description="Additional details or preferences for the desired job, if any.")

class Project(BaseModel):
    name: str = Field(..., description="The name of the project.")
    description: str = Field(..., description="A brief description of the project.")
    technologies: List[str] = Field(..., description="List of technologies used in the project.")
    responsibilities: List[str] = Field(..., description="List of responsibilities or tasks performed in the project.")

class WorkExperience(BaseModel):
    company: str = Field(..., description="Name of the company.")
    location: str = Field(..., description="Location of the company.")
    duration: str = Field(..., description="Duration of employment (e.g., Jan 2020 - Dec 2022).")
    position: str = Field(..., description="Position held at the company.")
    projects: List[Project] = Field(..., description="List of projects worked on during this job.")

class Education(BaseModel):
    university: str = Field(..., description="Name of the university or educational institution.")
    year: str = Field(..., description="Year of graduation or attendance.")

class Candidate(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")   
    name: str = Field(..., description="Full name of the candidate.")
    location: str = Field(..., description="Current location of the candidate.")
    contact_information: Dict[str, str] = Field(default_factory=dict, description="Contact details such as phone, email, and LinkedIn.")
    experience: str = Field(..., description="Overall experience of the candidate (e.g., 5 years in software development).")
    skills: List[str] = Field(..., description="Technical skills and tools the candidate is proficient in.")
    work_experience: List[WorkExperience] = Field(..., description="List of previous work experiences.")
    education: List[Education] = Field(..., description="Educational background of the candidate.")
    additional_skills: List[str] = Field(..., description="Additional skills the candidate possesses that may not directly relate to technical expertise.")
    additional_information: List[str] = Field(..., description="Any other relevant information about the candidate.")
    desired_job: DesiredJob = Field(..., description="Information about the candidate's desired job.")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "name": "Nguyen Van A",
                "location": "Thu Duc, Ho Chi Minh",
                "contact_information": {
                    "phone_number": "0123456789",
                    "email": "example1@gmail.com",
                    "linkedin": "https://www.linkedin.com/in/nguyenvana"
                },
                "experience": "3.5 years in software development",
                "skills": ["Python", "Java", "C++"],
                "work_experience": [
                    {
                        "company": "ABC Corp",
                        "location": "Ho Chi Minh City",
                        "duration": "Jan 2020 - Dec 2023",
                        "position": "Software Engineer",
                        "projects": [
                            {
                                "name": "E-commerce Platform",
                                "description": "Developed a scalable e-commerce platform.",
                                "technologies": ["Django", "React", "PostgreSQL"],
                                "responsibilities": ["Backend development", "Database design"]
                            }
                        ]
                    }
                ],
                "education": [
                    {
                        "university": "Ho Chi Minh University of Technology",
                        "year": "2019"
                    }
                ],
                "additional_skills": ["Team management", "Public speaking"],
                "additional_information": ["Certified AWS Developer", "Volunteered as a coding instructor"],
                "desired_job": {
                    "name": "Senior Software Engineer",
                    "skill_requirements": ["Python", "AWS", "Machine Learning"],
                    "experience_requirements": "5+ years in software engineering with leadership experience.",
                    "additional_details": "Prefer remote or hybrid work arrangements."
                }
            }
        }

class Job(BaseModel):
    id : str = Field(..., default_factory=uuid.uuid4, alias="_id")
    name: str = Field(..., description="The title or name of the job position (e.g., Software Engineer).")
    company_name: str = Field(..., description="The name of the company offering the job.")
    location: str = Field(..., description="The location where the job is based.")
    job_summary: str = Field(..., description="A brief summary or description of the job role.")
    skill_requirements: List[str] = Field(..., description="List of skills required for the job.")
    experience_requirements: str = Field(..., description="The required experience for the job role.")
    responsibilities: List[str] = Field(..., description="List of responsibilities or tasks involved in the job.")
    qualifications: Optional[List[str]] = Field(None, description="List of educational qualifications or certifications required.")
    benefits: Optional[List[str]] = Field(None, description="List of benefits offered by the company.")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Senior Software Engineer",
                "company_name": "Tech Innovations Inc.",
                "location": "Ho Chi Minh City, Vietnam",
                "job_summary": "Develop and maintain scalable web applications.",
                "skill_requirements": ["Python", "Django", "JavaScript", "AWS"],
                "experience_requirements": "5+ years in software engineering, with a focus on backend development.",
                "responsibilities": [
                    "Designing and implementing backend solutions.",
                    "Collaborating with frontend teams to deliver integrated solutions."
                ],
                "qualifications": ["Bachelor's degree in Computer Science", "AWS Certified Solutions Architect"],
                "benefits": ["Health insurance", "Remote work options", "Annual bonus"]
            }
        }
