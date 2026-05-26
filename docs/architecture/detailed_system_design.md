# TÀI LIỆU THIẾT KẾ HỆ THỐNG CHI TIẾT (DETAILED SYSTEM DESIGN)

Tài liệu này đóng vai trò là "bản thiết kế thi công" (Low-Level Design / Detailed Design) cho nền tảng Q-School. Dựa vào đây, đội ngũ Lập trình viên (Backend, Frontend, AI Engineer) có thể tiến hành code, phân chia cấu trúc thư mục, triển khai database và thiết lập môi trường (DevOps).

---

## 1. Tổng quan Công nghệ (Technology Stack)

Hệ thống được vận hành trên nền tảng các công nghệ mã nguồn mở hiện đại, đảm bảo tính ổn định, tốc độ và bảo mật cao.

| Lớp (Layer) | Công nghệ / Framework | Vai trò cốt lõi |
| :--- | :--- | :--- |
| **Frontend** | ReactJS, TailwindCSS | Xây dựng giao diện Web App SPA cho Giáo viên và Học sinh. |
| **Backend Framework** | FastAPI (Python 3.11+) | Xử lý API tốc độ cao, hỗ trợ tốt asyncio và hệ sinh thái AI. |
| **Relational Database** | PostgreSQL 15+ & pgvector | Lưu trữ dữ liệu cấu trúc (User, Quizzes, Lessons) và Vector Embeddings (RAG). |
| **ORM / Query Builder** | SQLAlchemy 2.0 | Giao tiếp với Database, mapping các Model Python. |
| **Cache / Queue** | Redis | Caching Token, OTP. Làm Broker (Trạm trung chuyển) cho Message Queue. |
| **Background Task** | Celery / RQ | Worker chạy ngầm, nhận lệnh từ Redis Queue để xử lý tác vụ AI nặng. |
| **AI Inference** | vLLM (Self-hosted) | Tối ưu hóa suy luận cho các model mã nguồn mở (Qwen/LLaMA) qua chuẩn API OpenAI. |
| **Object Storage** | Cloudflare R2 / MinIO | Lưu trữ file tĩnh (PDF, ảnh). Khuyên dùng Cloudflare R2 để miễn phí băng thông. |

---

## 2. Tiêu chuẩn Mã nguồn & Cấu trúc Thư mục (Codebase Architecture)

Backend FastAPI tuân thủ triệt để mô hình **Hexagonal Architecture (Ports and Adapters)**. Cấu trúc này giúp cô lập Logic nghiệp vụ (Domain) khỏi các công cụ kỹ thuật (Database, Framework).

### Cấu trúc Thư mục Dự kiến (Backend API)
```text
qschool-backend/
├── app/
│   ├── core/                   # Cấu hình lõi (Settings, Security, Exception Handlers)
│   ├── domain/                 # CORE LOGIC (Không phụ thuộc vào Database hay Framework)
│   │   ├── models/             # Business Entities (Ví dụ: User, Lesson, Quiz)
│   │   └── exceptions.py       # Custom Domain Exceptions
│   ├── application/            # USE CASES (Orchestration logic)
│   │   ├── ports/              # INBOUND & OUTBOUND PORTS (Interfaces / Abstract Base Classes)
│   │   │   ├── inbound/        # Interfaces cho Use Cases (Để Router gọi vào)
│   │   │   └── outbound/       # Interfaces cho Database/LLM (Để Use Case gọi ra)
│   │   └── use_cases/          # Thực thi logic từ Use-Case docs (VD: generate_lesson_plan)
│   ├── adapters/               # DRIVEN ADAPTERS (Giao tiếp với bên ngoài)
│   │   ├── database/           # SQLAlchemy Repositories, Migrations (Alembic)
│   │   ├── llm_client/         # Client gọi API tới vLLM Server
│   │   ├── storage/            # Tương tác với MinIO/S3
│   │   └── message_queue/      # Cấu hình đẩy Job vào Celery
│   └── entrypoints/            # DRIVING ADAPTERS (Nơi nhận Request)
│       ├── api_v1/             # FastAPI REST Routers (Controllers)
│       ├── sse/                # Server-Sent Events (SSE) handlers
│       └── celery_worker/      # Code chạy nền của Worker
├── tests/                      # Unit Tests, Integration Tests
├── requirements.txt            # Package dependencies
└── docker-compose.yml          # Triển khai môi trường Local
```

