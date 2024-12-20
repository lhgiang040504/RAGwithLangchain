'''from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:admin@cluster0.gsgut.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client.HR_MANAGER

collection_name = db['Candidate']'''

#from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.database import Database

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.database = None

    async def init(self):
        """Initialize MongoDB connection if not already established"""
        if not self.client:
            self.client = MongoClient(self.uri)
        if not self.database:
            self.database = self.client[self.db_name]  # Access or create the database

    async def close(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
    
    def get_database(self) -> Database:
        """Return the database instance"""
        return self.database
