import socket
import threading
import struct
import json
from pysilero import VADIterator
import numpy as np
import base64
from scipy.signal import resample
from io import BytesIO
import soundfile as sf
from utilss import log as Log

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
import time
from io import BytesIO

def asr(audio_data: bytes, asr_model: AutoModel):
    # global is_sv
    # global sv_pipeline

    tt = time.time()
    # if is_sv:
    #     if not sv_pipeline.check_speaker(audio_data):
    #         return None

    # with open(f"./tmp/{tt}.wav", "wb") as file:
    #     file.write(audio_data)
    audio_data = BytesIO(audio_data)
    res = asr_model.generate(
        input=audio_data,
        # input=f"{model.model_path}/example/zh.mp3",
        cache={},
        language="zh", # "zh", "en", "yue", "ja", "ko", "nospeech"
        ban_emo_unk=True,
        use_itn=False,
        disable_pbar=True,
        # batch_size=200,
    )
    # print(f"{model.model_path}/example/zh.mp3",)
    text = str(rich_transcription_postprocess(res[0]["text"])).replace(" ", "")
    # text = res[0]["text"]
    # print()
    # print(f"[{time.time() - tt}]{text}\n\n")
    if text:
        return text
    return None

def handle_client(client_socket: socket, asr_model: AutoModel):
    """处理客户端连接，确保完整接收消息"""
    vad_iterator = VADIterator(speech_pad_ms=300)
    current_speech = []
    current_speech_tmp = []
    status = False
    # 发送欢迎消息
    while True:
        # 接收完整消息
        data = rec(client_socket)
            
        if data is None:
            client_socket.close()
            Log.logger.info(f"客户端断开：{client_socket}")
            return
        
        # print(f"[客户端 {client_address}] {message}")
        data = json.loads(data)
        if data["type"] == "asr":
            audio_data = base64.urlsafe_b64decode(str(data["data"]).encode("utf-8"))
            samples = np.frombuffer(audio_data, dtype=np.int16)
            current_speech_tmp.append(samples)
            if len(current_speech_tmp) < 4:
                continue
            resampled = np.concatenate(current_speech_tmp.copy())
            resampled = (resampled / 32768.0).astype(np.float32)
            current_speech_tmp = []
            
            for speech_dict, speech_samples in vad_iterator(resampled):
                if "start" in speech_dict:
                    current_speech = []
                    status = True
                    # print("开始说话")
                    pass
                if status:
                    current_speech.append(speech_samples)
                else:
                    continue
                is_last = "end" in speech_dict
                if is_last:
                    # print("结束说话")
                    status = False
                    combined = np.concatenate(current_speech)
                    audio_bytes = b""
                    with BytesIO() as buffer:
                        sf.write(
                            buffer,
                            combined,
                            16000,
                            format="WAV",
                            subtype="PCM_16",
                        )
                        buffer.seek(0)
                        audio_bytes = buffer.read()  # 完整的 WAV bytes
                        res_text = asr(audio_bytes, asr_model)
                        if res_text:
                            # await c_websocket.send_text(res_text)
                            try:
                                send(client_socket, res_text)
                            except:
                                client_socket.close()
                                return
                    current_speech = []  # 清空当前段落
            # if not message:
            #     break
                
            # print(f"客户端: {message}")
            
            # # 如果客户端发送'quit'，则断开连接
            # if message.lower() == 'quit':
            #     send(client_socket, "已收到退出请求，再见！")
            #     break
                
            # # 回复客户端
            # response = f"已收到消息，长度为 {len(message)} 字节"
            # send(client_socket, response)
            
    # except Exception as e:
    #     print(f"处理客户端错误: {e}")
    # finally:
    #     client_socket.close()
    #     print("客户端连接已关闭")

def send(sock, data):
    """发送消息：先发送长度（4字节前缀），再发送数据"""
    # 计算数据长度（字节数）
    data_bytes = data.encode('utf-8')
    length = len(data_bytes)
    
    # 发送长度（使用4字节无符号整数，网络字节序）
    sock.sendall(struct.pack('>I', length))
    # 发送实际数据
    sock.sendall(data_bytes)

