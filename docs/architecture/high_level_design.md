# KIẾN TRÚC HỆ THỐNG TỔNG THỂ (HIGH-LEVEL SYSTEM ARCHITECTURE)

Tài liệu này mô tả kiến trúc tổng thể của nền tảng **Q-School AI**, bao gồm cách tổ chức các tầng dịch vụ (layers), luồng dữ liệu (data flow) và cơ sở hạ tầng (infrastructure) cần thiết để đáp ứng các yêu cầu nghiệp vụ (Use Cases).

## 1. Mục tiêu kiến trúc (Architectural Goals)
Do Q-School là một hệ thống EdTech có tích hợp Trí tuệ nhân tạo (AI-native), kiến trúc cần đáp ứng các tiêu chí cốt lõi:
- **Xử lý bất đồng bộ (Asynchronous Processing):** Các tác vụ AI như tóm tắt video, sinh giáo án, chấm bài tự luận đòi hỏi thời gian xử lý dài (5 - 30 giây). Hệ thống không được chặn (block) luồng trải nghiệm của người dùng.
- **Tách biệt quan tâm (Separation of Concerns):** Tách biệt dịch vụ lõi (Quản lý User, Lớp học, Dữ liệu truyền thống) với dịch vụ AI (Giao tiếp LLM, xử lý file/RAG).
- **Khả năng mở rộng (Scalability):** Dễ dàng mở rộng số lượng API server hoặc AI Worker độc lập khi lượng học sinh/giáo viên tăng đột biến (đặc biệt trong các kỳ thi).

## 2. Các thành phần chính (System Components)

### 2.1. Client Layer (Lớp người dùng)
- **Web App (Giáo viên & Quản lý):** Giao diện quản trị, tạo bài giảng, theo dõi sổ liên lạc. Xây dựng dưới dạng Single Page Application (SPA).
- **Web/Mobile App (Học sinh):** Giao diện làm bài tập (Quiz), học qua Flashcard, và giao tiếp trực tiếp với AI Tutor (Raina).

### 2.2. API Gateway & Load Balancer
- Điểm tiếp nhận duy nhất cho mọi request từ Client (Reverse Proxy).
- **Chức năng:** Định tuyến request (Routing), Giới hạn tốc độ (Rate Limiting để chống Spam/DDoS), và Xử lý SSL/TLS.

### 2.3. Application Layer (Lớp Xử lý nghiệp vụ)
Hệ thống áp dụng kiến trúc Microservices (ở mức độ tinh gọn), phân chia làm 2 dịch vụ chính:

1. **Core Service (Dịch vụ cốt lõi):**
   - Đảm nhiệm nghiệp vụ truyền thống: Đăng nhập (Auth), Quản lý người dùng, Quản lý lớp học.
   - Xử lý CRUD (Thêm, Đọc, Sửa, Xóa) cho các thực thể như Bài tập, Kế hoạch giáo dục, v.v.

2. **AI & NLP Service (Dịch vụ AI):**
   - Chịu trách nhiệm giao tiếp với Mô hình ngôn ngữ lớn (LLMs).
   - Xử lý tệp tin (Đọc PDF, trích xuất văn bản), xử lý ngôn ngữ tự nhiên (NLP).
   - Quản lý luồng RAG (Retrieval-Augmented Generation) để AI có thể trả lời dựa trên sách giáo khoa/tài liệu được cung cấp.

### 2.4. Message Queue Layer (Hàng đợi tác vụ)
- Cầu nối giao tiếp bất đồng bộ giữa Core Service và AI Service.
- Khi người dùng yêu cầu một tác vụ nặng (VD: Chấm điểm bài luận), Core Service sẽ đẩy yêu cầu vào **Message Queue**. AI Service đóng vai trò là Worker, lấy yêu cầu ra xử lý, sau khi hoàn thành sẽ thông báo lại kết quả.

### 2.5. Data Layer (Lớp Dữ liệu)
- **Relational Database:** Lưu trữ thông tin User, Lớp, Học bạ, Cấu trúc bài tập (Dữ liệu có cấu trúc).
- **Vector Database:** Lưu trữ nhúng (Embeddings) của sách giáo khoa, tài liệu tham khảo để phục vụ tìm kiếm ngữ nghĩa (Semantic Search) cho AI.
- **Cache / Session DB:** Lưu trữ phiên đăng nhập, Token, và Caching kết quả để tăng tốc độ phản hồi.
- **Object Storage:** Chứa các file ảnh, PDF, Word, Video do giáo viên/học sinh tải lên hoặc do AI sinh ra.

