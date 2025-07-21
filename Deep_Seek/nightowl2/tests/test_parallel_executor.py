import pytest
import asyncio
from core.parallel_executor import ParallelExecutor

async def dummy_task(target):
    return {"data": f"Result for {target}"}

@pytest.mark.asyncio
async def test_parallel_execution():
    executor = ParallelExecutor(max_workers=4)
    tools = [dummy_task, dummy_task, dummy_task]
    results = await executor.run_tools(tools, "TestPhase", "example.com")
    assert len(results) == 3
    assert "Result for example.com" in results[0]['data']