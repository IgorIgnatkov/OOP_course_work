from sqlalchemy import DateTime, String, Text,  func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    user_id: Mapped[int] = mapped_column()
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(12), nullable=True)
    private_id: Mapped[int] = mapped_column()


class House(Base):
    __tablename__ = 'house'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    street: Mapped[str] = mapped_column(String(150), nullable=True)
    number: Mapped[int] = mapped_column()
    flat: Mapped[int] = mapped_column()
    private_id: Mapped[int] = mapped_column()


class Payment(Base):
    __tablename__ = 'payment'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    private_id: Mapped[int] = mapped_column()
    payment_amount: Mapped[int] = mapped_column()
