import asyncio
import json
from typing import List

# VTubeStudio標準搭載のモデルは ParamA/I/U/E/O/ParamSilence が使用できないため、
# MouthOpen と MouthSmile のみを使用
class LipsyncController:
    async def control_mouth(self, websocket, mouth_open: float, mouth_smile: float):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "InjectParameterRequest",
            "messageType": "InjectParameterDataRequest",
            "data": {
                "mode": "set",
                "parameterValues": [
                    {
                        "id": "MouthOpen",
                        "value": mouth_open
                    },
                    {
                        "id": "MouthSmile",
                        "value": mouth_smile
                    }
                ]
            }
        }
        await websocket.send(json.dumps(request))
        await websocket.recv()

    async def lipsync(self, websocket, moras: List[dict]):
        # 母音に応じた口の形のマッピング
        vowel_to_mouth = {
            "a": (1.0, 1.0),
            "i": (0.2, 1.0),
            "u": (0.2, 0.2),
            "e": (0.5, 0.8),
            "o": (0.5, 0.3),
            "N": (0.0, 0.5),
            "pau": (0.0, 0.5)
        }
        # 遅延時間（API呼び出し時間やその他の遅延を考慮）
        delay_time = 0.0
        # 処理にかかった時間を計測
        prev_time = asyncio.get_event_loop().time()

        # 口の動きの制御
        for mora in moras:
            vowel = mora["vowel"]
            vowel_length = mora["vowel_length"] or 0.0
            consonant_length = mora["consonant_length"] or 0.0

            # 母音に応じて口の形を調整
            mouth_open_value, mouth_smile_value = vowel_to_mouth.get(vowel, (0.0, 0.0))

            # API呼び出し
            await self.control_mouth(websocket, mouth_open_value, mouth_smile_value)
            
            # 処理にかかった時間を計測
            time_1 = asyncio.get_event_loop().time()
            processing_time = time_1 - prev_time
            
            # 次の音素までの待機時間を計算
            wait_time = vowel_length + consonant_length - processing_time - delay_time

            # 次の音素までの待機時間が正の場合は待機
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                # スリープ誤差を考慮して遅延時間を計算し、次の音素の待機時間を調整
                time_2 = asyncio.get_event_loop().time()
                delay_time = time_2 - time_1 - wait_time
            else:
                # 待機時間が負の場合は遅延時間に代入し、次の音素の待機時間を調整
                delay_time = -wait_time
            
            # 処理にかかった時間を計測
            prev_time = asyncio.get_event_loop().time()

        # 口を閉じる
        await self.control_mouth(websocket, 0.0, 0.5)