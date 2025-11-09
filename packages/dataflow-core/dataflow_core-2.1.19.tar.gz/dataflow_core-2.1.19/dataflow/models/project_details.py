from sqlalchemy import Column, String, Enum, DateTime, Integer, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from dataflow.db import Base

class ProjectDetails(Base):

    """TABLE 'PROJECT_DETAIL'
    Attributes:
        project_id (int): Primary key for the project detail entry.
        project_name (str): Name of the project.
        git_url (str): URL of the Git repository.
        git_branch (str): Branch of the Git repository.
        git_folder (str): Folder path in the Git repository.
        type (str): Foreign key referencing the APP_TYPE table.
        slug (str): Slug identifier for the project.
        runtime (str): Runtime environment for the project.
        py_env (int): Foreign key referencing the PYTHON_ENV table.
        launch_url (str): URL to launch the project.
        status (str): Deployment status of the project.
        last_deployed (datetime): Timestamp of the last deployment.
        created_at (datetime): Timestamp of when the project was created.
        created_by (str): User who created the project.
        org_id (int): Foreign key referencing the ORGANIZATION table.
        airflow_config_file (str): Path to the Airflow configuration file.
    
    Relationships:
        app_type: Relationship to the AppType model.
    
    Constraints:
        UniqueConstraint: Ensures unique combination of org_id and slug.
    """
    __tablename__ = "PROJECT_DETAIL"
    __table_args__ = (UniqueConstraint('org_id', 'slug', name='uq_project_org_slug'),)
    
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String, nullable=False)
    git_url = Column(String)
    git_branch = Column(String, nullable=True)
    git_folder = Column(String, nullable=True)
    type = Column(String, ForeignKey('APP_TYPE.name'), nullable=False)
    slug = Column(String, nullable=False)
    runtime = Column(String, nullable=False)
    py_env = Column(Integer, nullable=True)
    launch_url = Column(String, nullable=True)  
    status = Column(Enum("pending", "created" ,"deployed", "stopped", "failed", name="deployment_status"), default="created", server_default="created")
    last_deployed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(String, nullable=False)
    org_id = Column(Integer, ForeignKey('ORGANIZATION.id', ondelete='CASCADE'), nullable=False)
    airflow_config_file = Column(String, nullable=True)

    app_type = relationship("AppType")
