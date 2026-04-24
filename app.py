from src.compiler import compile
from src.linter import linter
from src.query_engine import query

if __name__ == "__main__":
    # 测试增量编译（默认）
    print("=== Testing incremental compilation ===")
    #compile(incremental=False)

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
    
    session_id = "default"
    
    while True:
        question = input("\nYou: ")
        
        if question.lower() == 'exit':
            break
        
        print("Processing...")
        
        try:
            answer = query(
                question=question,
                session_id=session_id,
                load_history=True,
                save_history=True,
                stream= False
            )
            print(answer)
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nQuery system test completed.")

