import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm import LLM
from src.config import MODEL_NAME, API_KEY

# 测试LLM类的chat_invoke方法是否支持system_prompt参数
print("Testing LLM.chat_invoke with system_prompt...")

# 初始化LLM实例
llm = LLM(model_name=MODEL_NAME, api_key=API_KEY)

# 准备测试消息
messages = [{"role": "user", "content": "你好，告诉我一个关于猫的有趣事实"}]

# 准备系统提示词
system_prompt = "你是一个知识渊博的助手，专门回答关于动物的问题。"

# 测试chat_invoke方法
print("Testing chat_invoke with system_prompt...")
try:
    response = llm.chat_invoke(messages, system_prompt=system_prompt)
    print("Success! chat_invoke with system_prompt works.")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"Error: {str(e)}")

# 测试stream_chat方法
print("\nTesting stream_chat with system_prompt...")
try:
    print("Streaming response:")
    for chunk in llm.stream_chat(messages, system_prompt=system_prompt):
        print(chunk, end="", flush=True)
    print("\nSuccess! stream_chat with system_prompt works.")
except Exception as e:
    print(f"Error: {str(e)}")
