# CircuitPy_Gamepad.py
import asyncio

class CircuitPy_Gamepad:
    def __init__(self) -> None:
        pass
        
    """
        To initialize the Gamepad, use:
            from profile import CircuitPy_Gamepad, Profile
            CPGP = CircuitPy_Gamepad()
            profile_instance = Profile()
            CPGP.update(profile_instance)
    """
    async def _update(self, profile_instance: Profile) -> None:
        print("CircuitPy_Gamepad Loop Strarted...")
        while True:
           await profile_instance._update()
           await asyncio.sleep(0)

    async def update(self, profile_instance: Profile) -> None:
        await asyncio.gather(
            self._update(profile_instance)
        )