from langchain_community.chat_models import ChatTongyi
from typing import Union, List, Dict, Generator, Optional


class LLM:
    def __init__(self, model_name, api_key, temperature=0.1):
        self.model = ChatTongyi(
            model_name=model_name,
            dashscope_api_key=api_key,
            temperature=temperature,
        )
        # 存储最后一次调用的 tokens 使用信息
        self._last_usage = {
            'prompt_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0,
            'cached_tokens': 0
        }
        self._last_metadata = {}

    def _update_usage(self, usage: Dict, metadata: Dict = None):
        """
        更新内部存储的 usage 信息
        
        Args:
            usage: tokens 使用信息
            metadata: 元数据信息
        """
        self._last_usage = usage
        if metadata:
            self._last_metadata = metadata

    def get_usage(self) -> Dict:
        """
        获取最后一次调用的 tokens 使用信息
        
        Returns:
            dict: {
                'prompt_tokens': int,
                'output_tokens': int,
                'total_tokens': int,
                'cached_tokens': int
            }
        """
        return self._last_usage

    def get_metadata(self) -> Dict:
        """
        获取最后一次调用的元数据信息
        
        Returns:
            dict: {
                'model_name': str,
                'finish_reason': str,
                'request_id': str
            }
        """
        return self._last_metadata

    def chat_invoke(self, prompt: str, system_prompt: str = None) -> Dict:
        """
        调用 LLM 模型进行对话
        
        Args:
            prompt: 用户输入的提示词
            system_prompt: 系统提示词（可选）
            
        Returns:
            dict: {
                'response': str - 响应内容,
                'usage': {
                    'prompt_tokens': int,
                    'output_tokens': int,
                    'total_tokens': int,
                    'cached_tokens': int
                },
                'success': bool,
                'metadata': {
                    'model_name': str,
                    'finish_reason': str,
                    'request_id': str
                }
            }
        """
        try:
            # 构建消息列表
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            else:
                messages = [{"role": "user", "content": prompt}]
            
            # 调用模型
            response = self.model.invoke(messages)
            
            # 提取 tokens 使用信息
            usage = {
                'prompt_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cached_tokens': 0
            }
            
            metadata = {}
            
            # 从 response_metadata 中提取信息
            if hasattr(response, 'response_metadata'):
                resp_meta = response.response_metadata
                
                # 提取 token 信息
                if 'token_usage' in resp_meta:
                    token_info = resp_meta['token_usage']
                    usage['prompt_tokens'] = token_info.get('input_tokens', 0)
                    usage['output_tokens'] = token_info.get('output_tokens', 0)
                    usage['total_tokens'] = token_info.get('total_tokens', 0)
                    usage['cached_tokens'] = token_info.get('prompt_tokens_details', {}).get('cached_tokens', 0)
                
                # 提取其他元数据
                metadata['model_name'] = resp_meta.get('model_name', '')
                metadata['finish_reason'] = resp_meta.get('finish_reason', '')
                metadata['request_id'] = resp_meta.get('request_id', '')
            
            # 更新内部存储
            self._update_usage(usage, metadata)
            
            return {
                'response': response.content,
                'usage': usage,
                'success': True,
                'metadata': metadata
            }
        except Exception as e:
            error_usage = {
                'prompt_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cached_tokens': 0
            }
            self._update_usage(error_usage, {})
            
            return {
                'response': str(e),
                'usage': error_usage,
                'success': False,
                'metadata': {}
            }

    def chat_stream(self, prompt: str, system_prompt: str = None) -> Generator:
        """
        流式调用 LLM 模型
        
        Args:
            prompt: 用户输入的提示词
            system_prompt: 系统提示词（可选）
            
        Yields:
            dict: {
                'content': str - 当前片段内容,
                'usage': dict - 最终会在最后一个片段返回完整 tokens 信息,
                'success': bool,
                'metadata': dict
            }
        """
        try:
            # 构建消息列表
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            else:
                messages = [{"role": "user", "content": prompt}]
            
            # 使用流式调用
            full_response = ""
            usage = {
                'prompt_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cached_tokens': 0
            }
            metadata = {}
            
            # 流式输出内容
            for chunk in self.model.stream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    full_response += chunk.content
                    yield {
                        'content': chunk.content,
                        'usage': usage,  # 流式过程中 usage 为 0
                        'success': True,
                        'metadata': metadata
                    }
            
            # 流式结束后，使用 invoke 获取完整的 usage 信息
            # 这是因为 langchain 的流式 chunk 中不包含 token_usage
            complete_response = self.model.invoke(messages)
            
            # 从完整响应中提取 tokens 使用信息
            if hasattr(complete_response, 'response_metadata'):
                resp_meta = complete_response.response_metadata
                
                if 'token_usage' in resp_meta:
                    token_info = resp_meta['token_usage']
                    usage['prompt_tokens'] = token_info.get('input_tokens', 0)
                    usage['output_tokens'] = token_info.get('output_tokens', 0)
                    usage['total_tokens'] = token_info.get('total_tokens', 0)
                    usage['cached_tokens'] = token_info.get('prompt_tokens_details', {}).get('cached_tokens', 0)
                
                metadata['model_name'] = resp_meta.get('model_name', '')
                metadata['finish_reason'] = resp_meta.get('finish_reason', '')
                metadata['request_id'] = resp_meta.get('request_id', '')
            
            # 更新内部存储
            self._update_usage(usage, metadata)
            
        except Exception as e:
            error_usage = {
                'prompt_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cached_tokens': 0
            }
            self._update_usage(error_usage, {})
            
            yield {
                'content': str(e),
                'usage': error_usage,
                'success': False,
                'metadata': {}
            }
    
    def get_llm(self):
        """
        获取底层的 model 对象，供外部模块直接使用
        
        Returns:
            ChatTongyi: langchain 的 ChatTongyi 模型对象
        """
        return self.model


if __name__ == "__main__":
    from config import MODEL_NAME, API_KEY, TEMPERATURE
    
    # 测试普通调用
    print("=== 测试普通调用 ===")
    llm = LLM(MODEL_NAME, API_KEY, temperature=TEMPERATURE)
    result = llm.chat_invoke("你好啊", system_prompt="你是一个友好的助手")
    
    if result['success']:
        print(f"回复：{result['response']}")
        print(f"Tokens 使用：{result['usage']}")
        print(f"模型信息：{result['metadata']}")
    else:
        print(f"错误：{result['response']}")
    
    # 测试流式调用
    print("\n=== 测试流式调用 ===")
    for chunk in llm.chat_stream("你好啊", system_prompt="你是一个友好的助手"):
        if chunk['success']:
            print(chunk['content'], end='', flush=True)
    
    print("\n\n测试完成！")
