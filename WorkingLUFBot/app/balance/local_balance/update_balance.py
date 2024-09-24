from db.database import Database as db


# Function to update balances in the database
def update_balances(sender_id: int, receiver_id: int, amount: float):
    # Retrieve balances
    sender_balance = db.get_balance(sender_id)
    receiver_balance = db.get_balance(receiver_id)

    if sender_balance >= amount:
        # Deduct from sender
        new_sender_balance = sender_balance - amount
        db.update_balance(sender_id, new_sender_balance)

        # Add to receiver
        new_receiver_balance = receiver_balance + amount
        db.update_balance(receiver_id, new_receiver_balance)

        return True
    else:
        return False