from sqlalchemy.orm.attributes import flag_modified
from db.base import DBConnectorComponent
from db.model import User


class UserDBConnectorComponent(DBConnectorComponent):
    '''
    user component which is used to manager all user db interface
    '''
    tbl = User

    def get_user_by_email(self, email):
        def thd(conn):
            user = conn.query(self.tbl).filter(
                self.tbl.email == email).first()
            return user.to_dict() if user else None
        d = self.db.execute(thd)
        return d

    def get_user_by_id(self, user_id):
        def thd(conn):
            user = conn.query(self.tbl).filter(
                self.tbl.id == user_id).first()
            return user.to_dict() if user else None
        d = self.db.execute(thd)
        return d

    def add_new_user(self, **kwargs):
        def thd(conn):
            try:
                if kwargs.get("email", None) is None:
                    raise ValueError("request_id is required field")
                if kwargs.get("pwd", None) is None:
                    raise ValueError("number is required field")
                user = self.tbl(
                    name=kwargs.get("name", None),
                    email=kwargs.get("email"),
                    phone=kwargs.get("phone", None),
                    avatar=kwargs.get("avatar", "1"),
                    pwd=kwargs.get("pwd"),
                    active=True
                )
                conn.add(user)
                conn.commit()
            except Exception as err:
                print("err:", err)
            return user.id
        d = self.db.execute(thd)
        return d

    def update_user_by_id(self, user_id, **kwargs):
        def thd(conn):
            update_columns = [
                "name", "email", "phone", "avatar", "pwd",
            ]
            user = conn.query(self.tbl).filter(
                self.tbl.id == user_id).first()
            for col in update_columns:
                val = kwargs.get(col, None)
                if val is not None:
                    setattr(user, col, val)
                    flag_modified(user, col)
            conn.commit()
            return user.to_dict()
        d = self.db.execute(thd)
        return d

    def delete_user(self, user_id):
        def thd(conn):
            try:
                result = conn.query(self.tbl).filter(
                    self.tbl.id == user_id).delete()
                conn.commit()
            except Exception as err:
                print("delete user error: ", err)
            return result
        d = self.db.execute(thd)
        return d
