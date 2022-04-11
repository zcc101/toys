import asyncio


# python 原生协程
async def main():
    print('start main')
    await asyncio.sleep(3)
    print('end main')


print(123)
asyncio.run(main())
print(456)
