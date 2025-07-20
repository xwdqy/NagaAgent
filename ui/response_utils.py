import json

def extract_message(response: str) -> str:
    """
    解析后端返回的json字符串，优先取data.content，其次message，否则原样返回
    支持递归解析嵌套JSON和多步数组，自动用\n分隔多条消息
    :param response: 后端返回的json字符串
    :return: message内容（若解析失败则原样返回）
    """
    if not isinstance(response, str):
        return str(response)
    
    # 先尝试直接解析
    try:
        data = json.loads(response)
        # 如果是数组，递归拼接所有消息
        if isinstance(data, list):
            messages = [_recursive_extract(item) for item in data if _recursive_extract(item)]
            return '\n'.join(messages)
        extracted = _recursive_extract(data)
        if extracted and extracted != response:
            return extracted
    except:
        pass
    
    # 如果失败，尝试查找JSON子串
    try:
        # 查找可能的JSON起始位置
        start_pos = response.find('{')
        if start_pos >= 0:
            # 从第一个{开始尝试解析
            json_part = response[start_pos:]
            data = json.loads(json_part)
            if isinstance(data, list):
                messages = [_recursive_extract(item) for item in data if _recursive_extract(item)]
                return '\n'.join(messages)
            extracted = _recursive_extract(data)
            if extracted:
                return extracted
    except:
        pass
    
    # 如果都失败了，返回原始响应，但确保换行符正确
    return _normalize_line_endings(response)

def _recursive_extract(data) -> str:
    """递归提取消息内容"""
    if isinstance(data, dict):
        # 优先级：data.content > message > content > text > value
        for key in ['data', 'message', 'content', 'text', 'value']:
            if key in data:
                value = data[key]
                if isinstance(value, dict):
                    # 递归处理嵌套字典
                    nested_result = _recursive_extract(value)
                    if nested_result:
                        return nested_result
                elif isinstance(value, list):
                    # 处理数组类型，如choices数组
                    messages = [_recursive_extract(item) for item in value if _recursive_extract(item)]
                    if messages:
                        return '\n'.join(messages)
                elif isinstance(value, str) and value.strip():
                    # 检查是否还是JSON格式
                    try:
                        nested_data = json.loads(value)
                        nested_result = _recursive_extract(nested_data)
                        if nested_result:
                            return nested_result
                    except:
                        pass
                    # 确保换行符正确
                    return _normalize_line_endings(value.strip())
                elif value is not None:
                    return _normalize_line_endings(str(value).strip())
        
        # 如果没有找到标准字段，返回第一个字符串值
        for value in data.values():
            if isinstance(value, str) and value.strip():
                return _normalize_line_endings(value.strip())
    elif isinstance(data, list):
        # 处理数组类型
        messages = [_recursive_extract(item) for item in data if _recursive_extract(item)]
        if messages:
            return '\n'.join(messages)
    elif isinstance(data, str):
        return _normalize_line_endings(data.strip())
    
    return ""

def _normalize_line_endings(text: str) -> str:
    """标准化换行符，确保所有换行符都是\n格式"""
    if not isinstance(text, str):
        return str(text)
    
    # 统一换行符格式
    text = text.replace('\r\n', '\n')  # Windows换行符
    text = text.replace('\r', '\n')    # 旧版Mac换行符
    
    return text
