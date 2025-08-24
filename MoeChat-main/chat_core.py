from utilss import config as CConfig
import requests
import json
import time
import asyncio
from threading import Thread
import base64
from fastapi.responses import JSONResponse
from io import BytesIO
from pydantic import BaseModel
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from utilss.sv import SV
from utilss.agent import Agent
import re
import jionlp
from plugins.financial.plugin import financial_plugin_hook


if CConfig.config["Agent"]["is_up"]:
    agent = Agent()

try:
    model_dir = "./utilss/models/SenseVoiceSmall"
    asr_model = AutoModel(
        model=model_dir,
        disable_update=True,
        device="cuda:0",
    )
except:
    print("[提示]未安装ASR模型，开始自动安装ASR模型。")
    from modelscope import snapshot_download
    model_dir = snapshot_download(
        model_id="iic/SenseVoiceSmall",
        local_dir="./utilss/models/SenseVoiceSmall",
        revision="master"
    )
    model_dir = "./utilss/models/SenseVoiceSmall"
    asr_model = AutoModel(
        model=model_dir,
        disable_update=True,
        # device="cuda:0",
        device="cpu",
    )

# 载入声纹识别模型
sv_pipeline = ""
if CConfig.config["Core"]["sv"]["is_up"]:
    sv_pipeline = SV(CConfig.config["Core"]["sv"])
    is_sv = True
else:
    is_sv = False

# 提交到大模型
def to_llm(msg: list, res_msg_list: list, full_msg: list):
    def get_emotion(msg: str):
        res = re.findall(r'\[(.*?)\]', msg)
        if len(res) > 0:
            match = res[-1]
            if match and CConfig.config["extra_ref_audio"]:
                if match in CConfig.config["extra_ref_audio"]:
                    return match
    # def add_msg(msg: str):
    key = CConfig.config["LLM"]["key"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }

    data = {
        "model": CConfig.config["LLM"]["model"] ,
        "stream": True
    }
    if CConfig.config["LLM"]["extra_config"]:
        data.update(CConfig.config["LLM"]["extra_config"])
    data["messages"] = msg

    t_t = time.time()
    try:
        response = requests.post(url = CConfig.config["LLM"]["api"], json=data, headers=headers,stream=True)
    except:
        print("无法链接到LLM服务器")
        return JSONResponse(status_code=400, content={"message": "无法链接到LLM服务器"})
    
    # 信息处理
    # biao_dian_2 = ["…", "~", "～", "。", "？", "！", "?", "!"]
    biao_dian_3 = ["…", "~", "～", "。", "？", "！", "?", "!", ",", "，"]
    biao_dian_4 = ["…", "~", "～",  ",", "，"]

    res_msg = ""
    tmp_msg = ""
    j = True
    j2 = True
    ref_audio = ""
    ref_text = ""
    # biao_tmp = biao_dian_3
    for line in response.iter_lines():
        if line:
            try:
                if j:
                    print(f"\n[大模型延迟]{time.time() - t_t}")
                    t_t = time.time()
                    j = False
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data:"):
                    data_str = decoded_line[5:].strip()
                    if data_str:
                        msg_t = json.loads(data_str)["choices"][0]["delta"]["content"]
                        res_msg += msg_t
                        tmp_msg += msg_t
                res_msg = res_msg.replace("...", "…")
                tmp_msg = tmp_msg.replace("...", "…")
            except:
                err = line.decode("utf-8")
                print(f"[错误]：{err}")
                continue
            # if not tmp_msg:
            #     continue
            ress = ""
            stat = 0
            for ii in range(len(tmp_msg)):
                if tmp_msg[ii] in ["(", "（", "[", "{"]:
                    stat += 1
                    continue
                if tmp_msg[ii] in [")", "）", "]", "}"]:
                    stat -= 1
                    continue
                if stat != 0:
                    continue
                if tmp_msg[ii] not in biao_dian_3:
                    continue
                if (tmp_msg[ii] in biao_dian_4) and j2 == False and len(re.sub(r'[$(（[].*?[]）)]', '', tmp_msg[:ii+1])) <= 10:
                    continue

                # 提取文本中的情绪标签，并设置参考音频
                emotion = get_emotion(tmp_msg)
                if emotion:
                    if emotion in CConfig.config["extra_ref_audio"]:
                        ref_audio = CConfig.config["extra_ref_audio"][emotion][0]
                        ref_text = CConfig.config["extra_ref_audio"][emotion][1]
                ress = tmp_msg[:ii+1]
                ress = jionlp.remove_html_tag(ress)
                ttt = ress
                if j2:
                    print(f"\n[开始合成首句语音]{time.time() - t_t}")
                    for i in range(len(ress)):
                        if ress[i] == "\n" or ress[i] == " ":
                            try:
                                ttt = ress[i+1:]
                            except:
                                ttt = ""
                # if not j2:
                #     if len(re.sub(r'[$(（[].*?[]）)]', '', ttt)) < 4:
                #         continue
                if ttt:
                    res_msg_list.append([ref_audio, ref_text, ttt])
                # print(f"[合成文本]{ress}")
                if j2:
                    j2 = False
                try:
                    tmp_msg = tmp_msg[ii+1:]
                except:
                    tmp_msg = ""
                break


    if len(tmp_msg) > 0:
        emotion = get_emotion(tmp_msg)
        if emotion:
            if emotion in CConfig.config["extra_ref_audio"]:
                ref_audio = CConfig.config["extra_ref_audio"][emotion][0]
                ref_text = CConfig.config["extra_ref_audio"][emotion][1]
        res_msg_list.append([ref_audio, ref_text, tmp_msg])

    # 返回完整上下文 
    res_msg = jionlp.remove_html_tag(res_msg)
    if len(res_msg) == 0:
        full_msg.append(res_msg)
        res_msg_list.append("DONE_DONE")
        return
    ttt = ""
    for i in range(len(res_msg)):
        if res_msg[i] != "\n" and res_msg[i] != " ":
            ttt = res_msg[i:]
            break
            
    full_msg.append(ttt)
    print(full_msg)
    # print(res_msg_list)
    res_msg_list.append("DONE_DONE")

