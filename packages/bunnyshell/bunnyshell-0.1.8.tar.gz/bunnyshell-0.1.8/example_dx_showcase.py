"""
🎨 Bunnyshell Python SDK - Developer Experience Showcase

This example demonstrates the GOLD-standard DX achieved through the hybrid approach:
- Auto-generated type-safe models from OpenAPI spec
- Hand-crafted Pythonic client for superior UX
- Best of both worlds!

Features Demonstrated:
✅ Full IDE autocomplete on all models
✅ Type safety with Pydantic v2 validation
✅ Convenience properties for common operations
✅ Beautiful repr() for debugging
✅ Pythonic, E2B-inspired API
✅ Machine-readable error codes
"""

import os
from bunnyshell import Sandbox
from bunnyshell.models import ExecutionResult, FileInfo, Language, ErrorCode
from bunnyshell.errors import FileNotFoundError, CodeExecutionError

# API key from environment
API_KEY = os.environ.get("BUNNYSHELL_API_KEY", "hopx_f0dfeb804627ca3c1ccdd3d43d2913c9")


def showcase_type_safety():
    """Demonstrate type-safe models with IDE autocomplete."""
    print("\n" + "="*70)
    print("🎯 TYPE SAFETY & IDE AUTOCOMPLETE")
    print("="*70)
    
    # Type-safe model creation with validation
    result: ExecutionResult = ExecutionResult(
        stdout="Hello, World!\n",
        stderr="",
        exit_code=0,
        execution_time=0.123,
        success=True
    )
    
    # IDE knows all properties!
    print(f"✅ result.stdout type-checked: {result.stdout.strip()}")
    print(f"✅ result.exit_code type-checked: {result.exit_code}")
    print(f"✅ result.execution_time type-checked: {result.execution_time:.3f}s")
    
    # Enums for type safety
    lang: Language = Language.PYTHON
    print(f"✅ Language enum (type-safe): {lang.value}")
    
    # Error codes
    error_code: ErrorCode = ErrorCode.FILE_NOT_FOUND
    print(f"✅ ErrorCode enum (machine-readable): {error_code.value}")


def showcase_convenience_methods():
    """Demonstrate convenience properties for DX."""
    print("\n" + "="*70)
    print("🎁 CONVENIENCE METHODS")
    print("="*70)
    
    # FileInfo with convenience properties
    file = FileInfo(
        name="large_dataset.csv",
        path="/workspace/large_dataset.csv",
        size=5242880,  # 5MB in bytes
        is_directory=False
    )
    
    print(f"✅ file.name: {file.name}")
    print(f"✅ file.size: {file.size} bytes (raw)")
    print(f"✅ file.size_kb: {file.size_kb:.2f} KB (convenience!)")
    print(f"✅ file.size_mb: {file.size_mb:.2f} MB (convenience!)")
    print(f"✅ file.is_file: {file.is_file} (convenience!)")
    print(f"✅ file.is_dir: {file.is_dir} (alias for is_directory)")
    
    # ExecutionResult with rich_count
    result = ExecutionResult(
        stdout="Plot saved!",
        stderr="",
        exit_code=0,
        success=True,
        execution_time=1.234,
        rich_outputs=[]
    )
    
    print(f"✅ result.rich_count: {result.rich_count} (convenience!)")


def showcase_beautiful_repr():
    """Demonstrate beautiful repr() for debugging."""
    print("\n" + "="*70)
    print("💫 BEAUTIFUL DEBUGGING")
    print("="*70)
    
    # ExecutionResult repr
    result = ExecutionResult(
        stdout="Success!",
        stderr="",
        exit_code=0,
        success=True,
        execution_time=0.456
    )
    print(f"ExecutionResult: {repr(result)}")
    
    # FileInfo repr
    file = FileInfo(
        name="data.json",
        path="/workspace/data.json",
        size=2048,
        is_directory=False
    )
    print(f"FileInfo: {repr(file)}")
    
    # Directory repr
    dir_info = FileInfo(
        name="src",
        path="/workspace/src",
        size=0,
        is_directory=True
    )
    print(f"Directory: {repr(dir_info)}")


