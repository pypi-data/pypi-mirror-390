from pathlib import Path
import os

os.chdir(Path(__file__).parent)

os.system("jupyter nbconvert notebooks/userguide.ipynb --to markdown --output userguide.md")

with open("notebooks/userguide.md", "r", encoding="utf-8") as file:
    text = file.read()

text = text.replace("```python\n! python", "```\n> python")


lines = text.split("\n")

on_shell_snippet = False
on_python_snippet = False
on_python_snippet_output = False
end_of_python_snippet_output = False
on_python_snippet_decorator = False
snippet_started = False
for i, line in enumerate(lines):
    if line.strip().startswith("Couldn't find"):
        lines[i] = "<must_remove>"
    if line.startswith("%%python"):
        on_python_snippet = False
        lines[i] = "<must_remove>"
    if line.startswith("```bash") or line.startswith("> python"):
        on_shell_snippet = True
        continue
    if line.startswith("```python"):
        on_python_snippet = True
        continue
    if on_python_snippet:
        if line.startswith("```"):  # end of snippet containing python code. Need to continue for output
            lines[i] = "<must_remove>"  # remove this single line
            on_python_snippet = False  # end of snippet containing python code
            on_python_snippet_output = True  # the next is the output
            continue
        if line.startswith(" "):
            lines[i] = "... " + lines[i]
            continue
        if line.startswith("@"):
            lines[i] = ">>> " + lines[i]
            on_python_snippet_decorator = True
            continue
        if on_python_snippet_decorator:
            lines[i] = "... " + lines[i]
            on_python_snippet_decorator = False
            continue
        if len(line) == 0:
            lines[i] = "... " + lines[i]
            continue
        if line.startswith("```"):
            on_python_snippet = False
            continue
        lines[i] = ">>> " + lines[i]
    if on_python_snippet_output:
        if not line.startswith("    "):  # end or start of output snippet
            if end_of_python_snippet_output:  # end of output snippet
                lines[i] = "```"  # finalize output snippet
                on_python_snippet_output = False
                end_of_python_snippet_output = False
                continue
            else:
                lines[i] = "<must_remove>"  # remove this single line
                end_of_python_snippet_output = True  # the next will be the end of output snippet
                continue
        lines[i] = lines[i].strip()
        # else:
        #     lines[i] = lines[i].strip()
        #     if len(lines[i]) == 0:
        #         lines[i] = "<must_remove>"
    if on_shell_snippet:
        if line.startswith("```"):  # end of notebook snippet containing single line with cli command
            lines[i] = "<must_remove>"  # remove this single line
            continue
        if not line.startswith("    "):  # end or start of output snippet
            if snippet_started:  # end of output snippet, because it already started
                lines[i] = "```"  # finalize output snippet
                on_shell_snippet = False
                snippet_started = False
                continue
            else:
                snippet_started = True  # start of output snippet
                continue


text = "\n".join([line for line in lines if line != "<must_remove>"]).replace("... \n...", "...")
with open("notebooks/userguide.md", "w", encoding="utf-8") as file:
    file.write(text)

# with open("../../../src/clig/__init__.pyi", "w", encoding="utf-8") as file:
#     file.write(
#         '"""\n'
#         + text.replace('"""', '\\"\\"\\"')
#         .replace("```\n\n```", "```\n`\n```")
#         .replace("```\n\n\n```", "```\n`\n```")
#         + '"""\n'
#     )
