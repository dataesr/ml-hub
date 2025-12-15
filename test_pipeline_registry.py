"""
Test script for pipeline registry
This script verifies that the pipeline registry can properly list and configure pipelines.
"""
from ai_core.pipelines.registry import list_pipelines, get_pipeline

def test_list_pipelines():
    """Test listing all registered pipelines."""
    print("Testing list_pipelines()...")
    pipelines = list_pipelines()
    print(f"Found {len(pipelines)} pipelines:")
    for p in pipelines:
        print(f"  - {p.pipeline} (environment={p.environment})")
    print()

def test_get_pipeline():
    """Test getting a specific pipeline."""
    print("Testing get_pipeline()...")
    
    # Test local pipeline
    try:
        pipeline = get_pipeline("example-local")
        print(f"✓ Retrieved local pipeline: {pipeline.pipeline}")
        print(f"  Environment: {pipeline.environment}")
        print(f"  Description: {pipeline.description}")
        print(f"  Tags: {pipeline.tags}")
    except Exception as e:
        print(f"✗ Error getting local pipeline: {e}")
    
    print()
    
    # Test cloud pipeline
    try:
        pipeline = get_pipeline("example-cloud")
        print(f"✓ Retrieved cloud pipeline: {pipeline.pipeline}")
        print(f"  Environment: {pipeline.environment}")
        print(f"  Description: {pipeline.description}")
        print(f"  Tags: {pipeline.tags}")
        if hasattr(pipeline, 'infrastructure'):
            print(f"  Infrastructure: {pipeline.infrastructure}")
    except Exception as e:
        print(f"✗ Error getting cloud pipeline: {e}")
    
    print()

def test_pipeline_schema():
    """Test that pipeline schemas are properly generated."""
    print("Testing pipeline schemas...")
    
    try:
        pipeline = get_pipeline("example-local")
        if pipeline.input_schema:
            print(f"✓ Local pipeline schema: {pipeline.input_schema.__name__}")
            print(f"  Fields: {list(pipeline.input_schema.model_fields.keys())}")
        else:
            print("✗ Local pipeline has no schema")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()
    
    try:
        pipeline = get_pipeline("example-cloud")
        if pipeline.input_schema:
            print(f"✓ Cloud pipeline schema: {pipeline.input_schema.__name__}")
            print(f"  Fields: {list(pipeline.input_schema.model_fields.keys())}")
        else:
            print("✗ Cloud pipeline has no schema")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Pipeline Registry Test")
    print("=" * 60)
    print()
    
    test_list_pipelines()
    test_get_pipeline()
    test_pipeline_schema()
    
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)
