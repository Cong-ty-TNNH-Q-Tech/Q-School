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


class PermissionDeniedError(DomainException):
    """Không có quyền thực hiện thao tác này (domain-level authorization)."""

    pass


class InvalidRoleError(DomainException):
    """
    User tồn tại nhưng không có role phù hợp với thao tác.
    VD: Enroll một teacher vào lớp với tư cách 'student'.

    Security note: Router map exception này sang 404 (không phải 422/403)
    để không lộ thông tin user tồn tại nhưng sai role (security by obscurity).
    """

    pass


# ──────────────────────────────────────────────
# Content (Lesson / Quiz)
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


# ──────────────────────────────────────────────
# Generated Assets
# ──────────────────────────────────────────────
class AssetNotFoundError(DomainException):
    """Không tìm thấy generated asset."""

    pass


class AssetValidationError(DomainException):
    """Tham số asset hoặc loại asset không hợp lệ."""

    pass

