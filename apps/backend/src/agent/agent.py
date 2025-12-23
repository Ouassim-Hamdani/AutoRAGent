from smolagents import CodeAgent, PythonInterpreterTool, FinalAnswerTool, OpenAIServerModel, ToolCall, FinalAnswerStep
import os, json

from tools import ragify_document,parse_document,list_collections,query_collection
from prompt import PROMPT
from dotenv import load_dotenv

load_dotenv()


class AutoRAGENT:
    def __init__(self, model="gpt-5-mini", max_steps=12):
        self.model = OpenAIServerModel(
            model_id=model,
            api_base="https://api.openai.com/v1",
            api_key=os.environ["OPENAI_API_KEY"]
        )

        self.tools = [ragify_document,parse_document,list_collections,query_collection, PythonInterpreterTool(), FinalAnswerTool()]

        self.agent = CodeAgent(tools=self.tools, model=self.model,
                               additional_authorized_imports=['pandas', "os", 'matplotlib.*', "numpy.*", "seaborn.*",
                                                              "csv", "json", "posixpath"], max_steps=max_steps)

    def __call__(self, query, history=None, stream=False, session_id=None):
        if history:
            if session_id:
                return self.agent.run(
                    PROMPT + f"Session ID : {session_id}\n\n     Current History of Conversation : {history}\n\n   User New Question : {query}",
                    stream=stream)
            return self.agent.run(
                PROMPT + f"Current History of Conversation : {history}\n\n   User New Question : {query}",
                stream=stream)
        else:
            if session_id:
                self.agent.run(PROMPT + f"Session ID : {session_id}\n\n    User Question : {query}", stream=stream)
            return self.agent.run(PROMPT + f"User Question : {query}", stream=stream)

    def parse_step(self, step):
        if type(step) == ToolCall and step.name == "python_interpreter":
            print("happend")
            return f"\n```python\n{step.arguments}\n```\n\n", "code"
        elif type(step) == FinalAnswerStep:
            return f"{step.output}\n", "final"
        return "", "other"

if __name__ == "__main__":
    agent = AutoRAGENT()
    response = agent("Can you read this document for me? it's at '../../samples/sample.pdf' and tell me what it is about", stream=False)
    print(response)