def tts(datas: dict):
    res = requests.post(CConfig.config["GSV"]["api"], json=datas, timeout=10)
    if res.status_code == 200:
        return res.content
    else:
        print(f"[错误]tts语音合成失败！！！")
        print(datas)
        return None
    

def clear_text(msg: str):
    msg = re.sub(r'\{(image|meme|pics):.*?\}', '', msg) # 新增：移除所有image和meme标签
    msg = re.sub(r'[$(（[].*?[]）)]', '', msg)
    msg = msg.replace(" ", "").replace("\n", "")
    tmp_msg = ""
    biao = ["…", "~", "～", "。", "？", "！", "?", "!",  ",",  "，"]
    for i in range(len(msg)):
        if msg[i] not in biao:
          tmp_msg = msg[i:]
          break
    # msg = jionlp.remove_exception_char(msg)
    return tmp_msg


# TTS并写入队
def to_tts(tts_data: list):
    # def is_punctuation(char):
    #     return unicodedata.category(char).startswith('P')
    msg = clear_text(tts_data[2])
    # print(f"[实际输入文本]{tts_data[2]}[tts文本]{msg}")
    if len(msg) == 0:
        return "None"
    ref_audio = tts_data[0]
    ref_text = tts_data[1]
    datas = {
        "text": msg,
        "text_lang": CConfig.config["GSV"]["text_lang"],
        "ref_audio_path": CConfig.config["GSV"]["ref_audio_path"],
        "prompt_text": CConfig.config["GSV"]["prompt_text"],   
        "prompt_lang": CConfig.config["GSV"]["prompt_lang"],
        "seed": CConfig.config["GSV"]["seed"],
        "top_k": CConfig.config["GSV"]["top_k"],
        "batch_size": CConfig.config["GSV"]["batch_size"],
    }
    if CConfig.config["GSV"]["ex_config"]:
        for key in CConfig.config["GSV"]["ex_config"]:
            datas[key] = CConfig.config["GSV"]["ex_config"][key]
    if ref_audio:
        datas["ref_audio_path"] = ref_audio
        datas["prompt_text"] = ref_text
    try:
        byte_data = tts(datas)
        audio_b64 = base64.urlsafe_b64encode(byte_data).decode("utf-8")
        return audio_b64
    except:
        return "None"

