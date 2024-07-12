from sqlalchemy.orm.attributes import flag_modified
from db.base import DBConnectorComponent
from db.model import Shares


class SharesDBConnectorComponent(DBConnectorComponent):
    '''
    shares component which is used to manager all shares interface
    '''
    tbl = Shares

    def get_all_shares(self):
        def thd(conn):
            try:
                shares = conn.query(self.tbl).first()
            except Exception as err:
                print(f"get all bots err: {err}")
            return shares.to_dict()
        d = self.db.execute(thd)
        return d

    def add_new_shares(self, **kwargs):
        def thd(conn):
            try:
                shares = self.tbl(
                    bot_updated=kwargs.get("bot_updated"),
                )
                conn.add(shares)
                conn.commit()
            except Exception as err:
                print("add chat err: ", err)
            return shares.id
        d = self.db.execute(thd)
        return d

    def update_shares_by_id(self, shares_id, **kwargs):
        def thd(conn):
            update_columns = ["bot_updated"]
            shares = conn.query(self.tbl).filter(
                self.tbl.id == shares_id).first()
            for col in update_columns:
                val = kwargs.get(col, None)
                if val is not None:
                    setattr(shares, col, val)
                    flag_modified(shares, col)
            conn.commit()
            return shares.id
        d = self.db.execute(thd)
        return d