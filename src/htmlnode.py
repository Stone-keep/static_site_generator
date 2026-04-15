

class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("Child classes must implement to_html method")
    
    def props_to_html(self):
        if not self.props:
            return ""
        props_string = ""
        for prop in self.props.items():
            key, value = prop
            props_string += f' {key}="{value}"'
        return props_string
    
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError("LeafNode must have a value")
        if not self.tag:
            return self.value
        self_closing_tags = {'img', 'br', 'hr', 'input', 'meta', 'link'}
        if self.tag in self_closing_tags:
            return f"<{self.tag}{self.props_to_html()} />"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if not self.tag:
            raise ValueError("ParentNode must have a tag")
        if not self.children:
            raise ValueError("ParentNode must have children")
        to_html_string = f'<{self.tag}{self.props_to_html()}>'
        for child in self.children:
            to_html_string += child.to_html()
        to_html_string += f'</{self.tag}>'
        return to_html_string