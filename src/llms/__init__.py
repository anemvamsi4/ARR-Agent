from .anthropic import ChatAnthropic, anthropic_models
from .deepseek import ChatDeepSeek, deepseek_models
from .open_ai import ChatOpenAI, openai_models
from .google_llm import ChatGoogleGenerativeAI, google_models

def get_llm(platform: str, model: str = "default", **args):
    """
    Returns the appropriate chat model based on the specified platform and model.

    Args:
        platform (str): The platform to use. Options are "openai", "anthropic", or "deepseek".
        model (str): The model to use. If not specified, the default for the platform is used.
        **args: Additional arguments to pass to the model.

    Returns:
        Chat Model instance.
    """

    if platform == "anthropic":
        return ChatAnthropic(model = anthropic_models[model], **args)
    
    if platform == "deepseek":
        return ChatDeepSeek(model = deepseek_models[model], **args)
    
    if platform == "openai":
        return ChatOpenAI(model = openai_models[model], **args)
    
    if platform == "google":
        return ChatGoogleGenerativeAI(model= google_models[model], **args)
    