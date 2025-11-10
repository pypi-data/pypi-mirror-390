import os
import re
from pylibsrd import HtmlBuilder
import argparse


class Markdown:
    MultiLineTokens = ["checklist", "ul_item", "ol_item", "blockquote", "table", "paragraph"]

    def __init__(self, path, imageFolderPath=None, stylePath=None):
        self.imageFolderPath = imageFolderPath
        self.stylePath = stylePath
        self.path = path
        self.FileName_NoExt = os.path.splitext(os.path.basename(self.path))[0]
        self.Headings = [] # (level, text, id)

        with open(path, "r") as f:
            self.mdlines = f.readlines()

    def _Tokenise(self):
        tokens = []
        possibleHeadingLevels = ("# ", "## ", "### ", "#### ", "##### ")

        for line in self.mdlines:
            line = line.removesuffix("\n")

            if line.startswith("- [ ] ") or line.startswith("* [ ] "):  # Unchecked checklist
                tokens.append(("checklist", False, line[6:].strip()))

            elif line.startswith("- [x] ") or line.startswith("* [x] "):  # Checked checklist
                tokens.append(("checklist", True, line[6:].strip()))

            elif line.startswith("- ") or line.startswith("* "):  # Unordered List
                tokens.append(("ul_item", line[2:]))

            elif len(line) > 2 and line[0].isdigit() and line[1] == ".":  # Ordered List
                tokens.append(("ol_item", line[2:])) # Wont fail if string is only 2 long, due to slicing behaviour.

            elif line.startswith("> "):  # Blockquote
                tokens.append(("blockquote", line[2:]))

            elif line.startswith("|"): # Table row
                tokens.append(("table", line))

            elif line.startswith(possibleHeadingLevels):  # heading
                level = len(line.split(" ")[0])
                text = line[level:].strip()
                headingId = text.replace(" ", "_")

                
                # Make the heading id unique
                i = 0
                if headingId in [x[2] for x in self.Headings]:
                    i = 1
                    while headingId + str(i) in self.Headings:
                        i += 1

                if i != 0:
                    headingId += str(i)

                self.Headings.append((level, text, headingId))
                tokens.append(("heading", level, text, headingId))

            else:  # Everything else is a paragraph
                tokens.append(("paragraph", line))

            # Handle Linebreak
            if line.endswith("  "):
                tokens.append("linebreak")

        return self._join_multiline_tokens(tokens)
    
    @staticmethod
    def _join_multiline_tokens(tokens):
        newTokenList = []
        buffer = []

        for token in tokens:
            # Case 1: empty buffer, single line token
            if len(buffer) == 0 and token[0] not in Markdown.MultiLineTokens:
                newTokenList.append(token)

            # Case 2: not empty buffer, single line token
            elif len(buffer) > 0 and token[0] not in Markdown.MultiLineTokens:
                newTokenList.append((buffer[0][0], buffer.copy()))
                buffer.clear()
                
                newTokenList.append(token)

            # Case 3: not empty buffer, new multiline token
            elif len(buffer) > 0 and token[0] != buffer[0][0] and token[0] in Markdown.MultiLineTokens:
                newTokenList.append((buffer[0][0], buffer.copy()))
                buffer.clear()

                buffer.append(token)

            # Case 4: empty buffer or same token
            else: 
                buffer.append(token)

        if len(buffer) > 0: # Make sure the buffer does not get forgotten if the last element is a multiline.
            newTokenList.append((buffer[0][0], buffer.copy()))

        return newTokenList

    def GetHtml(self):
        tokens = self._Tokenise()
        preprocessedHtml = self._HTML_from_tokens(tokens)
        regexHtml = self._HTML_convert_inline_formatting(preprocessedHtml)
        return regexHtml
    def _HTML_from_tokens(self, tokens):
        html = HtmlBuilder(self.FileName_NoExt)
        html.initaliseHtml(self.stylePath)
        
        # Sidebar styles
        html.appendRawText('''<style>
        #__toc_button__ {position: fixed;top: 15px;left: 15px;z-index: 1001; background: #fff;color: var(--text);border: 1px solid var(--text);border-radius: 5px;cursor: pointer;font-size: 20px;padding: 5px 10px;line-height: 1;transition: all 0.3s ease; width: auto;display: block;}
        #__toc_button__:hover {background: var(--text);color: var(--background);}
        #__toc__ {position: fixed;top: 0;left: 0;width: 280px; height: 100vh; background: #fff;border-right: 1px solid var(--text);z-index: 1000;overflow-y: auto; padding: 20px;padding-top: 70px; transform: translateX(-100%);transition: transform 0.3s ease-in-out;display: block !important;}
        body.sidebar-open #__toc__ {transform: translateX(0);}
        #__container__ {transition: margin-left 0.3s ease-in-out;}
        .sidebar-overlay {position: fixed;top: 0;left: 0;width: 100%;height: 100%;background: rgba(0, 0, 0, 0.4);z-index: 999;opacity: 0;visibility: hidden;transition: opacity 0.3s ease, visibility 0.3s ease;}
        body.sidebar-open .sidebar-overlay {opacity: 1;visibility: visible;}
        @media (min-width: 992px) {body.sidebar-open #__toc_button__ {transform: translateX(280px);} body.sidebar-open .sidebar-overlay {opacity: 0;visibility: hidden;}}
        @media (max-width: 991px) {#__toc__ {width: 250px;}}
        body {max-width: 1000px; margin: 0 auto; padding: 20px; }                 
        </style>''')
        html.ImportMathJax()

        html.appendRawText('<button onclick="toc_click()" id="__toc_button__">&#9776;</button>')

        html.startDiv(id="__container__")
        html.appendRawText(f"\n<h1>{self.FileName_NoExt}</h1>\n")
        html.appendRawText(self._HTML_generate_toc())

        # Add the script to control the visibility
        html.appendRawText('''<div class="sidebar-overlay" onclick="toc_click()"></div>\n<script>function toc_click() {document.body.classList.toggle('sidebar-open');}</script>''')
        html.startDiv(id="__container__")
            
        for token in tokens:
            if token[0] == "heading":
                html.Heading(token[2], token[1], id=token[3])

            elif token[0] == "paragraph":
                p = ""
                pTokens = token[1]
                for pToken in pTokens:
                    p += str(pToken[1]).strip() + " "

                html.p(p)
            
            elif token[0] == "linebreak":
                html.br()

            elif token[0] == "ul_item":
                items = []
                ulTokens = token[1]
                for ulToken in ulTokens:
                    items.append(ulToken[1])

                html.ul(items)

            elif token[0] == "checklist": # Im just going to convert a checklist to a ul
                items = []
                ulTokens = token[1]
                for ulToken in ulTokens:
                    items.append(ulToken[2])

                html.ul(items)

            elif token[0] == "ol_item":
                items = []
                olTokens = token[1]
                for olToken in olTokens:
                    items.append(olToken[1])

                html.ol(items)

            elif token[0] == "blockquote":
                quote = ""
                bqTokens = token[1]
                for bqToken in bqTokens:
                    quote += bqToken[1]

                html.blockquote(quote)

            elif token[0] == "table":
                table = []

                tabTokens = token[1]
                for tabToken in tabTokens:
                    table.append(tabToken[1])

                headers = [h.strip() for h in table[0].split("|")[1:-1]]
                alignments = ["l"] * len(headers)  # Default left-align

                data = []
                for row in table[2:]:  # Skip header and separator row
                    data.append([cell.strip() for cell in row.split("|")[1:-1]])

                html.table(headers, alignments, data, Class="centre")
        
        html.endDiv()
        return html.GetHtml()
    def _HTML_convert_inline_formatting(self, text):
        # Links and images
        text = re.sub(r"!\[\[(.*?)\]\]", rf'<br><img src="{self.imageFolderPath}\1" alt="\1"/><br>', text)
        text = re.sub(r"(?<!\!)\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)

        # Handle Double-Dollar Maths FIRST
        text, MathsBlocks = self._HTML_handle_block_maths(text)
        text, InlineMaths = self._HTML_handle_inline_maths(text)        
        
        # bold and italics
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)

        text = self._HTML_restore_block_maths(text, MathsBlocks)
        text = self._HTML_restore_inline_maths(text, InlineMaths)

        # Handle Code Blocks
        text = re.sub(r"```(.*?)```", r"<pre><code>\1</code></pre>", text, flags=re.DOTALL)

        return text
    def _HTML_handle_block_maths(self, text):
        MathsBlocks = []

        def replacement_block(match:re.Match):
            MathsBlocks.append(match.group(0))
            return f"((==MATHS_BLOCK_{len(MathsBlocks)-1}==))"
        
        text = re.sub(r"\$\$(.*?)\$\$", replacement_block, text, flags=re.DOTALL)
        return text, MathsBlocks
    def _HTML_handle_inline_maths(self, text):
        InlineMaths = []

        def replacement_block(match:re.Match):
            InlineMaths.append(match.group(0))
            return f"((==INLINE_MATHS_{len(InlineMaths)-1}==))"
        
        text = re.sub(r"(?<!\$)\$(.*?)(?<!\\)\$", replacement_block, text)
        return text, InlineMaths
    def _HTML_restore_block_maths(self, text:str, MathsBlocks):
        for i in range(len(MathsBlocks)):
            maths = fr"\[{MathsBlocks[i][2:-2].strip()}\]"
            text = text.replace(f"((==MATHS_BLOCK_{i}==))", maths)

        return text
    def _HTML_restore_inline_maths(self, text, InlineMaths):
        for i in range(len(InlineMaths)):
            maths = fr"\({InlineMaths[i][1:-1].strip()}\)"
            text = text.replace(f"((==INLINE_MATHS_{i}==))", maths)

        return text
    def _HTML_generate_toc(self):
        # Personally I really like this code - 14/05/2025
        html = []
        stack  = [0]

        for level, text, id in self.Headings:
            if level >= 3:
                continue

            # Close lists if we're going up
            while stack[-1] != 0 and stack[-1] > level:
                html.append('</ol>') 
                stack.pop()

            # Open new <ul> if going deeper
            initalLevel = stack[-1]
            for i in range(level-stack[-1]):
                level = initalLevel + (i+1)

                html.append(f'<ol class="__toc_ol__ __lvl_{level}__">')
                stack.append(level)

            html.append(f'<li class="__toc_li__ __lvl_{level}__"><a class="__toc__a__ __lvl_{level}__" href="#{id}">{text}</a></li>')

        while stack[-1] != 0:
            html.append("</ol>")
            stack.pop()

        return f'<div id="__toc__" class="w3-hide w3-animate-top w3-container">\n{"\n".join(html)}\n</div>'


def _MarkHTML_script():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="The filepath to the markdown file you would like to parse to HTML")
    parser.add_argument("-d", "--directory", action="store_true", help="Directory mode... Will batch convert a folder instead of file.")
    parser.add_argument("-s", "--style_path", help="Specify a path to a css stylesheet to be included in the header. (If using -a, path should be from there)")
    parser.add_argument("-i", "--image_folder", help="Specify the path to a folder where images are stored")
    args = parser.parse_args()

    paths = []
    if args.directory:
        allPaths = os.listdir(args.file_path)
        [paths.append(p) for p in allPaths if p[-3:]==".md"]
    else:
        paths.append(args.file_path)

    for path in paths:
        md = None
        if args.style_path and args.image_folder:
            md = Markdown(path, args.image_folder, args.style_path)
        elif args.image_folder:
            md = Markdown(path, args.image_folder)
        elif args.style_path:
            md = Markdown(path, None, args.style_path)
        else:
            md = Markdown(path)

        if type(md) == Markdown:
            html = md.GetHtml()
            with open(os.path.splitext(path)[0]+'.html', "w+") as f:
                f.write(html)
        else:
            print("An error has occured.")
