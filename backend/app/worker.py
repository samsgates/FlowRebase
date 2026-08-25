import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .config import get_settings
from .workflows.temporal import ModernizationWorkflow


async def main():
    settings = get_settings()
    client = await Client.connect(settings.temporal_address, namespace=settings.temporal_namespace)
    # Real enterprise installations register activity implementations from dedicated worker packages.
    worker = Worker(client, task_queue="flowrebase-modernization", workflows=[ModernizationWorkflow], activities=[])
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
