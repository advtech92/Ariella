import aiosqlite


async def check_consent(user_id: int) -> bool:
    async with aiosqlite.connect("ariella.db") as db:
        cursor = await db.execute(
            "SELECT consent FROM user_consent WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        return row and row[0] == 1


async def give_consent(user_id: int):
    async with aiosqlite.connect("ariella.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO user_consent (user_id, consent) VALUES (?, ?)",  # noqa: E501
            (user_id, 1)
        )
        await db.commit()


async def revoke_consent(user_id: int):
    async with aiosqlite.connect("ariella.db") as db:
        await db.execute(
            "DELETE FROM user_consent WHERE user_id = ?",
            (user_id,)
        )
        await db.execute(
            "DELETE FROM user_notes WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()
