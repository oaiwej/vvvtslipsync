import httpx

class VoicevoxClient:
    def __init__(self, api_url):
        self.api_url = api_url

    async def create_audio_query(self, text: str, speaker: int):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/audio_query",
                params={"text": text, "speaker": speaker}
            )
            response.raise_for_status()
            return response.json()

    async def synthesize_audio(self, query_data: dict, speaker: int):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/synthesis",
                params={"speaker": speaker},
                json=query_data
            )
            response.raise_for_status()
            audio_data = response.content
            audio_format = response.headers.get("Content-Type", "audio/wav").split("/")[-1]
            return audio_data, audio_format
