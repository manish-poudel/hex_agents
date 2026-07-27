from pathlib import Path

from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader


def create_access_file_tool():

    @tool
    def access_file(filename: str) -> str:
        """
        Read a document file.
        Supports PDF and TXT files.
        """

        file_path = Path(filename)

        if not file_path.exists():
            print("file not found")
            print(file_path)
            return f"File not found: {file_path}"


        extension = file_path.suffix.lower()


        if extension == ".pdf":

            loader = PyPDFLoader(str(file_path))

            documents = loader.load()

            return "\n\n".join(
                doc.page_content
                for doc in documents
            )


        elif extension == ".txt":
            print("yuppy");

            text = file_path.read_text(
                encoding="utf-8"
            )
            print(text)
            return text


        else:
            return f"Unsupported file type: {extension}"


    return access_file