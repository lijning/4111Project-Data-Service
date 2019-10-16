from src.data_service.RDBDataTable import RDBDataTable
from src.data_service.data_table_adaptor import get_databases

DB_NAME = "lahman2019clean"
TBL_NAME = "schools"
CONNECT_INFO = {
    'host': 'localhost',
    'user': 'someone',
    'password': 'link',
    'db': 'lahman2019clean',
    'port': 3306
}

# tbl = RDBDataTable(db_name=DB_NAME, table_name=TBL_NAME, connect_info=CONNECT_INFO)
# print(tbl.get_row_count())
# print(tbl.get_primary_key_columns()) # []
print(get_databases(CONNECT_INFO))
if __name__ == '__main__':
    pass
