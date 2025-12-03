"""
Agent Lightning - Training Server Component
Runs independently and waits for agent clients to connect.
"""

import asyncio
import sys
from agentlightning.server import AgentLightningServer


async def main():
    """Start the training server."""
    print("\n" + "=" * 60)
    print("Agent Lightning - Training Server")
    print("=" * 60 + "\n")

    HOST = "127.0.0.1"
    PORT = 4747

    print(f"[Server] Initializing on {HOST}:{PORT}")
    server = AgentLightningServer(host=HOST, port=PORT)

    try:
        await server.start()
        print(f"[Server] ✓ Training Server started successfully!")
        print(f"[Server] URL: http://{HOST}:{PORT}")
        print(f"[Server] Waiting for clients to connect...\n")

        # Keep the server running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print(f"\n[Server] Shutting down...")
    except Exception as e:
        print(f"[Server] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
