from langchain_openai import ChatOpenAI

openai_models = {
    "gpt-4.5-preview": "gpt-4.5-preview",
    "gpt-4o" : "gpt-4o",
    "gpt-4o-mini" : "gpt-4o-mini",
    "o1" : "o1",
    "o1-mini" : "o1-mini",
    "o1-pro" : "o1-pro",
    "o3-mini" : "o1-mini",
    "default" : "o3-mini"
}

if __name__ == "__main__":
    import os
    import getpass


    def _set_env(var: str):
        if not os.environ.get(var):
            os.environ[var] = getpass.getpass(f"{var}: ")


    _set_env("OPENAI_API_KEY")

    llm = ChatOpenAI(
            model = openai_models["default"],
            temperature=0,
            max_tokens = 1024
        )
    
    user_input = ["Give me a code base structure for Comparative study of Losses for Semantic Segmentation on LITS dataset,"
                "using UNet and DeepLab V3+ models. Also with the code base structure, mention all the classes and functions"
                " that are required with their description, for each file of code base."]
    
    response = llm.invoke([{"role": "user",
                 "content": user_input}])
    print(response.content)