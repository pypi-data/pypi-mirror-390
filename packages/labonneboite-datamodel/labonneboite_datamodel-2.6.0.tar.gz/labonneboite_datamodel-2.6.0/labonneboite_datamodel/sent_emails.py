from typing import Optional
from datetime import datetime
from .base import BaseMixin
from sqlmodel import Field

class SentEmails(BaseMixin, table=True):
    """
    Table for logging all emails sent by the dispatcher.

    Attributes:
        id: Primary key autoincrement
        date_created: inherited from BaseMixin
        last_modified: inherited from BaseMixin
        external_id: Identifier of the email in the dispatcher
        template_id: Template name or id used for the email
        application_id: Linked application (optional)
        user_id: Linked user (optional)
        document_id: Linked document (optional)
        status: Status of the sending process (default=pending)
        error_message: Error details (optional if sending failed)
        attempt_count: attempts count default 0 
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(nullable=False, index=True)
    template_id: str = Field(nullable=False)
    application_id: Optional[int] = Field(default=None, nullable=True)
    user_id: Optional[int] = Field(default=None, nullable=True)
    document_id: Optional[int] = Field(default=None, nullable=True)
    status: str = Field(default="pending", nullable=False)
    error_message: Optional[str] = Field(default=None, nullable=True)
    attempt_count: int = Field(default=0, nullable=False)