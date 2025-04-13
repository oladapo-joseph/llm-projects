import json
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database configuration
DATABASE_URL = "sqlite:///all_data.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# FileInfo model representing the file_info table
class Details(Base):
    __tablename__ = "database"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, nullable=False, unique=True)
    file_path = Column(String, nullable=False)

    def __repr__(self):
        return f"<FileInfo(name='{self.file_name}', file_path='{self.file_path}')>"

# Create database tables
Base.metadata.create_all(engine)

# Session factory for database operations
Session = sessionmaker(bind=engine)

# Insert a new record into the file_info table
def addFile(name, csv_file_path):
    session = Session()
    try:
        file = session.query(Details).filter_by(file_name=name).first()
        print('Fetched DB')
        if file:
            return {"success": False, "message": f"A dataset with the name '{name}' already exists."}
        else:
            print('trying to save to DB')
            file_info = Details(file_name=name, file_path=csv_file_path)
            session.add(file_info)
            session.commit()
        return {"success": True, "message": f"Dataset '{name}' added successfully!"}
    except Exception as e:
        return {"success": False, "message": f"Error inserting file info: {e}"}
    finally:
        session.close()

# Retrieve all records from the file_info table
def getHistorical()->list:
    """
        This function gets the list of all existing stored data
    
    """
    session = Session()
    try:
        files = session.query(Details).all()
        return [(file.file_name, file.file_path) for file in files]
    except Exception as e:
        print(e)
    finally:
        session.close()


def getDirectory(name):
    session = Session()
    path = ''
    try:
        file = session.query(Details).filter_by(file_name=name).first()
        path = file.file_path 
    except Exception as e :
        print('file doesnt exist')
    return path