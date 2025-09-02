from pydantic import BaseModel  # 数据模型 #


class TranscriptionResult(BaseModel):
    text: str  # 识别文本 #


