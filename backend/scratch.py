import asyncio
from app.pipeline.orchestrator import run_pipeline
from app.core.config import settings

async def main():
    print("Running pipeline...")
    result = await run_pipeline("Build a CRM with login, contacts, dashboard, admin analytics")
    print("Status:", result.status)
    if result.status == "failed":
        print("Metrics:", result.metrics)

if __name__ == "__main__":
    asyncio.run(main())
