#!/usr/bin/env python3
"""
Async quick start - for FastAPI, aiohttp, etc.

Before running:
    export BUNNYSHELL_API_KEY="bns_your_key_here"
    pip install bunnyshell
"""

import asyncio
from bunnyshell import AsyncSandbox


async def main():
    print("🚀 Bunnyshell Async Quick Start\n")
    
    # Create sandbox
    sandbox = await AsyncSandbox.create(template="code-interpreter")
    
    try:
        print(f"✅ Created: {sandbox.sandbox_id}")
        
        # Get info
        info = await sandbox.get_info()
        print(f"🌐 URL: {info.public_host}")
        print(f"📊 Status: {info.status}")
        print(f"💾 Resources: {info.vcpu} vCPU, {info.memory_mb}MB")
    finally:
        # Cleanup
        await sandbox.kill()
        print("\n✅ Sandbox cleaned up!")


if __name__ == "__main__":
    asyncio.run(main())