def showcase_pythonic_api():
    """Demonstrate Pythonic, E2B-inspired API."""
    print("\n" + "="*70)
    print("🐍 PYTHONIC API (E2B-INSPIRED)")
    print("="*70)
    
    print("✅ Simple and intuitive:")
    print("""
    # Create sandbox with one line
    sandbox = Sandbox.create(template="code-interpreter")
    
    # Execute code - Pythonic!
    result = sandbox.run_code('print("Hello!")')
    print(result.stdout)  # IDE autocomplete!
    
    # File operations - simple!
    sandbox.files.write('/workspace/data.txt', 'Hello, World!')
    content = sandbox.files.read('/workspace/data.txt')
    
    # List files with type-safe results
    files: List[FileInfo] = sandbox.files.list('/workspace')
    for file in files:
        if file.is_file:  # Convenience property!
            print(f"{file.name}: {file.size_kb:.2f} KB")
    
    # Commands - straightforward!
    result = sandbox.commands.run('ls -la')
    if result.success:  # Convenience property!
        print(result.stdout)
    
    # Desktop automation - powerful!
    vnc = sandbox.desktop.get_vnc()
    sandbox.desktop.click(100, 100)
    screenshot = sandbox.desktop.screenshot()
    
    # All with type hints and IDE autocomplete! 🎉
    """)


def showcase_error_handling():
    """Demonstrate error handling with machine-readable codes."""
    print("\n" + "="*70)
    print("🚨 ERROR HANDLING (Machine-Readable Codes)")
    print("="*70)
    
    print("✅ Type-safe exception handling:")
    print("""
    from bunnyshell.errors import FileNotFoundError, ErrorCode
    
    try:
        content = sandbox.files.read('/nonexistent.txt')
    except FileNotFoundError as e:
        # All exception properties type-hinted!
        print(f"Error: {e.message}")
        print(f"Code: {e.code}")  # e.g., "FILE_NOT_FOUND"
        print(f"Request ID: {e.request_id}")
        print(f"Path: {e.path}")
        
        # Machine-readable code for handling
        if e.code == ErrorCode.FILE_NOT_FOUND.value:
            # Create the file
            sandbox.files.write('/nonexistent.txt', 'Now it exists!')
    
    # All error codes are type-safe enums!
    error_codes = [
        ErrorCode.FILE_NOT_FOUND,
        ErrorCode.EXECUTION_TIMEOUT,
        ErrorCode.DESKTOP_NOT_AVAILABLE,
        # ... 16 total codes, all type-safe!
    ]
    """)


def main():
    """Run all DX showcases."""
    print("\n" + "="*80)
    print("🎨 BUNNYSHELL PYTHON SDK - DEVELOPER EXPERIENCE SHOWCASE")
    print("="*80)
    print("\n📚 Hybrid Approach:")
    print("   ✅ Auto-generated models from OpenAPI (type-safe, validated)")
    print("   ✅ Hand-crafted client (Pythonic, E2B-inspired DX)")
    print("   ✅ Best of both worlds!")
    
    # Run all showcases
    showcase_type_safety()
    showcase_convenience_methods()
    showcase_beautiful_repr()
    showcase_pythonic_api()
    showcase_error_handling()
    
    print("\n" + "="*80)
    print("🎉 SDK DESIGNED FOR DEVELOPERS FROM:")
    print("   • OpenAI")
    print("   • Anthropic")
    print("   • Google")
    print("   • Microsoft")
    print("   • AWS")
    print("   • Stripe")
    print("="*80)
    print("\n✨ This is what GOLD-STANDARD developer experience looks like!")
    print()


if __name__ == "__main__":
    main()

