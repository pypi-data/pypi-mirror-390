from pathlib import Path
import base64
import io
import logging

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat, DocumentStream
    from docling.datamodel.pipeline_options import (
        PdfPipelineOptions,
        TableStructureOptions,
        TableFormerMode,
        EasyOcrOptions
    )
    from six import BytesIO
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

logging.getLogger("docling").setLevel(logging.ERROR)

def extract_structured_md(filename: str, encoded_data: str,  ocr_threshold:float = 0.1) -> str:
    if not DOCLING_AVAILABLE:
        raise ImportError(
            "Docling is not installed. Install it with: pip install multi-ai-handler[docling]"
        )

    file_like = io.BytesIO(base64.b64decode(encoded_data))
    ext = Path(filename).suffix.lower()
    filename = filename

    format_options = None

    if ext == '.pdf':
        table_opts = TableStructureOptions(
            mode=TableFormerMode.ACCURATE,
            do_cell_matching=True
        )

        ocr_opts = EasyOcrOptions(
            lang=["en"],
            force_full_page_ocr=False,
            # confidence_threshold=0.5,
            bitmap_area_threshold=ocr_threshold
        )

        pipeline_opts = PdfPipelineOptions(
            do_table_structure=True,
            table_structure_options=table_opts,
            ocr_options=ocr_opts
        )

        format_options = {InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)}

    converter = DocumentConverter(
        format_options=format_options
    )

    file_bytes = file_like.read()
    doc_stream = DocumentStream(name=filename,stream=BytesIO(file_bytes))
    result = converter.convert(doc_stream)
    md = result.document.export_to_markdown()
    return md