def ttts(res_list: list, audio_list: list):
    i = 0
    while True:
        if i < len(res_list):
            if res_list[i] == "DONE_DONE":
                audio_list.append("DONE_DONE")
                print(f"完成...")
                break
            # t_t = time.time()
            audio_list.append(to_tts(res_list[i]))
            # if i == 0:
            #     print(f"\n[首句语音耗时]{time.time() - t_t}")
            i += 1
        time.sleep(0.05)


# asr功能
def asr(params: str):
    global asr_model
    global is_sv
    global sv_pipeline

    audio_data = base64.urlsafe_b64decode(params.encode("utf-8"))

    tt = time.time()
    if is_sv:
        if not sv_pipeline.check_speaker(audio_data):
            return None
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
        # batch_size=200,
    )
    # print(f"{model.model_path}/example/zh.mp3",)
    text = str(rich_transcription_postprocess(res[0]["text"])).replace(" ", "")
    # text = res[0]["text"]
    print()
    print(f"[{time.time() - tt}]{text}\n\n")
    if text:
        return text
    return None

# 新增函数处理prompt
def _create_llm_prompt_for_financial_task(plugin_result: dict, original_msg_history: list) -> list:
    """
    根据插件返回结果，创建用于LLM润色的新Prompt。
    这是一个辅助函数，专门为财务任务生成给LLM的指令。
    """
    
    llm_context = plugin_result.get('llm_context', {})
    suggestion = llm_context.get('suggestion_for_llm', '')
    

    if plugin_result['status'] == 'success':
        system_prompt = (
            "一个财务插件刚刚成功处理了一笔用户的交易。"
            "你的任务是：基于插件提供的'任务总结'和'详细数据'，生成一句自然、友好、符合你人设的确认消息给用户。"
            "请不要重复数据，而是用口语化的方式进行确认和反馈。"
            f"任务总结: {suggestion}\n"
            f"详细数据: {json.dumps(llm_context.get('transaction_info', {}), ensure_ascii=False)}"
        )
    elif plugin_result['status'] == 'incomplete':
        system_prompt = (
            "一个财务插件发现用户的记账信息不完整，需要向用户提问以补全信息。"
            "你的任务是：基于插件提供的'提问建议'，生成一句自然、友好、符合你人设的问句来引导用户。"
            f"提问建议: {suggestion}\n"
            f"已提取的信息: {json.dumps(llm_context.get('extracted_info', {}), ensure_ascii=False)}"
        )
    else:
        # 
        system_prompt = "请基于以下信息和用户对话。"

    # 将这个特殊的系统提示和用户的对话历史结合起来，构成完整的上下文
    # 我们将系统提示放在历史消息的最前面，以指导LLM的后续行为
    final_prompt_list = [{"role": "system", "content": system_prompt}] + original_msg_history
    
    return final_prompt_list


class tts_data(BaseModel):
    msg: list

