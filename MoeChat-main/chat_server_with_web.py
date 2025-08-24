# Ver-Apple

#LOGO 打印功能
from rich.console import Console
from rich.text import Text
import time
import os

def print_moechat_logo(delay=0.2):
    console = Console()

    ascii_lines = [
        "███╗   ███╗ ██████╗ ███████╗ ██████╗██╗  ██╗ █████╗ ████████╗",
        "████╗ ████║██╔═══██╗██╔════╝██╔════╝██║  ██║██╔══██╗╚══██╔══╝",
        "██╔████╔██║██║   ██║█████╗  ██║     ███████║███████║   ██║   ",
        "██║╚██╔╝██║██║   ██║██╔══╝  ██║     ██╔══██║██╔══██║   ██║   ",
        "██║ ╚═╝ ██║╚██████╔╝███████╗╚██████╗██║  ██║██║  ██║   ██║   ",
        "╚═╝     ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ",
    ]

    gradient_colors = ["cyan", "bright_cyan", "bright_blue", "blue", "purple", "magenta"]
    total_lines = len(ascii_lines)

    # 初始化行缓冲为空字符串
    rendered_lines = [""] * total_lines

    def render_and_flush():
        console.clear()
        for line in rendered_lines:
            console.print(line if line else " " * len(ascii_lines[0]))

    # Step 1: 打印奇数行（0,2,4...）
    for i in range(0, total_lines, 2):
        rendered_lines[i] = Text(ascii_lines[i], style=gradient_colors[i % len(gradient_colors)])
        render_and_flush()
        time.sleep(delay)

    # Step 2: 打印偶数行（1,3,5...）
    for i in range(1, total_lines, 2):
        rendered_lines[i] = Text(ascii_lines[i], style=gradient_colors[i % len(gradient_colors)])
        render_and_flush()
        time.sleep(delay)

print_moechat_logo(delay=0.5)

import os
import sys
now_dir = os.getcwd()
sys.path.append(now_dir)
from utilss import config as CConfig
import requests
import time



# 创建数据文件夹
os.path.exists("data") or os.mkdir("data")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import chat_core
from external_server import router as models_router
# from pysilero import VADIterator

# -----------------------------------API接口部分----------------------------------------------------------

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(models_router, prefix="/web")
app.mount("/web/static", StaticFiles(directory="./web/static"), name="/web/static")


# 聊天接口
class tts_data(BaseModel):
    msg: list
@app.post("/api/chat")
async def tts_api(params: tts_data):
    return StreamingResponse(chat_core.text_llm_tts(params, time.time()), media_type="text/event-stream")


# asr接口
class asr_data(BaseModel):
    data: str
@app.post("/api/asr")
async def asr_api(params: asr_data):
    text = chat_core.asr(params.data)
    return text

# vad接口
# @app.websocket("/api/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     # state = np.zeros((2, 1, 128), dtype=np.float32)
#     # sr = np.array(16000, dtype=np.int64)
#     # 初始化 VAD 迭代器，指定采样率为 16000Hz
#     vad_iterator = VADIterator(speech_pad_ms=90)
#     while True:
#         try:
#             data = await websocket.receive_text()
#             data = json.loads(data)
#             if data["type"] == "asr":
#                 audio_data = base64.urlsafe_b64decode(str(data["data"]).encode("utf-8"))
#                 samples = np.frombuffer(audio_data, dtype=np.float32)
#                 # samples = nr.reduce_noise(y=samples, sr=16000)
#                 # samples = np.expand_dims(samples, axis=0)
#                 # ort_inputs = {"input": samples, "state": state, "sr": sr}
#                 # # 进行 VAD 预测
#                 # vad_prob = session.run(None, ort_inputs)[0]
#                 # # 判断是否为语音
#                 # if vad_prob > 0.7:
#                 #     print(f"[{time.time()}]说话中...")
#                 #     await websocket.send_text("说话中...")
#                 # 将重采样后的数据传递给 VAD 处理
#                 for speech_dict, speech_samples in vad_iterator(samples):
#                     if "start" in speech_dict:
#                         # current_speech = []
#                         print("开始说话...")
#                         websocket.send_text("开始说话...")
#                         pass
#                     # if status:
#                     #     current_speech.append(speech_samples)
#                     # else:
#                     #     continue
#                     is_last = "end" in speech_dict
#                     if is_last:
#                         # t = Thread(target=gen_audio, args=(current_speech.copy(), ))
#                         # t.daemon = True
#                         # t.start()
#                         websocket.send_text("结束说话")
#                         print("结束说话")
#                         # current_speech = []  # 清空当前段落

#         except:
#             break

# -----------------------------------API接口部分----------------------------------------------------------


if __name__ == "__main__":
    # global config_data
    t2s_weights = CConfig.config["GSV"]["GPT_weight"]
    vits_weights =  CConfig.config["GSV"]["SoVITS_weight"]
    if t2s_weights:
        print(f"设置GPT_weights...")
        params = {
            "weights_path": t2s_weights
        }
        try:
            requests.get(str(CConfig.config["GSV"]["api"]).replace("/tts", "/set_gpt_weights"), params=params)
        except:
            print(f"设置GPT_weights失败")
    if vits_weights:
        print(f"设置SoVITS...")
        params = {
            "weights_path": vits_weights
        }
        try:
            requests.get(str(CConfig.config["GSV"]["api"]).replace("/tts", "/set_sovits_weights"), params=params)
        except:
            print(f"设置SoVITS失败")
    uvicorn.run(app, host="0.0.0.0", port=8001)
