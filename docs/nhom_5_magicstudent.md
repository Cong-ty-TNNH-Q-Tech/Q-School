# NHÓM 5: MAGICSTUDENT (CÔNG CỤ DÀNH CHO HỌC SINH)

**Actor (Người dùng):** Học sinh (Student)

## 1. UC-FS-001: Học kèm 1-1 với Gia sư AI (AI Tutor - Raina)
* **Tình huống:** Học sinh gặp bài toán khó khi làm bài tập ở nhà và không có ai hướng dẫn.
* **Mô tả ngắn:** Use-case này cho phép Học sinh hỏi bài Gia sư AI. Hệ thống cung cấp các gợi ý từng bước (scaffolding) để học sinh tự tìm ra đáp án thay vì đưa ra kết quả trực tiếp.
* **Kết quả dự kiến:** AI gợi ý từng bước giải quyết vấn đề (không đưa ngay đáp án) để học sinh tự hiểu bài (Mức an toàn: Cao).
* **Luồng cơ bản:**
  | Hành động của tác nhân | Phản ứng của hệ thống | Dữ liệu |
  | :--- | :--- | :--- |
  | 1. Người dùng (Học sinh) nhập bài toán/câu hỏi cần giải đáp. | 2. Hệ thống nhận diện bài toán và xác định hướng dẫn giải. | - Đề bài* |
  | 3. Người dùng yêu cầu giải đáp. | 4. Hệ thống đặt câu hỏi gợi mở hoặc đưa ra bước giải thích đầu tiên. | - Lời gợi ý |
  | 5. Người dùng nhập câu trả lời cho bước gợi ý. | 6. Hệ thống xác nhận đúng/sai và điều hướng đến bước tiếp theo cho đến khi ra kết quả cuối. | - Tương tác của học sinh |
* **Luồng ngoại lệ:** Phát hiện câu hỏi vi phạm: Nếu học sinh hỏi các nội dung nguy hiểm, bạo lực, hệ thống từ chối trả lời và cảnh báo (Mức an toàn: Cao).
* **Yêu cầu đặc biệt:** Tránh cung cấp đáp án ngay lập tức. Tính năng này được cài đặt mức độ kiểm duyệt an toàn (Safety Level) ở mức Cao.
* **Tiền điều kiện:** Học sinh có tài khoản và đã đăng nhập vào phân hệ MagicStudent.
* **Điều kiện sau:** Học sinh hiểu được cách giải quyết vấn đề của bài học.
* **Điểm mở rộng:** Không có.

## 2. UC-FS-002: Hỗ trợ ôn tập học tập (Study Bot)
* **Tình huống:** Sắp tới kỳ thi, học sinh cần hệ thống lại toàn bộ kiến thức một chương học.
* **Mô tả ngắn:** Trợ lý ảo giúp học sinh lên lịch trình ôn thi, tóm tắt chương học và tạo flashcard ôn tập.
* **Kết quả dự kiến:** Lộ trình ôn tập và các thẻ ghi nhớ (flashcards) được tạo tự động.
* **Luồng cơ bản:**
  | Hành động của tác nhân | Phản ứng của hệ thống | Dữ liệu |
  | :--- | :--- | :--- |
  | 1. Người dùng cung cấp tài liệu bài học hoặc chủ đề cần ôn thi. | 2. Hệ thống phân tích dung lượng kiến thức và phân chia logic. | - Tài liệu/Chủ đề* |
  | 3. Người dùng yêu cầu hỗ trợ ôn tập. | 4. Hệ thống đề xuất lộ trình và tạo bộ thẻ ghi nhớ (Flashcard) tự động. | - Lộ trình & Flashcard |
  | 5. Người dùng tương tác học với Flashcard. | 6. Hệ thống lật thẻ đáp án và ghi nhận tiến độ học của người dùng. | - Thao tác lật thẻ |
