from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Float, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.config import settings
from app.database import Base

# Bảng trung gian n-n giữa Người dùng và Lớp học
user_class_association = Table(
    'user_class',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('class_id', Integer, ForeignKey('classes.id', ondelete='CASCADE'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, lecturer, student
    email = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    classes = relationship('Class', secondary=user_class_association, back_populates='users')
    submissions = relationship('Submission', back_populates='student')
    audit_logs = relationship('AuditLog', back_populates='user')

class Class(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    semester = Column(String, default="unknown", server_default="unknown", index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    is_blocked = Column(Boolean, default=False, server_default='false', nullable=False)

    # Relationships
    users = relationship('User', secondary=user_class_association, back_populates='classes')
    labs = relationship('Lab', back_populates='class_', cascade='all, delete-orphan')
    posts = relationship('ClassPost', back_populates='class_', cascade='all, delete-orphan', order_by='ClassPost.created_at.desc()')


class Semester(Base):
    __tablename__ = 'semesters'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # e.g. "FA25", "SP26", "SU26"
    is_active = Column(Boolean, default=False, nullable=False)     # True if marked as current active semester
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))


class Lab(Base):
    __tablename__ = 'labs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    grade_tag = Column(String, nullable=True, index=True) # Tag đầu điểm: ví dụ "Đầu điểm 1", "Chuyên cần", "Giữa kỳ", v.v.
    
    # form_fields lưu mảng cấu hình câu hỏi động dạng JSONB
    # [{id: "q1", type: "text"|"textarea"|"select"|"file", label: "...", options: ["...", "..."], required: true}]
    form_fields = Column(JSONB, nullable=False, server_default='[]')
    
    # attachment_files lưu danh sách tài liệu/file đính kèm của bài lab do giảng viên cung cấp
    # [{filename: "guideline.pdf", original_filename: "HuongDan.pdf", filepath: "/app/uploads/...", size_bytes: 12345, uploaded_at: "..."}]
    attachment_files = Column(JSONB, nullable=False, server_default='[]')
    
    deadline = Column(DateTime, nullable=False)
    
    # late_policy lưu cấu hình phạt nộp muộn
    # {allow_late: true, penalty_per_hour_percent: 1.0, max_penalty_percent: 50.0}
    late_policy = Column(JSONB, nullable=False, server_default='{"allow_late": true, "penalty_per_hour_percent": 0.0, "max_penalty_percent": 0.0}')
    
    # individual_extensions lưu danh sách gia hạn cá nhân dạng JSONB: {student_username: new_deadline}
    individual_extensions = Column(JSONB, nullable=True, server_default='{}')
    
    is_active = Column(Boolean, default=True)
    enable_vm = Column(Boolean, default=True, server_default='true', nullable=False)
    # VM Clipboard Isolation: Chặn copy từ trong máy ảo ra ngoài máy thật
    disable_vm_copy = Column(Boolean, default=False, server_default='false', nullable=False)
    # Chặn dán từ máy thật vào trong máy ảo
    disable_vm_paste = Column(Boolean, default=False, server_default='false', nullable=False)
    # Chế độ kiểm tra / thi (Exam Mode)
    is_exam_mode = Column(Boolean, default=False, server_default='false', nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)

    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    class_ = relationship('Class', back_populates='labs')
    created_by = relationship('User')
    submissions = relationship('Submission', back_populates='lab', cascade='all, delete-orphan')
    extension_requests = relationship('ExtensionRequest', back_populates='lab', cascade='all, delete-orphan')

class LabVM(Base):
    """Stable machine definition used in student VM naming and per-machine settings."""
    __tablename__ = 'lab_vms'

    id = Column(Integer, primary_key=True)
    lab_id = Column(Integer, ForeignKey('labs.id'), nullable=False, index=True)
    template_vmid = Column(Integer, nullable=False)
    is_linked_clone = Column(Boolean, nullable=False, default=True, server_default='true')
    cpu_cores = Column(Integer, nullable=True)
    ram_mb = Column(Integer, nullable=True)
    vm_protocol = Column(String, nullable=True)
    vm_port = Column(Integer, nullable=True)
    vm_username = Column(String, nullable=True)
    vm_password = Column(String, nullable=True)
    vm_drive_mode = Column(String, nullable=False, default='default', server_default='default')
    vm_drive_files = Column(JSONB, nullable=False, server_default='[]')

    lab = relationship('Lab', backref='vms')


class Submission(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey('labs.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # answers lưu câu trả lời động dạng JSONB: {q1: "Mã MD5...", q2: "Assembly...", q3: "Tải ảnh..."}
    answers = Column(JSONB, nullable=False, server_default='{}')
    
    # file_attachments lưu danh sách file đính kèm thực tế: [{field_id: "q3", filename: "image.png", filepath: "/app/uploads/..."}]
    file_attachments = Column(JSONB, nullable=False, server_default='[]')
    
    status = Column(String, default='draft')  # draft, submitted, graded, re_submit_requested
    
    score = Column(Float, nullable=True)
    late_penalty = Column(Float, default=0.0)
    comment = Column(String, nullable=True)
    
    submitted_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Chống đạo văn
    is_plagiarized = Column(Boolean, default=False)
    plagiarism_score = Column(Float, default=0.0)  # % trùng lặp
    plagiarism_details = Column(JSONB, nullable=True, server_default='[]')  # chi tiết trùng lặp: {student: "SV A", matched_field: "q2", score: 85.0}

    # Relationships
    lab = relationship('Lab', back_populates='submissions')
    student = relationship('User', back_populates='submissions')

class ExtensionRequest(Base):
    """Yêu cầu mở hạn nộp bài sau deadline của sinh viên gửi tới giảng viên"""
    __tablename__ = 'extension_requests'

    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey('labs.id', ondelete='CASCADE'), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    reason = Column(String, nullable=False)
    status = Column(String, default='pending', nullable=False) # pending, approved, rejected
    granted_deadline = Column(DateTime, nullable=True)
    response_note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    lab = relationship('Lab', back_populates='extension_requests')
    student = relationship('User')


class DirectMessage(Base):
    """Tin nhắn riêng giữa sinh viên và giảng viên"""
    __tablename__ = 'direct_messages'

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now, index=True)

    # Relationships
    sender = relationship('User', foreign_keys=[sender_id])
    recipient = relationship('User', foreign_keys=[recipient_id])


class ClassPost(Base):
    """Bảng tin lớp học (Classroom Stream)"""
    __tablename__ = 'class_posts'

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey('classes.id', ondelete='CASCADE'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    class_ = relationship('Class', back_populates='posts')
    author = relationship('User')
    comments = relationship('ClassComment', back_populates='post', cascade='all, delete-orphan', order_by='ClassComment.created_at.asc()')


class ClassComment(Base):
    """Bình luận trên bài đăng bảng tin lớp học"""
    __tablename__ = 'class_comments'

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('class_posts.id', ondelete='CASCADE'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    post = relationship('ClassPost', back_populates='comments')
    author = relationship('User')


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = Column(String, nullable=False)  # login, create_user, update_score, submit_lab, etc.
    target = Column(String, nullable=True)  # Chi tiết đối tượng bị tác động
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

    # Relationships
    user = relationship('User', back_populates='audit_logs')


class VmToolFile(Base):
    __tablename__ = 'vm_tool_files'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)
    scope = Column(String, nullable=False, default='common', index=True)  # 'common' hoặc 'lecturer_<username>'
    uploaded_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    uploaded_by = relationship('User')
