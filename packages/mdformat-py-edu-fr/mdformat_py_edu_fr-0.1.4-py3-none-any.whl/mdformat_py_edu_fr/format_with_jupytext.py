import jupytext
import re

from pathlib import Path


LABEL_PATTERN = re.compile("(?m)(^\\s*\\(\\w+\\)=)(\r?\n)(\\s*\r?\n)")

path_config_file = Path(__file__).absolute().parent / "jupytext.toml"
config = jupytext.config.load_jupytext_configuration_file(str(path_config_file))


def format_str(text: str) -> str:
    """Format the code of a notebook code using jupytext"""

    notebook = jupytext.reads(text, fmt="md:myst")
    if "kernelspec" not in notebook.metadata:
        return text

    if "learning" in notebook.metadata:
        # Fix common errors in learning metadata
        learning = notebook.metadata["learning"]
        for a in ["prerequisites", "objectives"]:
            # Fix singular instead of plural
            singular = a[:-1]
            if singular in learning:
                learning[a] = learning[singular]
                del learning[singular]

            # Fix string instead of list of string
            for b in ["discover", "remember", "understand", "apply"]:
                if a in learning and isinstance(learning[a].get(b), str):
                    learning[a][b] = [s.strip() for s in learning[a][b].split(",")]

    for cell in notebook.cells:
        if (
            cell.metadata is not None
            and "tags" in cell.metadata
            and cell.metadata["tags"] == []
        ):
            del cell.metadata["tags"]
        # Workaround mdformat-myst to remove empty lines between label and subsequent item
        if cell.cell_type == "markdown":
            cell.source = re.sub(LABEL_PATTERN, r"\1\2", cell.source)
    return jupytext.writes(notebook, fmt="md:myst", config=config)
