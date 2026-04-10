from sqlalchemy import BigInteger, DateTime, Text, func, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.core.database import Base
import enum



class TaskStatus(enum.Enum):
    
    open = 'open'
    in_progress = 'in_progress'
    done = 'done'
    cancelled = 'cancelled'

class Task(Base):

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, default=TaskStatus.open)
    is_family_task: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[int] = mapped_column(
        BigInteger,
       
        ForeignKey("users.id"),
        nullable=False,
        ) 
    
    assigned_to: Mapped[int | None] = mapped_column(
        BigInteger,
       
        ForeignKey("users.id"),
        nullable=True,
        )

    family_id: Mapped[int | None] = mapped_column(
        BigInteger,
       
        ForeignKey("families.id"),
        nullable=True,
        )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )


