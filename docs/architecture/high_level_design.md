# KIẾN TRÚC HỆ THỐNG TỔNG THỂ (HIGH-LEVEL SYSTEM ARCHITECTURE)

Tài liệu này mô tả kiến trúc tổng thể của nền tảng **Q-School AI**, được thiết kế theo mô hình **Modular Monolith (Nguyên khối theo Module)**. Mô hình này giúp tối ưu hóa chi phí vận hành, dễ dàng triển khai (deploy) cho các team quy mô vừa và nhỏ, nhưng vẫn đảm bảo khả năng xử lý các tác vụ AI phức tạp mà không làm gián đoạn trải nghiệm người dùng.

## 1. Mục tiêu kiến trúc (Architectural Goals)
Do Q-School là một hệ thống EdTech có tích hợp Trí tuệ nhân tạo (AI-native), kiến trúc cần đáp ứng các tiêu chí cốt lõi:
- **Xử lý bất đồng bộ (Asynchronous Processing):** Các tác vụ AI như tóm tắt video, sinh giáo án, chấm bài tự luận đòi hỏi thời gian xử lý dài (5 - 30 giây). Hệ thống sử dụng cơ chế Background Jobs / Queue để không chặn (block) luồng trải nghiệm của người dùng.
- **Tính Module hóa (Modularity):** Dù code chung trong 1 repository (Monolith), các module nghiệp vụ (Auth, Quản lý lớp học) và module AI (giao tiếp LLM) phải được phân tách rõ ràng ở cấp độ thư mục/code để dễ bảo trì.
- **Tối ưu chi phí (Cost-effective):** Giảm thiểu chi phí duy trì hạ tầng nhiều server so với Microservices. Có thể scale toàn bộ app khi cần thiết.

## 2. Các thành phần chính (System Components)

### 2.1. Client Layer (Lớp người dùng)
- **Web App (Giáo viên & Quản lý):** Giao diện quản trị, tạo bài giảng, theo dõi sổ liên lạc. Xây dựng dưới dạng Single Page Application (SPA).
- **Web/Mobile App (Học sinh):** Giao diện làm bài tập (Quiz), học qua Flashcard, và giao tiếp trực tiếp với AI Tutor (Raina).

### 2.2. API Gateway & Load Balancer
- Điểm tiếp nhận duy nhất cho mọi request từ Client (Reverse Proxy).
- **Chức năng:** Định tuyến request (Routing), Giới hạn tốc độ (Rate Limiting để chống Spam/DDoS), và Xử lý SSL/TLS.
- *Tech stack dự kiến:* Nginx / Cloudflare.

### 2.3. Application Layer (Lớp Xử lý nghiệp vụ - Monolithic Backend)
Toàn bộ logic của Q-School được gói gọn trong một Backend Server duy nhất nhưng được chia module rõ rệt:
- **Core Module:** Xử lý Đăng nhập (Auth), Quản lý người dùng, Lớp học, Quản lý CSDL (CRUD) cho các bài tập, câu hỏi, flashcard.
- **AI Integration Module:** Xử lý giao tiếp với các API Trí tuệ nhân tạo (OpenAI/Anthropic), đọc file PDF/OCR, xử lý văn bản và NLP. (Không tự host model nội bộ mà gọi API bên thứ 3 để giảm tải server).
- *Tech stack dự kiến:* Node.js (NestJS / Express) hoặc Python (FastAPI / Django).

### 2.4. Message Queue / Background Workers (Hàng đợi tác vụ)
- Thành phần **bắt buộc phải có** dù là kiến trúc Monolith.
- Khi người dùng gọi một tác vụ AI mất thời gian (Ví dụ: Chấm bài văn), Backend API sẽ ném công việc này vào Hàng đợi (Queue) và trả về phản hồi "Đang xử lý" cho Client ngay lập tức.
- Một Background Worker (chạy song song trong cùng Backend) sẽ lấy công việc ra xử lý ngầm, gọi OpenAI, và sau đó cập nhật kết quả.
- *Tech stack dự kiến:* Redis (BullMQ cho Node.js hoặc Celery cho Python).

### 2.5. Data Layer (Lớp Dữ liệu)
- **Relational Database:** Lưu trữ thông tin User, Lớp, Học bạ, Cấu trúc bài tập (Dữ liệu có cấu trúc). -> *PostgreSQL / MySQL.*
- **Cache / Session DB:** Lưu trữ phiên đăng nhập, Token, và Caching kết quả để tăng tốc độ phản hồi. -> *Redis.*
- **Vector Database (Tùy chọn):** Lưu trữ nhúng (Embeddings) để AI tra cứu sách giáo khoa (RAG). -> *Qdrant / pgvector.*
- **Object Storage:** Chứa các file ảnh, PDF, Word, Video do giáo viên/học sinh tải lên. -> *S3 / MinIO.*

