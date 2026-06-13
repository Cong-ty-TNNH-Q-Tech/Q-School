# BẢN THUYẾT MINH Ý TƯỞNG DỰ ÁN
**Cuộc thi: [Tên cuộc thi của bạn]**

## 1. Tên sản phẩm, dự án
**Q-School Teacher-Centric AI**
*(Nền tảng Trợ lý AI Toàn diện chuyên biệt hỗ trợ nâng cao hiệu suất và nghiệp vụ dành cho Giáo viên)*

## 2. Thông tin đội thi
* **Tên đội:** [Tên đội của bạn]
* **Thành viên:** [Tên thành viên 1 - Role], [Tên thành viên 2 - Role]
* **Đơn vị/Trường:** [Tên trường/công ty]
* **Liên hệ:** [Số điện thoại] - [Email]

---

## 3. Đặt vấn đề và cách giải quyết (25 điểm - Tính phù hợp)

### 3.1. Phân tích Pain-point của Giáo viên (Khách hàng mục tiêu)
Theo báo cáo quốc tế về môi trường dạy học (OECD TALIS) và khảo sát thực tế tại Việt Nam, Giáo viên đang đối mặt với cuộc khủng hoảng "Quá tải hành chính":
1. **Lãng phí thời gian chuyên môn:** Trung bình giáo viên mất **15 - 20 giờ/tuần** cho các công việc "không trực tiếp giảng dạy" như: chấm bài thủ công, thiết kế phiếu bài tập, viết nhận xét cá nhân hóa vào sổ liên lạc cuối kỳ.
2. **Bất cập trong cá nhân hóa:** Lớp học đông (40-50 học sinh), giáo viên không đủ thời gian để thiết kế Rubric (thang điểm) riêng hoặc lập Kế hoạch giáo dục cá nhân (IEP) cho các học sinh đặc biệt.
3. **Áp lực giao tiếp & Tâm lý:** Thiếu công cụ hỗ trợ xử lý khủng hoảng hành vi của học sinh hoặc soạn thảo email chuyên nghiệp gửi phụ huynh/Ban giám hiệu.

### 3.2. Cách giải quyết & Lý do "Vì sao AI?"
* **Giải pháp:** Q-School ra đời như một **"Co-pilot" (Trợ lý đồng hành)**, tự động hóa 80% khối lượng công việc hành chính và hỗ trợ tư vấn học thuật, giúp giáo viên lấy lại thời gian để tập trung vào việc "dạy người".
* **Vì sao AI?** Các phần mềm quản lý trường học (LMS) truyền thống như vnEdu, SMAS chỉ giúp "lưu trữ số liệu". Chỉ có **Generative AI (LLM)** kết hợp **Computer Vision (OCR/Face)** mới có khả năng *tư duy ngôn ngữ*, hiểu ngữ cảnh sư phạm để tự động sinh ra đề thi, đọc hiểu bài văn của học sinh để chấm điểm, và tạo ra những lời nhận xét sổ liên lạc mềm mỏng, mang tính khích lệ.

---

## 4. Thiết kế tổng quan & Tính đổi mới (20 điểm - Tính đổi mới)

### 4.1. Hệ sinh thái tính năng (Core Features) và Tính đổi mới (Ưu thế > 30%)
**Hệ sinh thái 15 tính năng toàn diện thiết kế riêng cho Giáo viên:**
Dự án bao phủ toàn bộ vòng đời giảng dạy của một giáo viên, được chia làm 4 nhóm chính:
1. **Nhóm Soạn giảng & Tạo nội dung:** Tự động tạo bài tập thực hành (Worksheet), soạn nội dung học thuật, tạo bộ câu hỏi trắc nghiệm (Quiz), và trích xuất danh sách từ vựng.
2. **Nhóm Đánh giá & Phản hồi:** Tự động tạo thang điểm đánh giá (Rubric), chấm và phản hồi bài viết của học sinh, tạo lời nhận xét sổ liên lạc cá nhân hóa, và thiết kế Kế hoạch giáo dục cá nhân (IEP).
3. **Nhóm Giao tiếp & Quản lý:** Hỗ trợ soạn email chuyên nghiệp, điều chỉnh văn phong tài liệu, gợi ý giải pháp can thiệp hành vi học sinh, và trích xuất câu hỏi từ video YouTube.
4. **Nhóm Trợ lý AI (AI Assistant):** Chatbot tương tác nghiệp vụ (Raina AI), tham vấn chuyên gia sư phạm ảo (Instructional Coach), và gợi ý ý tưởng hoạt động sáng tạo.

