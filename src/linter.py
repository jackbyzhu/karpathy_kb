import os
import re
import json
from src.config import WIKI_DIR


def scan_wiki_files(output_dir: str = WIKI_DIR):
    """
    扫描wiki目录下的所有md文件

    Args:
        output_dir: wiki目录路径

    Returns:
        dict: {文件名: 文件内容}的字典
    """
    if not os.path.isabs(output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, output_dir)

    wiki_files = {}
    concepts_dir = os.path.join(output_dir, "concepts")
    people_dir = os.path.join(output_dir, "people")

    for dir_path in [concepts_dir, people_dir]:
        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                if filename.endswith('.md'):
                    file_path = os.path.join(dir_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        wiki_files[filename] = f.read()

    return wiki_files


def extract_backlinks(markdown_content: str):
    """
    从Markdown内容中提取双向链接

    Args:
        markdown_content: Markdown文档内容

    Returns:
        list: 双向链接列表，如[[注意力机制]] -> [注意力机制]
    """
    pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, markdown_content)
    return matches


def check_dead_links(output_dir: str = WIKI_DIR):
    """
    检查知识库中的死链

    Args:
        output_dir: wiki目录路径

    Returns:
        dict: {源文件: [死链列表]}的字典
    """
    if not os.path.isabs(output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, output_dir)

    wiki_files = scan_wiki_files(output_dir)

    dead_links = {}

    for filename, content in wiki_files.items():
        links = extract_backlinks(content)
        file_dead_links = []

        for link in links:
            link_file = f"{link}.md"
            if link_file not in wiki_files:
                file_dead_links.append(link)

        if file_dead_links:
            dead_links[filename] = file_dead_links

    return dead_links


def remove_dead_links(dead_links: dict, output_dir: str = WIKI_DIR, dry_run: bool = True):
    """
    清除死链

    Args:
        dead_links: 死链字典 {源文件: [死链列表]}
        output_dir: wiki目录路径
        dry_run: 如果为True，只打印不实际修改

    Returns:
        list: 被修改的文件列表
    """
    if not os.path.isabs(output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, output_dir)

    modified_files = []

    for filename, dead_link_list in dead_links.items():
        for dir_name in ['concepts', 'people']:
            file_path = os.path.join(output_dir, dir_name, filename)
            if os.path.exists(file_path):
                break

        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        for dead_link in dead_link_list:
            pattern = rf'- \[\[{re.escape(dead_link)}\]\]\n'
            content = re.sub(pattern, '', content)

            pattern = rf'- \[\[{re.escape(dead_link)}\]\]'
            content = re.sub(pattern, '', content)

        if content != original_content:
            if dry_run:
                print(f"[DRY RUN] Would modify: {filename}")
                print(f"  Removed links: {dead_link_list}")
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Modified: {filename}")
                print(f"  Removed links: {dead_link_list}")
            modified_files.append(filename)

    return modified_files


def lint_knowledge_base(interactive: bool = True, output_dir: str = WIKI_DIR):
    """
    检查知识库中的死链

    Args:
        interactive: 是否交互式操作（询问用户是否清除死链）
        output_dir: wiki目录路径

    Returns:
        dict: 死链字典
    """
    if not os.path.isabs(output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, output_dir)

    print("Scanning knowledge base for dead links...")
    dead_links = check_dead_links(output_dir)

    if not dead_links:
        print("No dead links found. Knowledge base is clean!")
        return {}

    print(f"\nFound dead links in {len(dead_links)} files:")
    for filename, links in dead_links.items():
        print(f"\n{filename}:")
        for link in links:
            print(f"  - [[{link}]]")

    if interactive:
        print("\n" + "="*50)
        response = input("Do you want to remove these dead links? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            print("\nRemoving dead links...")
            remove_dead_links(dead_links, output_dir, dry_run=False)
            print("\nDead links removed successfully!")
        else:
            print("\nNo changes made.")
    else:
        print("\nUse remove_dead_links() to remove dead links.")

    return dead_links


def linter(output_dir: str = WIKI_DIR, remove: bool = False):
    """
    外部函数接口，检查知识库中的死链

    Args:
        output_dir: wiki目录路径
        remove: 是否自动删除死链

    Returns:
        dict: 死链字典 {源文件: [死链列表]}
    """
    if not os.path.isabs(output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, output_dir)

    print("Scanning knowledge base for dead links...")
    dead_links = check_dead_links(output_dir)

    if not dead_links:
        print("No dead links found. Knowledge base is clean!")
        return {}

    print(f"\nFound dead links in {len(dead_links)} files:")
    for filename, links in dead_links.items():
        print(f"\n{filename}:")
        for link in links:
            print(f"  - [[{link}]]")

    if remove:
        print("\nRemoving dead links...")
        remove_dead_links(dead_links, output_dir, dry_run=False)
        print("\nDead links removed successfully!")
    else:
        print("\nUse remove=True to remove dead links.")

    return dead_links


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        print("Running in dry-run mode...\n")
        dead_links = lint_knowledge_base(interactive=False)
        if dead_links:
            print("\nUse --remove flag to actually remove dead links.")
    elif len(sys.argv) > 1 and sys.argv[1] == '--remove':
        print("Removing dead links...\n")
        dead_links = check_dead_links()
        if dead_links:
            remove_dead_links(dead_links, dry_run=False)
            print("\nDone!")
        else:
            print("No dead links found.")
    else:
        print("=== Knowledge Base Linter ===\n")
        lint_knowledge_base(interactive=True)
