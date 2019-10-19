# README

## Explanation for implementation

### data_table_adaptor.py

Default connection information is put here.

#### get_databases

pass `show databases;` to mysql server.

#### get_tables

pass `show tables in <dbname>;` to mysql server.

### app.py

'GET', 'PUT', 'POST', 'DELETE' in RESTful APIs correspond to 'select', "update", "insert", "delete" in Relational databases respectively.

#### dbs / tbls

use the helper function from data_table_adpaptor

#### resourece_by_id

Primary key  are the last path parameter.

The desired fields are parsed from the query parameters.

When dealing with "PUT" method, the program will read new values from request body.

#### get_resource

The searching template for where-clause in the select statement is parsed from the query parameters.

Pagination is implemented using `limt` and `offset`  keywords in  SQL.