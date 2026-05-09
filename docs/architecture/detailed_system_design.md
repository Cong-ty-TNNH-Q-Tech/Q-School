# TÀI LIỆU THIẾT KẾ HỆ THỐNG CHI TIẾT (DETAILED SYSTEM DESIGN)

Tài liệu này đóng vai trò là "bản thiết kế thi công" (Low-Level Design / Detailed Design) cho nền tảng Q-School. Dựa vào đây, đội ngũ Lập trình viên (Backend, Frontend, AI Engineer) có thể tiến hành code, phân chia cấu trúc thư mục, triển khai database và thiết lập môi trường (DevOps).

---

## 1. Tổng quan Công nghệ (Technology Stack)

Hệ thống được vận hành trên nền tảng các công nghệ mã nguồn mở hiện đại, đảm bảo tính ổn định, tốc độ và bảo mật cao.

| Lớp (Layer) | Công nghệ / Framework | Vai trò cốt lõi |
| :--- | :--- | :--- |
| **Frontend** | ReactJS, TailwindCSS | Xây dựng giao diện Web App SPA cho Giáo viên và Học sinh. |
| **Backend Framework** | FastAPI (Python 3.11+) | Xử lý API tốc độ cao, hỗ trợ tốt asyncio và hệ sinh thái AI. |
| **Relational Database** | PostgreSQL 15+ | Lưu trữ dữ liệu cấu trúc (User, Quizzes, Lessons). Tích hợp pgvector (nếu cần RAG). |
| **ORM / Query Builder** | SQLAlchemy 2.0 | Giao tiếp với Database, mapping các Model Python. |
| **Cache / Queue** | Redis | Caching Token, OTP. Làm Broker (Trạm trung chuyển) cho Message Queue. |
| **Background Task** | Celery / RQ | Worker chạy ngầm, nhận lệnh từ Redis Queue để xử lý tác vụ AI nặng. |
| **AI Inference** | vLLM (Self-hosted) | Tối ưu hóa suy luận cho các model mã nguồn mở (Qwen/LLaMA) qua chuẩn API OpenAI. |
| **Object Storage** | MinIO (S3 Compatible) | Lưu trữ file tĩnh (PDF bài tập, ảnh, video tải lên). |

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
│       ├── websockets/         # WebSocket handlers
│       └── celery_worker/      # Code chạy nền của Worker
├── tests/                      # Unit Tests, Integration Tests
├── requirements.txt            # Package dependencies
└── docker-compose.yml          # Triển khai môi trường Local
```

---

## 3. Thiết kế Cơ sở Dữ liệu Tổng quát (Data Model Overview)

Database PostgreSQL được chia thành 3 cụm nghiệp vụ chính. (Bản ERD chi tiết kèm kiểu dữ liệu sẽ được thiết kế riêng).

1. **Nhóm Core & Auth:**
   - `users`: ID, Username, HashedPassword, Role (Teacher/Student/Admin), Status.
   - `profiles`: Họ tên, Email, Avatar, Điểm tích lũy (Gamification của học sinh).
2. **Nhóm Nghiệp vụ Soạn Giảng & Đánh giá (EdTech Core):**
   - `lessons`: Lưu giáo án sinh ra (Title, Content, Subject, Grade).
   - `quizzes` & `questions` & `answers`: Bộ bài kiểm tra trắc nghiệm, kèm cờ (flag) đánh dấu đáp án đúng.
   - `flashcards` & `flashcard_items`: Bộ thẻ nhớ của học sinh (Spaced Repetition).
3. **Nhóm AI & Học liệu (AI Workspace):**
   - `chat_sessions` & `chat_messages`: Lưu lịch sử hội thoại với Raina/Gia sư AI để giữ context.
   - `documents`: Quản lý siêu dữ liệu (Metadata) của các file (PDF/Word) đẩy lên MinIO.

*(Ghi chú: Nếu hệ thống chạy tính năng Tra cứu học liệu lớn (RAG), hệ thống sẽ kích hoạt tính năng `pgvector` trên PostgreSQL để lưu trữ cột `embedding_vector`, thay vì phải cài cắm riêng hệ quản trị Qdrant cho bớt cồng kềnh).*

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
- **Pagination:** Sử dụng Cursor-based hoặc Offset/Limit cho các list dài (Danh sách câu hỏi, Lịch sử trò chuyện).

### 4.2. Giao tiếp WebSocket (Real-time)
- Được sử dụng cho các chức năng **AI Chatbot (UC-FT-015)** và nhận kết quả từ Background Worker.
- **Cơ chế Streaming:** Giống ChatGPT, thay vì đợi vLLM sinh xong cả câu trả lời dài mới hiển thị, Celery Worker sẽ stream từng luồng Text (Token) qua WebSocket trả về Frontend (React) để tạo hiệu ứng gõ chữ thời gian thực (typing effect).

---

## 5. Thiết kế Luồng Xử lý AI & Inference (AI Pipeline)

### 5.1. Mô hình AI (vLLM Self-hosted)
- Sử dụng máy chủ GPU chạy framework **vLLM**.
- vLLM sẽ tự động phơi bày (expose) API tương thích 100% với chuẩn OpenAI (`/v1/chat/completions`). Do đó, Backend FastAPI chỉ cần dùng thư viện `openai-python` trỏ baseURL về địa chỉ IP của server nội bộ.

### 5.2. Vòng đời Background Worker (Celery + Redis)
1. **Producer:** API FastAPI nhận file và prompt, lưu DB trạng thái `Processing`. Bắn `task_id` vào Redis Queue.
2. **Broker:** Redis giữ `task_id` và phân phối.
3. **Consumer:** Celery Worker lấy task ra, làm sạch Data, gọi API sang vLLM, chờ kết quả.
4. Xử lý xong, Worker update DB thành `Completed`, bắn lệnh qua WebSocket báo cho Client cập nhật màn hình.

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
  - Các Router trong FastAPI được gắn Dependency Injection để kiểm tra Role. User `Student` không được phép truy cập vào các API có tiền tố `/api/v1/teacher/...`
- **Rate Limiting & Anti-Spam:** 
  - Đặt ngưỡng Rate Limit trên API Gateway (Nginx) để chống DDoS.
  - Đặt giới hạn ở tầng Application (Redis) cho các API gọi AI (VD: "Học sinh chỉ được hỏi AI Tutor 50 câu / ngày"). Chống lạm dụng tài nguyên GPU server.

---

## 7. Chiến lược Triển khai & CI/CD (Deployment & DevOps)

Hệ thống Q-School được đóng gói container hóa toàn bộ để đảm bảo tính đồng nhất giữa môi trường Dev và Production.

- **Dockerization:** Viết `Dockerfile` riêng biệt cho: React App, FastAPI Server, Celery Worker, vLLM Server.
- **Orchestration:** Dùng `docker-compose` (hoặc Kubernetes nếu quy mô cực lớn) để quản trị mạng lưới nội bộ giữa các container. Các Port nội bộ (Ví dụ: 5432 của Postgres, 6379 của Redis) tuyệt đối không expose ra ngoài Internet.
- **Web Server:** Dùng **Nginx** làm Reverse Proxy, gán chứng chỉ SSL (HTTPS), điều hướng `/api/*` về FastAPI và chuyển hướng các đường dẫn tĩnh về React App.
- **Giao thức khởi chạy (Uvicorn):** FastAPI chạy thực tế dưới sự quản lý của Gunicorn + Uvicorn worker class để tận dụng tối đa số lượng CPU Core của máy chủ Backend.
