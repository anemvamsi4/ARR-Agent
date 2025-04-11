from langchain_deepseek import ChatDeepSeek
import dotenv

dotenv.load_dotenv()

deepseek_models = {
    "deepseek-v3" : "deepseek-chat",
    "deepseek-r1" : "deepseek-reasoner",
    "default"     : "deepseek-reasoner"
}

if __name__ == "__main__":
    import os
    import getpass


    def _set_env(var: str):
        if not os.environ.get(var):
            os.environ[var] = getpass.getpass(f"{var}: ")


    _set_env("DEEPSEEK_API_KEY")

    llm = ChatDeepSeek(
            model = deepseek_models["default"],
            temperature=0,
            max_tokens=1024
        )
    
    user_input = ["Give me a code base structure for Comparative study of Losses for Semantic Segmentation on LITS dataset,"
                "using UNet and DeepLab V3+ models. Also with the code base structure, mention all the classes and functions"
                " that are required with their description, for each file of code base."]
    
    response = llm.invoke([{"role": "user",
                 "content": user_input}])
    print(response.content)