
class DBConnectorComponent:
    '''A fixed component of the DBConnector, handling one particular aspect of
    the database
    '''

    connector = None

    def __init__(self, connector):
        self.db = connector
