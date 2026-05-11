import os
import sys
import tempfile
from pathlib import Path

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_upstage import ChatUpstage, UpstageDocumentParseLoader

SYSTEM_PROMPT = """영수증 텍스트에서 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요.

{{
  "store_name": "string",
  "receipt_date": "YYYY-MM-DD",
  "receipt_time": "HH:MM 또는 null",
  "category": "식료품|외식|교통|쇼핑|의료|기타",
  "items": [{{"name": "string", "quantity": 1, "unit_price": 0, "total_price": 0}}],
  "subtotal": 0,
  "discount": 0,
  "tax": 0,
  "total_amount": 0,
  "payment_method": "string 또는 null"
}}"""

# 로컬 Windows Anaconda 환경에서 poppler 경로
_POPPLER_PATH = r"C:\Users\KOSTA\anaconda3\Library\bin"


def _get_poppler_path() -> str | None:
    # Vercel/Linux 환경은 시스템 PATH에 poppler 존재
    if os.environ.get("VERCEL") or sys.platform != "win32":
        return None
    return _POPPLER_PATH if Path(_POPPLER_PATH).exists() else None


def parse_receipt(file_bytes: bytes, content_type: str) -> dict:
    """
    영수증 파일을 OCR로 파싱하여 구조화된 JSON을 반환한다.
    1단계: UpstageDocumentParseLoader로 텍스트 추출
    2단계: ChatUpstage(solar-pro)로 JSON 구조화
    """
    api_key = os.environ["UPSTAGE_API_KEY"]

    # 임시 파일로 저장 (UpstageDocumentParseLoader는 파일 경로 필요)
    suffix = ".pdf" if content_type == "application/pdf" else ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # PDF는 첫 페이지만 OCR (성능 고려)
        loader = UpstageDocumentParseLoader(
            file_path=tmp_path,
            api_key=api_key,
            ocr="force",
            output_format="text",
        )
        docs = loader.load()
        ocr_text = docs[0].page_content if docs else ""
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    llm = ChatUpstage(api_key=api_key, model="solar-pro")
    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{ocr_text}"),
    ])

    chain = prompt | llm | parser
    return chain.invoke({"ocr_text": ocr_text[:3000]})
