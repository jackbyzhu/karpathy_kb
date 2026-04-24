import os
import re
import json
from src.ingest import DocumentProcessor
from src.llm import LLM
from src.config import (
    RAW_DIR, WIKI_DIR, OUTPUT_DIR, STATE_FILE,
    MODEL_NAME, API_KEY,
    COMPILATION_PROMPT, INCREMENTAL_COMPILATION_PROMPT,TEMPERATURE
)


def read_raw_files(raw_dir: str = RAW_DIR):
    """
    读取raw目录下的所有文件，利用ingest模块处理，并返回合并后的文本
    Args:
        raw_dir: raw目录的路径
    Returns:
        str: 所有文件内容合并后的文本
    """
    processor = DocumentProcessor()
    all_text = []

    supported_extensions = ['.pdf', '.md', '.txt', '.jpg', '.jpeg', '.png', '.gif']

    if not os.path.isabs(raw_dir):
        if os.path.exists(raw_dir):
            raw_dir = os.path.abspath(raw_dir)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            raw_dir = os.path.join(script_dir, raw_dir)

    print(f"Looking for files in: {raw_dir}")

    if not os.path.exists(raw_dir):
        print(f"Directory not found: {raw_dir}")
        return ""

    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            if file_ext in supported_extensions:
                try:
                    print(f"Processing: {file_path}")
                    text = processor.process(file_path)
                    all_text.append(f"=== {file_path} ===\n{text}\n")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    continue
            else:
                print(f"Skipping unsupported file: {file_path}")

    combined_text = "\n".join(all_text)
    return combined_text


def save_model_output(knowledge_base: str, output_file: str = "model.txt"):
    """
    将模型的原始输出保存到文件中
    """
    try:
        if not os.path.isabs(output_file):
            from src.config import PROJECT_ROOT
            output_file = os.path.join(PROJECT_ROOT, output_file)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(knowledge_base)

        print(f"Model output saved to: {output_file}")
        return True
    except Exception as e:
        print(f"Error saving model output: {str(e)}")
        return False


def compile_knowledge(raw_text: str, model_name: str = MODEL_NAME, api_key: str = API_KEY, prompt_template: str = COMPILATION_PROMPT):
    """
    使用LLM生成知识库
    """
    llm = LLM(model_name, api_key, temperature=TEMPERATURE)

    prompt = f"{prompt_template}\n{raw_text}"

    print("Generating knowledge base...")
    print(f"Prompt length: {len(prompt)} characters")

    try:
        response = llm.chat_invoke(prompt)
        knowledge_base = response.content

        save_model_output(knowledge_base)

        return knowledge_base
    except Exception as e:
        print(f"Error generating knowledge base: {str(e)}")
        return ""


def parse_wiki_output(knowledge_base: str):
    """
    解析知识库输出，提取每个Markdown文档
    使用```markdown和```作为每个文件的分隔符
    """
    try:
        documents = []

        pattern = r'```markdown\n(.*?)```'
        matches = re.findall(pattern, knowledge_base, re.DOTALL)

        for match in matches:
            doc = match.strip()
            if doc:
                documents.append(doc)

        return documents
    except Exception as e:
        print(f"Error parsing wiki output: {str(e)}")
        return []


def extract_title(markdown_content: str):
    """
    从Markdown内容中提取标题
    """
    title_match = re.search(r'title:\s*"(.*?)"', markdown_content)
    if title_match:
        return title_match.group(1)

    title_match = re.search(r'^#\s+(.*?)$', markdown_content, re.MULTILINE)
    if title_match:
        return title_match.group(1)

    return "Untitled"


def is_person_document(markdown_content: str):
    """
    判断是否为人物文档
    """
    tags_match = re.search(r'tags:\s*\[(.*?)\]', markdown_content)
    if tags_match:
        tags = tags_match.group(1)
        if '"人物"' in tags or '人物' in tags:
            return True

    content_lower = markdown_content.lower()
    if '简介' in content_lower and ('职业生涯' in content_lower or '个人简介' in content_lower):
        return True

    return False


