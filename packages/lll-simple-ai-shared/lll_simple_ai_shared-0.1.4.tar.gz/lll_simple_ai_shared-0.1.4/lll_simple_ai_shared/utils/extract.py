MODALITY_TYPES = {
    "asr": "语音",  # 语音识别输入
    "tts": "语音",  # 语音输出
    "motor": "动作",
    "vision": "图像",
}


def safe_event_to_string(event):
    try:
        # 检查understood_data
        understood_data = event.get("understood_data", None)
        if understood_data is None:
            return None

        modality_type = event.get("modality_type", None)
        if modality_type is None:
            modality_type = "未知"
        else:
            modality_type = MODALITY_TYPES.get(modality_type, "未知")

        # 获取event_entity
        event_entity = understood_data.get("event_entity", None)
        if (
            event_entity is None
            or not isinstance(event_entity, str)
            or not event_entity.strip()
        ):
            event_entity = "未知"
        else:
            event_entity = event_entity.strip()

        # 获取main_content
        main_content = understood_data.get("main_content", None)
        if (
            main_content is None
            or not isinstance(main_content, str)
            or not main_content.strip()
        ):
            main_content = "未知"
        else:
            main_content = main_content.strip()

        return f"类型: {modality_type} | 角色: {event_entity} | 内容: {main_content}"

    except Exception as e:
        print(e)
        return None


def extract_events_string(recent_events):
    if recent_events is None:
        return "无"
    if not recent_events:
        return "无"

    valid_strings = []
    for event in recent_events:
        # 跳过None事件
        if event is None:
            continue

        event_str = safe_event_to_string(event)
        if event_str:
            valid_strings.append(event_str)

    return "- " + "\n- ".join(valid_strings) if valid_strings else "无"


def default_extract_strings(data_list, field=None):
    """从对象列表中提取字符串"""
    if not data_list:
        return "无"

    strings = []
    for item in data_list:
        if field and hasattr(item, field):
            # 对象字段提取
            value = getattr(item, field, "")
        elif field and isinstance(item, dict):
            # 字典字段提取
            value = item.get(field, "")
        else:
            # 直接使用字符串
            value = str(item)

        if value and value not in strings:
            strings.append(str(value))

    return "- " + "\n- ".join(strings) if strings else "无"
