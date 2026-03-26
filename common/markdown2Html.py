import os
from common.Config import config

try:
    from markdown import markdown
except ModuleNotFoundError as e:
    os.system("pip3 install markdown")
    os.system("pip3 install python-markdown-math")
    os.system("pip3 install markdown_checklist")
    from markdown import markdown

# pip3 install xx -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
# 如果不行换个源

# HTML模板
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, minimal-ui">
    <title>{title}</title>
    <link rel="stylesheet" href="https://files.cnblogs.com/files/bpf-1024/markdown.css">
    <link rel="stylesheet" href="https://files.cnblogs.com/files/bpf-1024/tasklist.css">
    <link rel="stylesheet" href="https://files.cnblogs.com/files/bpf-1024/codehighlight.css">
    <link rel="stylesheet" href="https://files.cnblogs.com/files/bpf-1024/directory.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css" crossorigin="anonymous">
    <script src="https://files.cnblogs.com/files/bpf-1024/directory.js"></script>
    <script src="https://unpkg.com/mermaid@8.7.0/dist/mermaid.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex/dist/contrib/mathtex-script-type.min.js" defer></script>
</head>
<body>
    <article class="markdown-body" id="markdown-body">
        {content}
    </article>
</body>
</html>'''

# Markdown扩展配置
MARKDOWN_EXTENSIONS = [
    'toc',  # 目录，[toc]
    'extra',  # 缩写词、属性列表、释义列表、围栏式代码块、脚注、在HTML的Markdown、表格
    'mdx_math',
    'markdown_checklist.extension',  # checklist，- [ ]和- [x]
    'pymdownx.magiclink',  # 自动转超链接
    'pymdownx.caret',  # 上标下标
    'pymdownx.superfences',  # 多种块功能允许嵌套
    'pymdownx.betterem',  # 改善强调的处理
    'pymdownx.mark',  # 亮色突出文本
    'pymdownx.highlight',  # 高亮显示代码
    'pymdownx.tasklist',  # 任务列表
    'pymdownx.tilde',  # 删除线
]

EXTENSION_CONFIGS = {
    'mdx_math': {'enable_dollar_delimiter': True},
    'pymdownx.superfences': {
        "custom_fences": [{'name': 'mermaid', 'class': 'mermaid'}]
    },
    'pymdownx.highlight': {
        'linenums': True,
        'linenums_style': 'pymdownx-inline'
    },
    'pymdownx.tasklist': {'clickable_checkbox': True},
}


class MarkdownToHtml:
    """Markdown转HTML工具类"""

    def __init__(self, md_filename: str, encoding: str = 'utf-8'):
        self.md_filename = md_filename
        self.encoding = encoding

    def _read_md(self) -> str:
        """读取Markdown文件"""
        with open(self.md_filename, "r", encoding=self.encoding) as f:
            return f.read()

    def _get_title(self) -> str:
        """从文件名获取标题"""
        return os.path.splitext(os.path.basename(self.md_filename))[0]

    def _convert(self, md_text: str) -> str:
        """转换Markdown为HTML"""
        html_content = markdown(
            md_text,
            output_format='html',
            extensions=MARKDOWN_EXTENSIONS,
            extension_configs=EXTENSION_CONFIGS
        )
        return HTML_TEMPLATE.format(title=self._get_title(), content=html_content)

    def _write_html(self, html_path: str, html_text: str) -> None:
        """写入HTML文件"""
        with open(html_path, 'w', encoding=self.encoding) as f:
            f.write(html_text)

    def convert(self, html_path: str) -> bool:
        """
        转换Markdown文件为HTML

        Args:
            html_path: 输出HTML文件路径

        Returns:
            bool: 转换是否成功
        """
        try:
            md_text = self._read_md()
            html_text = self._convert(md_text)
            self._write_html(html_path, html_text)
            return True
        except Exception as e:
            print(f"<Error> {e}")
            return False


if __name__ == '__main__':
    path = os.path.join(config.BASE_PATH, 'markdown2Html')
    md_file = os.path.join(path, "result.md")
    html_file = os.path.join(path, "result.html")

    if MarkdownToHtml(md_file).convert(html_file):
        print('done')
