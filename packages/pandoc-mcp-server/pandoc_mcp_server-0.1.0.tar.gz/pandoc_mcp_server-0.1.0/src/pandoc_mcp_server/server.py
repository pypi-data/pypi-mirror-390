"""
Pandoc MCP Server - Professional Document Conversion Service

A robust Model Context Protocol (MCP) server implementation that provides
document format conversion capabilities using Pandoc with safety and reliability.

Features:
- Multi-format document conversion
- Automatic CJK typography optimization
- Safe argument validation
- Universal language support (Chinese, Japanese, Korean, Western)

Design Philosophy: Simple, Safe, Explicit
"""

import asyncio
import logging
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Final, Optional, Tuple, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import pypandoc


# Constants

# Safe extra arguments whitelist (prevents code execution via filters)
SAFE_EXTRA_ARGS: Final[set[str]] = {
    '--toc', '--table-of-contents',
    '--standalone', '-s',
    '--self-contained',
    '--toc-depth',
    '--number-sections',
    '--section-divs',
    '--citeproc',
    '--bibliography',
    '--csl',
    '--resource-path',
    '--css',
    '--template',
    '--metadata',
    '--variable',
    '--variable=linestretch',
    '--variable=geometry',
    '--variable=indent',
    '--variable=mainfont',
    '--variable=CJKmainfont',
    '--variable=fontsize',
    '--variable=documentclass',
    '--variable=columns',
    '--variable=parskip',
    '--variable=block-headings',
    '--include-in-header',
    '--wrap',
    '--columns',
    '--tab-stop',
    '--eol',
    '--preserve-tabs',
    '--shift-heading-level-by',
    '--reference-doc',
    '--pdf-engine',
    '--pdf-engine-opt',
}

# Format normalization mapping
FORMAT_ALIASES: Final[dict[str, str]] = {
    'md': 'markdown',
    'mkd': 'markdown',
    'markdown': 'markdown',
    'htm': 'html',
    'html': 'html',
    'tex': 'latex',
    'latex': 'latex',
    'rst': 'rst',
    'rest': 'rst',
    'txt': 'plain',
    'text': 'plain',
    'plain': 'plain',
    'docx': 'docx',
    'odt': 'odt',
    'pdf': 'pdf',
    'epub': 'epub',
    'ipynb': 'ipynb',
}

# PDF engines in preference order
PDF_ENGINES: Final[List[str]] = ['xelatex', 'lualatex', 'pdflatex', 'wkhtmltopdf']

# LaTeX typography template for CJK documents
LATEX_CJK_HEADER: Final[str] = r"""
% Universal Typography Optimization for All Languages
\usepackage{setspace}
\setstretch{1.8}

% Load xeCJK for automatic CJK handling
\usepackage{xeCJK}

% Universal line breaking - works for Chinese, Japanese, Korean, and mixed text
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip = 0pt plus 1pt

% Allow line breaks for all CJK scripts
\xeCJKsetup{
  CJKspace = true,
  CheckSingle = true,
  AllowBreakBetweenPuncts = false
}

% Ensure Western text respects word boundaries
\sloppy

% Paragraph spacing (override defaults)
\setlength{\parskip}{1.5em}
\setlength{\parindent}{0pt}

% Better spacing around paragraphs
\raggedbottom

% Improve punctuation spacing
\renewcommand{\baselinestretch}{1.8}
"""


# Logging Configuration


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# MCP Server Instance


app = Server("pandoc-mcp")



# Format Handling Functions


def normalize_format(format_str: str) -> str:
    """
    Normalize format string to Pandoc standard name.

    Args:
        format_str: Format string (e.g., 'md', 'html', 'tex')

    Returns:
        Normalized format name

    Examples:
        >>> normalize_format('md')
        'markdown'
        >>> normalize_format('HTML')
        'html'
    """
    format_lower = format_str.lower().strip()
    return FORMAT_ALIASES.get(format_lower, format_lower)


def infer_format_from_path(file_path: str) -> str:
    """
    Infer format from file extension.

    Args:
        file_path: Path to file

    Returns:
        Inferred format name

    Raises:
        ValueError: If extension is missing or unrecognized

    Examples:
        >>> infer_format_from_path('document.md')
        'markdown'
        >>> infer_format_from_path('output.pdf')
        'pdf'
    """
    ext = Path(file_path).suffix.lower()
    if not ext:
        raise ValueError(
            f"Cannot infer format: file has no extension: {file_path}"
        )

    ext_without_dot = ext[1:]
    if ext_without_dot not in FORMAT_ALIASES:
        supported = ', '.join(sorted(set(FORMAT_ALIASES.keys())))
        raise ValueError(
            f"Unrecognized file extension: {ext}\n"
            f"Supported extensions: {supported}"
        )

    return FORMAT_ALIASES[ext_without_dot]



