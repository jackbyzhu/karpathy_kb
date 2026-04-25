
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, UnstructuredImageLoader, TextLoader, UnstructuredMarkdownLoader

import os

class DocumentProcessor:
    def __init__(self):
        pass

    def _resolve_path(self, path):
        """解析路径，处理相对路径和绝对路径"""
        # 如果是绝对路径，直接返回
        if os.path.isabs(path):
            return path
        # 如果是相对路径，尝试相对于当前工作目录解析
        elif os.path.exists(path):
            return os.path.abspath(path)
        # 尝试相对于脚本所在目录解析
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            relative_path = os.path.join(script_dir, path)
            if os.path.exists(relative_path):
                return relative_path
            else:
                raise FileNotFoundError(f"File not found: {path}")

    def load_pdf(self, file_path: str):
        """加载并解析PDF文件"""
        try:
            resolved_path = self._resolve_path(file_path)
            loader = PyPDFLoader(resolved_path)
            documents = loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Failed to load PDF: {str(e)}")

    def load_webpage(self, url: str):
        """加载网页并转换为Markdown格式"""
        try:
            # 使用WebBaseLoader加载网页
            loader = WebBaseLoader(url)
            documents = loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Failed to load webpage: {str(e)}")

    def load_image(self, image_path: str):
        """加载图片并进行OCR"""
        try:
            resolved_path = self._resolve_path(image_path)
            loader = UnstructuredImageLoader(resolved_path)
            documents = loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Failed to load image: {str(e)}")

    def load_markdown(self, file_path: str):
        """加载并解析Markdown文件"""
        try:
            resolved_path = self._resolve_path(file_path)
            loader = UnstructuredMarkdownLoader(resolved_path)
            documents = loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Failed to load Markdown: {str(e)}")

    def load_text(self, file_path: str):
        """加载并解析文本文件"""
        try:
            resolved_path = self._resolve_path(file_path)
            # 先尝试utf-8，失败则回退到gbk
            try:
                loader = TextLoader(resolved_path, encoding='utf-8')
                documents = loader.load()
            except UnicodeDecodeError:
                loader = TextLoader(resolved_path, encoding='gbk')
                documents = loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Failed to load text: {str(e)}")

    def preprocess(self, documents):
        """对文档进行预处理，包括文本清理"""
        try:
            # 合并所有文档内容
            text = "\n".join([doc.page_content for doc in documents])
            
            # 清理文本
            text = text.replace("\n\n", "\n").strip()
            
            return text
        except Exception as e:
            raise Exception(f"Failed to preprocess documents: {str(e)}")

    def process(self, document_path: str):
        """统一处理文档的接口，根据文档路径自动判断类型并解析"""
        try:
            if document_path.endswith(".pdf"):
                documents = self.load_pdf(document_path)
            elif document_path.startswith("http"):
                documents = self.load_webpage(document_path)
            elif any(document_path.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                documents = self.load_image(document_path)
            elif document_path.endswith(".md"):
                documents = self.load_markdown(document_path)
            elif document_path.endswith(".txt"):
                documents = self.load_text(document_path)
            else:
                raise ValueError(f"Unsupported document type: {document_path}")
            
            text = self.preprocess(documents)
            return text
        except Exception as e:
            raise Exception(f"Failed to process document: {str(e)}")
