---
name: PR Deep Review
description: Review Pull Request chuyên sâu qua 10 vòng kiểm tra (Tích hợp Auto-context, Backward Compatibility & Github Action)
---

# PR Deep Review Workflow (/pr-deep-review)

Workflow này hướng dẫn AI đóng vai trò là một Senior/Staff Engineer để thực hiện review Pull Request cực kỳ khắt khe, kết hợp tự động hóa và phân tích sâu, đảm bảo code đạt tiêu chuẩn production.

## Cách sử dụng
Sử dụng slash command sau trên chat:
`/pr-deep-review <pr_number_or_url>` 
(Ví dụ: `/pr-deep-review 235`)

## Các bước thực hiện
Khi nhận được yêu cầu review, AI BẮT BUỘC phải thực hiện tuần tự các bước sau:

### Giai đoạn 1: Chuẩn bị & Thu thập bối cảnh (Pre-check & Context)
1. **Auto-discovery Context:** Tự động tìm và đọc lướt các file cấu hình dự án (như `AGENTS.md`, `CLAUDE.md`, `openapi.yaml`, hoặc thư mục `docs/`) để nạp các quy tắc riêng của dự án.
2. **Thu thập dữ liệu PR:** Đọc nội dung diff của PR (Sử dụng `gh pr view` và `gh pr diff` qua terminal, hoặc đọc từ codebase).
3. **Automated Verification (Nếu có thể):** Chủ động chạy các lệnh test/linter nhanh (vd: `npm run lint`, `pytest`, `cargo check`) để đảm bảo PR không bị lỗi syntax/build cơ bản trước khi review logic.
4. **Chiến lược Chunking (Cho PR lớn):** Nếu PR có >15 files, AI PHẢI chia nhỏ thành nhiều đợt review theo module/domain để tránh mất bối cảnh (hallucination).

### Giai đoạn 2: Tiến hành 10 Vòng Review Nội Bộ (10-Round Deep Scan)
Sử dụng tư duy tuần tự (sequential thinking) để soi xét PR qua 10 khía cạnh:

- **Vòng 1 - Metadata & Issue Link:** PR đã link Issue chưa? Tên commit/PR có đúng chuẩn semantic không?
- **Vòng 2 - Documentation Match:** API, Schema, hoặc Database thay đổi có khớp hoàn toàn với tài liệu hệ thống (openapi, ERD) không? Có tự ý thêm bớt field không?
- **Vòng 3 - Project Rules & Architecture:** Code có phá vỡ cấu trúc (Hexagonal, MVC, Clean Architecture) và tuân thủ chặt chẽ `AGENTS.md` không?
- **Vòng 4 - SOLID & Design Patterns:** Có vi phạm SRP, OCP, LSP, ISP, DIP không? Code có bị thắt nút (tight coupling) hay lạm dụng if/else không?
- **Vòng 5 - Logical Correctness & Edge Cases:** Luồng chính chạy đúng không? Đã bẫy lỗi (try-catch, null, empty, timeout, concurrency) triệt để chưa?
- **Vòng 6 - Performance & Scalability:** Có vòng lặp thừa, N+1 Query trong DB, hoặc nguy cơ rò rỉ bộ nhớ (memory leak) không? Dữ liệu lớn đã dùng pagination chưa?
- **Vòng 7 - Security & Auth:** Đầu vào (input) đã được sanitize chưa? Có nguy cơ SQLi, XSS, lộ API Key không? Logic phân quyền có chặt chẽ không?
- **Vòng 8 - Backward Compatibility (Rất Quan Trọng):** Những thay đổi này có vô tình làm sập Frontend cũ, Mobile App, hoặc xóa mất field/column đang được client sử dụng không?
- **Vòng 9 - Best Practices & Clean Code:** Đặt tên có dễ hiểu không? Có hardcode (magic numbers/strings) không? Ghi log (logging) có chuẩn mực không?
- **Vòng 10 - Testing & Coverage:** PR có kèm Unit Test / Integration Test cho luồng mới không? Test có thực sự kiểm chứng logic không?

### Giai đoạn 3: Tổng hợp & Hành động (Action)
BẮT BUỘC KHÔNG ĐƯỢC output kết quả review dông dài ra chat của user. Thay vào đó, AI PHẢI tổng hợp nội dung và SỬ DỤNG `gh cli` ĐỂ SUBMIT REVIEW TRỰC TIẾP LÊN GITHUB thông qua tool chạy lệnh terminal (`run_command`).

- ❌ **REQUEST CHANGES (Nếu phát hiện vấn đề):**
  - Bước 1: Trình bày chi tiết review (liệt kê lỗi từng file, nguyên nhân vi phạm, code đề xuất) và lưu vào một file text/markdown tạm thời (ví dụ: `pr_review_msg.txt`).
  - Bước 2: Chạy lệnh terminal: `gh pr review <pr_number> --request-changes --body-file pr_review_msg.txt`
  - Bước 3: Sau khi Submit xong, báo cáo thật ngắn gọn vào chat của user: *"Đã submit Request Changes trực tiếp lên Github cho PR #<pr_number>."*

- ✅ **APPROVE (Nếu code hoàn hảo):**
  - Chạy lệnh terminal: `gh pr review <pr_number> --approve --body "LGTM! Code hoàn hảo, đã vượt qua 10 vòng deep review."`
  - Báo cáo thật ngắn gọn vào chat của user: *"Đã Approve PR #<pr_number> trên Github."*

## Tiêu chí tối thượng (Core Directives)
- Review với tâm thế của một Tech Lead khó tính: KHÔNG NHƯỢNG BỘ trước code smell hay convention sai lệch.
- Đặt tính Ổn định (Stability), Tương thích ngược (Backward Compatibility) và Bảo mật (Security) lên hàng đầu.
