from pydantic import BaseModel, Field
from .file_loader import Loader
from .vectorstore import VectorDB
from .offline_rag import Offline_RAG

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

class InputQA(BaseModel):
    question: str = Field(..., title = 'Question to ask the model')

class OutputQA(BaseModel):
    answer: str = Field(..., title = 'Answer from the model')

def build_rag_chatbot_chain(llm, data_dir, data_type, workers_for_load=2):
    doc_loaded = Loader(file_type = data_type).load_dir(data_dir, workers=workers_for_load)
    retriever = VectorDB(documents = doc_loaded).get_retriever()
    rag_chain = Offline_RAG(llm).get_chain(retriever)

    return rag_chain

def build_rag_parser_chain(llm, object):
    cv_parser = JsonOutputParser(pydantic_object=object)
    cv_prompt = PromptTemplate(
        input_variables=["cv_content"],  # Only include the actual variables used in the template
        template="""
        You are a highly skilled language model specializing in extracting structured information from unstructured text. Your task is to parse resumes or CVs into a structured JSON format. Extract and organize the following information:

        - **Name**: The full name of the candidate.
        - **Location**: The city and country where the candidate resides.
        - **Contact_Information**: Email address, phone number and other contact details (if available).
        - **Experience**: Total years of professional experience or a summary.
        - **Skills**: List of technical, professional, or interpersonal skills mentioned.
        - **Work_Experience**: For each job, include:
        - Company: Name of the organization.
        - Location: City and country.
        - Duration: Start and end dates or the total duration.
        - Position: Job title.
        - Projects: For each project, include:
            - Name: Project name.
            - Description: What the project was about.
            - Technologies: Technologies used in the project.
            - Responsibilities: Key responsibilities undertaken.
        - **Education**: Include:
        - University: Name of the institution.
        - Year: Graduation year or years of attendance.
        - **Additional_Skills**: Any extra skills or certifications.
        - **Additional_Information**: Other professional qualities or awards, or achievements.

        Return the output strictly in JSON format, without any additional commentary or text.
        
        Example:
        CV Content:
        ```
        John Doe
        Address: New York, USA
        Email: john.doe@example.com | Phone: +123456789
        Professional Experience: Over 10 years in software development and project management.
        Skills: Python, JavaScript, React, Project Management, Agile Methodologies.
        Work Experience:
        - Company: Tech Solutions Inc.
            Location: San Francisco, USA
            Duration: Jan 2015 - Dec 2020
            Position: Senior Software Engineer
            Projects:
            - Name: Inventory Management System
                Description: A web-based inventory tracking system.
                Technologies: Python, Django, PostgreSQL
                Responsibilities: Designed and implemented backend services.
        Education:
        - University: Stanford University
            Year: 2014
        Additional Skills: Certified Scrum Master
        Additional Information: Received Employee of the Year award (2019).
        ```

        Expected JSON Output:
        ```
        dict(
        "name": "John Doe",
        "location": "New York, USA",
        "contact_information": dict('emai': "john.doe@example.com, 'phone': 123456789"),
        "experience": "Over 10 years in software development and project management.",
        "skills": ["Python", "JavaScript", "React", "Project Management", "Agile Methodologies"],
        "work_experience": [
            dict(
            "company": "Tech Solutions Inc.",
            "location": "San Francisco, USA",
            "duration": "Jan 2015 - Dec 2020",
            "position": "Senior Software Engineer",
            "projects": [
                dict(
                "name": "Inventory Management System",
                "description": "A web-based inventory tracking system.",
                "technologies": ["Python", "Django", "PostgreSQL"],
                "responsibilities": ["Designed and implemented backend services."]
                )
            ]
            )
        ],
        "education": [
            dict(
            "university": "Stanford University",
            "year": "2014"
            )
        ],
        "additional_skills": ["Certified Scrum Master"],
        "additional_information": ["Received Employee of the Year award (2019)."]
        )
        ```
        Now parse the following CV content:
        ```
        {cv_content}
        ```
        """
    )
    
    chain = cv_prompt | llm | cv_parser

    return chain