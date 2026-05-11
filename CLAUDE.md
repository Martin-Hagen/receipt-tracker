# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소에서 작업할 때 참고하는 가이드입니다.

## 프로젝트 개요

영수증 지출 관리 앱 — 영수증 이미지/PDF를 업로드하면 Upstage Vision LLM이 구조화된 JSON으로 파싱하고, 결과를 `expenses.json` 파일에 저장하는 경량 웹 애플리케이션. DB 미사용.

**기술 스택**: React 18 + Vite (프론트엔드) · Python FastAPI (백엔드) · LangChain + Upstage Vision LLM (OCR) · TailwindCSS · Vercel (배포)

## 목표 디렉토리 구조

```
receipt-tracker/
├── frontend/          # Vite + React 앱
│   └── src/
│       ├── pages/     # Dashboard.jsx, UploadPage.jsx, ExpenseDetail.jsx
│       ├── components/ # DropZone, ParsePreview, ExpenseCard, SummaryCard, FilterBar, Badge, Modal, Toast
│       └── api/axios.js
├── backend/           # FastAPI 앱
│   ├── main.py
│   ├── routers/       # upload.py, expenses.py, summary.py
│   ├── services/      # ocr_service.py, storage_service.py
│   └── data/expenses.json
└── vercel.json
```

## 개발 명령어

**백엔드**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload      # http://localhost:8000/docs
```

**프론트엔드**
```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
npm run build
```

## 환경 변수

프로젝트 루트의 `.env` (이미 존재, 절대 커밋 금지):
- `UPSTAGE_API_KEY` — Upstage 콘솔 API 키
- `GROQ_API_KEY` — Groq API 키 (보조)

Vercel 배포 시 필요한 환경 변수: `UPSTAGE_API_KEY` 만 등록하면 됨. `VITE_API_BASE_URL`은 `.env.production`에서 `""`(빈값)으로 설정해 같은 도메인 상대 경로 사용. 백엔드는 `VERCEL=1` 감지 시 자동으로 `/tmp/expenses.json` 경로 사용.

## 핵심 아키텍처 결정 사항

**OCR 파이프라인**: `UpstageDocumentParseLoader`(ocr='force') → 텍스트 추출 → `ChatUpstage(model='solar-pro')` + `JsonOutputParser` → 구조화된 지출 객체. PDF는 `pdf2image`로 이미지 변환 후 처리 (Poppler 필요). `document-digitization-vision`은 chat completions API 미지원 — `UpstageDocumentParseLoader`가 올바른 OCR 방법. 로컬 Windows에서는 `convert_from_path(..., poppler_path=r'C:\...\anaconda3\Library\bin')` 필요.

**데이터 영속성**: 로컬 개발 시 `backend/data/expenses.json`, Vercel은 `/tmp/expenses.json` (컨테이너 재시작 시 초기화). 프론트엔드는 `localStorage`에 병행 저장하여 서버리스 재시작에 대응.

**API 라우트** (모두 `/api` 접두사):
- `POST /upload` — multipart 업로드, 파싱된 JSON 반환 (아직 저장 안 됨)
- `GET /expenses?from=&to=` — 날짜 필터 지원 목록 조회
- `DELETE /expenses/{id}` — UUID로 항목 삭제
- `PUT /expenses/{id}` — 부분 업데이트
- `GET /summary?month=` — 총합 및 카테고리별 통계

**지출 JSON 스키마** (주요 필드): `id` (UUID v4), `store_name`, `receipt_date` (YYYY-MM-DD), `category` (식료품|외식|교통|쇼핑|의료|기타), `items[]`, `total_amount`, `payment_method`

## UI/스타일 규칙

- **색상**: 주요 색상 `indigo-600`, 배경 `gray-50`, 카드·모달 `white`
- **폰트**: Pretendard (CDN), 폴백으로 Noto Sans KR
- **레이아웃**: `max-w-4xl mx-auto`, sticky 헤더 `h-16`
- **반응형 그리드**: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4`
- **Toast**: `fixed bottom-4 right-4`, 3초 자동 소멸, 동시에 하나만 표시
- **오류 처리**: 4xx → amber Toast, 5xx/네트워크 오류 → red Toast + 재시도 버튼, 로딩 중 → `opacity-50 cursor-not-allowed`로 버튼 비활성화

## OCR 시스템 프롬프트 규칙

LLM은 JSON만 응답해야 함 (앞뒤 텍스트 없음). 카테고리는 반드시 `식료품`, `외식`, `교통`, `쇼핑`, `의료`, `기타` 중 하나. 날짜 형식 `YYYY-MM-DD`, 시각 형식 `HH:MM` 또는 `null`.

## Vercel 배포 주의 사항

- 백엔드는 `@vercel/python` + Mangum으로 Python 서버리스 실행
- 프론트엔드는 `@vercel/static-build`로 빌드
- 파일 시스템 비지속 — `/tmp`에 쓴 데이터는 컨테이너 재시작 시 소멸
- `pdf2image` PDF 변환은 Poppler 설치 필요; 의존 전 `/tmp` 경로 사용 가능 여부 확인 필수

### Source Code가 변경되거나 라이브러리 버전이 변경되면 반드시 @PRD_영수증_지출관리앱.md 같이 업데이트 하고, 완료 기준의 Check Box에 완료된 사항들도 모두 체크표시 하세요.