if __name__ == "__main__":
    import asyncio
    from app import start_fastapi

    import argparse

    args = argparse.ArgumentParser()

    asyncio.run(start_fastapi(args))