---

## 3. Thiết kế Cơ sở Dữ liệu Tổng quát (Data Model Overview)

Database PostgreSQL được chia thành 3 cụm nghiệp vụ chính. (Bản ERD chi tiết kèm kiểu dữ liệu sẽ được thiết kế riêng).

1. **Nhóm Core & Auth:**
   - `users`, `profiles`: Quản lý danh tính và Gamification.
   - `classes`, `class_students`: Quản lý Lớp học và Học sinh.
2. **Nhóm Nghiệp vụ Soạn Giảng & Giao Bài (EdTech Core):**
   - `lessons`, `quizzes`, `questions`, `answers`, `rubrics`: Cấu trúc bài giảng, bộ đề thi và tiêu chí chấm điểm.
   - `class_assignments`: Quản lý việc giao bài cho các Lớp (Nội dung số).
   - `flashcard_sets`, `flashcards`: Thẻ ghi nhớ.
3. **Nhóm Theo dõi Học sinh (Student Tracking):**
   - `quiz_attempts`, `student_answers`: Lưu lịch sử thi trắc nghiệm và câu trả lời chi tiết.
   - `essay_submissions`: Lưu bài văn nộp và lời nhận xét của AI (AI Feedback).
   - `flashcard_reviews`: Lưu độ khó thẻ bài theo từng học sinh (Spaced Repetition).
4. **Nhóm AI & Học liệu (AI Workspace):**
   - `ai_prompts`: Quản trị System Prompts cho các "Nhân cách AI".
   - `chat_sessions`, `chat_messages`: Lưu lịch sử hội thoại (hỗ trợ context RAG qua `document_id`).
   - `generated_assets`: Gom nhóm tất cả văn bản do AI sinh ra (Email, IEP, Nhận xét) để chống rác Database.
   - `documents`, `document_chunks`: Lưu siêu dữ liệu file và Vector Embeddings (pgvector) cho RAG.
   - `ai_tasks`: Bảng giám sát tiến trình Celery (Pending, Completed).
5. **Nhóm Thương mại & Thanh toán (SaaS Billing):**
   - `plans`: Cấu hình các gói cước (Free, Pro, Enterprise) và giới hạn tính năng.
   - `user_subscriptions`: Trạng thái gói cước hiện tại của Học sinh/Giáo viên.
   - `payment_transactions`: Lịch sử giao dịch thanh toán qua Webhook (Stripe/VNPay).

---

## 4. Thiết kế Giao tiếp API & Real-time (Interface Guidelines)

### 4.1. Chuẩn hóa RESTful API
- **Endpoint naming:** Dùng danh từ số nhiều (VD: `/api/v1/lessons`, `/api/v1/users`).
- **Standard Response:** Mọi API (kể cả lỗi) đều trả về chuẩn JSON đồng nhất:
  ```json
  {
    "status": "success",  // hoặc "error"
    "data": { ... },      // Payload (nếu success)
    "message": "...",     // Thông báo chi tiết
    "error_code": 0       // Mã lỗi nội bộ (nếu error)
  }
  ```
- **Pagination:** Bắt buộc sử dụng **Cursor-based Pagination** cho các list dữ liệu lớn và liên tục thay đổi (như Lịch sử trò chuyện, Feed). Hạn chế tối đa dùng Offset/Limit để tránh suy giảm hiệu năng cơ sở dữ liệu.

### 4.2. Giao tiếp HTTP Streaming (Server-Sent Events - SSE)
- Được sử dụng cho các chức năng **AI Chatbot (UC-FT-015)** và nhận kết quả AI.
- **Cơ chế Streaming:** Giống ChatGPT, thay vì đợi vLLM sinh xong cả câu trả lời, Backend sử dụng **SSE** (`StreamingResponse` của FastAPI) để stream từng luồng Text (Token) về Frontend (React) theo chiều từ Server -> Client, tạo hiệu ứng gõ chữ thời gian thực. **Tuyệt đối không dùng WebSockets** để đảm bảo tính ổn định qua Load Balancer.

---

## 5. Thiết kế Luồng Xử lý AI & Inference (AI Pipeline)

