import logging
from datetime import datetime, timedelta
from db.database import Database

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

db = Database()

level_points = [0, 1, 3, 5, 8, 12, 18]
text = " Now you can do bla bla bla!"

async def award_exp(user_id, exp_points, message):
    try:
        db.cursor.execute("SELECT points, level FROM exp WHERE user_id = ?", (user_id,))
        result = db.cursor.fetchone()
        if not result:
            logger.warning(f"No experience data found for user {user_id}.")
            return None

        current_points, current_level = result
        new_points = current_points + exp_points

        while new_points >= level_points[current_level] and current_level < len(level_points) - 1:
            current_level += 1

        db.cursor.execute("UPDATE exp SET points = ?, level = ? WHERE user_id = ?", (new_points, current_level, user_id))
        db.connection.commit()

        await message.answer(f"You've earned {exp_points} EXP points! Your current level is {current_level}.")
        
    except Exception as e:
        logger.error(f"Error awarding EXP points: {e}")
        await message.answer("An error occurred while awarding EXP points. Please try again later.")

async def user_level(user_id, message):
    try:
        db.cursor.execute("SELECT points, level FROM exp WHERE user_id = ?", (user_id,))
        result = db.cursor.fetchone()
        if not result:
            logger.warning(f"No experience data found for user {user_id}.")
            return None

        points, current_level = result
        new_level = current_level

        while points >= level_points[new_level] and new_level < len(level_points) - 1:
            new_level += 1

        if new_level > current_level:
            db.cursor.execute("UPDATE exp SET level = ? WHERE user_id = ?", (new_level, user_id))
            db.connection.commit()
            await message.answer(f"Congratulations! You've reached level {new_level}!!!{text}")
        return new_level

    except Exception as e:
        logger.error(f"Error updating user level: {e}")
        await message.answer("An error occurred while updating your level. Please try again later.")
        return None

async def get_points(user_id):
    try:
        db.cursor.execute("SELECT amount FROM profiles WHERE user_id = ?", (user_id,))
        amount = db.cursor.fetchone()
        if not amount:
            logger.warning(f"No profile found for user {user_id}.")
            return None
        amount = amount[0]

        db.cursor.execute("SELECT points FROM exp WHERE user_id = ?", (user_id,))
        points = db.cursor.fetchone()
        if not points:
            logger.warning(f"No experience data found for user {user_id}.")
            return None
        points = points[0]

        db.cursor.execute("SELECT created_at FROM profiles WHERE user_id = ?", (user_id,))
        created_at = db.cursor.fetchone()
        if not created_at:
            logger.warning(f"No creation date found for user {user_id}.")
            return None
        created_at = datetime.strptime(created_at[0], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - created_at) > timedelta(weeks=1):
            points += 5

        db.cursor.execute("UPDATE exp SET points = ? WHERE user_id = ?", (points, user_id))
        db.connection.commit()
        return points
    except Exception as e:
        logger.error(f"Error getting points: {e}")
        return None

def increment_chat_count(user_id):
    try:
        db.cursor.execute("SELECT amount FROM profiles WHERE user_id = ?", (user_id,))
        amount = db.cursor.fetchone()[0]
        amount += 1
        db.cursor.execute("UPDATE profiles SET amount = ? WHERE user_id = ?", (amount, user_id))
        db.connection.commit()
    except Exception as e:
        logger.error(f"Error incrementing chat count: {e}")
