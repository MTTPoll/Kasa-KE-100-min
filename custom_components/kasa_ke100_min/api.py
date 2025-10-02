class KasaKE100API:
    async def get_current_temperature(self) -> int:
        return 21  # Dummy-Wert

    async def set_target_temperature(self, temp: int):
        print(f"Set target temp: {temp}")

class KasaT110API:
    async def is_open(self) -> bool:
        return False  # Dummy