def save_to_wiki(documents, output_dir: str = WIKI_DIR):
    """
    将解析后的Markdown文档保存到相应文件夹中
    人物文档保存到wiki/people文件夹
    其他文档保存到wiki/concepts文件夹
    """
    saved_files = []

    if not os.path.isabs(output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, output_dir)

    # 确保wiki目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    concepts_dir = os.path.join(output_dir, "concepts")
    people_dir = os.path.join(output_dir, "people")

    for dir_path in [concepts_dir, people_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    for i, doc in enumerate(documents):
        title = extract_title(doc)
        filename = f"{title}.md".replace('/', '_').replace('\\', '_')

        if title == "README":
            file_path = os.path.join(output_dir, filename)
        elif is_person_document(doc):
            file_path = os.path.join(people_dir, filename)
        else:
            file_path = os.path.join(concepts_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc)
            saved_files.append(file_path)
            print(f"Saved: {file_path}")
        except Exception as e:
            print(f"Error saving {filename}: {str(e)}")

    return saved_files


def get_compiled_files(state_file: str = STATE_FILE):
    """
    获取已编译的文件列表
    """
    try:
        if not os.path.isabs(state_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            state_file = os.path.join(script_dir, state_file)

        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('compiled_files', []))
        return set()
    except Exception as e:
        print(f"Error reading compiled files: {str(e)}")
        return set()


def save_compiled_files(compiled_files: set, state_file: str = STATE_FILE):
    """
    保存已编译的文件列表
    """
    try:
        if not os.path.isabs(state_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            state_file = os.path.join(script_dir, state_file)

        state_dir = os.path.dirname(state_file)
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)

        data = {'compiled_files': list(compiled_files)}
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Compiled files state saved: {len(compiled_files)} files")
        return True
    except Exception as e:
        print(f"Error saving compiled files: {str(e)}")
        return False


def get_existing_concepts(output_dir: str = WIKI_DIR):
    """
    获取知识库中已有的概念列表，用于增量编译时的双向链接
    """
    try:
        if not os.path.isabs(output_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, output_dir)

        concepts = []
        concepts_dir = os.path.join(output_dir, "concepts")
        people_dir = os.path.join(output_dir, "people")

        if os.path.exists(concepts_dir):
            for filename in os.listdir(concepts_dir):
                if filename.endswith('.md') and filename != 'README.md':
                    title = filename[:-3]
                    concepts.append(title)

        if os.path.exists(people_dir):
            for filename in os.listdir(people_dir):
                if filename.endswith('.md'):
                    title = filename[:-3]
                    concepts.append(title)

        if concepts:
            return "\n".join([f"- {c}" for c in sorted(concepts)])
        return "（暂无现有概念）"
    except Exception as e:
        print(f"Error getting existing concepts: {str(e)}")
        return "（暂无现有概念）"


def get_uncompiled_files(raw_dir: str = RAW_DIR, compiled_files: set = None):
    """
    获取未编译的文件列表
    """
    if compiled_files is None:
        compiled_files = set()

    if not os.path.isabs(raw_dir):
        if os.path.exists(raw_dir):
            raw_dir = os.path.abspath(raw_dir)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            raw_dir = os.path.join(script_dir, raw_dir)

    uncompiled_files = {}
    supported_extensions = ['.pdf', '.md', '.txt', '.jpg', '.jpeg', '.png', '.gif']

    if not os.path.exists(raw_dir):
        return uncompiled_files

    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            if file_ext in supported_extensions:
                if file not in compiled_files:
                    uncompiled_files[file] = file_path

    return uncompiled_files


def update_tag_json_for_new_files(new_files: list, output_dir: str = WIKI_DIR):
    """
    根据新增加的文件更新tag.json
    """
    try:
        if not os.path.isabs(output_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, output_dir)

        index_dir = os.path.join(output_dir, "index")
        tag_file = os.path.join(index_dir, "tag.json")

        tags = {}
        if os.path.exists(tag_file):
            with open(tag_file, 'r', encoding='utf-8') as f:
                tags = json.load(f)

        for file_path in new_files:
            if not os.path.exists(file_path):
                continue

            rel_path = os.path.relpath(file_path, output_dir)
            filename = rel_path.replace('\\', '/')

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tags_match = re.search(r'tags:\s*\[(.*?)\]', content)
            if tags_match:
                tag_str = tags_match.group(1)
                tag_list = re.findall(r'"([^"]+)"', tag_str)
                for tag in tag_list:
                    if tag not in tags:
                        tags[tag] = []
                    if filename not in tags[tag]:
                        tags[tag].append(filename)

        with open(tag_file, 'w', encoding='utf-8') as f:
            json.dump(tags, f, ensure_ascii=False, indent=2)

        print(f"Tag JSON updated with {len(new_files)} new files")
        return True
    except Exception as e:
        print(f"Error updating tag JSON: {str(e)}")
        return False


def generate_tag_json(output_dir: str = WIKI_DIR):
    """
    生成Obsidian需要的tag.json文件
    """
    try:
        if not os.path.isabs(output_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, output_dir)

        index_dir = os.path.join(output_dir, "index")
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)

        tags = {}
        concepts_dir = os.path.join(output_dir, "concepts")
        people_dir = os.path.join(output_dir, "people")

        if os.path.exists(concepts_dir):
            for filename in os.listdir(concepts_dir):
                if filename.endswith('.md') and filename != 'README.md':
                    file_path = os.path.join(concepts_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tags_match = re.search(r'tags:\s*\[(.*?)\]', content)
                        if tags_match:
                            tag_str = tags_match.group(1)
                            tag_list = re.findall(r'"([^"]+)"', tag_str)
                            for tag in tag_list:
                                if tag not in tags:
                                    tags[tag] = []
                                rel_path = os.path.relpath(file_path, output_dir)
                                tags[tag].append(rel_path.replace('\\', '/'))

        if os.path.exists(people_dir):
            for filename in os.listdir(people_dir):
                if filename.endswith('.md'):
                    file_path = os.path.join(people_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tags_match = re.search(r'tags:\s*\[(.*?)\]', content)
                        if tags_match:
                            tag_str = tags_match.group(1)
                            tag_list = re.findall(r'"([^"]+)"', tag_str)
                            for tag in tag_list:
                                if tag not in tags:
                                    tags[tag] = []
                                rel_path = os.path.relpath(file_path, output_dir)
                                tags[tag].append(rel_path.replace('\\', '/'))

        tag_file = os.path.join(index_dir, "tag.json")
        with open(tag_file, 'w', encoding='utf-8') as f:
            json.dump(tags, f, ensure_ascii=False, indent=2)

        print(f"Tag JSON generated: {tag_file}")
        print(f"Found {len(tags)} unique tags")
        return True
    except Exception as e:
        print(f"Error generating tag JSON: {str(e)}")
        return False


def build_wiki(knowledge_base: str, output_dir: str = WIKI_DIR):
    """
    从知识库输出构建wiki
    """
    documents = parse_wiki_output(knowledge_base)

    if not documents:
        print("No documents found in knowledge base.")
        return []

    print(f"Found {len(documents)} documents in knowledge base.")

    saved_files = save_to_wiki(documents, output_dir)

    print(f"Successfully saved {len(saved_files)} files to {output_dir}.")
    return saved_files


def compile(
    raw_files: list = None,
    file_paths: list = None,
    incremental: bool = True,
    raw_dir: str = RAW_DIR,
    output_dir: str = WIKI_DIR
):
    """
    编译函数，整合了增量编译和全量编译

    Args:
        raw_files: 要编译的raw文件名列表（用于指定编译特定文件）
        file_paths: 要编译的raw文件路径列表（用于指定编译特定文件）
        incremental: 是否使用增量编译模式，默认为True
        raw_dir: raw目录路径
        output_dir: wiki输出目录路径

    Returns:
        bool: 是否编译成功
    """
    if incremental:
        # 获取未编译的文件
        if file_paths:
            compiled_files = get_compiled_files()
            uncompiled_files = {}
            for fp in file_paths:
                filename = os.path.basename(fp)
                if filename not in compiled_files:
                    uncompiled_files[filename] = fp
        elif raw_files:
            compiled_files = get_compiled_files()
            uncompiled_files = {}
            for fn in raw_files:
                if fn not in compiled_files:
                    uncompiled_files[fn] = os.path.join(raw_dir, fn)
        else:
            compiled_files = get_compiled_files()
            print(f"Already compiled files: {len(compiled_files)}")
            uncompiled_files = get_uncompiled_files(raw_dir, compiled_files)
            print(f"New files to compile: {len(uncompiled_files)}")

        if not uncompiled_files:
            print("无可用文件用于编译。知识库已是最新状态。")
            return False

        # 加载已存在的wiki知识库内容作为参考
        existing_wiki_content = ""
        if os.path.exists(output_dir):
            print("Loading existing wiki content as reference...")
            # 扫描wiki目录下的所有md文件
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.md') and file != 'README.md':
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                existing_wiki_content += f"=== {os.path.relpath(file_path, output_dir)} ===\n{content}\n\n"
                        except Exception as e:
                            print(f"Error reading {file_path}: {str(e)}")

        # 处理未编译的文件
        processor = DocumentProcessor()
        raw_content = ""

        print(f"Processing {len(uncompiled_files)} new files...")
        for filename, file_path in uncompiled_files.items():
            try:
                print(f"Processing: {file_path}")
                text = processor.process(file_path)
                raw_content += f"=== {filename} ===\n{text}\n"
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue

        if not raw_content:
            print("没有内容可处理。")
            return False

        # 构建完整的提示词，包含新文件和已存在的wiki内容作为参考
        existing_concepts = get_existing_concepts(output_dir)
        prompt_template = INCREMENTAL_COMPILATION_PROMPT.format(existing_concepts=existing_concepts)
        full_prompt = f"{prompt_template}\n\n## 新文件内容：\n{raw_content}\n\n## 已存在的知识库内容（作为参考）：\n{existing_wiki_content}\n\n## 重要说明：\n1. 只处理新文件和需要更新的文件\n2. 对于已存在的文件，只有在内容确实需要更新时才输出\n3. 不要为了修改而修改，要根据实际内容变化来决定\n4. 对于不需要更新的文件，不要输出\n5. 对于新文件，输出完整的内容" 

        knowledge_base = compile_knowledge(raw_content, prompt_template=full_prompt)

        if knowledge_base:
            print("\nKnowledge base generated successfully!")
            print(f"Output length: {len(knowledge_base)} characters")

            print("\nBuilding wiki...")
            saved_files = build_wiki(knowledge_base, output_dir)

            if saved_files:
                print(f"\nWiki built successfully with {len(saved_files)} files!")

                new_compiled = set(uncompiled_files.keys())
                all_compiled = compiled_files | new_compiled
                save_compiled_files(all_compiled)

                print("\nUpdating tag.json...")
                generate_tag_json(output_dir)

                print("\n增量编译完成！")
                return True
            else:
                print("Failed to build wiki.")
                return False
        else:
            print("Failed to generate knowledge base.")
            return False
    else:
        if file_paths:
            processor = DocumentProcessor()
            all_text = []
            for fp in file_paths:
                try:
                    print(f"Processing: {fp}")
                    text = processor.process(fp)
                    all_text.append(f"=== {os.path.basename(fp)} ===\n{text}\n")
                except Exception as e:
                    print(f"Error processing {fp}: {str(e)}")
                    continue
            raw_text = "\n".join(all_text)
        elif raw_files:
            processor = DocumentProcessor()
            all_text = []
            for fn in raw_files:
                fp = os.path.join(raw_dir, fn)
                try:
                    print(f"Processing: {fp}")
                    text = processor.process(fp)
                    all_text.append(f"=== {fn} ===\n{text}\n")
                except Exception as e:
                    print(f"Error processing {fp}: {str(e)}")
                    continue
            raw_text = "\n".join(all_text)
        else:
            print("Reading all files from raw directory...")
            raw_text = read_raw_files(raw_dir)

        if not raw_text:
            print("No content to process.")
            return False

        knowledge_base = compile_knowledge(raw_text)

        if knowledge_base:
            print("\nKnowledge base generated successfully!")
            print(f"Output length: {len(knowledge_base)} characters")

            print("\nBuilding wiki...")
            saved_files = build_wiki(knowledge_base, output_dir)

            if saved_files:
                print(f"\nWiki built successfully with {len(saved_files)} files!")
                for file_path in saved_files:
                    print(f"- {os.path.basename(file_path)}")

                print("\nGenerating tag.json...")
                generate_tag_json(output_dir)

                all_raw_files = get_uncompiled_files(raw_dir, set())
                compiled_files = set(all_raw_files.keys())
                save_compiled_files(compiled_files)

                print("\n全量编译完成！")
                return True
            else:
                print("Failed to build wiki.")
                return False
        else:
            print("Failed to generate knowledge base.")
            return False
