from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )


class CreateTimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class UpdateTimestampMixin:
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )
