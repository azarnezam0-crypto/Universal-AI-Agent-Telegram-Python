from sqlalchemy import desc
from db.models import User, ConversationHistory, UserPreference


class MemoryService:
    def get_or_create_user(self, db, telegram_id, username=None, full_name=None):
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user is None:
            user = User(telegram_id=telegram_id, username=username, full_name=full_name)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            changed = False
            if username and user.username != username:
                user.username = username
                changed = True
            if full_name and user.full_name != full_name:
                user.full_name = full_name
                changed = True
            if changed:
                db.commit()
        return user

    def get_history(self, db, user, limit=None):
        limit = limit or (user.memory_window or 20)
        rows = (
            db.query(ConversationHistory)
            .filter(ConversationHistory.telegram_id == user.telegram_id)
            .order_by(desc(ConversationHistory.timestamp))
            .limit(limit)
            .all()
        )
        rows = list(reversed(rows))
        return [{"role": r.role, "content": r.content} for r in rows]

    def add_message(self, db, user, role, content, model_used=None):
        db.add(
            ConversationHistory(
                telegram_id=user.telegram_id,
                role=role,
                content=content,
                model_used=model_used,
            )
        )
        db.commit()

    def clear_history(self, db, user):
        db.query(ConversationHistory).filter(
            ConversationHistory.telegram_id == user.telegram_id
        ).delete()
        db.commit()

    def set_preference(self, db, user, key, value):
        pref = (
            db.query(UserPreference)
            .filter(UserPreference.telegram_id == user.telegram_id, UserPreference.key == key)
            .first()
        )
        if pref:
            pref.value = value
        else:
            db.add(UserPreference(telegram_id=user.telegram_id, key=key, value=value))
        db.commit()

    def get_preference(self, db, user, key, default=None):
        pref = (
            db.query(UserPreference)
            .filter(UserPreference.telegram_id == user.telegram_id, UserPreference.key == key)
            .first()
        )
        return pref.value if pref else default

    def get_all_preferences(self, db, user):
        return {
            p.key: p.value
            for p in db.query(UserPreference)
            .filter(UserPreference.telegram_id == user.telegram_id)
            .all()
        }

    def all_users(self, db):
        return db.query(User).all()
