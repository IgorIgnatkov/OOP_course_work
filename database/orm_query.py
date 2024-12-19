from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Payment


async def orm_add_user(session: AsyncSession, data: dict):
    for user in await orm_get_users(session):
        if user.user_id == data["user_id"]:
            return
    obj = User(
        name=data["name"],
        user_id=data["user_id"],
        last_name=(data["last_name"]),
        phone_number=data["phone_number"],
        private_id=data["private_id"],
    )
    session.add(obj)
    await session.commit()


async def orm_get_payment_data(session: AsyncSession, user_id: int):
    user = await orm_get_user(session, user_id)
    user_private_id = user.private_id

    for payment in await orm_get_payments(session):
        payment_private_id = payment.private_id
        if user_private_id == payment_private_id:
            payment_data = {
                "payment_amount": payment.payment_amount,
                "payment_private_id": payment.private_id,
            }
            return payment_data

    return None


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    user = await session.execute(query)
    return user.scalar_one_or_none()


async def orm_get_payments(session: AsyncSession):
    query = select(Payment)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_update_payment(session: AsyncSession, private_id: int):
    query = update(Payment).where(Payment.private_id == private_id).values(
        payment_amount = 0,
    )

    await session.execute(query)
    await session.commit()