async def text_llm_tts(params: tts_data, start_time):
    # ================== 1. 统一的消息准备阶段 ==================
    
    # 初始化将要传递给LLM的最终消息列表
    msg_list_for_llm = []
    
    # 检查MoeChat总配置文件中的插件开关
    is_balancer_enabled = CConfig.config.get('Plugins', {}).get('Balancer', {}).get('enabled', False)

    if is_balancer_enabled:
        # 插件已启用，进入插件处理流程
        session_id = "user_main_session"  # 关键点：实际应用中这里应该是动态的、每个用户唯一的ID
        user_message = params.msg[-1]["content"]

        print(f"[插件钩子] 正在处理消息: '{user_message}'")
        plugin_result = financial_plugin_hook(user_message, session_id)
        print(f"[插件钩子] 返回结果: \n{json.dumps(plugin_result, indent=2, ensure_ascii=False)}")

        if plugin_result['financial_detected']:
            # 只要检测到财务意图（无论成功与否），就调用辅助函数为LLM创建新的、带有指导的Prompt
            print("[决策] 检测到财务意图，正在为LLM创建润色任务...")
            msg_list_for_llm = _create_llm_prompt_for_financial_task(plugin_result, params.msg)
    
    # 如果经过插件处理后，msg_list_for_llm 列表仍然为空
    # (这说明插件被禁用，或者插件判断当前消息与财务无关)
    # 则执行MoeChat原来的常规聊天逻辑来填充它。
    if not msg_list_for_llm:
        print("[决策] 非财务消息或插件禁用，进入常规聊天流程。")
        if CConfig.config["Agent"]["is_up"]:
            global agent
            t = time.time()
            msg_list_for_llm = agent.get_msg_data(params.msg[-1]["content"])
            print(f"[提示]获取上下文耗时：{time.time() - t}")
        else:
            msg_list_for_llm = params.msg
            
    # ================== 2. 统一的LLM和TTS处理阶段 ==================
    # 无论消息来自插件包装还是常规聊天，最终都汇入到这里，使用同一套处理流水线
    
    res_list = []
    audio_list = []
    full_msg = []
    
    print("[核心流程] 已将最终Prompt送入LLM和TTS处理流水线。")
    
    # 将最终构建好的消息列表(msg_list_for_llm)传递给 to_llm 线程
    llm_t = Thread(target=to_llm, args=(msg_list_for_llm, res_list, full_msg, ))
    llm_t.daemon = True
    llm_t.start()
    
    tts_t = Thread(target=ttts, args=(res_list, audio_list, ))
    tts_t.daemon = True
    tts_t.start()

    # ================== 3. 统一的流式返回阶段 (这部分代码来自您的原始版本，保持不变) ==================
    i = 0
    stat = True
    emotion_processed = False  # 标记是否已处理表情包
    
    while True:
        if i < len(audio_list):
            if audio_list[i] == "DONE_DONE":
                # === 新增：在对话结束前处理表情包 ===
                if not emotion_processed and len(full_msg) > 0 and full_msg[0]:
                    try:
                        # 导入表情包系统（延迟导入避免循环依赖）
                        from meme_system import get_emotion_service
                        
                        # 获取表情包服务实例
                        emotion_service = get_emotion_service()
                        if not emotion_service.is_healthy():
                            print("[表情包系统] 初始化表情包服务...")
                            emotion_service.initialize()
                        
                        # 处理LLM回复，获取表情包响应
                        meme_sse_response = emotion_service.process_llm_response(full_msg[0])
                        
                        if meme_sse_response:
                            print("[表情包系统] 发送表情包到前端")
                            yield meme_sse_response
                        else:
                            print("[表情包系统] 本次不发送表情包")
                            
                    except ImportError:
                        print("[表情包系统] 表情包模块未安装，跳过表情包处理")
                    except Exception as e:
                        print(f"[表情包系统] 处理表情包时发生错误：{e}")
                    
                    emotion_processed = True
                # =======================================
                
                # 发送结束信号
                data = {"file": None, "message": full_msg[0], "done": True}
                if CConfig.config["Agent"]["is_up"]:    # 刷新智能体上下文内容
                    agent.add_msg(re.sub(r'<.*?>', '', full_msg[0]).strip())
                yield f"data: {json.dumps(data)}\n\n"
                break  # 结束循环
            
            # 发送音频和文本数据
            data = {"file": audio_list[i], "message": res_list[i][2], "done": False}
            
            if stat:
                print(f"\n[服务端首句处理耗时]{time.time() - start_time}\n")
                stat = False
            
            yield f"data: {json.dumps(data)}\n\n"
            i += 1
        
        await asyncio.sleep(0.05)