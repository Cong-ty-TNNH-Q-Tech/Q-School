# Q-School AI — Hệ Thống Hướng Dẫn Dành Cho AI Agent (Agent Instructions)

Tài liệu này cung cấp bộ quy chuẩn (Guidelines) bắt buộc dành cho mọi lập trình viên và AI Agent (như Claude, GPT) khi tham gia phát triển mã nguồn của dự án **Q-School AI**.

## 1. Tổng quan dự án (Project Overview)
**Q-School AI** là một nền tảng Công nghệ Giáo dục (EdTech) kết hợp Trí tuệ Nhân tạo (AI-native) hoạt động theo mô hình **SaaS**. Dự án bao gồm các tính năng cốt lõi của một hệ thống LMS (Học sinh, Giáo viên, Bài tập, Flashcard) kết hợp với AI Workspace (Sinh giáo án tự động, Chat AI, RAG).

- **Frontend:** React + Vite + TypeScript (Kiến trúc MVVM)
- **Backend:** FastAPI (Python) + SQLAlchemy
- **Kiến trúc lõi:** **Hexagonal Architecture** (Modular Monolith)
- **Hạ tầng AI:** Máy chủ vLLM nội bộ (Self-hosted)
- **Database:** PostgreSQL (với `pgvector` HNSW Index) + Redis
- **Tài liệu tham chiếu:** Mọi Agent **BẮT BUỘC** phải tham chiếu `docs/api/openapi.yaml` và `docs/architecture/erd_schema.md` trước khi sinh code.

---

## 2. Nguyên tắc chung (General Guidelines)
- Luôn giữ tâm thế **Scale & Stability**: Mọi dòng code phải được tối ưu cho hàng nghìn người dùng cùng lúc.
- **Security-First**: Không bao giờ hardcode API Keys, cấu hình Database. Sử dụng biến môi trường (Environment Variables).
- Chức năng liên quan đến AI **LUÔN LUÔN** phải có Rate Limiting (`HTTP 429`) và kiểm tra quyền gói cước (`HTTP 402`).

---

## 3. Quy chuẩn Backend (FastAPI + Hexagonal Architecture)

Dự án tuyệt đối tuân thủ mô hình **Hexagonal Architecture** (Ports & Adapters).
- **Core Domain:** Không được phép chứa bất kỳ logic nào liên quan đến Framework (FastAPI) hay Database (SQLAlchemy). Nó chỉ chứa logic nghiệp vụ thuần túy (Entities, Use Cases).
- **Driving Adapters (Primary):** Các Routers/Controllers của FastAPI. Chỉ dùng để nhận HTTP Request, gọi Use Case và trả về HTTP Response.
- **Driven Adapters (Secondary):** Nơi chứa code tương tác thực tế với PostgreSQL, vLLM, Cloudflare R2, Redis.
- **Dependency Injection (DI):** Sử dụng cơ chế DI của FastAPI (`Depends`) để inject các Repository vào Use Case.

### 3.1. Xử lý AI (AI Processing Rules)
- **Streaming:** Chỉ sử dụng **Server-Sent Events (SSE)** thông qua `StreamingResponse` để stream kết quả AI. **Tuyệt đối KHÔNG sử dụng WebSockets** do vấn đề thiếu ổn định khi qua Load Balancer.
- **Background Tasks:** Các tác vụ AI nặng (Chấm điểm tự luận, Sinh giáo án) phải được đẩy vào Queue (Celery/Redis). Router trả về HTTP 202 ngay lập tức.
- **Vector Search (RAG):** Mọi lệnh tìm kiếm nội dung (Embeddings) phải tận dụng **HNSW Index** của pgvector.

---

## 4. Quy chuẩn Frontend (React + Vite + TypeScript)

- **UI/UX Core:** Sử dụng **Shadcn UI** và Tailwind CSS để xây dựng giao diện. Tránh viết CSS thuần nếu không cần thiết.
- **Mô hình MVVM:** 
  - **Model:** Các interface/type TypeScript định nghĩa theo `openapi.yaml`.
  - **ViewModel:** Sử dụng Custom Hooks (`useChat`, `useAuth`) kết hợp với thư viện quản lý trạng thái (Zustand hoặc React Query) để xử lý logic gọi API và quản lý State.
  - **View:** Component UI thuần túy, không chứa logic gọi API trực tiếp.
- **Mock API:** Khi Backend chưa sẵn sàng, Agent phải tự động tạo file Mock dựa trên cấu trúc Response chuẩn (`{"status": "success", "data": {...}}`) được quy định trong `openapi.yaml`.
- **Trải nghiệm:** Tự động kết nối luồng SSE từ Backend để hiển thị chữ kiểu gõ phím (Typewriter effect) cho Chat AI.

---

## 5. Xử lý Dữ liệu Lớn (Big Data & Pagination)
- **Cấm sử dụng Offset Pagination** (`page`, `limit`) cho các bảng dữ liệu lớn liên tục thay đổi (như Lịch sử tin nhắn, Feed).
- **Bắt buộc dùng Cursor Pagination** (Truyền `cursor` là ID của phần tử cuối cùng) cho toàn bộ API lấy dữ liệu luồng (Ví dụ: `GET /chat/sessions/{session_id}/messages`).

---

## 6. Mô hình Thanh toán SaaS (Billing Enforcement)
- Hệ thống kinh doanh trên 3 Gói cước (Free, Pro, Enterprise).
- Bất kỳ API nào thuộc Nhóm AI (Chat, Generate) phải kiểm tra trạng thái Subscription của User.
- Nếu vượt quá giới hạn (Rate Limit), trả về lỗi `TooManyRequestsError` (Code: 4290).
- Nếu User cạn lượt/hết hạn gói VIP, trả về lỗi `PaymentRequiredError` (Code: 4020).

---

## 7. Git & Development Workflow

1. **Quy tắc đọc tài liệu:** Bất cứ khi nào tạo API mới, AI Agent phải cập nhật vào `docs/api/openapi.yaml` **TRƯỚC**, sau đó mới tiến hành viết code Backend/Frontend.
2. **Quy tắc định dạng Git Commit:** `<type>(<scope>): <description>` (Ví dụ: `feat(ai-chat): implement SSE streaming for Qwen model`).
3. **Mọi dữ liệu nhạy cảm (User Data):** Bắt buộc phải triển khai cơ chế **Soft Delete** (`deleted_at`). Không dùng lệnh `DELETE` thẳng vào CSDL.

*Phiên bản tài liệu: 1.0.0 (Áp dụng từ Giai đoạn Implementation)*
