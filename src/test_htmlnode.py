import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

node1 = HTMLNode(props={
    "href": "https://www.google.com",
    "target": "_blank",
})

node2 = HTMLNode(props={"test1": "value1", "test2": "value2"})

node3 = HTMLNode("aaa", "bbb", "ccc", {"ddd": "eee", "fff": "ggg", "hhh": "iii"})

node4 = LeafNode("p", "Hello, world!")

node5 = LeafNode("a", "Click me!", {"href": "https://www.google.com"})


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        self.assertEqual(node1.props_to_html(), ' href="https://www.google.com" target="_blank"')

    def test_props_to_html2(self):
        self.assertEqual(node2.props_to_html(), ' test1="value1" test2="value2"')

    def test_props_to_html3(self):
        self.assertEqual(node3.props_to_html(), ' ddd="eee" fff="ggg" hhh="iii"')

    def test_repr_html(self):
        self.assertEqual(repr(node3), "HTMLNode(aaa, bbb, ccc, {'ddd': 'eee', 'fff': 'ggg', 'hhh': 'iii'})")

    def test_leaf_to_html_p(self):
        self.assertEqual(node4.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a_href(self):
        self.assertEqual(node5.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_repr_leaf(self):
        self.assertEqual(repr(node5), "LeafNode(a, Click me!, {'href': 'https://www.google.com'})")

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )