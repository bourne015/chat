from sqlalchemy.orm.attributes import flag_modified
from db.base import DBConnectorComponent
from db.model import Order


class OrderDBConnectorComponent(DBConnectorComponent):
    '''
    Order component which is used to manager all Order db interface
    '''
    tbl = Order

    def get_all_orders(self):
        def thd(conn):
            try:
                orders = conn.query(self.tbl).order_by(self.tbl.created_at).all()
            except Exception as err:
                print(f"get all orders err: {err}")
            return [od.to_dict() for od in orders]
        d = self.db.execute(thd)
        return d

    def get_orders_by_owner_id(self, owner_id):
        def thd(conn):
            try:
                ods = conn.query(self.tbl).filter(
                    self.tbl.owner_id == owner_id).all()
            except Exception as err:
                print(f"get ods err: {err}")
            return [od.to_dict() for od in ods]
        d = self.db.execute(thd)
        return d

    def get_order_by_out_trade_no(self, out_trade_no):
        def thd(conn):
            od = conn.query(self.tbl).filter(
                self.tbl.out_trade_no == out_trade_no).first()
            return od.to_dict() if od else None
        d = self.db.execute(thd)
        return d

    def add_new_order(self, **kwargs):
        def thd(conn):
            try:
                if kwargs.get("name", None) is None:
                    raise ValueError("name is required field")
                if kwargs.get("user_id", None) is None:
                    raise ValueError("user_id is required field")
                od = self.tbl(
                    user_id=kwargs.get("user_id", None),
                    name=kwargs.get("name"),
                    out_trade_no=kwargs.get("out_trade_no", None),
                    type=kwargs.get("type", None),
                    pid=kwargs.get("pid", None),
                    money=kwargs.get("money", None),
                    status=kwargs.get("status", 0),
                    param=kwargs.get("param", None),
                    created_at=kwargs.get("created_at"),
                    updated_at=kwargs.get("updated_at"),
                )
                conn.add(od)
                conn.commit()
            except Exception as err:
                print("err:", err)
            return od.to_dict()
        d = self.db.execute(thd)
        return d

    def update_order_by_id(self, order_id, **kwargs):
        def thd(conn):
            try:
                update_columns = [
                    "money", "status",
                    "created_at", "updated_at",
                ]
                od = conn.query(self.tbl).filter(
                    self.tbl.id == order_id).first()
                for col in update_columns:
                    val = kwargs.get(col, None)
                    if val is not None:
                        setattr(od, col, val)
                        flag_modified(od, col)
                conn.commit()
            except Exception as e:
                print("terr: ", e)
            return od.to_dict()
        d = self.db.execute(thd)
        return d

    def delete_order(self, order_id):
        def thd(conn):
            try:
                result = conn.query(self.tbl).filter(
                    self.tbl.id == order_id).delete()
                conn.commit()
            except Exception as err:
                print("delete order error: ", err)
            return result
        d = self.db.execute(thd)
        return d
