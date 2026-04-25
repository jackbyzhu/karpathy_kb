import os
import re
import json
from src.llm import LLM
from src.config import WIKI_DIR, OUTPUT_DIR, TEMPERATURE


def load_all_wiki_content(output_dir: str = WIKI_DIR):
    """
    加载wiki目录下所有md文件的内容

    Args:
        output_dir: wiki目录路径

    Returns:
        str: 所有md文件的内容合并
    """
    if not os.path.isabs(output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, output_dir)

    all_content = []
    concepts_dir = os.path.join(output_dir, "concepts")
    people_dir = os.path.join(output_dir, "people")
    index_dir = os.path.join(output_dir, "index")

    for dir_path in [concepts_dir, people_dir, index_dir]:
        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                if filename.endswith('.md'):
                    file_path = os.path.join(dir_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    relative_path = os.path.relpath(file_path, output_dir)
                    all_content.append(f"=== {relative_path} ===\n{content}\n")

    return "\n".join(all_content)


def load_conversation(session_id: str, sessions_dir: str = None):
    """
    加载指定会话的对话历史

    Args:
        session_id: 会话ID
        sessions_dir: sessions目录路径

    Returns:
        list: 对话历史列表 [{role: "user"/"assistant", content: str}]
    """
    if sessions_dir is None:
        sessions_dir = os.path.join(OUTPUT_DIR, "sessions")
    else:
        if not os.path.isabs(sessions_dir):
            from src.config import PROJECT_ROOT
            sessions_dir = os.path.join(PROJECT_ROOT, sessions_dir)

    session_file = os.path.join(sessions_dir, f"{session_id}.md")

    if not os.path.exists(session_file):
        return []

    messages = []
    with open(session_file, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'(=== User ===|=== Assistant ===)\n(.*?)(?====|=== User ===|=== Assistant ===|$)'
    matches = re.findall(pattern, content, re.DOTALL)

    for role, msg_content in matches:
        if role == '=== User ===':
            messages.append({"role": "user", "content": msg_content.strip()})
        elif role == '=== Assistant ===':
            messages.append({"role": "assistant", "content": msg_content.strip()})

    return messages


def save_conversation(session_id: str, role: str, content: str, sessions_dir: str = None):
    """
    保存对话到会话文件（追加模式）

    Args:
        session_id: 会话ID
        role: 角色 ("user" 或 "assistant")
        content: 对话内容
        sessions_dir: sessions目录路径
    """
    if sessions_dir is None:
        sessions_dir = os.path.join(OUTPUT_DIR, "sessions")
    else:
        if not os.path.isabs(sessions_dir):
            from src.config import PROJECT_ROOT
            sessions_dir = os.path.join(PROJECT_ROOT, sessions_dir)

    if not os.path.exists(sessions_dir):
        os.makedirs(sessions_dir)

    session_file = os.path.join(sessions_dir, f"{session_id}.md")

    role_marker = "=== User ===" if role == "user" else "=== Assistant ==="

    with open(session_file, 'a', encoding='utf-8') as f:
        f.write(f"{role_marker}\n{content}\n\n")


def build_system_prompt(wiki_content: str):
    """
    构建系统提示词，要求AI完全根据知识库回答

    Args:
        wiki_content: 知识库内容

    Returns:
        str: 系统提示词
    """
    return f"""你是一个基于知识库的问答助手。请完全根据以下知识库内容回答用户的问题。

## 重要规则：
1. **必须严格基于知识库内容回答**，不要添加知识库中没有的信息
2. 如果知识库中没有相关信息，明确告知用户"暂无相关内容"
3. 在回答中可以引用知识库中的具体内容作为依据
4. 保持回答的准确性和一致性
5. **必须在回答的最后列出引用的知识库文档**（不包含README.md）

## 知识库内容：
{wiki_content}

## 回答格式：
- 如果有相关信息：
  1. 详细引用知识库内容进行回答
  2. 最后以"引用的知识库文档："开头，列出所有引用的文档路径（不包含README.md）
- 如果没有相关信息：明确说明"暂无相关内容"

请开始回答用户的问题。
"""


def query(
    question: str,
    session_id: str = "default",
    load_history: bool = True,
    save_history: bool = True,
    stream: bool = False,
    model_name: str = None,
    api_key: str = None,
    output_dir: str = WIKI_DIR
):
    """
    外部函数接口，用户提问，模型根据知识库回答

    Args:
        question: 用户问题
        session_id: 会话 ID，用于存储和加载对话历史
        load_history: 是否加载历史对话到当前会话
        save_history: 是否保存本次对话到历史记录
        stream: 是否流式输出
        model_name: 模型名称，默认使用 config 中的配置
        api_key: API 密钥，默认使用 config 中的配置
        output_dir: wiki 目录路径

    Returns:
        str: AI 回答内容（stream=False 时）
        generator: AI 回答内容的生成器（stream=True 时）
        dict: 包含 usage(tokens 使用信息)
    """
    from src.config import MODEL_NAME, API_KEY

    model_name = model_name or MODEL_NAME
    api_key = api_key or API_KEY

    if not os.path.isabs(output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, output_dir)

    # 确保 wiki 目录及其子目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        concepts_dir = os.path.join(output_dir, "concepts")
        people_dir = os.path.join(output_dir, "people")
        index_dir = os.path.join(output_dir, "index")
        sessions_dir = os.path.join(output_dir, "..", "output", "sessions")
        for dir_path in [concepts_dir, people_dir, index_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        if not os.path.exists(sessions_dir):
            os.makedirs(sessions_dir)
        print(f"Created wiki directory structure: {output_dir}")
        return "错误：知识库为空，请先编译知识库。", {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    print("Loading knowledge base...")
    wiki_content = load_all_wiki_content(output_dir)

    if not wiki_content:
        return "错误：知识库为空，请先编译知识库。", {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    print(f"Knowledge base loaded: {len(wiki_content)} characters")

    system_prompt = build_system_prompt(wiki_content)

    llm = LLM(model_name=model_name, api_key=api_key, temperature=TEMPERATURE)

    messages = []
    if load_history:
        history = load_conversation(session_id)
        if history:
            print(f"Loaded {len(history)} historical messages")
            messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]

    messages.append({"role": "user", "content": question})

    if stream:
        response = ""
        chunk_count = 0
        
        # 使用流式调用
        try:
            for chunk_result in llm.chat_stream(question, system_prompt=system_prompt):
                chunk_count += 1
                if chunk_result['success'] and chunk_result.get('content'):
                    content = chunk_result['content']
                    response += content
                    print(content, end='', flush=True)
        except Exception as e:
            print(f"\n流式输出过程中出错：{str(e)}")
            # 如果流式失败，回退到普通调用
            print("回退到普通调用模式...")
            result = llm.chat_invoke(question, system_prompt=system_prompt)
            if result['success']:
                response = result['response']
                print(response, end='')
            else:
                return f"错误：{result['response']}", llm.get_usage()
        
        print()  # 换行
        
        # 从 LLM 实例获取 tokens 使用信息
        final_usage = llm.get_usage()
        final_metadata = llm.get_metadata()
        
        if save_history:
            save_conversation(session_id, "user", question)
            save_conversation(session_id, "assistant", response)
        
        # 打印 tokens 使用信息
        if final_usage.get('total_tokens', 0) > 0:
            print(f"Tokens used: {final_usage['total_tokens']} (input: {final_usage['prompt_tokens']}, output: {final_usage['output_tokens']}, cached: {final_usage['cached_tokens']})")
            if final_metadata.get('model_name'):
                print(f"Model: {final_metadata['model_name']}")
        
        return response, final_usage
    else:
        result = llm.chat_invoke(question, system_prompt=system_prompt)
        usage = result.get('usage', {'prompt_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cached_tokens': 0})
        metadata = result.get('metadata', {})
        
        if result['success']:
            answer = result['response']
            
            # 打印 tokens 使用信息
            print(f"Tokens used: {usage['total_tokens']} (input: {usage['prompt_tokens']}, output: {usage['output_tokens']}, cached: {usage['cached_tokens']})")
            if metadata.get('model_name'):
                print(f"Model: {metadata['model_name']}")
            
            if save_history:
                save_conversation(session_id, "user", question)
                save_conversation(session_id, "assistant", answer)
            
            return answer, usage
        else:
            print(f"Error: {result['response']}")
            return result['response'], usage


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python query_engine.py <question> [session_id] [--stream]")
        print("Example: python query_engine.py '什么是注意力机制？' my_session")
        sys.exit(1)

    question = sys.argv[1]
    session_id = sys.argv[2] if len(sys.argv) > 2 else "default"
    stream = "--stream" in sys.argv

    print(f"=== Session: {session_id} ===\n")

    if stream:
        print("Streaming mode...\n")
        query(question, session_id=session_id, load_history=True, save_history=True, stream=True)
    else:
        answer = query(question, session_id=session_id, load_history=True, save_history=True, stream=False)
        print(f"Answer:\n{answer}")
