import asyncpg
import asyncio

async def test():
    try:
        conn = await asyncpg.connect('postgresql://postgres:password@127.0.0.1:5432/ahrie_ai')
        version = await conn.fetchval('SELECT version()')
        print(f"Connected successfully! PostgreSQL version: {version}")
        await conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(test())