**Tính đổi mới & Khác biệt so với thị trường:**
Khác với việc giáo viên dùng ChatGPT/Gemini chung chung (thường sinh ra nội dung lan man, sai văn phong sư phạm), Q-School khác biệt ở chỗ:
* **Prompt Engineering ngầm định chuẩn sư phạm:** Các tính năng như "Tạo nhận xét" tuân thủ chặt chẽ quy tắc "bánh mì kẹp thịt" (Khen - Góp ý - Khích lệ). Hay tính năng tạo IEP được map đúng chuẩn tâm lý học giáo dục.
* **Tự động hóa luồng làm việc O2O (Offline to Online):** Tích hợp công nghệ OCR, cho phép giáo viên chụp ảnh bài làm trên giấy của học sinh, AI sẽ đọc chữ viết tay và tự động chấm điểm theo Rubric, giải quyết triệt để nỗi đau chấm bài tự luận.

### 4.2. Kiến trúc giải pháp & Tích hợp API VNPT
Dự án kiến trúc theo mô hình Microservices, trong đó khai thác tối đa tài nguyên API từ VNPT:
* **VNPT SmartReader (5.1 OCR & 5.2 Bóc tách thông tin) - *Core Feature*:** 
  * *Ứng dụng:* Giáo viên dùng điện thoại chụp ảnh bài kiểm tra viết tay của học sinh hoặc chụp 1 trang sách giáo khoa. OCR bóc tách nội dung -> Đưa vào LLM để tự động chấm điểm lỗi ngữ pháp (UC-FT-008) hoặc tự động sinh câu hỏi trắc nghiệm (UC-FT-005).
* **VNPT Smartbot (4.2 Hỏi đáp LLM nâng cao):**
  * *Ứng dụng:* Trái tim của hệ thống **Raina AI Chatbot** (UC-FT-015) và **AI Instructional Coach** (UC-FT-016), đóng vai trò chuyên gia tư vấn nghiệp vụ, giải pháp can thiệp hành vi học sinh (UC-FT-013) theo kịch bản sư phạm.
* **VNPT SmartVoice (3.1 Text to Speech & 3.2 Speech to Text):**
  * *Ứng dụng:* Giáo viên ra lệnh bằng giọng nói (STT) để AI tạo đề cương. Hoặc AI dùng giọng đọc bản ngữ (TTS) để phát âm bộ danh sách từ vựng (UC-FT-006) cho giáo viên ngoại ngữ.
* **vnFace (2.1 Nền tảng điểm danh):**
  * *Ứng dụng:* Tự động hóa việc gọi tên đầu giờ thông qua camera lớp học, giảm tải thêm 5-10 phút hành chính mỗi tiết học.
* **VNPT SmartUX (7.1 Thu thập tương tác):** Theo dõi thói quen click chuột của Giáo viên trên dashboard để tối ưu hóa UI/UX liên tục.

---

## 5. Phương hướng triển khai (25 điểm - Tính khả thi)

