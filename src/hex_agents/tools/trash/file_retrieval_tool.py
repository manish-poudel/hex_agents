from pathlib import Path

from langchain.tools import StructuredTool
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader


class FileRetrievalTool:

    def __init__(self, path: str):
        self.path = path

    def invoke(self) -> str:

        directory = Path(self.path)

        if not directory.exists():
            raise FileNotFoundError(directory)

        documents = []

        for glob_pattern, loader_cls in [
            ("**/*.pdf", PyPDFLoader),
            ("**/*.md", TextLoader),
            ("**/*.txt", TextLoader),
        ]:

            kwargs = {}

            if loader_cls == TextLoader:
                kwargs["loader_kwargs"] = {
                    "encoding": "utf-8"
                }

            loader = DirectoryLoader(
                str(directory),
                glob=glob_pattern,
                loader_cls=loader_cls,
                silent_errors=True,
                **kwargs,
            )

            documents.extend(loader.load())

        #
        # Agent should receive text
        #

        return "\n\n".join(
            doc.page_content
            for doc in documents
        )

    def as_tool(self):

        return StructuredTool.from_function(
            func=self.invoke,
            name="access_file",
            description=(
                "Read all supported documents from "
                "the configured directory."
            ),
        )