### 2.6. External APIs (Tích hợp bên ngoài)
- **LLM Provider:** API của OpenAI/Anthropic hoặc hệ thống suy luận LLM nội bộ (vLLM/Ollama).
- **YouTube API:** Lấy dữ liệu Transcript/Subtitle.
- **Email/SMTP:** Gửi thông báo và mã OTP.

---

## 3. Biểu đồ Kiến trúc (High-Level Architecture Diagram)

```mermaid
flowchart TD
    %% Clients
    ClientWeb[("💻 Web App\n(React/Next/Vue)")]
    ClientMobile[("📱 Mobile App\n(Học sinh)")]

    %% Gateway
    Gateway{"API Gateway\n(Nginx/Traefik)"}

    %% Services
    subgraph AppLayer [Application Layer]
        Core[("⚙️ Core Service\n(Node.js/Python)\nAuth, Users, CRUD")]
        AI_SVC[("🧠 AI & NLP Service\n(Python - FastAPI)\nLLM, RAG, File Proc")]
    end

    %% Queue
    Queue[("📬 Message Queue\n(Redis/RabbitMQ)")]

    %% Databases
    subgraph DataLayer [Data Storage Layer]
        Postgres[(🗄️ Relational DB\n(PostgreSQL/MySQL))]
        Redis[(⚡ Cache\n(Redis))]
        VecDB[(🤖 Vector DB\n(Qdrant/Milvus))]
        S3[(☁️ Object Storage\n(S3/MinIO))]
    end

    %% External
    subgraph External [External Integrations]
        LLM[("LLM APIs\n(OpenAI/Local)")]
        YT[("YouTube API")]
        Mail[("Email SMTP")]
    end

    %% Connections
    ClientWeb & ClientMobile -->|HTTP / WebSocket| Gateway
    Gateway --> Core
    Gateway --> AI_SVC

    Core -->|Sync Request| Postgres
    Core -->|Cache/OTP| Redis
    Core -->|Upload File| S3
    
    %% Async Flow
    Core -->|1. Push Job (Async)| Queue
    Queue -->|2. Pull Job| AI_SVC
    AI_SVC -->|3. Update Status| Core
    Core -.->|4. Push Notification| ClientWeb

    %% AI DB
    AI_SVC -->|Retrieve/Store Docs| S3
    AI_SVC -->|Semantic Search| VecDB
    
    %% External calls
    Core --> Mail
    AI_SVC --> LLM
    AI_SVC --> YT
```

## 4. Các luồng xử lý điển hình (Typical Data Flows)

### 4.1. Luồng xử lý Đồng bộ (Synchronous Flow)
*(Ví dụ: Xem hồ sơ cá nhân - UC-SYS-004)*
1. Client gửi request GET `/profile`.
2. API Gateway định tuyến đến Core Service.
3. Core Service kiểm tra Token trong Cache (Redis).
4. Core Service truy vấn thông tin từ Relational DB và trả về cho Client.

### 4.2. Luồng xử lý Bất đồng bộ (Asynchronous Flow)
*(Ví dụ: Chấm và phản hồi bài viết - UC-FT-008)*
1. Giáo viên upload file bài luận. Core Service lưu file vào **Object Storage (S3)** và lưu bản ghi vào DB với trạng thái `Pending`.
2. Core Service đẩy thông báo vào **Message Queue**: `"Cần chấm bài luận ID 123"`.
3. Client hiển thị thanh tải (Loading/Processing) cho người dùng.
4. **AI Service** lấy Job từ Queue. Tải file từ S3, trích xuất text, gọi **LLM API** để chấm điểm dựa trên tiêu chí (Rubric).
5. Sau 15 giây, AI Service lưu kết quả vào Database, cập nhật trạng thái thành `Done`, đồng thời gọi Webhook/Queue báo cho Core Service.
6. Core Service gửi tín hiệu **WebSocket** thông báo cho Client hiển thị kết quả.

## 5. Cân nhắc kỹ thuật (Technical Considerations)
- **Bảo mật (Security):** Mọi request đi qua API Gateway đều phải được đính kèm JWT (JSON Web Token) hợp lệ. Tài liệu tải lên (S3) cần được cấu hình quyền truy cập nghiêm ngặt.
- **WebSocket:** Cần thiết lập máy chủ WebSocket trên Core Service để cung cấp trải nghiệm real-time khi chat với AI hoặc khi nhận kết quả từ các tác vụ ngầm.
- **RAG System:** Đối với tính năng Trợ lý học tập, văn bản PDF dài cần được chia nhỏ (chunking) và nhúng (embedding) để đưa vào Vector DB, giúp giảm thiểu chi phí token khi gọi LLM.
