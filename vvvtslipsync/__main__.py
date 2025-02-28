import uvicorn
import argparse
from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from pydantic import BaseModel
from contextlib import asynccontextmanager
from pydub import AudioSegment
from io import BytesIO
from vvvtslipsync.vts_client import VTSClient
from vvvtslipsync.lipsync_controller import LipsyncController
from vvvtslipsync.voicevox_client import VoicevoxClient
from vvvtslipsync.utils import split_sentences, extract_moras

# リクエストモデル
class TextRequest(BaseModel):
    text: str
    speaker_id: int = 1


def main():
    parser = argparse.ArgumentParser(description="Start the FastAPI server for VOICEVOX and VTubeStudio integration.")
    perser.add_argument("--port", type=str, default="8000", help="Port number of the FastAPI server")
    parser.add_argument("--voicevox-api-url", type=str, default="http://localhost:50021", help="URL of the VOICEVOX API")
    parser.add_argument("--vts-ws-url", type=str, default="ws://localhost:8001", help="WebSocket URL of VTubeStudio")
    parser.add_argument("--vts-plugin-name", type=str, default="VOICEVOX Bridge", help="Plugin name for VTubeStudio")
    parser.add_argument("--vts-plugin-developer", type=str, default="Your Name", help="Plugin developer name for VTubeStudio")
    
    args = parser.parse_args()
    
    
    vts_client = VTSClient(args.vts_plugin_name, args.vts_plugin_developer, args.vts_ws_url)
    lipsync_controller = LipsyncController()
    voicevox_client = VoicevoxClient(args.voicevox_api_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await vts_client.connect()
        yield
        await vts_client.disconnect()

    app = FastAPI(lifespan=lifespan)

    @app.post("/speak")
    async def speech(request: TextRequest, background_tasks: BackgroundTasks):
        try:
            # 認証済みトークンを使用
            if vts_client.authenticated_token is None:
                raise HTTPException(status_code=401, detail="VTubeStudio authentication token is missing")
            
            # テキストを文に分割
            sentences = split_sentences(request.text)
            moras = []
            audio_data = AudioSegment.empty()
            audio_format = None

            for sentence in sentences:
                # VOICEVOXへのリクエスト
                speaker_id = request.speaker_id
                query_data = await voicevox_client.create_audio_query(sentence, speaker=speaker_id)
                sentence_audio_data, sentence_audio_format = await voicevox_client.synthesize_audio(query_data, speaker=speaker_id)
                audio_data += AudioSegment.from_wav(BytesIO(sentence_audio_data))
                audio_format = sentence_audio_format
                moras += extract_moras(query_data)
            
            audio_data_file = audio_data.export(BytesIO(), audio_format)

            # 口の動きを開始
            background_tasks.add_task(lipsync_controller.lipsync, vts_client.websocket_session, moras)

            # 音声をレスポンス
            return Response(content=audio_data_file.read(), media_type="audio/wav")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