### 5.1. Nguồn dữ liệu & Tính pháp lý
* Q-School sử dụng các khung chương trình GDPT 2018 (public data) để tinh chỉnh AI. 
* Thay vì dùng server LLM nước ngoài có rủi ro rò rỉ thông tin, việc sử dụng các API nội địa của VNPT giúp hệ thống tuân thủ tuyệt đối **Nghị định 13/2023/NĐ-CP về Bảo vệ dữ liệu cá nhân**, đặc biệt an toàn cho dữ liệu nhạy cảm của trẻ em/học sinh.

### 5.2. Kỹ thuật Build & Deploy
* **Frontend:** React/Next.js (Web Dashboard), React Native (Mobile App cho giáo viên chụp ảnh OCR).
* **Backend:** Python (FastAPI) chuyên xử lý AI pipeline và kết nối API VNPT.
* **Hạ tầng:** Container hóa bằng Docker, deploy trên nền tảng Cloud (có thể triển khai trên VNPT Cloud để nội bộ hóa dữ liệu).

### 5.3. Ước tính chi phí vận hành
* Hạ tầng Server: ~100$/tháng (Giai đoạn đầu).
* Phí API (VNPT OCR, Face, LLM): Tính theo lượt Request (Pay-as-you-go). Khởi điểm dùng gói tài trợ của cuộc thi, tối ưu prompt để giảm token, đảm bảo chi phí/User luôn thấp hơn giá bán.

### 5.4. Lộ trình triển khai (Roadmap GTM - Go To Market)
* **Tháng 1-2 (MVP):** Ra mắt 3 tính năng lõi (Tạo Bài tập, Chấm điểm bằng OCR VNPT SmartReader, Tạo nhận xét).
* **Tháng 3-4 (Testing & Feedback):** Pilot tại 2-3 trường học địa phương/trung tâm tiếng Anh để thu thập SmartUX.
* **Tháng 5-6 (Scale & Commercialize):** Ra mắt bản hoàn thiện, tích hợp vnFace và Trợ lý Raina, mở đăng ký gói cước.

---

## 6. Tác động dự kiến (20 điểm)

### 6.1. Ước tính quy mô thị trường (TAM - SAM - SOM)
* **TAM (Thị trường tổng):** ~1.2 triệu giáo viên các cấp và hơn 10.000 trung tâm giáo dục trên toàn quốc.
* **SAM (Thị trường khả thi):** ~300.000 giáo viên trẻ, các giáo viên trường tư thục quốc tế và các trung tâm ngoại ngữ (nhóm có thu nhập ổn định, sẵn sàng chi trả cho công nghệ).
* **SOM (Mục tiêu 1 năm đầu):** Chiếm lĩnh 10% SAM, tương đương **30.000 người dùng trả phí**, và ký kết B2B với 50 trung tâm giáo dục.

### 6.2. Lợi ích Xã hội & Ưu thế cạnh tranh
* **Xã hội:** Trực tiếp giảm tình trạng *Burnout* (kiệt sức) ở giáo viên. Một giáo viên hạnh phúc và có thời gian rảnh rỗi sẽ mang lại chất lượng giáo dục tốt nhất cho học sinh.
* **Ưu thế cạnh tranh (Moat):** Tốc độ nội địa hóa. Sự kết hợp hoàn hảo giữa công nghệ Nhận diện văn bản (SmartReader) và Xử lý ngôn ngữ (SmartBot) tạo ra rào cản kỹ thuật lớn đối với các startup giáo dục nhỏ lẻ.

### 6.3. Mô hình doanh thu (Business Model)
* **B2C (SaaS cho Giáo viên):** 
  * Gói Freemium: Miễn phí tạo 10 tài liệu/tháng.
  * Gói Pro (~99.000 VNĐ/tháng): Không giới hạn, cấp quyền sử dụng OCR bóc tách bài kiểm tra tự luận, tạo nhận xét không giới hạn.
* **B2B (Giải pháp cho Trường học/Trung tâm):** Tính phí theo năm, gói Enterprise tích hợp hệ thống điểm danh vnFace và quản trị đồng bộ.
