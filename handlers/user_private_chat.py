import time

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession


from database.orm_query import orm_add_user, orm_get_payment_data, orm_update_payment, orm_get_user
from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard

user_private_router = Router()

class Registration(StatesGroup):
    name = State()
    last_name = State()
    phone_number = State()
    private_id = State()


@user_private_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        text="<strong>Добро пожаловать в бота для оплаты ЖКХ услуг!</strong>\n\nВам необходимо пройти регистрацию, чтобы им пользоваться",
        parse_mode=ParseMode.HTML
    )

    time.sleep(3)

    await start_registration_name(message, state)



async def start_registration_name(message: types.Message, state: FSMContext):
    await message.answer(
        text="<strong>Введите ваше имя:</strong>",
        parse_mode=ParseMode.HTML
    )

    await state.set_state(Registration.name)


@user_private_router.message(Registration.name)
async def registration_last_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(
        text="<strong>Введите вашу фамилию:</strong>",
        parse_mode=ParseMode.HTML
    )

    await state.set_state(Registration.last_name)


@user_private_router.message(Registration.last_name)
async def registration_phone_number(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)

    await message.answer(
        text="<strong>Введите номер телефона в формате: +7XXXXXXXXXX</strong>",
        parse_mode=ParseMode.HTML
    )

    await state.set_state(Registration.phone_number)


@user_private_router.message(Registration.phone_number)
async def registration_private_id(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.text)

    await message.answer(
        text="<strong>Введите приватный ключ, который вам выдали наши сотрудники</strong>",
        parse_mode=ParseMode.HTML
    )

    await state.set_state(Registration.private_id)


@user_private_router.message(Registration.private_id)
async def end_registration(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(private_id=int(message.text))
    user_id = message.from_user.id
    user_data = await state.get_data()
    await state.clear()

    user_data["user_id"] = user_id

    await orm_add_user(session, user_data)

    await message.answer(
        text="<strong>Регистрация прошла успешна!</strong>",
        reply_markup=get_keyboard(
            "Оплатить ЖКХ",
            "Личный кабинет",
            "Посмотреть задолженность",
            "Техническая поддержка",
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, )
        ),
        parse_mode=ParseMode.HTML
    )


@user_private_router.message(F.text == "Оплатить ЖКХ")
async def payment(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    payment_data = await orm_get_payment_data(session, user_id)
    payment_amount = payment_data["payment_amount"]
    payment_private_id = payment_data["payment_private_id"]
    if payment_amount == None:
        await message.answer(
            text="У вас нет дома для оплаты ЖКХ, обратитесь в техническую поддержку",
        )
        return

    await message.answer(

        text="Ваш счет на оплату:",
        reply_markup=get_callback_btns(
            btns={f"Оплатить {payment_amount} рублей": f"check_payment_{payment_private_id}"},
            sizes = (1, ),
        )
    )


@user_private_router.callback_query(F.data.startswith("check_payment_"))
async def check_payment(callback: types.CallbackQuery, session: AsyncSession):
    await callback.message.answer(
        text="<strong>Платеж проведен успешно!</strong>",
        parse_mode=ParseMode.HTML
    )

    callback_data = callback.data
    payment_private_id = int(callback_data.split("_")[-1])

    await orm_update_payment(session, payment_private_id)


@user_private_router.message(F.text == "Личный кабинет")
async def user_account(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id

    user = await orm_get_user(session, user_id)

    await message.answer(
        text=(
            f"<strong>Ваши данные:</strong>\n\n"
            f"<strong>Имя:</strong> {user.name}\n"
            f"<strong>Фамилия:</strong> {user.last_name}\n"
            f"<strong>Телефон:</strong> {user.phone_number}\n"
            f"<strong>Приватный ключ:</strong> {user.private_id}\n"
        ),
        parse_mode=ParseMode.HTML
    )


@user_private_router.message(F.text == "Посмотреть задолженность")
async def check_payment_amount(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    payment_data = await orm_get_payment_data(session, user_id)
    payment_amount = payment_data["payment_amount"]

    await message.answer(
        text=f"Ваша задолженность по ЖКХ составляет: <strong>{payment_amount} рублей</strong>",
        parse_mode=ParseMode.HTML
    )


@user_private_router.message(F.text == "Техническая поддержка")
async def tech_info(message: types.Message):
    await message.answer(
        text="При возникновении технических трудностей обратитесь к разработчикам:\n\n<a href='https://github.com/IgorIgnatkov'>Игнатков Игорь</>\n\n<a href='https://github.com/khalikovv'>Халиков Вадим</>",
        parse_mode=ParseMode.HTML
    )
