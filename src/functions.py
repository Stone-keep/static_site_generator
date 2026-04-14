from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re

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