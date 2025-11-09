import asyncio
from typing import Callable, Dict, List


def amain_wrapper(afunc: Callable, args_list: List[Dict]):
    async def amain(afunc: Callable, args_list: List[Dict]):
        tasks = []
        for args in args_list:
            tasks.append(afunc(**args))
        return await asyncio.gather(*tasks)
    return asyncio.run(amain(afunc, args_list))
