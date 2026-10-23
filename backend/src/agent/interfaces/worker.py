"""Role travailleur de la meme image (ET-007).

MS-0 ne traite aucun job metier : le processus reste pret, reagit a SIGTERM et
n'ouvre aucune connexion sortante.
"""

from __future__ import annotations

import asyncio
import signal
import sys


async def run() -> int:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(signum, stop.set)
    print("Travailleur pret (MS-0 : aucun job metier).", flush=True)
    await stop.wait()
    print("Travailleur arrete proprement.", flush=True)
    return 0


def main() -> int:
    return asyncio.run(run())


if __name__ == "__main__":
    sys.exit(main())