### 2.6. External APIs (Tích hợp bên ngoài)
- **LLM Provider:** API của OpenAI (GPT-4o), Anthropic (Claude) hoặc Google Gemini.
- **YouTube API:** Lấy dữ liệu Transcript/Subtitle.
- **Email/SMTP:** Gửi thông báo và mã OTP.

---

## 3. Biểu đồ Kiến trúc (Modular Monolith Architecture Diagram)

```mermaid
flowchart TD
    %% Clients
    ClientWeb[("💻 Web App\n(SPA)")]
    ClientMobile[("📱 Mobile App\n(Học sinh)")]

    %% Gateway
    Gateway{"API Gateway\n(Nginx)"}

    %% Backend Monolith
    subgraph AppLayer [Monolithic Backend Service]
        direction TB
        API[("⚙️ API Endpoints\n(Auth, CRUD, Routing)")]
        Worker[("🛠️ Background Worker\n(Xử lý AI ngầm)")]
        
        API -.->|Push Job| Worker
        Worker -.->|Update Status| API
    end

    %% Queue
    Queue[("📬 Message Queue\n(Redis)")]:

    %% Databases
    subgraph DataLayer [Data Storage Layer]
        Postgres[(🗄️ Relational DB\n(PostgreSQL))]
        RedisCache[(⚡ Cache/Session\n(Redis))]
        VecDB[(🤖 Vector DB\n(Tùy chọn))]
        S3[(☁️ Object Storage\n(S3/MinIO))]
    end

    %% External
    subgraph External [External Integrations]
        LLM[("LLM APIs\n(OpenAI/Anthropic)")]
        YT[("YouTube API")]
        Mail[("Email SMTP")]
    end

    %% Connections
    ClientWeb & ClientMobile -->|HTTP / WebSocket| Gateway
    Gateway --> API

    API -->|Sync Request| Postgres
    API -->|Cache/OTP| RedisCache
    API -->|Upload File| S3
    
    %% Async Flow via Queue
    API -->|1. Ném Job| Queue
    Queue -->|2. Nhận Job| Worker
    Worker -->|Lưu kết quả| Postgres
    API -.->|WebSocket / Polling| ClientWeb

    %% AI DB
    Worker -->|Đọc file| S3
    Worker -->|Tra cứu tài liệu| VecDB
    
    %% External calls
    API --> Mail
    Worker --> LLM
    Worker --> YT
```

## 4. Các luồng xử lý điển hình (Typical Data Flows)

### 4.1. Luồng xử lý Đồng bộ (Synchronous Flow)
*(Ví dụ: Xem danh sách học sinh - UC-SYS-004)*
1. Client gửi request GET `/students`.
2. API Gateway định tuyến đến Backend API.
3. Backend kiểm tra Token (JWT) và quyền hạn (RBAC).
4. Backend truy vấn CSDL (PostgreSQL) và trả về danh sách dạng JSON cho Client ngay lập tức (<200ms).

### 4.2. Luồng xử lý Bất đồng bộ qua Worker (Asynchronous Flow)
*(Ví dụ: Nhờ AI sinh giáo án - UC-FT-001)*
1. Giáo viên nhấn nút "Tạo giáo án". Client gửi request POST `/lessons/generate` chứa thông tin môn học.
2. Backend API lưu một bản ghi "Giáo án Nháp" vào DB với trạng thái `Processing`.
3. Backend API đẩy thông điệp "Cần sinh giáo án ID X" vào **Message Queue (Redis)** và lập tức trả về cho Client HTTP 202 Accepted.
4. Client hiển thị giao diện Loading.
5. **Background Worker** chạy ngầm (trong cùng codebase Backend) lấy thông điệp từ Queue. Worker gọi **OpenAI API** để sinh giáo án.
6. Sau khoảng 10 giây OpenAI trả kết quả, Worker lưu nội dung giáo án vào DB, đổi trạng thái thành `Completed`.
7. Backend gửi tín hiệu qua **WebSocket** (hoặc Client gọi API kiểm tra định kỳ - Long Polling) để báo Client cập nhật giao diện hiển thị giáo án.