* **Luồng ngoại lệ:** Không có.
* **Yêu cầu đặc biệt:** Đảm bảo độ chính xác của kiến thức chuyên môn (High Safety Level).
* **Tiền điều kiện:** Đăng nhập với vai trò Học sinh.
* **Điều kiện sau:** Học sinh có công cụ để học thuộc lòng kiến thức.
* **Điểm mở rộng:** Không có.

## 3. UC-FS-003: Chat với nhân vật lịch sử/văn học (Character Chatbot)
* **Tình huống:** Học sinh cần làm bài thu hoạch môn Lịch sử hoặc Văn học và muốn tìm hiểu góc nhìn của nhân vật.
* **Mô tả ngắn:** Học sinh tương tác dưới dạng nhập vai (Role-play) với một nhân vật ảo (Albert Einstein, Thạch Sanh...) để tìm hiểu kiến thức sinh động.
* **Kết quả dự kiến:** Cuộc trò chuyện nhập vai (role-play) với một nhân vật lịch sử/văn học (Mức an toàn: Trung bình, cần giám sát nội dung nhập vai).
* **Luồng cơ bản:**
  | Hành động của tác nhân | Phản ứng của hệ thống | Dữ liệu |
  | :--- | :--- | :--- |
  | 1. Người dùng chọn nhân vật từ danh sách hoặc nhập tên nhân vật. | 2. Hệ thống tải "System Prompt" (tính cách, kiến thức) của nhân vật tương ứng. | - Tên nhân vật* |
  | 3. Người dùng đặt câu hỏi trò chuyện. | 4. Hệ thống (AI) đóng vai nhân vật, dùng ngôi thứ nhất để trả lời câu hỏi đúng bối cảnh lịch sử/văn học. | - Câu hỏi của học sinh |
  | 5. Người dùng tiếp tục trò chuyện. | 6. Hệ thống duy trì tính cách nhân vật xuyên suốt phiên chat. | - Phản hồi nhập vai |
* **Luồng ngoại lệ:** Nhập nhân vật không phù hợp/vi phạm chuẩn mực: Hệ thống từ chối khởi tạo nhân vật.
* **Yêu cầu đặc biệt:** Giọng văn phải phản ánh đúng thời đại và tính cách nhân vật (Medium Safety Level: Cần giám sát tránh AI hư cấu sai lệch lịch sử).
* **Tiền điều kiện:** Đăng nhập vai trò Học sinh.
* **Điều kiện sau:** Học sinh hiểu rõ hơn về nhân vật.
* **Điểm mở rộng:** Không có.

## 4. UC-FS-005: Tạo nội dung sáng tạo (Content Creator)
* **Tình huống:** Học sinh cần viết kịch bản cho vở kịch của lớp hoặc lập dàn ý bài thuyết trình.
* **Mô tả ngắn:** Hỗ trợ học sinh phác thảo ý tưởng, dàn ý cho các bài viết sáng tạo như thơ, kịch bản, bài văn biểu cảm.
* **Kết quả dự kiến:** Dàn ý chi tiết hoặc bản nháp nội dung sáng tạo.
* **Luồng cơ bản:**
  | Hành động của tác nhân | Phản ứng của hệ thống | Dữ liệu |
  | :--- | :--- | :--- |
  | 1. Người dùng nhập thể loại (Thơ/Kịch...) và chủ đề mong muốn. | 2. Hệ thống phân tích cấu trúc của thể loại văn học tương ứng. | - Thể loại*<br>- Chủ đề* |
  | 3. Người dùng yêu cầu tạo dàn ý. | 4. Hệ thống đưa ra cấu trúc bài viết (Mở, Thân, Kết) và các ý tưởng gợi ý (Không viết hộ toàn bài). | - Dàn ý/Gợi ý |
  | 5. Người dùng phát triển bài viết từ dàn ý. | 6. Hệ thống có thể góp ý chỉnh sửa trên bài viết của học sinh. | - Bản nháp của học sinh |
