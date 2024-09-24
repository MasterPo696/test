import sqlite3
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection:
            self.connection.close()

    def add_queue(self, user_id):
        try:
            self.cursor.execute("INSERT INTO 'queue' (user_id) VALUES (?)", (user_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding user {user_id} to queue: {e}")

    def delete_queue(self, user_id):
        try:
            self.cursor.execute("DELETE FROM 'queue' WHERE user_id = ?", (user_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error deleting user {user_id} from queue: {e}")

    def get_queue(self):
        try:
            queue = self.cursor.execute("SELECT * FROM queue").fetchone()
            if queue:
                logger.debug(f"Queue retrieved: {queue}")
                return queue[1]
            return False
        except sqlite3.Error as e:
            logger.error(f"Error retrieving queue: {e}")
            return False

    def create_chat(self, user_id, partner_id):
        if partner_id != 0:
            try:
                created_time = datetime.now()
                self.cursor.execute(
                    "INSERT INTO 'chat_now' (user_id, partner_id, created_time) VALUES (?, ?, ?)",
                    (user_id, partner_id, created_time)
                )
                # Update last_partner_id for both users
                self.update_last_partner_id(user_id, partner_id)
                self.update_last_partner_id(partner_id, user_id)
                self.connection.commit()
                return True
            except sqlite3.Error as e:
                logger.error(f"Error creating chat: {e}")
                return False

    def get_chat_created_time(self, user_id):
        try:
            time = self.cursor.execute("SELECT created_time FROM 'chat_now' WHERE user_id = ?", (user_id,)).fetchone()
            return time
        except sqlite3.Error as e:
            logger.error(f"Error fetching chat creation time: {e}")
            return False

    def get_chat(self, user_id):
        try:
            chat = self.cursor.execute("SELECT * FROM 'chat_now' WHERE user_id = ? OR partner_id = ?", (user_id, user_id)).fetchone()
            logger.debug(f"Fetched chat for user {user_id}: {chat}")
            if chat:
                return [chat[0], chat[1] if chat[1] != user_id else chat[2]]
            return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching chat: {e}")
            return None

    def delete_chat(self, user_id):
        try:
            self.cursor.execute("DELETE FROM 'chat_now' WHERE user_id = ? OR partner_id = ?", (user_id, user_id))
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error deleting chat for user {user_id}: {e}")

    def create_chat_logs(self, message_count, chat_started, chat_ended, male_friend_id, female_friend_id):
        try:
            self.cursor.execute(
                "INSERT INTO chat_logs (message_count, chat_started, chat_ended, male_friend_id, female_friend_id) VALUES (?, ?, ?, ?, ?)",
                (message_count, chat_started, chat_ended, male_friend_id, female_friend_id)
            )
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error creating chat logs: {e}")

    def chat_exists(self, user_id):
        try:
            result = self.cursor.execute("SELECT partner_id FROM 'chat_now' WHERE user_id = ? OR partner_id = ?", (user_id, user_id))
            # Fetch one result from the database
            chat = result.fetchone()

            # If chat is found, return True, otherwise return False
            return chat is not None

        except sqlite3.Error as e:
            logger.error(f"Error checking chat for user {user_id}: {e}")
            return False

    def add_like(self, user_id):
        try:
            self.cursor.execute("SELECT last_partner_id FROM users WHERE user_id = ?", (user_id,))
            result = self.cursor.fetchone()
            if result:
                last_partner_id = result[0]
                if last_partner_id is not None:
                    self.cursor.execute("UPDATE users SET likes_count = likes_count + 1 WHERE user_id = ?", (last_partner_id,))
                    self.connection.commit()
                    logger.debug(f"Updated likes for user {last_partner_id}")
                else:
                    logger.debug(f"No last_partner_id found for user {user_id}")
            else:
                logger.debug(f"No profile found for user {user_id}")
        except sqlite3.Error as e:
            logger.error(f"Error updating likes for user {user_id}: {e}")

    def add_dislike(self, user_id):
        try:
            self.cursor.execute("SELECT last_partner_id FROM users WHERE user_id = ?", (user_id,))
            result = self.cursor.fetchone()
            if result:
                last_partner_id = result[0]
                if last_partner_id is not None:
                    self.cursor.execute("UPDATE users SET dislikes_count = dislikes_count + 1 WHERE user_id = ?", (last_partner_id,))
                    self.connection.commit()
                    logger.debug(f"Updated dislikes for user {last_partner_id}")
                else:
                    logger.debug(f"No last_partner_id found for user {user_id}")
            else:
                logger.debug(f"No profile found for user {user_id}")
        except sqlite3.Error as e:
            logger.error(f"Error updating dislikes for user {user_id}: {e}")

    def save_report(self, user_id: int, partner_id: int, report_message: str, report_type: int):
        try:
            self.cursor.execute(
                "INSERT INTO reports (user_id, partner_id, description, report_type) VALUES (?, ?, ?, ?)",
                (user_id, partner_id, report_message, report_type)
            )
            self.connection.commit()
            logger.debug("Report saved successfully")
        except sqlite3.Error as e:
            logger.error(f"Error saving report: {e}")

    def user_exists(self, user_id):
        try:
            result = self.cursor.execute("SELECT date_of_creation FROM 'users' WHERE user_id = ?", (user_id,)).fetchone()
            return result is not None
        except sqlite3.Error as e:
            logger.error(f"Error checking if user {user_id} exists: {e}")
            return False

    def create_profile(self, user_id, name, sex, referral_id):
        try:
            
            now = datetime.now()
            self.cursor.execute(
                "INSERT INTO 'users' (user_id, name, likes_count, date_of_creation, dislikes_count, last_partner_id, sex, referral_id) VALUES (?, ?, 0, ?, 0, NULL, ?, ?)",
                (user_id, name, now, sex, referral_id)
            )
            self.cursor.execute("INSERT INTO friends (user_id) VALUES (?)", (user_id, ))
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error creating profile for user {user_id}: {e}")

    def get_gender(self, user_id):
        try:
            chat = self.cursor.execute("SELECT sex FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return chat
        except sqlite3.Error as e:
            logger.error(f"Error fetching gender for user {user_id}: {e}")

    def update_gender(self, user_id, gender):
        try:
            self.cursor.execute("UPDATE users SET sex = ? WHERE user_id = ?", (gender, user_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating gender for user {user_id}: {e}")

    def get_looking_for(self, user_id):
        try:
            looking_for = self.cursor.execute("SELECT interested_in FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return looking_for
        except sqlite3.Error as e:
            logger.error(f"Error getting looking_for for user {user_id}: {e}")

    def update_interested_in(self, user_id, interested_in):
        try:
            self.cursor.execute("UPDATE users SET interested_in = ? WHERE user_id = ?", (interested_in, user_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating interested_in for user {user_id}: {e}")
            return None

    from datetime import datetime
    def get_profile(self, user_id):
        try:
            profile = self.cursor.execute("SELECT * FROM 'users' WHERE user_id = ?", (user_id,)).fetchone()
            logger.debug(f"Fetched profile for user {user_id}: {profile}")
            return profile
        except sqlite3.Error as e:
            logger.error(f"Error fetching profile for user {user_id}: {e}")
            return None

    def update_name(self, name, user_id):
        try:
            self.cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating name for user {user_id}: {e}")
            return None

    def update_last_partner_id(self, user_id, partner_id):
        try:
            self.cursor.execute("UPDATE users SET last_partner_id = ? WHERE user_id = ?", (partner_id, user_id))
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating last_partner_id for user {user_id}: {e}")

    def create_report(self, user_id, partner_id, report_message):
        try:
            self.cursor.execute(
                "INSERT INTO 'reports' (user_id, partner_id, description) VALUES (?, ?, ?)",
                (user_id, partner_id, report_message)
            )
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error creating report by user {user_id} for {partner_id}: {e}")

    def update_referral(self, user_id, referral_id):
        try:
            self.cursor.execute(
                "UPDATE users SET referral_id = ? WHERE user_id = ?",
                (referral_id, user_id)
            )
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating referral by user {user_id} for {referral_id}: {e}")

    def get_level(self, user_id):
        try:
            level_result = self.cursor.execute("SELECT level FROM exp WHERE user_id = ?", (user_id,))
            return level_result.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Error selecting level for user {user_id}: {e}")
            return None

    def get_last_partner(self, user_id):
        try:
            last_partner_id = self.cursor.execute("SELECT last_partner_id FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return last_partner_id
        except sqlite3.Error as e:
            logger.error(f"Error getting last partner for user {user_id}: {e}")

    def get_balance(self, user_id: int) -> float:
        try:
            self.cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0.0
        except sqlite3.Error as e:
            logger.error(f"Error fetching balance for user {user_id}: {e}")
            return 0.0

    def update_balance(self, user_id: int, new_balance: float):
        try:
            self.cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
            self.connection.commit()
            logger.debug(f"Updated balance for user {user_id} to {new_balance}")
        except sqlite3.Error as e:
            logger.error(f"Error updating balance for user {user_id}: {e}")

    def check_wallets(self, user_id):
        try:
            wallet_data = self.cursor.execute("SELECT wallet_address, verif FROM wallets WHERE user_id = ?", (user_id,)).fetchone()
            logger.debug(f"Wallet data for user {user_id}: {wallet_data}")
            return wallet_data
        except sqlite3.Error as e:
            logger.error(f"Error getting wallet data for user {user_id}: {e}")
            return None

    def delete_wallet(self, user_id):
        try:
            self.cursor.execute("DELETE FROM wallets WHERE user_id = ?", (user_id,))
            self.connection.commit()
            logger.debug(f"Wallet data for user {user_id} was deleted!")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting wallet data for user {user_id}: {e}")
            return None

    def getting_random_float(self, user_id):
        try:
            random_amount = self.cursor.execute("SELECT random_int FROM wallets WHERE user_id = ?", (user_id,)).fetchone()
            return random_amount
        except sqlite3.Error as e:
            logger.error(f'Error verifying wallet for user {user_id}: {e}')
            return None

    def saving_wallet(self, user_id, wallet_address, random_int):
        try:
            self.cursor.execute("INSERT INTO wallets (wallet_address, random_int, user_id) VALUES (?, ?, ?)", (wallet_address, random_int, user_id))
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f'Error saving wallet for user {user_id}: {e}')
            return None

    def vacuum_database(self):
        try:
            self.connection.execute("VACUUM")
            logger.debug('Database vacuumed successfully.')
        except sqlite3.Error as e:
            logger.error(f'Error vacuuming database: {e}')

    import sqlite3

    def add_frn(self, user_id, friend_id):
        try:
            # Get the current friends list for the user
            result = self.cursor.execute("SELECT * FROM friends WHERE user_id = ?", (user_id,)).fetchone()
            
            # Check if the user already has friends
            if result:
                # Check for an empty friend slot
                for i in range(1, 6):  # Iterate over friend_1 to friend_5 slots
                    if result[i] is None:  # If the slot is empty, add the friend here
                        self.cursor.execute(f"UPDATE friends SET friend_{i} = ? WHERE user_id = ?", (friend_id, user_id))
                        self.connection.commit()  # Commit changes to the database
                        return True
                # If no empty slot is found, return False (indicating that the user has the maximum number of friends)
                return False
            else:
                # If the user doesn't have an entry in the friends table, create one and add the friend in friend_1
                self.cursor.execute("INSERT INTO friends (user_id, friend_1) VALUES (?, ?)", (user_id, friend_id))
                self.connection.commit()  # Commit changes to the database
                return True
        except sqlite3.Error as e:
            logger.error(f'Error adding friend for {user_id}: {e}')
            return False


    # def add_frn(self, user_id, friend_is):
    def create_frns_list(self, user_id):
        try:
            self.cursor.execute("INSERT INTO friends (user_id) VALUE (?)", (user_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            return False
    
    def update_balance(self, user_id: int, new_balance: float):
        try:
            self.cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
            self.connection.commit()
            logger.debug(f"Updated balance for user {user_id} to {new_balance}")
        except sqlite3.Error as e:
            logger.error(f"Error updating balance for user {user_id}: {e}")


    def update_TRD_status(self, user_id, status):
        try:
            self.cursor.execute('UPDATE TRD SET status = ? WHERE partner_id = ?', (status,user_id))
            self.connection.commit()
            # logger.debug(f"Updated balance for user {user_id} to {}")
        except sqlite3.Error as e:
            logger.error(f"Error updating status for user {user_id}: {e}")

        
    def create_TRD_request(self, user_id, partner_id, price, request):
        try:
            now = datetime.now()  # Текущее время
            ends_at = now + timedelta(hours=12)  # Добавляем 12 часов к текущему времени
            
            # Выполняем вставку данных в таблицу TRD
            self.cursor.execute("INSERT INTO TRD (user_id, partner_id, created_at, ends_at, price, request) VALUES (?, ?, ?, ?, ?, ?)", 
                                (user_id, partner_id, now, ends_at, price, request))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f'Error creating TRD request for {user_id}: {e}')
            return False
    

    def delete_TRD_request(self, user_id):
        try:
            result = self.cursor.execute("DELETE FROM TRD WHERE partner_id = ?", (user_id,)).fetchone()
            self.connection.commit()
            
            return result
        except sqlite3.Error as e:
            logger.error(f'Error deleting TRD request for {user_id}: {e}')
            return False

    def get_TRD_request(self, user_id):
        try:
            result = self.cursor.execute("SELECT * FROM TRD WHERE partner_id = ?", (user_id,)).fetchone()
            self.connection.commit()
            return result
        except sqlite3.Error as e:
            logger.error(f'Error getting TRD request for {user_id}: {e}')
            return False

    def get_frns_list(self, user_id):
        # print((print(user_id)))
        # print(user_id)
        try:
            # Fetch the row corresponding to the user_id
            result = self.cursor.execute("SELECT friend_1, friend_2, friend_3, friend_4, friend_5 FROM friends WHERE user_id = ?", (user_id,)).fetchone()
            
            if result:
                # Filter out None values and return a list of friends
                return [friend for friend in result if friend is not None]
            else:
                # Return an empty list if no friends are found
                return []
        except sqlite3.Error as e:
            logger.error(f'Error getting friends list for {user_id}: {e}')
            return None

#     # Добавление друга
# # Добавление друга
#     def make_friends(self, user_id, friend_id):
#         try:
#             result = self.get_friends_list(user_id)

#             if result is None:  # Если у пользователя еще нет друзей
#                 self.cursor.execute("INSERT INTO friends (user_id, friend_1) VALUES (?, ?)", (user_id, friend_id))
#             else:
#                 # Ищем первое свободное место для добавления друга
#                 existing_friends = [result[i] for i in range(1, 6) if result[i] is not None]  # Считаем уже добавленных друзей

#                 if len(existing_friends) < 5:  # Если меньше 5 друзей, добавляем нового
#                     for i in range(1, 6):
#                         if result[i] is None:  # Если ячейка для друга пуста
#                             self.cursor.execute(f"UPDATE friends SET friend_{i} = ? WHERE user_id = ?", (friend_id, user_id))
#                             break
#                 else:
#                     return False  # Лимит друзей достигнут

#             self.connection.commit()
#             return True
#         except sqlite3.Error as e:
#             logger.error(f'Error creating friend for {user_id}: {e}')
#             return False

#     # Отправка запроса на добавление в друзья
#     def send_friendship_request(self, user_id, friend_id):
#         try:
#             # Логика отправки запроса в базу данных, например:
#             self.cursor.execute("INSERT INTO friendship_requests (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))
#             self.connection.commit()
#             return True
#         except sqlite3.Error as e:
#             logger.error(f'Error creating friendship request for {user_id}: {e}')
#             return False 
        

    def send_friendship_request(self, user_id, friend_id):
            try:
                try:
                    
                # Логика отправки запроса в базу данных, например:
                    self.cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))   
                except:
                    self.cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id)) 
                finally:
                    self.connection.commit()
                return True
            except sqlite3.Error as e:
                logger.error(f'Error creating friendship request for {user_id}: {e}')
                return False 
            
    def get_last_fren_number(frns_list):
            if frns_list[1]:
                if frns_list[2]:
                    if frns_list[3]:
                        if frns_list[4]:
                            if frns_list[5]:
                                return 5
                            else: 
                                return 4
                        else:
                            return 3
                    else:
                        return 2
                else:
                    return 1       
            else:
                return 0


    def rules_agree(self, user_id, result):
        res = 1 if result == True else 0
        try:
            self.cursor.execute("UPDATE users SET rules = ? WHERE user_id = ?", (res, user_id))  
            self.connection.commit()
            return True
        except sqlite3.Error as e:
                logger.error(f'Error updating rules for {user_id}: {e}')
                return False 


