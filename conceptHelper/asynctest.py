import asyncio
import time 

async def main():
    print("Start")

    async def hello():
        await asyncio.sleep(1)
        print("Hello")

    async def world():
        await asyncio.sleep(2)
        print("World")

    await asyncio.gather(hello(), world())

    print("End")

start = time.time()
asyncio.run(main())
print(time.time()-start)