"""EnvHub core implementation"""

import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from rock.envhub.api.schemas import DeleteEnvRequest, EnvInfo, GetEnvRequest, ListEnvsRequest, RegisterRequest
from rock.envhub.database.base import Base
from rock.envhub.database.docker_env import RockDockerEnv

# Configure logging
logger = logging.getLogger(__name__)


class EnvHub(ABC):
    """EnvHub abstract base class"""

    def __init__(self, db_url: str = "sqlite:///./rock_envs.db"):
        """
        Initialize EnvHub

        Args:
            db_url: Database URL
        """
        self.db_url = db_url

    @abstractmethod
    def register(self, request: RegisterRequest) -> EnvInfo:
        """
        Register or update environment

        Args:
            request: Registration request

        Returns:
            Environment information
        """
        pass

    @abstractmethod
    def get_env(self, request: GetEnvRequest) -> EnvInfo:
        """
        Get environment

        Args:
            request: Get environment request

        Returns:
            Environment information
        """
        pass

    @abstractmethod
    def list_envs(self, request: ListEnvsRequest) -> list[EnvInfo]:
        """
        List environments

        Args:
            request: List environments request

        Returns:
            List of environment information
        """
        pass

    @abstractmethod
    def delete_env(self, request: DeleteEnvRequest) -> bool:
        """
        Delete environment

        Args:
            request: Delete environment request

        Returns:
            Returns True if deletion is successful, otherwise returns False
        """
        pass


class DockerEnvHub(EnvHub):
    """Docker environment Hub class, inherited from EnvHub"""

    def __init__(self, db_url: str = "sqlite:///./rock_envs.db"):
        """
        Initialize DockerEnvHub

        Args:
            db_url: Database URL
        """
        super().__init__(db_url=db_url)
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        """Context manager for database sessions.
        Provides a SQLAlchemy session that automatically handles commit/rollback
        and ensures proper cleanup of resources.
        Yields:
            A SQLAlchemy session object.
        """
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rollback due to error: {e}")
            raise
        finally:
            session.close()

    def register(self, request: RegisterRequest) -> EnvInfo:
        """
        Register or update environment

        Args:
            request: Registration request

        Returns:
            Environment information
        """
        logger.info(f"Registering environment: {request.env_name}")
        with self.get_session() as session:
            try:
                # Check if environment already exists
                db_env = session.query(RockDockerEnv).filter(RockDockerEnv.env_name == request.env_name).first()
                if db_env:
                    # Update existing environment
                    db_env.image = request.image
                    db_env.owner = request.owner
                    db_env.description = request.description
                    db_env.tags = request.tags
                    db_env.extra_spec = request.extra_spec
                    db_env.update_at = datetime.now()
                else:
                    # Create new environment
                    db_env = RockDockerEnv(
                        env_name=request.env_name,
                        image=request.image,
                        owner=request.owner,
                        description=request.description,
                        tags=request.tags,
                        extra_spec=request.extra_spec,
                    )
                    session.add(db_env)

                session.commit()
                session.refresh(db_env)

                return EnvInfo(
                    env_name=db_env.env_name,
                    image=db_env.image,
                    owner=db_env.owner,
                    description=db_env.description,
                    tags=db_env.tags if db_env.tags else [],
                    extra_spec=db_env.extra_spec,
                    create_at=db_env.create_at,
                    update_at=db_env.update_at,
                )
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to register environment {request.env_name}: {e}")
                raise

    def get_env(self, request: GetEnvRequest) -> EnvInfo:
        """
        Get environment

        Args:
            request: Get environment request

        Returns:
            Environment information
        """
        logger.info(f"Getting environment: {request.env_name}")
        with self.get_session() as session:
            db_env = session.query(RockDockerEnv).filter(RockDockerEnv.env_name == request.env_name).first()
            if not db_env:
                raise Exception(f"Environment {request.env_name} not found")

            return EnvInfo(
                env_name=db_env.env_name,
                image=db_env.image,
                owner=db_env.owner,
                description=db_env.description,
                tags=db_env.tags if db_env.tags else [],
                extra_spec=db_env.extra_spec,
                create_at=db_env.create_at,
                update_at=db_env.update_at,
            )

    def list_envs(self, request: ListEnvsRequest) -> list[EnvInfo]:
        """
        List environments

        Args:
            request: List environments request

        Returns:
            List of environment information
        """
        logger.info(f"Listing environments with owner={request.owner}, tags={request.tags}")
        with self.get_session() as session:
            query = session.query(RockDockerEnv)
            if request.owner:
                query = query.filter(RockDockerEnv.owner == request.owner)
            if request.tags:
                # Filter environments that have any of the specified tags
                filtered_envs = []
                all_envs = query.all()
                for env in all_envs:
                    if env.tags and any(tag in env.tags for tag in request.tags):
                        filtered_envs.append(env)
                envs = []
                for db_env in filtered_envs:
                    envs.append(
                        EnvInfo(
                            env_name=db_env.env_name,
                            image=db_env.image,
                            owner=db_env.owner,
                            description=db_env.description,
                            tags=db_env.tags if db_env.tags else [],
                            extra_spec=db_env.extra_spec,
                            create_at=db_env.create_at,
                            update_at=db_env.update_at,
                        )
                    )
                return envs

            db_envs = query.all()
            envs = []
            for db_env in db_envs:
                envs.append(
                    EnvInfo(
                        env_name=db_env.env_name,
                        image=db_env.image,
                        owner=db_env.owner,
                        description=db_env.description,
                        tags=db_env.tags if db_env.tags else [],
                        extra_spec=db_env.extra_spec,
                        create_at=db_env.create_at,
                        update_at=db_env.update_at,
                    )
                )

            return envs

    def delete_env(self, request: DeleteEnvRequest) -> bool:
        """
        Delete environment

        Args:
            request: Delete environment request

        Returns:
            Returns True if deletion is successful, otherwise returns False
        """
        logger.info(f"Deleting environment: {request.env_name}")
        with self.get_session() as session:
            db_env = session.query(RockDockerEnv).filter(RockDockerEnv.env_name == request.env_name).first()
            if not db_env:
                return False

            session.delete(db_env)
            session.commit()
            return True
