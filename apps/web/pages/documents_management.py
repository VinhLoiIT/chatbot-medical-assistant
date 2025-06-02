import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import json
from pathlib import Path

from agno.document.chunking.strategy import ChunkingStrategy
from agno.document.chunking.fixed import FixedSizeChunking
from agno.document.reader.pdf_reader import PDFReader
from agno.document.reader.text_reader import TextReader

import pandas as pd

from configs.db import clear_knowledge_base, get_kb_vector_db_collection, knowledge_base
from configs.settings import settings
from configs.logger import logger


st.set_page_config(
    page_title="Document Management",
    layout="wide",
    initial_sidebar_state="expanded",
)


def build_file_identifier(uploaded_file: UploadedFile) -> str:
    file_identifier = f"{uploaded_file.name}_{uploaded_file.size}"
    return file_identifier


def get_chunking_strategy() -> ChunkingStrategy:
    return FixedSizeChunking(chunk_size=5000, overlap=0)


def clear_data():
    collection = get_kb_vector_db_collection()
    for item in collection.iterator(include_vector=False, return_properties=True):
        metadata = json.loads(item.properties["meta_data"])
        file_path = Path(metadata["file_path"])
        file_path.unlink(missing_ok=True)
    clear_knowledge_base()


def get_reader(file_type: str, chunking_strategy: ChunkingStrategy | None = None):
    chunking_strategy = chunking_strategy or get_chunking_strategy()
    if file_type == ".pdf":
        return PDFReader(chunking_strategy=chunking_strategy)
    if file_type == ".txt":
        return TextReader(chunking_strategy=chunking_strategy)

    raise TypeError(f"File type {file_type} is not supported")


def fetch_documents(fetch_size: int = 15) -> pd.DataFrame:
    collection = get_kb_vector_db_collection()
    data = []
    for idx, item in enumerate(
        collection.iterator(
            include_vector=True, return_properties=True, cache_size=fetch_size
        )
    ):
        data.append(item.properties)
        if idx == fetch_size:
            break

    if len(data) > 0:
        df = pd.DataFrame.from_records(data)
        df = df[["name", "meta_data"]]
        # NOTE: use this to preview content as well (it maybe very long)
        # df = df[["name", "meta_data", "content"]]
        return df

    return pd.DataFrame()


st.markdown("# Upload documents")
uploaded_files = st.file_uploader(
    "Add a Document (.pdf, .txt)",
    key="file_upload",
    type=("pdf", "txt"),
    accept_multiple_files=True,
)
upload_notices = st.container()
if uploaded_files:
    data_dir = Path(settings.DEFAULT_DATA_DIR)
    data_dir.mkdir(exist_ok=True, parents=True)

    for uploaded_file in uploaded_files:
        file_identifier = build_file_identifier(uploaded_file)
        data_path = data_dir / file_identifier

        if data_path.exists():
            upload_notices.info(
                f"Document {uploaded_file.name} already exists. Skip processing"
            )
        else:
            alert = upload_notices.info("Processing document...", icon="ℹ️")

            logger.info("Storing uploaded file to: %s", data_path)
            with open(data_path, "wb") as f:
                f.write(uploaded_file.read())
            logger.info("Finished storing file to: %s", data_path)

            file_type = Path(uploaded_file.name).suffix.lower()
            reader = get_reader(file_type)
            if reader:
                docs = reader.read(data_path)
                for doc in docs:
                    # NOTE: update this if we use remote cloud storage
                    # this is mainly for local development and testing
                    doc.meta_data["file_path"] = str(data_path)
                knowledge_base.load_documents(docs, upsert=True)
                upload_notices.success(f"{uploaded_file.name} added to knowledge base")
            alert.empty()

st.divider()

st.markdown("# Knowledge base preview")
fetch_count = 15
st.text(f"Sampling {fetch_count} samples in the vector database:")
df = fetch_documents(fetch_size=fetch_count)
if len(df) > 0:
    st.table(df)
else:
    st.info("Knowledge base is empty")

if st.button("Clear knowledge base", type="primary"):
    clear_data()
    st.rerun()
