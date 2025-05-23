from sqlalchemy.orm.attributes import flag_modified
from db.base import DBConnectorComponent
from db.model import McpServer


class MCPDBConnectorComponent(DBConnectorComponent):
    '''
    mcp component which is used to manager all mcp db interface
    '''
    tbl = McpServer

    def get_all_mcps(self):
        def thd(conn):
            try:
                mcps = conn.query(self.tbl).order_by(self.tbl.created_at).all()
            except Exception as err:
                print(f"get all mcps err: {err}")
            return [mcp.to_dict() for mcp in mcps]
        d = self.db.execute(thd)
        return d

    def get_mcp_by_owner_id(self, owner_id):
        def thd(conn):
            try:
                mcps = conn.query(self.tbl).filter(
                    self.tbl.owner_id == owner_id).all()
            except Exception as err:
                print(f"get mcp err: {err}")
            return [mcp.to_dict() for mcp in mcps]
        d = self.db.execute(thd)
        return d

    def get_mcp_by_id(self, mcp_id):
        def thd(conn):
            mcp = conn.query(self.tbl).filter(
                self.tbl.id == mcp_id).first()
            return mcp.to_dict() if mcp else None
        d = self.db.execute(thd)
        return d

    def add_new_mcp(self, **kwargs):
        def thd(conn):
            try:
                if kwargs.get("name", None) is None:
                    raise ValueError("name is required field")
                if kwargs.get("id", None) is None:
                    raise ValueError("id is required field")
                mcp = self.tbl(
                    id=kwargs.get("id"),
                    name=kwargs.get("name"),
                    description=kwargs.get("description", None),
                    command=kwargs.get("command", None),
                    args=kwargs.get("args", None),
                    custom_environment=kwargs.get("custom_environment", None),
                    owner_id=kwargs.get("owner_id", None),
                    owner_name=kwargs.get("owner_name", None),
                    is_public=kwargs.get("is_public", False),
                    created_at=kwargs.get("created_at"),
                    updated_at=kwargs.get("updated_at"),
                )
                conn.add(mcp)
                conn.commit()
            except Exception as err:
                print("err:", err)
            return mcp.to_dict()
        d = self.db.execute(thd)
        return d

    def update_mcp_by_id(self, mcp_id, **kwargs):
        def thd(conn):
            try:
                update_columns = [
                    "name", "alias", "command", "args", "custom_environment",
                    "description", "owner_id", "owner_name", "is_public",
                    "created_at", "updated_at",
                ]
                mcp = conn.query(self.tbl).filter(
                    self.tbl.id == mcp_id).first()
                for col in update_columns:
                    val = kwargs.get(col, None)
                    if val is not None:
                        setattr(mcp, col, val)
                        flag_modified(mcp, col)
                conn.commit()
            except Exception as e:
                print("terr: ", e)
            return mcp.to_dict()
        d = self.db.execute(thd)
        return d

    def delete_mcp(self, mcp_id):
        def thd(conn):
            try:
                result = conn.query(self.tbl).filter(
                    self.tbl.id == mcp_id).delete()
                conn.commit()
            except Exception as err:
                print("delete mcp error: ", err)
            return result
        d = self.db.execute(thd)
        return d
