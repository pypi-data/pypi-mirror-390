from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Any, cast

from adaptive_sdk.graphql_client import (
    CursorPageInput,
    JobInput,
    ListJobsJobs,
    ListJobsFilterInput,
    JobKind,
    ListJobsJobsNodes,
)


from .base_resource import SyncAPIResource, AsyncAPIResource, UseCaseResource
from adaptive_sdk.output_types import JobDataPlus

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


class Jobs(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Resource to interact with jobs.
    """

    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    def get(self, job_id: str) -> JobDataPlus | None:
        job_data = self._gql_client.describe_job(id=job_id).job
        return JobDataPlus.from_job_data(job_data) if job_data else None

    def list(
        self,
        first: int | None = 100,
        last: int | None = None,
        after: str | None = None,
        before: str | None = None,
        kind: (
            list[
                Literal[
                    "TRAINING",
                    "EVALUATION",
                    "DATASET_GENERATION",
                    "MODEL_CONVERSION",
                    "CUSTOM",
                ]
            ]
            | None
        ) = None,
        use_case: str | None = None,
    ) -> ListJobsJobs:
        use_case = self.optional_use_case_key(use_case)
        page = CursorPageInput(first=first, last=last, after=after, before=before)
        validated_filter = ListJobsFilterInput(
            useCase=use_case,
            kind=[JobKind(k) for k in kind] if kind else None,
        )
        jobs = self._gql_client.list_jobs(page=page, filter=validated_filter, order=[]).jobs
        new_nodes: list[JobDataPlus] = []
        for i in jobs.nodes:
            new_nodes.append(JobDataPlus.from_job_data(i))
        jobs.nodes = cast(list[ListJobsJobsNodes], new_nodes)

        return jobs

    def run(
        self,
        recipe_key: str,
        args: dict[str, Any],
        num_gpus: int,
        name: str | None = None,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> JobDataPlus:
        job_data = self._gql_client.create_job(
            input=JobInput(
                recipe=recipe_key,
                args=args,
                useCase=self.use_case_key(use_case),
                computePool=compute_pool,
                name=name,
                numGpus=num_gpus,
            )
        ).create_job
        return JobDataPlus.from_job_data(job_data)

    def cancel(self, job_id: str) -> JobDataPlus:
        job_data = self._gql_client.cancel_job(job_id=job_id).cancel_job
        return JobDataPlus.from_job_data(job_data)


class AsyncJobs(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Async resource to interact with external rewards servers.
    """

    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    async def get(self, job_id: str) -> JobDataPlus | None:
        job_data = (await self._gql_client.describe_job(id=job_id)).job
        return JobDataPlus.from_job_data(job_data) if job_data else None

    async def list(
        self,
        first: int | None = 100,
        last: int | None = None,
        after: str | None = None,
        before: str | None = None,
        kind: (
            list[
                Literal[
                    "TRAINING",
                    "EVALUATION",
                    "DATASET_GENERATION",
                    "MODEL_CONVERSION",
                    "CUSTOM",
                ]
            ]
            | None
        ) = None,
        use_case: str | None = None,
    ) -> ListJobsJobs:
        page = CursorPageInput(first=first, last=last, after=after, before=before)
        validated_filter = ListJobsFilterInput(
            useCase=self.use_case_key(use_case),
            kind=[JobKind[k] for k in kind] if kind else None,
        )
        jobs = (await self._gql_client.list_jobs(page=page, filter=validated_filter)).jobs
        new_nodes: list[JobDataPlus] = []
        for i in jobs.nodes:
            new_nodes.append(JobDataPlus.from_job_data(i))
        jobs.nodes = cast(list[ListJobsJobsNodes], new_nodes)
        return jobs

    async def run(
        self,
        recipe_key: str,
        args: dict[str, Any],
        num_gpus: int,
        name: str | None = None,
        use_case: str | None = None,
        compute_pool: str | None = None,
    ) -> JobDataPlus:
        job_data = (
            await self._gql_client.create_job(
                input=JobInput(
                    recipe=recipe_key,
                    args=args,
                    useCase=self.use_case_key(use_case),
                    computePool=compute_pool,
                    numGpus=num_gpus,
                    name=name,
                )
            )
        ).create_job
        return JobDataPlus.from_job_data(job_data)

    async def cancel(self, job_id: str) -> JobDataPlus:
        job_data = (await self._gql_client.cancel_job(job_id=job_id)).cancel_job
        return JobDataPlus.from_job_data(job_data)
