"""
Word文档内容添加MCP服务主程序

提供Word文档内容添加功能的MCP服务器
"""

import os
import sys
# 设置FastMCP所需的环境变量
os.environ.setdefault('FASTMCP_LOG_LEVEL', 'INFO')

# 设置控制台编码为UTF-8，避免Unicode错误
if sys.platform == "win32":
    try:
        # 尝试设置控制台编码为UTF-8
        os.system("chcp 65001 >nul 2>&1")
    except:
        pass

from fastmcp import FastMCP
from .tools import (
    create_document,
    add_heading,
    add_paragraph,
    add_table,
    add_picture,
    add_page_break
)

# 初始化FastMCP服务器
mcp = FastMCP("Word文档内容添加")


def register_tools():
    """使用FastMCP装饰器注册所有工具"""

    @mcp.tool()
    async def create_document_tool(output_filename: str, template: str = "", overwrite: bool = False, output_dir: str = ""):
        """【仅用于创建全新文档】创建一个新的Word文档（可选基于模板）
        
        【重要使用场景】
        - 当用户要求创建一个全新的文档时使用
        - 当指定的文档路径不存在时使用
        - 不要用于向已存在的文档添加内容！
        - 若目标文件已存在且未设置覆盖，将不报错并返回“复用现有文档”的提示，便于继续添加内容。
        
        【正确使用】
        - "创建一个新的报告文档"
        - "基于模板创建新文档"
        - "在桌面创建新的Word文档"
        
        【错误使用】
        - "向现有文档添加标题" → 应使用 add_heading_tool
        - "在已有文档中插入表格" → 应使用 add_table_tool
        - "给现有文档添加内容" → 应使用相应的 add_* 工具
        
        参数：
        - output_filename: 文件名（仅文件名，自动补全 .docx 扩展名）
        - template: 模板 .docx 路径（可选，传空字符串则不使用）
        - overwrite: 是否允许覆盖已存在文件（默认False）
        - output_dir: 输出路径（仅目录路径，默认桌面；自动识别OneDrive或本地桌面）
        """
        template_param = template if template and template.strip() else None
        output_dir_param = output_dir if output_dir and output_dir.strip() else None
        return await create_document(output_filename, template_param, overwrite, output_dir_param)

    @mcp.tool()
    async def add_heading_tool(filename: str, text: str, level: int = 1):
        """【向已存在文档添加标题】向现有Word文档添加标题
        
        【重要】此工具用于向已存在的文档添加内容，文档必须已经存在！
        如需创建新文档，请先使用 create_document_tool。
        
        参数：
        - filename: 已存在的Word文档路径
        - text: 标题文本
        - level: 标题级别（1-9，1为最高级别）
        """
        return await add_heading(filename, text, level)

    @mcp.tool()
    async def add_paragraph_tool(filename: str, text: str, style: str = ""):
        """【向已存在文档添加段落】向现有Word文档添加段落
        
        【重要】此工具用于向已存在的文档添加内容，文档必须已经存在！
        如需创建新文档，请先使用 create_document_tool。
        
        参数：
        - filename: 已存在的Word文档路径
        - text: 段落文本
        - style: 可选的段落样式名称
        """
        # Convert empty string to None for the actual function
        style_param = style if style and style.strip() else None
        return await add_paragraph(filename, text, style_param)

    @mcp.tool()
    async def add_table_tool(filename: str, rows: int, cols: int, data: list = []):
        """【向已存在文档添加表格】向现有Word文档添加表格
        
        【重要】此工具用于向已存在的文档添加内容，文档必须已经存在！
        如需创建新文档，请先使用 create_document_tool。
        
        参数：
        - filename: 已存在的Word文档路径
        - rows: 表格行数
        - cols: 表格列数
        - data: 可选的二维数组数据填充表格
        """
        # Convert empty list to None for the actual function
        data_param = data if data else None
        return await add_table(filename, rows, cols, data_param)

    @mcp.tool()
    async def add_picture_tool(filename: str, image_path: str, width: float = 0.0):
        """【向已存在文档添加图片】向现有Word文档添加图片
        
        【重要】此工具用于向已存在的文档添加内容，文档必须已经存在！
        如需创建新文档，请先使用 create_document_tool。
        
        参数：
        - filename: 已存在的Word文档路径
        - image_path: 图片文件路径
        - width: 可选的图片宽度（英寸，按比例缩放；未提供或为 0 时，若图片原始宽度超过文档内容区域宽度，将自动按内容宽度 100% 缩放）
        """
        # Convert 0.0 to None for the actual function
        width_param = width if width > 0 else None
        return await add_picture(filename, image_path, width_param)

    @mcp.tool()
    async def add_page_break_tool(filename: str):
        """【向已存在文档添加分页符】向现有Word文档添加分页符
        
        【重要】此工具用于向已存在的文档添加内容，文档必须已经存在！
        如需创建新文档，请先使用 create_document_tool。
        
        参数：
        - filename: 已存在的Word文档路径
        """
        return await add_page_break(filename)


def main():
    """服务器的主入口点 - 只支持stdio传输"""
    # 注册所有工具
    register_tools()

    print("启动Word文档内容添加MCP服务器...")
    print("提供以下功能:")
    print("- create_document_tool: 【仅用于创建新文档】创建全新的Word文档")
    print("- add_heading_tool: 【向已存在文档添加内容】添加标题")
    print("- add_paragraph_tool: 【向已存在文档添加内容】添加段落")
    print("- add_table_tool: 【向已存在文档添加内容】添加表格")
    print("- add_picture_tool: 【向已存在文档添加内容】添加图片")
    print("- add_page_break_tool: 【向已存在文档添加内容】添加分页符")
    print("")
    print("【重要提示】")
    print("  - 如果文档不存在，请使用 create_document_tool 创建")
    print("  - 如果文档已存在，请使用 add_* 工具添加内容")
    print("  - 不要用 create_document_tool 向已存在的文档添加内容！")

    try:
        # 只使用stdio传输运行
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("\n正在关闭Word文档内容添加服务器...")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