def rec(sock):
    """接收消息：先读取长度前缀，再读取对应长度的数据"""
    # 先读取4字节的长度前缀
    length_bytes = sock.recv(4)
    if not length_bytes:
        return None  # 连接关闭
    
    # 解析长度（网络字节序转主机字节序）
    length = struct.unpack('>I', length_bytes)[0]
    
    # 循环读取直到获取完整数据
    data_bytes = b''
    while len(data_bytes) < length:
        # 每次最多读取剩余长度的数据
        remaining = length - len(data_bytes)
        chunk = sock.recv(min(remaining, 4096))  # 缓冲区设为4096字节
        if not chunk:
            return None  # 连接中断
        data_bytes += chunk
    
    return data_bytes.decode('utf-8')

def start_server(host: str, port: int, asr_model: AutoModel):
    """启动服务器"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    Log.logger.info(f"socket_asr服务启动，监听 {host}:{port}...")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            Log.logger.info(f"新连接：{addr}")
            # 启动线程处理客户端
            client_thread = threading.Thread(target=handle_client, args=(client_socket, asr_model, ))
            client_thread.start()
    except KeyboardInterrupt:
        Log.logger.info("服务器正在关闭...")
    finally:
        server_socket.close()

# if __name__ == "__main__":
#     start_server("0.0.0.0", 8002, asr_model)

# class ImprovedFullDuplexServer:
#     def __init__(self, host: str, port: int, asr_model: AutoModel, ):
#         self.host = host
#         self.port = port
#         self.server_socket = None
#         self.running = False
#         self.asr_model = asr_model
    
#     # asr功能
#     def asr(self, audio_data: bytes):
#         # global is_sv
#         # global sv_pipeline

#         tt = time.time()
#         # if is_sv:
#         #     if not sv_pipeline.check_speaker(audio_data):
#         #         return None

#         # with open(f"./tmp/{tt}.wav", "wb") as file:
#         #     file.write(audio_data)
#         audio_data = BytesIO(audio_data)
#         res = self.asr_model.generate(
#             input=audio_data,
#             # input=f"{model.model_path}/example/zh.mp3",
#             cache={},
#             language="zh", # "zh", "en", "yue", "ja", "ko", "nospeech"
#             ban_emo_unk=True,
#             use_itn=False,
#             # batch_size=200,
#         )
#         # print(f"{model.model_path}/example/zh.mp3",)
#         text = str(rich_transcription_postprocess(res[0]["text"])).replace(" ", "")
#         # text = res[0]["text"]
#         print()
#         print(f"[{time.time() - tt}]{text}\n\n")
#         if text:
#             return text
#         return None
        
#     def start_server(self):
#         try:
#             self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#             self.server_socket.bind((self.host, self.port))
#             self.server_socket.listen(5)
#             self.running = True
            
#             print(f"服务器启动成功，监听 {self.host}:{self.port}")
            
#             while self.running:
#                 try:
#                     client_socket, client_address = self.server_socket.accept()
#                     print(f"客户端 {client_address} 已连接")
                    
#                     # 为每个客户端创建处理线程
#                     client_thread = threading.Thread(
#                         target=self.handle_client, 
#                         args=(client_socket, client_address)
#                     )
#                     client_thread.daemon = True
#                     client_thread.start()
                    
#                 except Exception as e:
#                     if self.running:
#                         print(f"接受连接时出错: {e}")
                        
#         except Exception as e:
#             print(f"服务器启动失败: {e}")
#         finally:
#             self.stop_server()
    
#     def send_message(self, client_socket, message):
#         """发送带长度前缀的消息"""
#         try:
#             # 将消息编码为字节
#             if isinstance(message, dict):
#                 message_bytes = json.dumps(message).encode('utf-8')
#             else:
#                 message_bytes = str(message).encode('utf-8')
            
#             # 计算消息长度
#             message_length = len(message_bytes)
            
#             # 发送长度信息（使用4字节整数）
#             length_prefix = struct.pack('!I', message_length)
#             client_socket.send(length_prefix)
            
#             # 发送实际消息内容
#             client_socket.send(message_bytes)
            
#             # print(f"发送消息: {message} (长度: {message_length} 字节)")
            
#         except Exception as e:
#             pass
#             # print(f"发送消息时出错: {e}")
    
#     def receive_message(self, client_socket):
#         """接收带长度前缀的消息"""
#         try:
#             # 首先接收4字节的长度信息
#             length_data = self._recv_exact(client_socket, 4)
#             if not length_data:
#                 return None
                
#             # 解析长度
#             message_length = struct.unpack('!I', length_data)[0]
#             # print(f"准备接收长度为 {message_length} 字节的消息")
            
#             # 根据长度接收完整消息
#             message_data = self._recv_exact(client_socket, message_length)
#             if not message_data:
#                 return None
                
#             # 解码消息
#             message = message_data.decode('utf-8')
#             data = json.loads(message)
#             return data
            
#         except Exception as e:
#             # print(f"接收消息时出错: {e}")
#             return None
    
#     def _recv_exact(self, sock, length):
#         """确保接收指定长度的数据"""
#         data = b''
#         while len(data) < length:
#             chunk = sock.recv(length - len(data))
#             if not chunk:
#                 return None
#             data += chunk
#         return data
    
#     def handle_client(self, client_socket, client_address):
#         """处理客户端连接"""
#         vad_iterator = VADIterator(speech_pad_ms=270)
#         current_speech = []
#         current_speech_tmp = []
#         status = False
#     # try:
#         while self.running:
#             # 接收客户端消息
#             data = self.receive_message(client_socket)
#             if data is None:
#                 break
#             # print(f"[客户端 {client_address}] {message}")
#             if data["type"] == "asr":
#                 audio_data = base64.urlsafe_b64decode(str(data["data"]).encode("utf-8"))
#                 samples = np.frombuffer(audio_data, dtype=np.float32)
#                 current_speech_tmp.append(samples)
#                 if len(current_speech_tmp) < 9:
#                     continue
#                 resampled = np.concatenate(current_speech_tmp.copy())
#                 current_speech_tmp = []
#                 # resampled = resample(samples, 1600)
#                 resampled = resample(resampled, 1600)
#                 resampled = resampled.astype(np.float32)
                
#                 for speech_dict, speech_samples in vad_iterator(resampled):
#                     if "start" in speech_dict:
#                         current_speech = []
#                         status = True
#                         pass
#                     if status:
#                         current_speech.append(speech_samples)
#                     else:
#                         continue
#                     is_last = "end" in speech_dict
#                     if is_last:
#                         status = False
#                         combined = np.concatenate(current_speech)
#                         audio_bytes = b""
#                         with BytesIO() as buffer:
#                             sf.write(
#                                 buffer,
#                                 combined,
#                                 16000,
#                                 format="WAV",
#                                 subtype="PCM_16",
#                             )
#                             buffer.seek(0)
#                             audio_bytes = buffer.read()  # 完整的 WAV bytes
#                             res_text = self.asr(audio_bytes)
#                             if res_text:
#                                 # await c_websocket.send_text(res_text)
#                                 self.send_message(client_socket, res_text)
#                         current_speech = []  # 清空当前段落
#                 # 发送回复消息
#                 # reply = f"服务器收到: {message}"
#                 # self.send_message(client_socket, reply)
                
#                 # if message.lower() == 'quit':
#                 #     break
                    
#         # except Exception as e:
#         #     print(f"处理客户端 {client_address} 时出错: {e}")
#         # finally:
#         #     client_socket.close()
#         #     print(f"客户端 {client_address} 连接已关闭")
    
#     def stop_server(self):
#         self.running = False
#         if self.server_socket:
#             self.server_socket.close()

# if __name__ == "__main__":
#     server = ImprovedFullDuplexServer()
#     try:
#         server.start_server()
#     except KeyboardInterrupt:
#         print("\n正在关闭服务器...")

