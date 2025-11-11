__all__ = [
    "DomoJob",
    "DomoTrigger",
    "DomoTrigger_Schedule",
    # Application route exceptions
    "Application_GET_Error",
    "ApplicationError_NoJobRetrieved",
    "Application_CRUD_Error",
]

import datetime as dt
from dataclasses import dataclass, field
from typing import Optional

import httpx

from ...auth import DomoAuth
from ...base import DomoEntity
from ...routes import application as application_routes
from ...routes.application import (
    Application_CRUD_Error,
    Application_GET_Error,
    ApplicationError_NoJobRetrieved,
)
from .Job_Base import DomoJob_Base, DomoTrigger, DomoTrigger_Schedule


@dataclass(eq=False)
class DomoJob(DomoEntity):
    """A class for interacting with Domo Application Jobs.

    This class represents a job within a Domo application, providing methods
    for retrieving, creating, updating, and executing jobs.

    Attributes:
        auth: Authentication object for API requests
        id: Unique identifier for the job (job_id)
        application_id: ID of the parent application
        name: Name of the job
        raw: Raw API response data

        # Additional Job-specific attributes
        user_id: ID of the user who created the job
        logs_dataset_id: Dataset ID where job logs are stored
        execution_timeout: Timeout in minutes for job execution
        is_enabled: Whether the job is enabled (has triggers)
        customer_id: Customer ID
        created_dt: Job creation datetime
        updated_dt: Job last update datetime
        description: Job description
        execution_payload: Job execution configuration
        share_state: Job sharing state
        accounts: list of account IDs associated with the job
        triggers: list of job triggers
    """

    # Required DomoEntity attributes
    auth: DomoAuth = field(repr=False)
    id: str  # job_id
    raw: dict = field(default_factory=dict, repr=False)

    # Job-specific required attributes
    application_id: str = None
    name: str = None

    # Job-specific optional attributes
    user_id: str = None
    logs_dataset_id: str = None
    execution_timeout: int = 1440
    is_enabled: bool = False
    customer_id: str = None
    created_dt: Optional[dt.datetime] = None
    updated_dt: Optional[dt.datetime] = None
    description: str = None
    execution_payload: dict = field(default_factory=dict)
    share_state: dict = field(default_factory=dict)
    accounts: list[str] = field(default_factory=list)
    triggers: list[DomoTrigger] = field(default_factory=list)

    @property
    def display_url(self) -> str:
        """Generate the URL to display this job in the Domo interface.

        Returns:
            str: URL to view the job in Domo
        """
        return f"https://{self.auth.domo_instance}.domo.com/admin/applications/{self.application_id}/jobs/{self.id}"

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict):
        """Create a DomoJob instance from a dictionary representation.

        Args:
            auth: Authentication object
            obj: Dictionary containing job data from API

        Returns:
            DomoJob: New instance with populated attributes
        """
        # Use DomoJob_Base conversion logic
        base_obj = DomoJob_Base._convert_API_res_to_DomoJob_base_obj(obj=obj)

        return cls(
            auth=auth,
            raw=obj,
            **base_obj,
        )

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        application_id: str,
        job_id: str,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
    ):
        """Retrieve a job by its ID.

        Args:
            auth: Authentication object
            application_id: ID of the parent application
            job_id: Unique identifier of the job
            return_raw: Return raw ResponseGetData instead of DomoJob
            debug_api: Enable API debugging
            session: Optional httpx session for request pooling
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output

        Returns:
            DomoJob or ResponseGetData: The job object or raw response

        Raises:
            ApplicationError_NoneRetrieved: If job retrieval fails
        """
        res = await application_routes.get_application_job_by_id(
            auth=auth,
            application_id=application_id,
            job_id=job_id,
            session=session,
            debug_api=debug_api,
            parent_class=cls.__name__,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        if return_raw:
            return res

        return cls.from_dict(auth=auth, obj=res.response)

    async def update(
        self,
        body: dict = None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
    ):
        """Update this job's configuration.

        Args:
            body: Dictionary containing job update data (uses to_dict if None)
            return_raw: Return raw ResponseGetData instead of DomoJob
            debug_api: Enable API debugging
            session: Optional httpx session for request pooling
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output

        Returns:
            DomoJob or ResponseGetData: Updated job object or raw response

        Raises:
            CRUD_ApplicationJob_Error: If update fails
        """
        if body is None:
            body = self.to_dict()

        res = await application_routes.update_application_job(
            auth=self.auth,
            body=body,
            job_id=self.id,
            application_id=self.application_id,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        if return_raw:
            return res

        # Refresh the job data
        return await self.get_by_id(
            auth=self.auth,
            application_id=self.application_id,
            job_id=self.id,
            debug_api=debug_api,
            session=session,
        )

    async def execute(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
    ):
        """Execute this job.

        Args:
            return_raw: Return raw ResponseGetData
            debug_api: Enable API debugging
            session: Optional httpx session for request pooling
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output

        Returns:
            ResponseGetData: Response from job execution

        Raises:
            CRUD_ApplicationJob_Error: If execution fails
        """
        res = await application_routes.execute_application_job(
            auth=self.auth,
            application_id=self.application_id,
            job_id=self.id,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
        )

        if return_raw:
            return res

        return res

    def to_dict(self) -> dict:
        """Convert the job to a dictionary for API requests.

        Returns:
            dict: Dictionary representation of the job
        """
        trigger_ls = (
            [self.triggers[0].schedule.to_dict()] if len(self.triggers) > 0 else []
        )

        execution_payload = self.execution_payload or {}
        if self.logs_dataset_id:
            execution_payload.update({"metricsDatasetId": self.logs_dataset_id})

        return {
            "jobId": self.id,
            "jobName": self.name,
            "userId": self.user_id,
            "applicationId": self.application_id,
            "customerId": self.customer_id,
            "executionTimeout": self.execution_timeout,
            "executionPayload": execution_payload,
            "shareState": self.share_state,
            "triggers": trigger_ls,
            "jobDescription": self.description,
            "accounts": self.accounts,
        }

    @classmethod
    async def create(
        cls,
        auth: DomoAuth,
        application_id: str,
        job_name: str,
        execution_payload: dict,
        job_description: str = None,
        execution_timeout: int = 1440,
        accounts: list[str] = None,
        triggers: list[dict] = None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
    ):
        """Create a new job in the application.

        Args:
            auth: Authentication object
            application_id: ID of the parent application
            job_name: Name for the new job
            execution_payload: Job execution configuration
            job_description: Optional job description
            execution_timeout: Timeout in minutes (default 1440)
            accounts: list of account IDs
            triggers: list of job triggers
            return_raw: Return raw ResponseGetData instead of DomoJob
            debug_api: Enable API debugging
            session: Optional httpx session for request pooling
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output

        Returns:
            DomoJob or ResponseGetData: Created job object or raw response

        Raises:
            CRUD_ApplicationJob_Error: If creation fails
        """
        body = {
            "jobName": job_name,
            "jobDescription": job_description,
            "executionTimeout": execution_timeout,
            "executionPayload": execution_payload,
            "accounts": accounts or [],
            "triggers": triggers or [],
        }

        res = await application_routes.create_application_job(
            auth=auth,
            body=body,
            application_id=application_id,
            debug_api=debug_api,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=cls.__name__,
        )

        if return_raw:
            return res

        # Get the created job
        job_id = res.response.get("jobId")
        return await cls.get_by_id(
            auth=auth,
            application_id=application_id,
            job_id=job_id,
            debug_api=debug_api,
            session=session,
        )
