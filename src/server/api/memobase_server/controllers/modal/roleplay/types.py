from typing import TypedDict
from ....prompts.roleplay import zh_detect_interest, zh_infer_plot

ChatInterest = TypedDict("ChatInterest", {"status": str, "action": str})

InferPlot = TypedDict(
    "InferPlot", {"themes": str | None, "overview": str | None, "timeline": str | None}
)

PROMPTS = {
    "en": {},
    "zh": {
        "detect_interest": zh_detect_interest,
        "infer_plot": zh_infer_plot,
    },
}
