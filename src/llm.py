from langchain_community.chat_models import ChatTongyi
from src.ingest import DocumentProcessor


class LLM:
    def __init__(self, model_name, api_key, temperature=0.1):
        self.model = ChatTongyi(
            model_name=model_name,
            dashscope_api_key=api_key,
            temperature=temperature,
        )

    def chat_invoke(self, messages: list, system_prompt: str = None):
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages
        return self.model.invoke(full_messages)

    def chat_stream(self, messages: list, system_prompt: str = None):
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages
        return self.model.stream(full_messages)

    def stream_chat(self, messages: list, system_prompt: str = None):
        return self.chat_stream(messages, system_prompt)


if __name__ == "__main__":
    # 测试ingest模块
    print("Testing DocumentProcessor...")
    processor = DocumentProcessor()

    # 测试处理Markdown文件
    md_path = r"C:\Users\94795\Desktop\27考研王道408操作系统 前五章完整版笔记.pdf"
    print(f"Processing file: {md_path}")
    try:
        text = processor.process(md_path)
        print("Successfully processed cat.md")
        print(text)
    except Exception as e:
        print(f"Error processing cat.md: {str(e)}")
