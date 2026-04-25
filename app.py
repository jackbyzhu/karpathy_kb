from src.compiler import compile
from src.linter import linter
from src.query_engine import query

if __name__ == "__main__":
    # 测试增量编译（默认）
    print("=== Testing incremental compilation ===")
    compile(incremental=True)

    # 或者测试全量编译
    # print("=== Testing full compilation ===")
    # compile(incremental=False)

    # 或者指定特定文件编译
    # print("=== Testing specific files compilation ===")
    # compile(raw_files=["cat.md", "dog.md"])

    # 检测并删除死链
    print("\n=== Testing dead link detection and removal ===")
    dead_links = linter(remove=True)
    if dead_links:
        print("Dead links found and removed:")
        for files, links in dead_links.items():
            print(f"- {files}: {links}")
    else:
        print("No dead links found.")

    # 测试对话系统
    print("\n=== Testing query system ===")
    print("Enter your questions (type 'exit' to quit):")
    
    session_id = "1"
    total_tokens = 0  # 累计 tokens 使用
    
    while True:
        question = input("\nYou: ")
        
        if question.lower() == 'exit':
            break
        
        print("Processing...\n")
        
        try:
            # 使用流式输出
            answer, usage = query(
                question=question,
                session_id=session_id,
                load_history=True,
                save_history=True,
                stream=True
            )
            
            # 显示 tokens 使用信息
            if usage and usage.get('total_tokens', 0) > 0:
                print(f"\n✅ 本次 Tokens 使用：")
                print(f"   - 输入：{usage['prompt_tokens']}")
                print(f"   - 输出：{usage['output_tokens']}")
                print(f"   - 总计：{usage['total_tokens']}")
                if usage.get('cached_tokens', 0) > 0:
                    print(f"   - 缓存：{usage['cached_tokens']}")
                
                # 累计 tokens
                total_tokens += usage['total_tokens']
                print(f"\n📊 累计 Tokens 使用：{total_tokens}")
            else:
                print(f"\n⚠️ 未能获取 tokens 使用信息")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\nQuery system test completed.")

