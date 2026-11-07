from pydantic import BaseModel, Field, computed_field, model_validator, model_serializer
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from app.config import settings

# --- TOKEN & LOGIN SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str
    username: str
    email: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class LoginSchema(BaseModel):
    username: str
    password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None



# --- USER SCHEMAS ---
class UserBase(BaseModel):
    username: str
    full_name: str
    role: str
    email: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- CLASS SCHEMAS ---
class ClassBase(BaseModel):
    name: str
    description: Optional[str] = None
    semester: Optional[str] = "unknown"
    is_blocked: Optional[bool] = False

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    semester: Optional[str] = None
    is_blocked: Optional[bool] = None

class ClassOut(ClassBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ClassWithStudents(ClassOut):
    users: List[UserOut] = []

    class Config:
        from_attributes = True

# --- EXTENSION REQUEST SCHEMAS ---
class ExtensionRequestCreate(BaseModel):
    reason: str

class ExtensionRequestRespond(BaseModel):
    status: Literal["approved", "rejected"]
    granted_deadline: Optional[datetime] = None
    response_note: Optional[str] = None

class ExtensionRequestBatchRespond(BaseModel):
    request_ids: Optional[List[int]] = None # If None or empty, applies to all pending requests in the lab
    status: Literal["approved", "rejected"]
    granted_deadline: Optional[datetime] = None
    response_note: Optional[str] = None

class ExtensionRequestOut(BaseModel):
    id: int
    lab_id: int
    student_id: int
    student: Optional[UserOut] = None
    reason: str
    status: str
    granted_deadline: Optional[datetime] = None
    response_note: Optional[str] = None
    created_at: datetime
    responded_at: Optional[datetime] = None

    @computed_field
    @property
    def student_username(self) -> Optional[str]:
        return self.student.username if self.student else None

    @computed_field
    @property
    def student_name(self) -> Optional[str]:
        return self.student.full_name if self.student else None

    class Config:
        from_attributes = True

# --- DIRECT MESSAGE SCHEMAS ---
class DirectMessageCreate(BaseModel):
    recipient_id: int
    content: str

class DirectMessageOut(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    is_read: bool
    created_at: datetime
    sender: Optional[UserOut] = None
    recipient: Optional[UserOut] = None

    class Config:
        from_attributes = True

# --- CLASS POST & COMMENT SCHEMAS ---
class ClassCommentCreate(BaseModel):
    content: str

class ClassCommentOut(BaseModel):
    id: int
    post_id: int
    author_id: int
    author: Optional[UserOut] = None
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ClassPostCreate(BaseModel):
    content: str

class ClassPostOut(BaseModel):
    id: int
    class_id: int
    author_id: int
    author: Optional[UserOut] = None
    content: str
    created_at: datetime
    comments: List[ClassCommentOut] = []

    class Config:
        from_attributes = True

# --- SEMESTER SCHEMAS ---
class SemesterBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = False

class SemesterCreate(SemesterBase):
    pass

class SemesterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class SemesterOut(SemesterBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- LAB SCHEMAS ---
class LabVMEditable(BaseModel):
    cpu_cores: Optional[int] = None
    ram_mb: Optional[int] = None
    vm_protocol: Optional[Literal["rdp", "vnc", "ssh"]] = None
    vm_port: Optional[int] = Field(default=None, ge=1, le=65535)
    vm_username: Optional[str] = None
    vm_drive_mode: Optional[Literal["default", "custom"]] = "default"
    vm_drive_files: Optional[List[str]] = Field(default_factory=list)

class LabVMCreate(LabVMEditable):
    template_vmid: int
    is_linked_clone: Optional[bool] = True
    vm_protocol: Literal["rdp", "vnc", "ssh"] = settings.DEFAULT_VM_PROTOCOL
    vm_port: int = Field(default=settings.DEFAULT_VM_PORT, ge=1, le=65535)
    vm_password: Optional[str] = Field(default=None, min_length=1)

class LabVMUpdate(LabVMEditable):
    id: int
    vm_password: Optional[str] = Field(default=None, min_length=1)

    class Config:
        extra = "forbid"

class LabVMOut(LabVMEditable):
    id: int
    template_vmid: int
    is_linked_clone: bool

    class Config:
        from_attributes = True

class LabBase(BaseModel):
    title: str
    description: Optional[str] = None
    grade_tag: Optional[str] = None
    form_fields: List[Dict[str, Any]] = []
    attachment_files: Optional[List[Dict[str, Any]]] = []
    deadline: datetime
    late_policy: Dict[str, Any] = {
        "allow_late": True,
        "penalty_per_hour_percent": 0.0,
        "max_penalty_percent": 0.0
    }
    individual_extensions: Optional[Dict[str, str]] = {}
    is_active: Optional[bool] = True
    enable_vm: Optional[bool] = True
    disable_vm_copy: Optional[bool] = False
    disable_vm_paste: Optional[bool] = False
    is_exam_mode: Optional[bool] = False
    template_vmid: Optional[int] = settings.DEFAULT_TEMPLATE_VMID
    is_linked_clone: Optional[bool] = True
    vm_protocol: Literal["rdp", "vnc", "ssh"] = settings.DEFAULT_VM_PROTOCOL
    vm_port: int = Field(default=settings.DEFAULT_VM_PORT, ge=1, le=65535)
    vm_username: Optional[str] = None
    vm_drive_mode: Optional[Literal["default", "custom"]] = "default"
    vm_drive_files: Optional[List[str]] = []
    cpu_cores: Optional[int] = None
    ram_mb: Optional[int] = None
    vms: List[LabVMCreate] = Field(default_factory=list)
    class_id: int

class LabCreate(LabBase):
    vm_password: Optional[str] = Field(default=None, min_length=1)

class LabUpdate(BaseModel):
    template_vmid: Optional[int] = None
    is_linked_clone: Optional[bool] = None
    vm_protocol: Optional[Literal["rdp", "vnc", "ssh"]] = None
    vm_port: Optional[int] = Field(default=None, ge=1, le=65535)
    vm_username: Optional[str] = None
    vm_password: Optional[str] = Field(default=None, min_length=1)
    vm_drive_mode: Optional[Literal["default", "custom"]] = None
    vm_drive_files: Optional[List[str]] = None
    cpu_cores: Optional[int] = None
    ram_mb: Optional[int] = None
    vms: Optional[List[LabVMUpdate]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    grade_tag: Optional[str] = None
    form_fields: Optional[List[Dict[str, Any]]] = None
    attachment_files: Optional[List[Dict[str, Any]]] = None
    deadline: Optional[datetime] = None
    late_policy: Optional[Dict[str, Any]] = None
    individual_extensions: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None
    enable_vm: Optional[bool] = None
    disable_vm_copy: Optional[bool] = None
    disable_vm_paste: Optional[bool] = None
    is_exam_mode: Optional[bool] = None
    class_id: Optional[int] = None

class LabClone(BaseModel):
    target_class_id: int
    new_title: Optional[str] = None
    new_deadline: Optional[datetime] = None
    grade_tag: Optional[str] = None


class LabOut(LabBase):
    vms: List[LabVMOut] = Field(default_factory=list)
    id: int
    created_by_id: int
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def read_machine_configuration(cls, value: Any) -> Any:
        """Expose the old flat fields as a view of a single definition, not duplicated DB state."""
        if isinstance(value, dict):
            return value
        result = {column.name: getattr(value, column.name) for column in value.__table__.columns}
        definitions = sorted(value.vms, key=lambda item: item.id)
        result["vms"] = definitions
        if len(definitions) == 1:
            for key in ("template_vmid", "is_linked_clone", "vm_protocol", "vm_port",
                        "vm_username", "vm_drive_mode", "vm_drive_files", "cpu_cores", "ram_mb"):
                result[key] = getattr(definitions[0], key)
        return result

    @model_serializer(mode="wrap")
    def serialize_lab(self, handler: Any) -> Dict[str, Any]:
        """Multiple definitions have no unambiguous legacy scalar configuration."""
        result = handler(self)
        if len(self.vms) > 1:
            for key in ("template_vmid", "is_linked_clone", "vm_protocol", "vm_port",
                        "vm_username", "vm_drive_mode", "vm_drive_files", "cpu_cores", "ram_mb"):
                result.pop(key, None)
        return result

    class Config:
        from_attributes = True

# --- SUBMISSION SCHEMAS ---
class SubmissionBase(BaseModel):
    lab_id: int
    answers: Dict[str, Any] = {}

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionDraft(BaseModel):
    answers: Dict[str, Any] = {}

class SubmissionOut(BaseModel):
    id: int
    lab_id: int
    student_id: int
    student: Optional[UserOut] = None
    answers: Dict[str, Any]
    file_attachments: List[Dict[str, Any]] = []
    status: str
    score: Optional[float] = None
    late_penalty: float
    comment: Optional[str] = None
    submitted_at: Optional[datetime] = None
    updated_at: datetime
    is_plagiarized: bool
    plagiarism_score: float
    plagiarism_details: Optional[List[Dict[str, Any]]] = []

    class Config:
        from_attributes = True

class GradeSubmissionSchema(BaseModel):
    score: float
    comment: Optional[str] = None
    request_resubmit: Optional[bool] = False

# --- AUDIT LOG SCHEMAS ---
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    user: Optional[UserOut] = None
    action: str
    target: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
