from pydantic import BaseModel, Field
from typing import List, Literal, Union
from ..utils.prompt_template import PromptTemplate
from ..utils.extract import extract_events_string, default_extract_strings


class BaseAction(BaseModel):
    type: Literal["tts", "motor"] = Field(..., description="计划类型")
    action: str = Field(..., description="具体动作名称")


class TTSAction(BaseAction):
    type: str = "tts"
    action: Literal["speak", "pause", "emphasize"] = Field(
        ..., description="语音动作类型：speak(说话)、pause(暂停)、emphasize(强调)"
    )
    data: str = Field(..., description="要说的具体文本内容")
    emotion: str = "neutral"
    speed: float = Field(default=1.0, description="语速0.5-2.0")


# TODO: 完善类型
class MotorAction(BaseAction):
    type: Literal["motor"] = "motor"
    action: Literal["move", "release"] = Field(...)
    duration: float = Field(default=1.0, description="动作持续时间(秒)")
    speed: float = Field(default=1.0, description="运动速度倍数")


class BehaviorPlan(BaseModel):
    plan: List[Union[TTSAction]] = Field(..., description="行为计划序列")
    current_situation: str = Field(
        ...,
        description="根据你的行为计划，更新你对当前情境认知",
    )


behavior_system_template = """下面是当前的信息，请根据你的角色生成语音、动作行为计划：

【当前情境】
{{current_situation}}

【刚才的对话和事件】
{{recent_events}}

【相关的历史记忆】
{{episodic_memories}}

【你正在做的事】
{{active_goals}}

【社交规范】
{{social_norms}}"""


behavior_template = f"""
<|im_start|>system
{behavior_system_template}
<|im_end|>
<|im_start|>assistant
"""

behavior_output_json_template = PromptTemplate(
    template="""请严格按照指定的JSON格式输出。

# 输出要求
你必须输出一个JSON对象，包含以下字段：

- `current_situation`: 字符串。根据你制定的行为计划，更新对当前情境的认知和理解，说明为什么这样的行为序列适合当前情境。

- `plan`字段是动作对象数组，每个对象必须包含：
  - `type`: 字符串，动作类型：`"tts"`(语音)

  ## 根据type选择对应字段：

  ### 当 type = "tts" 时，包含：
  - `action`: 字符串，必须是：`"speak"`(说话)、`"pause"`(暂停)、`"emphasize"`(强调)
  - `data`: 字符串，要说的具体文本
  - `emotion`: 字符串，情感类型，默认"neutral"
  - `speed`: 数字0.5-2.0，语速，默认1.0

# 输出示例
```json
{examples}""",
    variables={
        "examples": """{
  "plan": [
    {
      "type": "tts",
      "action": "speak",
      "data": "我注意到您刚刚进入了客厅",
      "emotion": "neutral",
      "speed": 1.0
    },
    {
      "type": "tts", 
      "action": "pause",
      "data": "短暂停顿等待用户反应",
      "emotion": "neutral",
      "speed": 1.0
    }
  ],
  "current_situation": "用户刚进入昏暗环境，采用分步沟通策略：先告知观察结果，再停顿给予反应时间，这样既礼貌又有效"
}"""
    },
)


def behavior_task_format_inputs(inputs):
    return {
        "current_situation": inputs.get("current_situation", "未知"),
        "recent_events": extract_events_string(inputs.get("recent_events", [])),
        # TODO: 增加时间
        "episodic_memories": inputs.get(
            "episodic_memories_text",
            default_extract_strings(inputs.get("episodic_memories", []), "content"),
        ),
        "active_goals": default_extract_strings(
            inputs.get("active_goals", []), "description"
        ),
        "social_norms": default_extract_strings(inputs.get("social_norms", [])),
    }