### 5.1. Mô hình AI (vLLM Self-hosted)
- Sử dụng máy chủ GPU chạy framework **vLLM**.
- vLLM sẽ tự động phơi bày (expose) API tương thích 100% với chuẩn OpenAI (`/v1/chat/completions`). Do đó, Backend FastAPI chỉ cần dùng thư viện `openai-python` trỏ baseURL về địa chỉ IP của server nội bộ.

### 5.2. Vòng đời Background Worker (Celery + Redis)
1. **Producer:** API FastAPI nhận file và prompt, lưu DB trạng thái `Processing`. Bắn `task_id` vào Redis Queue.
2. **Broker:** Redis giữ `task_id` và phân phối.
3. **Consumer:** Celery Worker lấy task ra, làm sạch Data, gọi API sang vLLM, chờ kết quả.
4. Xử lý xong, Worker update DB thành `Completed`, và thông qua Pub/Sub hoặc SSE để Client nhận biết tiến trình hoàn tất.

### 5.3. RAG Pipeline (Retrieval-Augmented Generation) - Tùy chọn
Dành cho chức năng "Tổng hợp kiến thức sách giáo khoa".
- **Ingestion:** Giáo viên tải PDF -> Trích xuất text -> Chia nhỏ (Chunking bằng LangChain) -> Biến thành Vectors (Embeddings) -> Lưu vào `pgvector`.
- **Retrieval:** Học sinh hỏi -> Biến câu hỏi thành Vector -> Truy vấn 3 đoạn Text sát nghĩa nhất trong DB -> Ném cả Câu hỏi + 3 Đoạn Text đó làm Prompt gửi cho vLLM trả lời.

---

## 6. Bảo mật & Cấp quyền (Security & Authorization)

- **Authentication (Xác thực):** 
  - Sử dụng **JWT (JSON Web Token)** để cấp quyền truy cập. Token hết hạn ngắn (15 phút), kèm theo `Refresh Token` lưu trong HttpOnly Cookie.
  - Mật khẩu lưu trữ phải mã hóa bằng chuẩn `Bcrypt`.
- **Authorization (Phân quyền - RBAC):** 
  - Các Router trong FastAPI sử dụng **Dependency Injection** (`TeacherDep`, `CurrentUserDep`, `AdminDep`) để kiểm tra Role. Ví dụ: Endpoint tạo Lesson inject `TeacherDep` — nếu User không có role `teacher` hoặc `admin`, hệ thống trả về 403 Forbidden. Phương pháp này linh hoạt hơn URL-prefix và cho phép kiểm soát quyền ở mức từng endpoint.
- **Rate Limiting, Anti-Spam & SaaS Billing:** 
  - Đặt ngưỡng Rate Limit trên API Gateway (Nginx) để chống DDoS.
  - **Mô hình SaaS:** API AI kiểm tra quyền lợi theo gói cước (`user_subscriptions`). 
    - Nếu sử dụng quá tần suất: Trả về lỗi `429 Too Many Requests`.
    - Nếu hết lượt/hết hạn gói VIP: Trả về lỗi `402 Payment Required` yêu cầu nâng cấp gói cước.

---

## 7. Chiến lược Triển khai & CI/CD (Deployment & DevOps)

Hệ thống Q-School được đóng gói container hóa toàn bộ để đảm bảo tính đồng nhất giữa môi trường Dev và Production.

- **Dockerization:** Viết `Dockerfile` riêng biệt cho: React App, FastAPI Server, Celery Worker, vLLM Server.
- **Orchestration:** Dùng `docker-compose` (hoặc Kubernetes nếu quy mô cực lớn) để quản trị mạng lưới nội bộ giữa các container. Các Port nội bộ (Ví dụ: 5432 của Postgres, 6379 của Redis) tuyệt đối không expose ra ngoài Internet.
- **Web Server:** Dùng **Nginx** làm Reverse Proxy, gán chứng chỉ SSL (HTTPS), điều hướng `/api/*` về FastAPI và chuyển hướng các đường dẫn tĩnh về React App.
- **Giao thức khởi chạy (Uvicorn):** FastAPI chạy thực tế dưới sự quản lý của Gunicorn + Uvicorn worker class để tận dụng tối đa số lượng CPU Core của máy chủ Backend.
