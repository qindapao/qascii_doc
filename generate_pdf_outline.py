#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Outline Generator

This script extracts a table of contents from specified pages in a PDF
document, searches for matching titles in the body, and generates a structured
outline (bookmarks) for navigation.

Usage:
    python generate_pdf_outline.py input=your.pdf toc_pages=1-2 \
            output=with_outline.pdf offset=0

Dependencies:
    - PyMuPDF (install via `pip install pymupdf`)

Author: xxxxx
Date: 2025-09-02
:TODO:  1. 文档的尾部以及正经出版物还需要的东西的配置方法。
"""

import os
import re
import sys
import shlex
import json
from typing import List, Tuple
import fitz  # PyMuPDF

MANUAL_JSON = "outline_errors.json"
CONFIG_JSON = "generate_pdf_outline.json"

PAGE_SIZES = {
    "A4": (595, 842),   # portrait
    "A3": (842, 1191),
    "A5": (420, 595),
}

FONTNAME = "CustomChineseFont"


def insert_preface_pages(
        pdf_doc: fitz.Document, preface_content_info, opts: dict):
    """
    Insert one or more preface pages immediately after the cover page.
    """
    if isinstance(preface_content_info, str):
        preface_pages = [preface_content_info]
    else:
        preface_pages = preface_content_info

    cover = opts.get("cover", "A4")
    font_path = opts.get("font_path", "./fonts/KaiGenGothicCN-Regular.ttf")
    width, height = PAGE_SIZES.get(cover.upper(), PAGE_SIZES["A4"])

    for i, page_text in enumerate(preface_pages):
        # pno=1 表示插在封面后面，+i 是为了多页递增
        page = pdf_doc.new_page(pno=1 + i, width=width, height=height)

        page.insert_font(fontname=FONTNAME, fontfile=font_path)

        # 序言标题
        page.insert_textbox(
            fitz.Rect(0, 80, width, 120),
            "序言",
            fontsize=24,
            fontname=FONTNAME,
            fill=(0, 0, 0),
            align=1
        )

        # 序言正文
        margin_x = 60
        margin_top = 140
        page.insert_textbox(
            fitz.Rect(margin_x, margin_top, width - margin_x, height - 80),
            page_text,
            fontsize=12,
            fontname=FONTNAME,
            fill=(0.1, 0.1, 0.1),
            align=0
        )

        print(f"\U0001f4dd 已插入序言第 {i+1} 页")

    print(f"✅ 共插入 {len(preface_pages)} 页序言（封面后）")


def _insert_logo(page, logo_path, width):
    logo_width = 80   # 你可以调整大小
    logo_height = 80
    logo_x = (width - logo_width) / 2
    logo_y = 100  # 距离页面顶部的距离
    page.insert_image(
        fitz.Rect(logo_x, logo_y, logo_x + logo_width,
                  logo_y + logo_height),
        filename=logo_path
    )
    print(f"\U0001f5bc️ 已插入 logo：{logo_path}")


def insert_cover_page(
    pdf_doc: fitz.Document,
    opts: dict
):
    """
    Insert a cover page at the beginning of a PDF document.

    This function creates a new page at the start of the given PDF document
    and populates it with a title, subtitle, author, date, and optionally a
    full-page background image. Page size, font, and text content can be
    customized via the `opts` dictionary.

    Args:
        pdf_doc (fitz.Document):
            The PDF document object (PyMuPDF Document) to modify.
        opts (dict):
            A dictionary of cover page options. Supported keys include:
                - cover (str): Page size identifier (e.g., "A4", "A3", "A5").
                  Defaults to "A4".
                - font_path (str): Path to the font file to use for text.
                  Defaults to "./fonts/KaiGenGothicCN-Regular.ttf".
                - image_path (str): Path to a background image file (optional).
                - title (str): Main title text. Defaults to
                  "\U0001f4d8 技术文档标题".
                - subtitle (str): Subtitle text. Defaults to
                  副标题：自动生成书签的 PDF 工具".
                - author (str): Author text. Defaults to "作者：xxxxx".
                - date (str): Date text. Defaults to "日期：2025-09-02".

    Notes:
        - If `image_path` is provided and the file exists, it will be inserted
          as a full-page background image.
        - The font file should support the characters you intend to display
          (e.g., Chinese characters) to avoid missing glyphs.
        - Page dimensions are retrieved from the `PAGE_SIZES` mapping; if the
          specified size is not found, A4 dimensions are used.

    Example:
        >>> import fitz
        >>> doc = fitz.open()
        >>> insert_cover_page(doc, {
        ...     "title": "My Technical Document",
        ...     "author": "John Doe",
        ...     "date": "2025-09-03"
        ... })
        >>> doc.save("output.pdf")
    """
    cover = opts.get("cover", "A4")
    font_path = opts.get("font_path", "./fonts/KaiGenGothicCN-Regular.ttf")
    image_path = opts.get("image_path")
    logo_path = opts.get("logo_path")
    title = opts.get("title", "\U0001f4d8 技术文档标题")
    subtitle = opts.get("subtitle", "副标题：自动生成书签的 PDF 工具")
    author = opts.get("author", "作者：xxxxx")
    date = opts.get("date", "日期：2025-09-02")

    width, height = PAGE_SIZES.get(cover.upper(), PAGE_SIZES["A4"])
    page = pdf_doc.new_page(pno=0, width=width, height=height)

    # 注册中文字体
    page.insert_font(fontname=FONTNAME, fontfile=font_path)

    # 插入整页背景图
    if image_path and os.path.exists(image_path):
        bg_rect = fitz.Rect(0, 0, width, height)
        page.insert_image(bg_rect, filename=image_path)
        print(f"\U0001f5bc️ 已插入整页背景图：{image_path}")

    # 插入 logo（居中放在标题上方）
    if logo_path and os.path.exists(logo_path):
        _insert_logo(page, logo_path, width)

    # 插入标题
    page.insert_textbox(
        fitz.Rect(0, 200, width, 250),
        title,
        fontsize=28,
        fontname=FONTNAME,
        fill=(0, 0, 0),
        align=1
    )

    # 插入副标题
    page.insert_textbox(
        fitz.Rect(0, 260, width, 310),
        subtitle,
        fontsize=18,
        fontname=FONTNAME,
        fill=(0.2, 0.2, 0.2),
        align=1
    )

    # 插入作者和日期
    page.insert_textbox(
        fitz.Rect(0, 320, width, 390),  # 高度至少 50pt,
        f"{author}\n\n{date}",
        fontsize=14,
        fontname=FONTNAME,
        fill=(0.4, 0.4, 0.4),
        align=1
    )

    print(f"✅ 已插入封面页（尺寸：{cover.upper()}，"
          f"字体：{os.path.basename(font_path)}）")


def clean_title(title: str) -> str:
    """
    Cleans up a title string by trimming whitespace and removing known trailing
    artifacts.

    Specifically removes a trailing '一' character, which may appear due to PDF
    encoding or formatting issues in extracted text.

    Args:
        title (str): The raw title string extracted from the PDF.

    Returns:
        str: The cleaned title string.
    """
    title = title.strip()
    if title.endswith("一"):
        title = title[:-1]
    return title


def check_toc_errors(toc_list: List[Tuple[int, str, int]]):
    """
    Checks the table of contents list for entries with unresolved page numbers
    (i.e., page == 0).

    If any errors are found:
        - Prints a formatted error list.
        - Dumps the full TOC list to a JSON file for manual correction.
        - Prints the current command-line invocation for easy rerun.
        - Exits the program to prevent further processing.

    Args:
        toc_list (List[Tuple[int, str, int]]): The list of TOC entries in the
        format [level, title, page_number].

    Returns:
        None. Exits the program if errors are detected.
    """
    err_list = [
        f"(error) [Level {level} → Title: {title} → Page {page_num}]"
        for level, title, page_num in toc_list if page_num == 0
    ]
    if err_list:
        print("\U0001f4d8 TOC check error happen:")
        print(*err_list, sep='\n')
        with open(MANUAL_JSON, 'w', encoding='utf-8') as cf:
            json.dump(toc_list, cf, ensure_ascii=False, indent=4)

        current_command = "python " + shlex.quote(sys.argv[0])
        for arg in sys.argv[1:]:
            current_command += " " + shlex.quote(arg)
        print(
            f"\n\U0001f4cb 手动更新 {MANUAL_JSON} 文件后，"
            "你可以使用以下命令重新运行程序："
        )
        print(current_command)
        sys.exit(1)


def get_toc(
        pdf_doc: fitz.Document,
        toc_start_page: int,
        toc_end_page: int) -> List[Tuple[int, str, int]]:
    """
    Extracts a list of outline entries from the specified table-of-contents
    pages in a PDF document.

    Bugs: 如果两个标题跨页，依然有文本错乱问题！

    Args:
        pdf_document (fitz.Document): The opened PDF document.
        start_page (int): The zero-based index of the first TOC page.
        end_page (int): The zero-based index of the last TOC page (inclusive).

    Returns:
        List[Tuple[int, str, int]]: A list of outline entries in the format
                                    [level, title, page_number].
    """
    if os.path.exists(MANUAL_JSON):
        with open(MANUAL_JSON, 'r', encoding='utf-8') as mf:
            pdf_toc_list = json.load(mf)
        return pdf_toc_list

    pdf_toc_dict = {}
    title_regex = r'^\s*(((\d+\.)+)\s*(.*))'
    index = 0
    for i in range(toc_start_page, toc_end_page + 1):
        for line in pdf_doc[i].get_text().splitlines():
            # 示例格式：1.2.3 标题名称 ...... 23
            match = re.match(title_regex, line)
            if match:
                level = len(match.group(2).split('.')) - 1
                title = clean_title(match.group(1).strip())
                pdf_toc_dict[title] = [index, level, 0]
                index += 1
    for page_num in range(toc_end_page+1, len(pdf_doc)):
        for line in pdf_doc[page_num].get_text().splitlines():
            # print(f"\U0001f4c4 Page {page_num + 1} Line: {repr(line)}")
            match = re.match(title_regex, line)
            if match:
                title = clean_title(match.group(1).strip())
                if title in pdf_toc_dict:
                    pdf_toc_dict[title][2] = page_num+1

    # dict to list
    # {'xx': [1, 3, 56], 'yy': [0, 1, 78]} to
    # [ [1, 'yy', 78], [3, 'xx', 56] ]

    # [
    #     (1, [3, 'xx', 56]),
    #     (0, [1, 'yy', 78])
    # ]
    transformed = [
            (v[0], [v[1], k, v[2]])
            for k, v in pdf_toc_dict.items()
            ]

    pdf_toc_list = [item for _, item in sorted(transformed)]

    check_toc_errors(pdf_toc_list)

    # 元组中只保留第2个元素
    return pdf_toc_list


if __name__ == "__main__":
    # 解析配置的JSON文件
    config_json = {}
    with open(CONFIG_JSON, 'r', encoding='utf-8') as f:
        config_json = json.load(f)

    input_path = config_json['input']
    output_path = config_json['output']
    toc_range = config_json['toc_pages'].split('-')
    offset = config_json['offset']
    cover_size = config_json.get('cover')

    # 打开 PDF
    doc = fitz.open(input_path)
    if cover_size:
        insert_cover_page(doc, config_json)
        offset += 1  # 所有书签页码偏移 +1

    preface_content = config_json.get("preface")
    if preface_content:
        insert_preface_pages(doc, preface_content, config_json)
        # 如果是列表，按页数增加 offset
        offset += len(preface_content) if isinstance(
                preface_content, list) else 1

    # PyMuPDF 页码从 0 开始
    start_page = int(toc_range[0]) - 1 + offset
    end_page = int(toc_range[-1]) - 1 + offset
    toc = get_toc(doc, start_page, end_page)

    # 插入书签并保存
    doc.set_toc(toc)
    print(f"begin to save file: {output_path}")
    # 只嵌入实际使用到的字形
    doc.subset_fonts()
    # 暂时不要用 ez_save 可能破坏结构
    # garbage=4：最大程度清理无用对象
    #       garbage=3      |       garbage=4
    #  清理重复的 PDF 对象 | 包括 garbage=3 的所有操作，
    # （xref entries）     | 还会清理重复的 streams（
    #                      | 图像、字体等二进制数据）
    # deflate=True：压缩流数据
    # clean=False：避免误删有效内容
    doc.save(output_path, garbage=4, deflate=True, clean=False)
    print(f"✅ 成功生成带书签的 PDF：{output_path}")