* **Luồng ngoại lệ:** Không có.
* **Yêu cầu đặc biệt:** Không viết thay học sinh 100% để chống gian lận học thuật (High Safety Level).
* **Tiền điều kiện:** Đăng nhập vai trò Học sinh.
* **Điều kiện sau:** Học sinh có khung sườn để tự làm bài.
* **Điểm mở rộng:** Không có.

## 5. UC-FS-006: Hỗ trợ nghiên cứu (Research Assistant)
* **Tình huống:** Học sinh làm tiểu luận và cần tìm các số liệu, sự kiện lịch sử đáng tin cậy.
* **Mô tả ngắn:** Giúp học sinh tìm kiếm số liệu, sự kiện có thật để phục vụ cho các bài tiểu luận, báo cáo.
* **Kết quả dự kiến:** Các thông tin được tổng hợp, trích dẫn rõ ràng, hỗ trợ việc nghiên cứu.
* **Luồng cơ bản:**
  | Hành động của tác nhân | Phản ứng của hệ thống | Dữ liệu |
  | :--- | :--- | :--- |
  | 1. Người dùng nhập câu hỏi nghiên cứu hoặc từ khóa khoa học. | 2. Hệ thống tra cứu cơ sở dữ liệu học thuật. | - Từ khóa nghiên cứu* |
  | 3. Người dùng yêu cầu tổng hợp thông tin. | 4. Hệ thống trả về các đoạn thông tin đã tổng hợp kèm theo trích dẫn/nguồn đáng tin cậy. | - Thông tin & Nguồn |
  | 5. Người dùng lưu thông tin. | 6. Hệ thống xuất file dạng danh mục tài liệu tham khảo. | - Tệp kết quả |
* **Luồng ngoại lệ:** Yêu cầu thông tin quá mới hoặc không có nguồn xác thực: Hệ thống thông báo không thể cung cấp dữ liệu chính xác.
* **Yêu cầu đặc biệt:** Thông tin đưa ra bắt buộc phải có fact-check, không hallucination (High Safety Level).
* **Tiền điều kiện:** Đăng nhập vai trò Học sinh.
* **Điều kiện sau:** Học sinh thu thập đủ dữ liệu làm bài.
* **Điểm mở rộng:** Không có.

## 6. UC-FS-007: Tự kiểm tra kiến thức (Quiz Me!)
* **Tình huống:** Học sinh học xong bài và muốn tự test xem mình đã nhớ bài chưa trước khi gấp sách.
* **Mô tả ngắn:** Học sinh tự tạo các bài test nhỏ để kiểm tra xem mình đã hiểu bài trên lớp chưa.
* **Kết quả dự kiến:** Các câu hỏi trắc nghiệm ngẫu nhiên để đánh giá năng lực bản thân.
* **Luồng cơ bản:**
  | Hành động của tác nhân | Phản ứng của hệ thống | Dữ liệu |
  | :--- | :--- | :--- |
  | 1. Người dùng dán nội dung bài học và chọn "Bắt đầu Quiz". | 2. Hệ thống sinh ngay lập tức 5-10 câu hỏi ngẫu nhiên dạng trắc nghiệm hoặc điền khuyết. | - Nội dung bài* |
  | 3. Người dùng chọn đáp án cho từng câu. | 4. Hệ thống đối chiếu kết quả và báo đúng/sai lập tức sau mỗi câu. | - Lựa chọn của người dùng |
  | 5. Người dùng nộp bài (Submit). | 6. Hệ thống hiển thị điểm tổng và giải thích chi tiết các câu sai. | - Bảng điểm, Giải thích |
* **Luồng ngoại lệ:** Không có.
* **Yêu cầu đặc biệt:** Giải thích phải dễ hiểu, giúp học sinh nhận ra lỗi sai (High Safety Level).
* **Tiền điều kiện:** Đăng nhập vai trò Học sinh.
* **Điều kiện sau:** Nắm được mức độ hiểu bài của bản thân.
* **Điểm mở rộng:** Không có.