# Argument Validation


def validate_extra_args(extra_args: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate extra_args against whitelist to prevent code injection.

    Args:
        extra_args: List of Pandoc arguments

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_extra_args(['--toc', '--standalone'])
        (True, None)
        >>> validate_extra_args(['--lua-filter=evil.lua'])
        (False, "Unsafe argument not allowed: --lua-filter")
    """
    if not extra_args:
        return True, None

    for arg in extra_args:
        # Extract argument name (without value)
        arg_name = arg.split('=')[0] if '=' in arg else arg

        if arg_name not in SAFE_EXTRA_ARGS:
            allowed = ', '.join(sorted(SAFE_EXTRA_ARGS))
            return False, (
                f"Unsafe argument not allowed: {arg_name}\n"
                f"Allowed arguments: {allowed}"
            )

    return True, None


def has_variable(var_name: str, extra_args: List[str]) -> bool:
    """
    Check if user has specified a Pandoc variable.

    Args:
        var_name: Variable name to check
        extra_args: List of extra arguments

    Returns:
        True if variable is present, False otherwise

    Examples:
        >>> has_variable('fontsize', ['--variable=fontsize:12pt'])
        True
        >>> has_variable('margin', ['--variable=fontsize:12pt'])
        False
    """
    return any(
        f'--variable={var_name}' in arg or f'--variable={var_name}:' in arg
        for arg in extra_args
    )



# PDF Engine Detection


def check_pdf_engine() -> Optional[str]:
    """
    Check if PDF engine is available on system.

    Returns:
        Name of first available PDF engine, or None if not found

    Note:
        Checks engines in preference order: xelatex, lualatex, pdflatex, wkhtmltopdf
    """
    for engine in PDF_ENGINES:
        if shutil.which(engine):
            return engine
    return None


def select_pdf_engine(extra_args: List[str]) -> None:
    """
    Auto-select optimal PDF engine if not specified by user.

    Args:
        extra_args: List of extra arguments (modified in-place)

    Side Effects:
        Appends --pdf-engine argument to extra_args if not present
    """
    has_explicit_engine = any(
        arg.startswith('--pdf-engine') for arg in extra_args
    )

    if has_explicit_engine:
        logger.info("Using user-specified PDF engine")
        return

    # Prefer xelatex for Unicode/CJK support
    if shutil.which('xelatex'):
        extra_args.append('--pdf-engine=xelatex')
        logger.info("Auto-selected PDF engine: xelatex (best for Unicode/CJK)")
    elif shutil.which('lualatex'):
        extra_args.append('--pdf-engine=lualatex')
        logger.info("Auto-selected PDF engine: lualatex (Unicode support)")
    else:
        engine = check_pdf_engine()
        logger.info(f"Using default PDF engine: {engine}")



# CJK Font Detection


def get_default_cjk_font() -> Optional[str]:
    """
    Detect and return a suitable CJK (Chinese/Japanese/Korean) font.

    Returns:
        Font name if found, None otherwise

    Note:
        Returns platform-specific defaults:
        - Windows: Microsoft YaHei
        - macOS: PingFang SC
        - Linux: Noto Sans CJK SC
    """
    system = platform.system()

    font_map = {
        'Windows': 'Microsoft YaHei',
        'Darwin': 'PingFang SC',  # macOS
        'Linux': 'Noto Sans CJK SC',
    }

    font = font_map.get(system, 'Noto Sans CJK SC')
    logger.info(f"Using default {system} CJK font: {font}")
    return font


def configure_cjk_font(extra_args: List[str]) -> None:
    """
    Auto-configure CJK font if not specified by user.

    Args:
        extra_args: List of extra arguments (modified in-place)

    Side Effects:
        Appends --variable=mainfont argument if not present
    """
    has_explicit_font = any(
        'mainfont' in arg.lower() or 'cjkmainfont' in arg.lower()
        for arg in extra_args
    )

    if has_explicit_font:
        return

    cjk_font = get_default_cjk_font()
    if cjk_font:
        extra_args.append(f'--variable=mainfont:{cjk_font}')
        logger.info(f"Auto-configured CJK font: {cjk_font}")
    else:
        logger.warning(
            "No CJK font detected. "
            "Chinese/Japanese/Korean text may not display correctly."
        )



# CJK Typography


def apply_cjk_typography(extra_args: List[str]) -> Optional[str]:
    """
    Apply CJK typography optimizations via LaTeX header injection.

    Args:
        extra_args: List of extra arguments (modified in-place)

    Returns:
        Path to temporary LaTeX header file, or None if creation failed

    Side Effects:
        - Creates temporary .tex file with LaTeX commands
        - Appends --include-in-header argument to extra_args
    """
    try:
        temp_fd, temp_file = tempfile.mkstemp(suffix='.tex', text=True)
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            f.write(LATEX_CJK_HEADER)

        extra_args.append(f'--include-in-header={temp_file}')
        logger.info("Applied CJK typography optimization")
        return temp_file

    except Exception as e:
        logger.warning(f"Failed to create LaTeX header: {e}")
        return None



# PDF Configuration

def configure_pdf_output(extra_args: List[str], to_format: str) -> Optional[str]:
    """
    Configure optimal PDF output settings including engine, fonts, and typography.

    Args:
        extra_args: List of extra arguments (modified in-place)
        to_format: Target format

    Returns:
        Path to temporary header file if created, None otherwise

    Raises:
        ValueError: If PDF engine is not available

    Side Effects:
        Modifies extra_args to include PDF-specific options
    """
    if to_format != 'pdf':
        return None

    # Verify PDF engine availability
    if not check_pdf_engine():
        raise ValueError(
            "PDF conversion requires a LaTeX engine or wkhtmltopdf.\n"
            "Please install one of: TeX Live, MiKTeX, or wkhtmltopdf"
        )

    # Configure engine, font, and typography
    select_pdf_engine(extra_args)
    configure_cjk_font(extra_args)
    temp_header = apply_cjk_typography(extra_args)

    return temp_header



# File Operations


def ensure_output_directory(output_file: str, create_dirs: bool) -> None:
    """
    Ensure output directory exists.

    Args:
        output_file: Path to output file
        create_dirs: Whether to create directories

    Raises:
        ValueError: If directory doesn't exist and create_dirs is False
    """
    output_dir = os.path.dirname(output_file)
    if not output_dir:
        return

    if os.path.exists(output_dir):
        return

    if create_dirs:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created directory: {output_dir}")
    else:
        raise ValueError(
            f"Output directory does not exist: {output_dir}\n"
            f"Set create_dirs=true to auto-create"
        )


def validate_file_overwrite(output_file: str, overwrite: bool) -> None:
    """
    Validate that output file can be written.

    Args:
        output_file: Path to output file
        overwrite: Whether to allow overwriting

    Raises:
        ValueError: If file exists and overwrite is False
    """
    if os.path.exists(output_file) and not overwrite:
        raise ValueError(
            f"Output file already exists: {output_file}\n"
            f"Set overwrite=true to allow overwriting"
        )



# Pandoc Capabilities


def get_pandoc_capabilities() -> dict[str, any]:
    """
    Get Pandoc capabilities by querying the system.

    Returns:
        Dictionary containing version, formats, and engines

    Note:
        Runs pandoc commands to query available features
    """
    try:
        version = pypandoc.get_pandoc_version()

        # Get input formats
        result_input = subprocess.run(
            ['pandoc', '--list-input-formats'],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        readers = (
            result_input.stdout.strip().split('\n')
            if result_input.returncode == 0
            else []
        )

        # Get output formats
        result_output = subprocess.run(
            ['pandoc', '--list-output-formats'],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        writers = (
            result_output.stdout.strip().split('\n')
            if result_output.returncode == 0
            else []
        )

        # Check available PDF engines
        pdf_engines = [engine for engine in PDF_ENGINES if shutil.which(engine)]

        return {
            'pandoc_version': version,
            'readers': readers,
            'writers': writers,
            'pdf_engines_available': pdf_engines,
        }

    except Exception as e:
        logger.error(f"Failed to get capabilities: {e}")
        return {
            'pandoc_version': 'unknown',
            'readers': [],
            'writers': [],
            'pdf_engines_available': [],
            'error': str(e)
        }



# MCP Tool Definitions


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all tools provided by this server.

    Returns:
        List of available MCP tools
    """
    return [
        Tool(
            name="convert",
            description=(
                "Convert document from one format to another using Pandoc. "
                "Automatically optimizes typography for CJK languages. "
                "Supports format auto-detection from file extensions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Complete path to input file (with extension)"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Complete path to output file (with extension)"
                    },
                    "from_format": {
                        "type": "string",
                        "description": "Source format (optional, will infer from input_file extension if not provided)"
                    },
                    "to_format": {
                        "type": "string",
                        "description": "Target format (optional, will infer from output_file extension if not provided)"
                    },
                    "extra_args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional Pandoc arguments (e.g., ['--toc', '--standalone'])"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Allow overwriting existing output file (default: false)",
                        "default": False
                    },
                    "create_dirs": {
                        "type": "boolean",
                        "description": "Create parent directories if they don't exist (default: false)",
                        "default": False
                    }
                },
                "required": ["input_file", "output_file"]
            }
        ),
        Tool(
            name="capabilities",
            description=(
                "Get information about Pandoc installation and supported formats. "
                "Returns version, available readers/writers, and PDF engine status."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Execute tool based on name and arguments.

    Args:
        name: The name of the tool to call
        arguments: Dictionary of tool arguments

    Returns:
        List of text content containing results or error messages
    """
    try:
        if name == "convert":
            return await handle_convert(arguments)
        elif name == "capabilities":
            return await handle_capabilities(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

    except Exception as e:
        logger.error(f"Tool '{name}' failed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]



# Tool Handlers


async def handle_convert(args: dict) -> list[TextContent]:
    """
    Handle document conversion request.

    Args:
        args: Tool arguments containing input/output files and options

    Returns:
        List of TextContent with result message

    Raises:
        ValueError: If validation fails or conversion errors occur
    """
    # Extract arguments
    input_file = args.get("input_file")
    output_file = args.get("output_file")
    from_format = args.get("from_format")
    to_format = args.get("to_format")
    extra_args = args.get("extra_args", [])
    overwrite = args.get("overwrite", False)
    create_dirs = args.get("create_dirs", False)

    temp_header_file: Optional[str] = None

    try:
        # Validate input
        if not os.path.exists(input_file):
            raise ValueError(f"Input file not found: {input_file}")

        # Infer formats
        from_format = (
            normalize_format(from_format)
            if from_format
            else infer_format_from_path(input_file)
        )
        to_format = (
            normalize_format(to_format)
            if to_format
            else infer_format_from_path(output_file)
        )

        # Validate arguments
        is_valid, error_msg = validate_extra_args(extra_args)
        if not is_valid:
            raise ValueError(error_msg)

        # Configure PDF if needed
        temp_header_file = configure_pdf_output(extra_args, to_format)

        # Validate output
        validate_file_overwrite(output_file, overwrite)
        ensure_output_directory(output_file, create_dirs)

        # Add resource path for relative references
        input_dir = os.path.dirname(os.path.abspath(input_file))
        final_extra_args = extra_args + [f'--resource-path={input_dir}']

        # Execute conversion
        logger.info(
            f"Converting {input_file} ({from_format}) -> "
            f"{output_file} ({to_format})"
        )

        pypandoc.convert_file(
            input_file,
            to_format,
            format=from_format,
            outputfile=output_file,
            extra_args=final_extra_args
        )

        logger.info(f"Conversion completed: {output_file}")

        # Build success message
        result_msg = (
            f"✓ Conversion successful\n\n"
            f"Input:  {input_file} ({from_format})\n"
            f"Output: {output_file} ({to_format})\n"
        )

        if extra_args:
            result_msg += f"Extra args: {' '.join(extra_args)}\n"

        return [TextContent(type="text", text=result_msg)]

    except Exception as e:
        logger.error(f"Conversion failed: {e}", exc_info=True)
        raise ValueError(f"Pandoc conversion failed: {str(e)}")

    finally:
        # Clean up temporary files
        if temp_header_file and os.path.exists(temp_header_file):
            try:
                os.unlink(temp_header_file)
                logger.debug("Cleaned up temporary header file")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")


async def handle_capabilities(args: dict) -> list[TextContent]:
    """
    Handle capabilities query request.

    Args:
        args: Tool arguments (ignored)

    Returns:
        List of TextContent with capability information
    """
    logger.info("Querying Pandoc capabilities...")

    caps = get_pandoc_capabilities()

    # Format output
    lines = [
        "Pandoc MCP Server Capabilities",
        "=" * 50,
        "",
        f"Pandoc Version: {caps['pandoc_version']}",
        "",
        "PDF Engines Available: ",
    ]

    if caps['pdf_engines_available']:
        lines.append(", ".join(caps['pdf_engines_available']))
    else:
        lines.append("None (install TeX Live or wkhtmltopdf for PDF support)")

    lines.extend([
        "",
        f"Supported Input Formats ({len(caps['readers'])}):",
        ", ".join(caps['readers']),
        "",
        f"Supported Output Formats ({len(caps['writers'])}):",
        ", ".join(caps['writers']),
    ])

    if 'error' in caps:
        lines.extend(["", f"Warning: {caps['error']}"])

    output = "\n".join(lines)
    return [TextContent(type="text", text=output)]



# Server Runtime


async def run_server() -> None:
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main() -> None:
    """
    Start the Pandoc MCP server.

    This is the application entry point. The server communicates
    with clients via standard input/output (stdio).
    """
    logger.info("Starting Pandoc MCP Server v0.2.0")
    logger.info("Ready to accept document conversion requests")

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
