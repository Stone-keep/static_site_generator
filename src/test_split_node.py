import unittest
from functions import split_nodes_delimiter, split_nodes_image, split_nodes_link
from textnode import TextNode, TextType

class TestSplitNodesDelimiter(unittest.TestCase):

    def test_split_bold(self):
        nodes = [TextNode("This is **bold** text", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(new_nodes, [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT)
        ])

    def test_split_italic(self):
        nodes = [TextNode("This is *italic* text", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.assertEqual(new_nodes, [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT)
        ])

    def test_no_delimiter(self):
        nodes = [TextNode("This is a text node", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(new_nodes, [
            TextNode("This is a text node", TextType.TEXT)
        ])

    def test_multiple_nodes(self):
        nodes = [
            TextNode("This is **bold** text", TextType.TEXT),
            TextNode("And this is *italic* text", TextType.TEXT)
        ]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "*", TextType.ITALIC)
        self.assertEqual(new_nodes, [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
            TextNode("And this is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT)
        ])

    def test_code_delimiter(self):
        nodes = [TextNode("This is `code` text", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(new_nodes, [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT)
        ])

    def test_bold_type_input(self):
        nodes = [TextNode("**Bold** text", TextType.BOLD)]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(new_nodes, [
            TextNode("**Bold** text", TextType.BOLD)
        ])

    def test_odd_number_of_delimiters(self):
        nodes = [TextNode("This is **bold text without closing delimiter", TextType.TEXT)]
        with self.assertRaises(Exception):
            split_nodes_delimiter(nodes, "**", TextType.BOLD)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_image_no_image(self):
        nodes = [TextNode("No image here", TextType.TEXT)]
        new_nodes = split_nodes_image(nodes)
        self.assertEqual(new_nodes, [TextNode("No image here", TextType.TEXT)])

    def test_split_image_with_text_after(self):
        node = TextNode("![icon](https://example.com/icon.png) completed", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("icon", TextType.IMAGE, "https://example.com/icon.png"),
                TextNode(" completed", TextType.TEXT),
            ],
        )

    def test_split_link(self):
        node = TextNode("A [link](https://example.com) here", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("A ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" here", TextType.TEXT),
            ],
        )

    def test_split_multiple_links(self):
        node = TextNode("links [one](https://one) and [two](https://two)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("links ", TextType.TEXT),
                TextNode("one", TextType.LINK, "https://one"),
                TextNode(" and ", TextType.TEXT),
                TextNode("two", TextType.LINK, "https://two"),
            ],
        )

    def test_split_link_no_link(self):
        nodes = [TextNode("No link here", TextType.TEXT)]
        new_nodes = split_nodes_link(nodes)
        self.assertEqual(new_nodes, [TextNode("No link here", TextType.TEXT)])

    def test_split_link_with_parentheses_in_url(self):
        node = TextNode("A [link](https://example.com/file(name).png) end", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("A ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com/file(name).png"),
                TextNode(" end", TextType.TEXT),
            ],
        )