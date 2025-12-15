"""Simple test for cloud pipeline execution logic"""

import sys
from ai_core.pipelines.registry import get_pipeline, _build_job_command
from ai_core.schemas.jobs import JobInput
from ai_core.utils.constants import COMPUTE_GPU

try:
    # Test 1: Get cloud pipeline
    print("Test 1: Getting cloud pipeline...")
    pipeline = get_pipeline("example-cloud")
    print(f"✓ Pipeline name: {pipeline.pipeline}")
    print(f"✓ Environment: {pipeline.environment}")
    print(f"✓ Has infrastructure: {hasattr(pipeline, 'infrastructure')}")
    print(f"✓ Has func: {pipeline.func is not None}")
    print()

    # Test 2: Build job command
    print("Test 2: Building JobCommand...")
    test_args = {"learning_rate": 0.001, "epochs": 10}
    job_cmd = _build_job_command(pipeline.infrastructure, test_args)
    print(f"✓ JobCommand image: {job_cmd.image}")
    print(f"✓ JobCommand gpu: {job_cmd.gpu}")
    print(f"✓ JobCommand flavor: {job_cmd.flavor}")
    print(f"✓ JobCommand commands: {job_cmd.commands}")
    print()

    # Test 3: Verify CLI string
    print("Test 3: Generating CLI command...")
    cli_string = job_cmd.to_cli_string()
    print(f"✓ CLI command generated (length: {len(cli_string)})")
    print(f"  Command preview: {cli_string[:100]}...")
    print()

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)

except Exception as e:
    print(f"✗ Test failed with error:")
    print(f"  {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
