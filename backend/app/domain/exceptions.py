"""
Domain Exceptions — Lỗi nghiệp vụ thuần túy, không phụ thuộc Framework.
Các Use Case raise những exception này; Router sẽ map sang HTTP exceptions.
"""


class DomainException(Exception):
    """Base exception cho tầng Domain."""
    pass


# ──────────────────────────────────────────────
# Auth / User
# ──────────────────────────────────────────────
class UserAlreadyExistsError(DomainException):
    """Email hoặc username đã được sử dụng."""
    pass


class InvalidCredentialsError(DomainException):
    """Sai mật khẩu hoặc email không tồn tại."""
    pass


class UserNotFoundError(DomainException):
    """Không tìm thấy người dùng."""
    pass


class InactiveUserError(DomainException):
    """Tài khoản bị vô hiệu hóa."""
    pass


# ──────────────────────────────────────────────
# Class / Enrollment
# ──────────────────────────────────────────────
class ClassNotFoundError(DomainException):
    """Không tìm thấy lớp học."""
    pass


class StudentAlreadyEnrolledError(DomainException):
    """Học sinh đã tham gia lớp học này."""
    pass


class NotEnrolledError(DomainException):
    """Học sinh chưa tham gia lớp học."""
    pass


# ──────────────────────────────────────────────
# Content (Lesson / Quiz / Rubric)
# ──────────────────────────────────────────────
class LessonNotFoundError(DomainException):
    """Không tìm thấy bài giảng."""
    pass


class QuizNotFoundError(DomainException):
    """Không tìm thấy bài kiểm tra."""
    pass


class QuizAttemptNotFoundError(DomainException):
    """Không tìm thấy lượt làm bài."""
    pass


class RubricNotFoundError(DomainException):
    """Không tìm thấy rubric."""
    pass


# ──────────────────────────────────────────────
# AI / Billing
# ──────────────────────────────────────────────
class AIQuotaExceededError(DomainException):
    """Người dùng đã hết lượt sử dụng AI trong ngày."""
    pass


class SubscriptionExpiredError(DomainException):
    """Gói cước đã hết hạn."""
    pass


class DocumentNotFoundError(DomainException):
    """Không tìm thấy tài liệu."""
    pass


class DocumentNotReadyError(DomainException):
    """Tài liệu chưa được xử lý xong (đang parsing)."""
    pass
