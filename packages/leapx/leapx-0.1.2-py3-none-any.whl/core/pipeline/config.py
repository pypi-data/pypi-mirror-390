from enum import Enum
class OcrProviderEnum(Enum):
    "azure": "AzureClass"

class LayoutParserEnum(Enum):
    "layout-conserve": "LayoutConserverClass"

class LLMEngine(Enum):
    "aws-bedrock": "BedrockClass"
