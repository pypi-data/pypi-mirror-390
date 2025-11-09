from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal, List
from ..utils.prompt_template import PromptTemplate
from ..utils.extract import extract_events_string, default_extract_strings


class MemoryQueryType(Enum):
    NONE = "none"
    LONG_TERM_CACHED = "long_term_cached"
    LONG_TERM_FRESH = "long_term_fresh"


class MemoryQueryPlan(BaseModel):
    query_type: Literal["none", "long_term_cached", "long_term_fresh"] = Field(
        default="none",
        description="""
查询类型，根据当前消息判断：
- none: 不查询任何记忆
- long_term_cached: 需要长期记忆的相关信息
- long_term_fresh: 需要长期记忆的相关信息，要求最新信息或信息可能已变化
""",
    )

    query_triggers: List[str] = Field(
        default_factory=list,
        description="用于搜索记忆的关键词列表，应该是名词或核心概念",
    )

    time_range: List[int] = Field(
        default_factory=list, description="查询时间范围[起始天数, 结束天数]"
    )
    importance_score_filter: int = Field(
        default=0, description="重要性分数阈值(0-100)，只查询分数大于等于此值的记忆"
    )


class UnderstoodData(BaseModel):
    event_type: Literal["user_command", "sensor_alert", "object_detected", "other"] = (
        Field(
            default="other",
            description="事件类型: user_command(用户指令)、sensor_alert(传感器预警)、object_detected(识别到特定物体或人)、other(其他)",
        )
    )
    response_priority: Literal["low", "medium", "high", "critical"] = Field(
        ...,
        description="根据安全性、紧急性判断响应紧急程度: low(低)、medium(中)、high(高)、critical(极高)",
    )
    main_content: str = Field(..., description="用一句话清晰概括当前信息的核心内容")
    current_situation: str = Field(
        ...,
        description="综合当前信息与历史上下文，生成对整体情境的连贯理解。形成完整的情境认知",
    )
    event_entity: str = Field(..., description="触发事件的主体")
    key_entities: List[str] = Field(
        default_factory=list, description="从信息中提取的重要名词或实体"
    )
    importance_score: int = Field(
        default=0, description="当前事件的重要程度分数(0-100)"
    )
    memory_query_plan: MemoryQueryPlan = Field(
        ..., description="制定从长期记忆中查询相关信息的计划"
    )


understand_system_template = """下面是当前的信息，请根据你的角色将杂乱的多模态信息整理成一条结构化的“工作记忆”：

你可能会收到来自以下来源的原始信息：
- [ASR]： 自动语音识别文本，可能包含错误或歧义。
- [TEXT]： 文本信息，但可能有错别字。

【需要你理解的信息】
[{{understand_event_type}}]{{understand_event}}

【刚才的对话和事件】
{{recent_events}}

【你正在做的事】
{{active_goals}}

请简单总结需要你理解的多模态信息。"""


understand_template = f"""
<|im_start|>system
{understand_system_template}
<|im_end|>
<|im_start|>assistant
"""

understand_output_json_template = PromptTemplate(
    template="""请你严格按照指定的JSON格式输出。

# 输出要求
你必须输出一个JSON对象，包含以下字段：

## 一级字段说明：
- `event_type`: 字符串，枚举类型。必须是以下之一：
  - `"user_command"`: 用户指令
  - `"sensor_alert"`: 传感器预警  
  - `"object_detected"`: 识别到特定物体或人
  - `"other"`: 其他类型事件

- `response_priority`: 字符串，枚举类型。根据安全性、紧急性判断响应紧急程度，必须是：
  - `"low"`: 低优先级
  - `"medium"`: 中优先级  
  - `"high"`: 高优先级
  - `"critical"`: 极高优先级

- `main_content`: 字符串。用**一句话**清晰概括当前信息的核心内容。

- `current_situation`: 字符串。综合当前信息与历史上下文，生成对整体情境的连贯理解，形成完整的情境认知。

- `event_entity`: 字符串。触发事件的主体（谁或什么触发了这个事件）。

- `key_entities`: 数组，包含字符串。从信息中提取的重要名词或实体。

- `importance_score`: 整数，范围0-100。当前事件的重要程度分数。

- `memory_query_plan`: 对象，包含记忆查询计划的详细信息。

## memory_query_plan 子对象字段说明：
- `query_type`: 字符串，枚举类型。必须是：
  - `"none"`: 不查询任何记忆
  - `"long_term_cached"`: 需要长期记忆的相关信息
  - `"long_term_fresh"`: 需要长期记忆的相关信息，要求最新信息或信息可能已变化

- `query_triggers`: 数组，包含字符串。用于搜索记忆的关键词列表，应该是名词或核心概念。

- `time_range`: 数组，包含两个整数。查询时间范围[起始天数, 结束天数]，如[0, 7]表示最近7天。

- `importance_score_filter`: 整数，范围0-100。重要性分数阈值，只查询分数大于等于此值的记忆。

# 输出示例
```json
{examples}""",
    variables={
        "examples": """{
  "event_type": "user_command",
  "response_priority": "medium", 
  "main_content": "用户要求打开客厅的灯光",
  "current_situation": "用户在晚上进入客厅后发出了开灯指令，表明需要照明",
  "event_entity": "用户",
  "key_entities": ["客厅", "灯光", "用户"],
  "importance_score": 30,
  "memory_query_plan": {
    "query_type": "long_term_fresh",
    "query_triggers": ["客厅", "灯光"],
    "time_range": [0, 7],
    "importance_score_filter": 0
  }
}"""
    },
)


def understand_task_format_inputs(inputs):
    return {
        "understand_event_type": inputs.get("understand_event", {}).get("type", "未知"),
        "understand_event": inputs.get("understand_event", {}).get("text", "无"),
        "recent_events": extract_events_string(inputs.get("recent_events", [])),
        "active_goals": default_extract_strings(
            inputs.get("active_goals", []), "description"
        ),
    }
