from sqlalchemy.orm.attributes import flag_modified
from db.base import DBConnectorComponent
from db.model import Chat


class ChatDBConnectorComponent(DBConnectorComponent):
    '''
    Chat component which is used to manager all Chat db interface
    '''
    tbl = Chat

    def get_chat_by_user_id(self, user_id):
        def thd(conn):
            chat = conn.query(self.tbl).filter(
                self.tbl.user_id == user_id).all()
            return chat.to_dict() if chat else None
        d = self.db.execute(thd)
        return d

    def get_chat_by_id(self, chat_id):
        def thd(conn):
            chat = conn.query(self.tbl).filter(
                self.tbl.id == chat_id).first()
            return chat.to_dict() if chat else None
        d = self.db.execute(thd)
        return d

    def add_new_chat(self, **kwargs):
        def thd(conn):
            if kwargs.get("user_id", None) is None:
                raise ValueError("user_id is required field")
            chat = self.tbl(
                user_id=kwargs.get("user_id"),
                content=kwargs.get("content"),
            )
            conn.add(chat)
            conn.commit()
            return chat.id
        d = self.db.execute(thd)
        return d

    def update_chat_by_id(self, chat_id, **kwargs):
        def thd(conn):
            update_columns = [
                "title", "content",
            ]
            chat = conn.query(self.tbl).filter(
                self.tbl.id == chat_id).first()
            for col in update_columns:
                val = kwargs.get(col, None)
                if val is not None:
                    setattr(chat, col, val)
                    flag_modified(chat, col)
            conn.commit()
            return chat.to_dict()
        d = self.db.execute(thd)
        return d

    def delete_chat(self, chat_id):
        def thd(conn):
            result = conn.query(self.tbl).filter(
                self.tbl.id == chat_id).delete()
            conn.commit()
            return result
        d = self.db.execute(thd)
        return d
