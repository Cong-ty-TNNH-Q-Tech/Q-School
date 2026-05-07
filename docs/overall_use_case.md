# Biểu đồ Use-case Tổng Quát (Overall Use-case Diagram)

Dưới đây là biểu đồ mô tả tổng quát các luồng tương tác giữa các Tác nhân (Actors) và Hệ thống (Q-School System), được chia thành 5 nhóm tính năng chính.

```mermaid
flowchart LR
    %% Actors
    Teacher(["🧑‍🏫 Giáo viên"])
    Student(["🎓 Học sinh"])
    Admin(["👔 Quản lý trường học"])

    %% System Boundary
    subgraph QSchool ["Hệ thống Q-School AI"]
        
        subgraph G1 ["Nhóm 1: Soạn giảng & Tạo nội dung"]
            UC3(["UC-FT-003: Tạo bài tập thực hành"])
            UC4(["UC-FT-004: Tạo nội dung học thuật"])
            UC5(["UC-FT-005: Tạo bài kiểm tra trắc nghiệm"])
            UC6(["UC-FT-006: Tạo danh sách từ vựng"])
        end

        subgraph G2 ["Nhóm 2: Đánh giá & Phản hồi"]
            UC7(["UC-FT-007: Tạo thang điểm (Rubric)"])
            UC8(["UC-FT-008: Chấm & phản hồi bài viết"])
            UC9(["UC-FT-009: Nhận xét sổ liên lạc"])
            UC10(["UC-FT-010: Tạo kế hoạch IEP"])
        end

        subgraph G3 ["Nhóm 3: Giao tiếp & Quản lý"]
            UC11(["UC-FT-011: Soạn email chuyên nghiệp"])
            UC12(["UC-FT-012: Điều chỉnh văn phong"])
            UC13(["UC-FT-013: Giải pháp can thiệp hành vi"])
            UC14(["UC-FT-014: Tạo câu hỏi từ YouTube"])
        end

        subgraph G4 ["Nhóm 4: AI Assistant"]
            UC15(["UC-FT-015: Trợ lý sư phạm (Raina)"])
            UC16(["UC-FT-016: Hướng dẫn phương pháp"])
            UC17(["UC-FT-017: Tạo ý tưởng sáng tạo"])
        end

        subgraph G5 ["Nhóm 5: MagicStudent"]
            UC18(["UC-FS-001: Học kèm 1-1 (AI Tutor)"])
            UC19(["UC-FS-002: Ôn tập (Study Bot)"])
            UC20(["UC-FS-003: Chat với nhân vật ảo"])
            UC21(["UC-FS-005: Tạo nội dung sáng tạo"])
            UC22(["UC-FS-006: Hỗ trợ nghiên cứu"])
            UC23(["UC-FS-007: Tự kiểm tra (Quiz Me!)"])
            UC24(["UC-FS-008: Tóm tắt văn bản"])
            UC25(["UC-FS-009: Dịch thuật ngữ liệu"])
        end
    end

    %% Relationships
    Teacher --> G1
    Teacher --> G2
    Teacher --> G3
    Teacher --> G4
    Admin --> G3
    Student --> G5

    style Teacher fill:#f9f,stroke:#333,stroke-width:2px
    style Student fill:#bbf,stroke:#333,stroke-width:2px
    style Admin fill:#bfb,stroke:#333,stroke-width:2px
    style QSchool fill:#f4f4f9,stroke:#666,stroke-width:2px,stroke-dasharray: 5 5
```