## 7. UC-FS-008: Tóm tắt văn bản (Text Summarizer)
* **Tình huống:** Học sinh phải đọc một bài báo khoa học dài 10 trang và muốn nắm ý chính trước.
* **Mô tả ngắn:** Rút gọn các bài báo khoa học hoặc tài liệu học tập dài thành các luận điểm chính dễ nhớ.
* **Kết quả dự kiến:** Bản tóm tắt ngắn gọn chứa các luận điểm cốt lõi của bài viết.
* **Luồng cơ bản:**
  | Hành động của tác nhân | Phản ứng của hệ thống | Dữ liệu |
  | :--- | :--- | :--- |
  | 1. Người dùng dán văn bản dài (hoặc upload tệp). | 2. Hệ thống xử lý NLP để nhận diện các câu chủ đề và loại bỏ ý phụ. | - Văn bản gốc/Tệp* |
  | 3. Người dùng chọn độ dài tóm tắt mong muốn (Ngắn/Vừa). | 4. Hệ thống trả về đoạn tóm tắt gạch đầu dòng rõ ràng. | - Mức độ tóm tắt*<br>- Bản tóm tắt |
  | 5. Người dùng copy kết quả. | 6. Hệ thống lưu lịch sử. | - Dữ liệu copy |
* **Luồng ngoại lệ:** Tệp tải lên bị lỗi mã hóa chữ (font error): Hệ thống báo lỗi và yêu cầu dùng văn bản dạng text thô.
* **Yêu cầu đặc biệt:** Không làm thay đổi bản chất sự thật của văn bản gốc (High Safety Level).
* **Tiền điều kiện:** Đăng nhập vai trò Học sinh.
* **Điều kiện sau:** Học sinh đọc xong nội dung cốt lõi nhanh chóng.
* **Điểm mở rộng:** Không có.

## 8. UC-FS-009: Dịch thuật ngữ liệu (Text Translator)
* **Tình huống:** Học sinh cần đọc tài liệu tham khảo bằng tiếng Anh nhưng gặp nhiều từ vựng chuyên ngành khó.
* **Mô tả ngắn:** Dịch ngữ liệu học tập từ ngôn ngữ này sang ngôn ngữ khác, ưu tiên giữ nguyên ngữ cảnh chuyên ngành học thuật.
* **Kết quả dự kiến:** Bản dịch tiếng Việt chuẩn xác, giữ nguyên ngữ cảnh học thuật.
* **Luồng cơ bản:**
  | Hành động của tác nhân | Phản ứng của hệ thống | Dữ liệu |
  | :--- | :--- | :--- |
  | 1. Người dùng dán văn bản cần dịch và chọn Ngôn ngữ đích. | 2. Hệ thống nhận diện ngôn ngữ gốc và bối cảnh từ vựng. | - Đoạn văn gốc*<br>- Ngôn ngữ đích* |
  | 3. Người dùng bấm "Dịch". | 4. Hệ thống trả về kết quả dịch thuật, hiển thị song song 2 ngôn ngữ để dễ đối chiếu. | - Bản dịch |
  | 5. Người dùng bôi đen từ khó trong bản dịch. | 6. Hệ thống hiển thị popup giải nghĩa từ đó (nếu được yêu cầu). | - Thao tác tra từ |
* **Luồng ngoại lệ:** Không có.
* **Yêu cầu đặc biệt:** Chất lượng dịch thuật mượt mà, văn phong tự nhiên, đúng thuật ngữ (High Safety Level).
* **Tiền điều kiện:** Đăng nhập vai trò Học sinh.
* **Điều kiện sau:** Học sinh hiểu được tài liệu ngoại ngữ.
* **Điểm mở rộng:** Không có.
