# Pandoc MCP Server

基于 Model Context Protocol (MCP) 的 Pandoc 文档转换服务，针对中文/CJK 排版优化。

## ✨ 特性

- 支持多种文档格式互转（Markdown、PDF、HTML、DOCX 等）
- 自动从文件扩展名推断格式
- **针对中文、日文、韩文文档的排版优化**
- 中西文混排智能换行
- 安全参数验证，防止代码注入
- 自动检测和配置 CJK 字体
- 零配置生成精美排版的 PDF

## 📦 安装

### 快速开始（使用 uvx，推荐）

```bash
# 无需安装！直接使用 uvx 运行
uvx pandoc-mcp-server
```

### 从 PyPI 安装

```bash
pip install pandoc-mcp-server
```

### 从源码安装

```bash
git clone https://github.com/yourusername/pandoc-mcp-server
cd pandoc-mcp-server
pip install -e .
```

## 🎯 系统要求

### 必需

- **Python 3.10+**
- **Pandoc** - 必须安装在系统中
  - Windows: `winget install pandoc`
  - macOS: `brew install pandoc`
  - Linux: `sudo apt install pandoc`

### 可选（PDF 支持）

- **TeX Live**（推荐）- 生成精美排版的 PDF
  - Windows: https://tug.org/texlive/windows.html
  - macOS: `brew install --cask mactex`
  - Linux: `sudo apt install texlive-full`

## ⚙️ 配置

### 在 Claude Desktop 中使用（stdio 模式）

编辑 Claude Desktop 配置文件：

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

**方式一：使用 uvx（最简单，推荐）**

```json
{
  "mcpServers": {
    "pandoc": {
      "command": "uvx",
      "args": ["pandoc-mcp-server"]
    }
  }
}
```

**方式二：使用本地安装**

```json
{
  "mcpServers": {
    "pandoc": {
      "command": "python",
      "args": ["-m", "pandoc_mcp_server.server"]
    }
  }
}
```

**方式三：使用 uv 运行本地源码（开发用）**

```json
{
  "mcpServers": {
    "pandoc": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/pandoc-mcp-server",
        "run",
        "pandoc-mcp"
      ]
    }
  }
}
```

## 🚀 使用方法

### MCP 工具

#### `convert`

将文档从一种格式转换为另一种格式。

**参数：**
- `input_file`（必需）：输入文件的完整路径
- `output_file`（必需）：输出文件的完整路径
- `from_format`（可选）：源格式（省略时自动推断）
- `to_format`（可选）：目标格式（省略时自动推断）
- `extra_args`（可选）：额外的 Pandoc 参数
- `overwrite`（可选）：是否允许覆盖已存在的文件（默认：false）
- `create_dirs`（可选）：是否创建不存在的父目录（默认：false）

**示例：**

```python
# Markdown 转 PDF（自动 CJK 优化）
convert(
    input_file="document.md",
    output_file="output.pdf"
)

# HTML 转 DOCX，带自定义选项
convert(
    input_file="page.html",
    output_file="document.docx",
    extra_args=["--toc", "--number-sections"],
    overwrite=true
)
```

#### `capabilities`

获取 Pandoc 安装信息和支持的格式。

## 🎨 CJK 排版特性

服务会自动为中文、日文、韩文文档优化 PDF 输出：

### 自动优化

- ✅ **通用 CJK 换行** - 支持中文、日文、韩文
- ✅ **混合语言支持** - 正确处理 CJK-西文混排
- ✅ **字体自动检测** - 微软雅黑（Windows）、苹方（macOS）、思源黑体（Linux）
- ✅ **优化间距** - 1.8 倍行距，1.5em 段落间距
- ✅ **无文字溢出** - 智能换行防止文字被截断
- ✅ **专业排版** - 基于 LaTeX 渲染

### 自定义 PDF 样式

通过 `extra_args` 覆盖默认设置：

```python
convert(
    input_file="doc.md",
    output_file="output.pdf",
    extra_args=[
        "--variable=mainfont:SimSun",          # 使用特定字体
        "--variable=fontsize:14pt",            # 更大字号
        "--variable=linestretch:2.0",          # 更大行距
        "--variable=geometry:margin=3cm",      # 更宽页边距
        "--toc",                               # 添加目录
        "--number-sections"                    # 章节编号
    ]
)
```

## 🔧 命令行使用

安装后也可以从命令行使用：

```bash
# 启动 MCP 服务器（stdio 模式）
pandoc-mcp
```

## 🐛 故障排除

### "Pandoc not found"
使用系统包管理器安装 Pandoc（参见系统要求部分）。

### "PDF engine not found"
安装 TeX Live 或其他 LaTeX 发行版以支持 PDF。

### "中文显示为方框"
服务会自动检测字体。如果仍有问题，手动指定：
```python
extra_args=["--variable=mainfont:SimSun"]
```

### "PDF 中文字溢出"
这应该已被 CJK 排版引擎自动修复。如果仍有问题，尝试重启 MCP 服务器。

## 📚 支持的格式

**输入格式：**
- Markdown (md, markdown)
- HTML (html, htm)
- LaTeX (tex, latex)
- reStructuredText (rst)
- 纯文本 (txt)
- DOCX, ODT
- EPUB
- Jupyter Notebook (ipynb)

**输出格式：**
- PDF（精美的 CJK 排版）
- Markdown, HTML, LaTeX
- DOCX, ODT, RTF
- EPUB, EPUB3
- 纯文本
- 更多格式...

## 🤝 贡献

欢迎贡献代码！请随时提交 Pull Request。

## 📄 许可证

MIT License - 详见 LICENSE 文件。

## 🙏 致谢

- 基于 [Pandoc](https://pandoc.org/) - 通用文档转换器
- 使用 [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- 灵感来自 [mcp-pandoc](https://github.com/vivekVells/mcp-pandoc)

## 🔗 链接

- [GitHub 仓库](https://github.com/yourusername/pandoc-mcp-server)
- [PyPI 包](https://pypi.org/project/pandoc-mcp-server/)
- [问题跟踪](https://github.com/yourusername/pandoc-mcp-server/issues)
- [MCP 文档](https://modelcontextprotocol.io/)
- [Pandoc 文档](https://pandoc.org/MANUAL.html)

