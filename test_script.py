import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        # Test 1: Empty POST
        r1 = await client.post("http://127.0.0.1:8000/reset")
        print("Empty POST:", r1.status_code, r1.text)
        
        # Test 2: JSON {} POST
        r2 = await client.post("http://127.0.0.1:8000/reset", json={})
        print("{} POST:", r2.status_code, r2.text)

if __name__ == '__main__':
    asyncio.run(test())
