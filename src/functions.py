import logging

logger = logging.getLogger(__name__)

from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
from blocks import BlockType
import re
import os
import shutil



def extract_markdown_images(text):
    matches = re.findall(r"!\[(.*?)\]\(([^()\s]+(?:\([^()]*\)[^()]*)*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[(.*?)\]\(([^()\s]+(?:\([^()]*\)[^()]*)*)\)", text)
    return matches

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise ValueError(f"Unsupported text type: {text_node.text_type}")
        
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue
        split_node = node.text.split(sep=delimiter)
        if len(split_node) % 2 == 0:
                raise Exception("Delimiter not found in text node")
        for i, part in enumerate(split_node):
            if part == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))
    
    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue
        text = node.text
        matches = extract_markdown_images(text)
        if not matches:
            new_nodes.append(node)
            continue
        remaining = text
        for match in matches:
            alt_text, link = match
            split_node = remaining.split(sep=f"![{alt_text}]({link})", maxsplit=1)
            if split_node[0]:
                new_nodes.append(TextNode(split_node[0], TextType.TEXT))
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, link))
            remaining = split_node[1]
        if remaining:
            new_nodes.append(TextNode(remaining, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue
        text = node.text
        matches = extract_markdown_links(text)
        if not matches:
            new_nodes.append(node)
            continue
        remaining = text
        for match in matches:
            link_text, link = match
            split_node = remaining.split(sep=f"[{link_text}]({link})", maxsplit=1)
            if split_node[0]:
                new_nodes.append(TextNode(split_node[0], TextType.TEXT))
            new_nodes.append(TextNode(link_text, TextType.LINK, link))
            remaining = split_node[1]
        if remaining:
            new_nodes.append(TextNode(remaining, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    blocks_new = []
    for block in blocks:
        block = block.strip()
        if block:
            blocks_new.append(block)
    return blocks_new

def block_to_block_type(block):
    block_lines = block.split("\n")
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    if block.startswith((">", "> ")):
        return BlockType.QUOTE
    if block.startswith("- "):
        for line in block_lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST
    if block.startswith("1. "):
        for i in range(len(block_lines)):
            if not block_lines[i].startswith(f"{i+1}. "):
                return BlockType.PARAGRAPH
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for node in text_nodes:
        html_node = text_node_to_html_node(node)
        html_nodes.append(html_node)
    return html_nodes

def block_heading_to_html_node(block):
    level = len(block.split()[0])
    heading_text = block[level+1:]
    heading_children = text_to_children(heading_text)
    tag = f"h{level}"
    return ParentNode(tag, heading_children)

def block_code_to_html_node(block):
    code_text = block[3:-3].strip()
    code_node = LeafNode("code", code_text)
    return ParentNode("pre", [code_node])

def block_unordered_list_to_html_node(block):
    list_items = block.split("\n")
    li_children = []
    for item in list_items:
        item_text = item[2:]
        list_item_children = text_to_children(item_text)
        li_node = ParentNode("li", list_item_children)
        li_children.append(li_node)
    return ParentNode("ul", li_children)

def block_ordered_list_to_html_node(block):
    list_items = block.split("\n")
    li_children = []
    for item in list_items:
        item_text = item.split(". ", 1)[1]
        list_item_children = text_to_children(item_text)
        li_node = ParentNode("li", list_item_children)
        li_children.append(li_node)
    return ParentNode("ol", li_children)

def block_quote_to_html_node(block):
    quote_lines = block.split("\n")
    quote_text = " ".join([line[1:].strip() if line.startswith(">") else line for line in quote_lines])
    quote_children = text_to_children(quote_text)
    return ParentNode("blockquote", quote_children)

def block_paragraph_to_html_node(block):
    paragraph_children = text_to_children(block.replace("\n", " "))
    return ParentNode("p", paragraph_children)

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING:
            children.append(block_heading_to_html_node(block))
        elif block_type == BlockType.CODE:
            children.append(block_code_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            children.append(block_unordered_list_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            children.append(block_ordered_list_to_html_node(block))
        elif block_type == BlockType.QUOTE:
            children.append(block_quote_to_html_node(block))
        else:
            children.append(block_paragraph_to_html_node(block))
    return ParentNode("div", children)

def copy_files(dir1, dir2):
    path1 = os.path.abspath(dir1)
    path2 = os.path.abspath(dir2)
    if not os.path.exists(path1):
        raise Exception(f"Directory {dir1} does not exist")
    if not os.path.isdir(path1):
        raise Exception (f"{dir1} is not a directory")
    if os.path.exists(path2):
        shutil.rmtree(path2)
        logger.info(f"Removed existing directory: {path2}")
    if not os.path.exists(path2):
        os.mkdir(path2)
        logger.info(f"Created directory: {path2}")
    for item in os.listdir(path1):
        item_path1 = os.path.join(path1, item)
        item_path2 = os.path.join(path2, item)
        if os.path.isdir(item_path1):
            logger.info(f"Entering directory: {item_path1}")
            copy_files(item_path1, item_path2)
        else:
            shutil.copy(item_path1, item_path2)
            logger.info(f"Copied file: {item_path1} -> {item_path2}")

def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    raise Exception("H1 header not found")

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path} template")
    from_path_abs = os.path.abspath(from_path)
    template_path_abs = os.path.abspath(template_path)
    dest_path_abs = os.path.abspath(dest_path)
    dest_path_dir = os.path.dirname(dest_path_abs)
    if not os.path.exists(dest_path_dir):
        os.makedirs(dest_path_dir)
    with open(from_path_abs, "r+") as f1, open(template_path_abs, "r+") as f2:
        input = f1.read()
        template = f2.read()
        title = extract_title(input)
        html_node = markdown_to_html_node(input)
        html_string = html_node.to_html()
        template_updated = template.replace("{{ Title }}", title)
        template_updated = template_updated.replace("{{ Content }}", html_string)
        
        with open(dest_path_abs, "w") as f3:
            f3.write(template_updated)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    content_dir_abs = os.path.abspath(dir_path_content)
    template_path_abs = os.path.abspath(template_path)
    dest_dir_abs = os.path.abspath(dest_dir_path)
    for root, dirs, files in os.walk(content_dir_abs):
        for file in files:
            if file.endswith('.md'):
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(root, content_dir_abs)
                if rel_path == '.':
                    dest_file = os.path.join(dest_dir_abs, file.replace('.md', '.html'))
                else:
                    dest_file = os.path.join(dest_dir_abs, rel_path, file.replace('.md', '.html'))
                generate_page(src_file, template_path_abs, dest_file)
       