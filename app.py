####################################################################################################
#
# DO NOT WORRY ABOUT ANY OF THE STUFF IN THIS SECTION. THIS HELPS YOU IMPLEMENT.
#
#


# Import functions and objects the microservice needs.
# - Flask is the top-level application. You implement the application by adding methods to it.
# - Response enables creating well-formed HTTP/REST responses.
# - requests enables accessing the elements of an incoming HTTP/REST request.
#
from flask import Flask, Response, request
from datetime import datetime
import json
import src.data_service.data_table_adaptor as dta

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# The convention is that a compound primary key in a path has the elements sepatayed by "_"
# For example, /batting/willite01_BOS_1960_1 maps to the primary key for batting
_key_delimiter = "_"
_host = "127.0.0.1"
_port = 5002
_api_base = "/api"

application = Flask(__name__)


def handle_args(args):
    """

    :param args: The dictionary form of request.args.
    :return: The values removed from lists if they are in a list. This is flask weirdness.
        Sometimes x=y gets represented as {'x': ['y']} and this converts to {'x': 'y'}
    """

    result = {}

    if args is not None:
        for k, v in args.items():
            if type(v) == list:
                v = v[0]
            result[k] = v

    return result


# 1. Extract the input information from the requests object.
# 2. Log the information
# 3. Return extracted information.
#
def log_and_extract_input(method, path_params=None):
    req = request

    path = request.path
    args = dict(request.args)
    data = None
    headers = dict(request.headers)
    method = request.method
    url = request.url
    base_url = request.base_url

    try:
        if request.data is not None:
            data = request.json
        else:
            data = None
    except Exception as e:
        # This would fail the request in a more real solution.
        data = "You sent something but I could not get JSON out of it."

    log_message = str(datetime.now()) + ": Method " + method

    # Get rid of the weird way that Flask sometimes handles query parameters.
    args = handle_args(args)

    inputs = {
        "path": path,
        "method": method,
        "path_params": path_params,
        "query_params": args,
        "headers": headers,
        "body": data,
        "url": url,
        "base_url": base_url
    }

    # Pull out the fields list as a separate element.
    if args and args.get('fields', None):
        fields = args.get('fields')
        fields = fields.split(",")
        del args['fields']
        inputs['fields'] = fields

    if args:
        inputs["offset"] = args.pop("offset", None)
        inputs["limit"] = args.pop("limit", None)

    log_message += " received: \n" + json.dumps(inputs, indent=2)
    logger.debug(log_message)

    return inputs


def log_response(path, rsp):
    """

    :param path: The path parameter received.
    :param rsp: Response object
    :return:
    """
    msg = rsp
    logger.debug(str(datetime.now()) + ": \n" + str(rsp))


def get_field_list(inputs):
    return inputs.get('fields', None)


# def get_field_list(inputs):
#     params = inputs.get('query_params', None)
#     if params is None:
#         return None
#     else:
#         fields = params.get("fields", None)
#         if fields is None:
#             return None
#         else:
#             return fields.split(',')

def format_links(url: str, limit: int, offset: int):
    limit = int(limit)
    offset = int(offset)
    if '&limit=' not in url:
        url = url + '&limit={}'.format(limit)
    if '&offset=' not in url:
        url = url + '&offset={}'.format(offset)
    if offset == 0:
        return [
            {"rel": "current",
             "href": url},
            {"rel": "next",
             "href": url.replace("offset={}".format(offset),
                                 "offset={}".format(offset + limit))}
        ]
    if offset - limit < 0:
        previous = {"rel": "previous",
                    "href": url.replace("offset={}".format(offset),
                                        "offset={}".format(0))}
    else:
        previous = {"rel": "previous",
                    "href": url.replace("offset={}".format(offset),
                                        "offset={}".format(offset - limit))}
    return [
        {"rel": "current",
         "href": url},
        {"rel": "next",
         "href": url.replace("offset={}".format(offset),
                             "offset={}".format(offset + limit))},
        previous
    ]


def generate_error(status_code, ex=None, msg=None):
    """

    This used to be more complicated in previous semesters, but we simplified for fall 2019.
    Does not do much now.
    :param status_code:
    :param ex:
    :param msg:
    :return:
    """

    rsp = Response("Oops", status=500, content_type="text/plain")

    if status_code == 500:
        if msg is None:
            msg = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."

        rsp = Response(msg, status=status_code, content_type="text/plain")

    return rsp


####################################################################################################
#
# THESE ARE JUST SOME EXAMPLES TO HELP YOU UNDERSTAND WHAT IS GOING ON.
#
#

# This function performs a basic health check. We will flesh this out.
@application.route("/health", methods=["GET"])
def health_check():
    rsp_data = {"status": "healthy", "time": str(datetime.now())}
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp


@application.route("/demo/<parameter>", methods=["GET", "PUT", "DELETE", "POST"])
def demo(parameter):
    """
    This simple echoes the various elements that you get for handling a REST request.
    Look at https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data

    :param parameter: A list of the path parameters.
    :return: None
    """

    inputs = log_and_extract_input(demo, {"parameter": parameter})

    msg = {
        "/demo received the following inputs": inputs
    }

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp


####################################################################################################
#
# YOU HAVE TO COMPLETE THE IMPLEMENTATION OF THE FUNCTIONS BELOW.
#
#
@application.route("/api/databases", methods=["GET"])
def dbs():
    """

    :return: A JSON object/list containing the databases at this endpoint.
    """
    ls_dbs = dta.get_databases()
    data = {"databases": ls_dbs}
    rsp = Response(json.dumps(ls_dbs), status=200, content_type="application/json")
    return rsp


@application.route("/api/databases/<dbname>", methods=["GET"])
def tbls(dbname):
    """

    :param dbname: The name of a database/sche,a
    :return: List of tables in the database.
    """

    inputs = log_and_extract_input(tbls, None)
    ls_tbls = dta.get_tables(dbname)
    data = {"tables": ls_tbls, "dbname": dbname}
    rsp = Response(json.dumps(ls_tbls), status=200, content_type="application/json")
    return rsp


@application.route('/api/<dbname>/<resource>/<primary_key>', methods=['GET', 'PUT', 'DELETE'])
def resource_by_id(dbname, resource, primary_key: str):
    """

    :param dbname: Schema/database name.
    :param resource: Table name.
    :param primary_key: Primary key in the form "col1_col2_..._coln" with the values of key columns.
    :return: Result of operations.
    """

    result = None

    try:
        # Parse the incoming request into an application specific format.
        context = log_and_extract_input(resource_by_id, (dbname, resource, primary_key))

        tbl = dta.get_rdb_table(table_name=resource, db_name=dbname)
        ls_pks = primary_key.split("_")
        field_list = get_field_list(context)

        if request.method == 'GET':

            result = tbl.find_by_primary_key(ls_pks, field_list=field_list)
            if result is None:
                data = []
                status = 404
            else:
                data = result
                status = 200
            content = {"data": data, "dbname": dbname}
            resp = Response(json.dumps(content), status=status, content_type="application/json")
            return resp

        elif request.method == 'DELETE':

            result = tbl.delete_by_key(ls_pks)
            content = {'result': result}
            resp = Response(json.dumps(content), status=200, content_type="application/json")
            return resp

        elif request.method == 'PUT':

            kvp_to_put = context.get("body", None)
            if kvp_to_put is None:
                return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
            result = tbl.update_by_key(ls_pks, kvp_to_put)
            content = {'result': result}
            return Response(json.dumps(content), status=200, content_type="application/json")

    except Exception as e:
        print(e)
        return handle_error(e, result)


@application.route('/api/<dbname>/<resource_name>', methods=['GET', 'POST'])
def get_resource(dbname, resource_name):
    result = None

    try:
        context = log_and_extract_input(get_resource, (dbname, resource_name))
        tbl = dta.get_rdb_table(table_name=resource_name, db_name=dbname)

        if request.method == 'GET':
            template = context.get("query_params", None)
            fields = get_field_list(context)
            limit = context.get("limit", 5)
            offset = context.get("offset", 0)
            if limit is None or offset is None:
                limit = 5
                offset = 0
            data = tbl.find_by_template(template=template, field_list=fields,
                                        offset=int(offset), limit=int(limit))
            original_url = context.get("url", None)
            content = {"data": data,
                       "links": format_links(original_url, int(limit), int(offset))}
            return Response(json.dumps(content), status=200,
                            content_type="application/json")

        elif request.method == 'POST':
            kvp_to_put = context.get("body", None)
            if kvp_to_put is None:
                return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
            result = tbl.insert(kvp_to_put)
            if result == 1:
                content = {"result": result, "msg": "Entry successfully inserted."}
                return Response(json.dumps(content), status=201,
                                content_type="application/json")
            else:
                content = {"result": result, "msg": "Entry insertion failed."}
                return Response(json.dumps(content), status=400,
                                content_type="application/json")
        else:
            result = "Invalid request."
            return result, 400, {'Content-Type': 'text/plain; charset=utf-8'}
    # except Exception as e:
    except TypeError as e:
        print("Exception e = ", e)
        return handle_error(e, result)


@application.route('/api/<dbname>/<parent_name>/<primary_key>/<target_name>', methods=['GET'])
def get_by_path(dbname, parent_name, primary_key, target_name):
    # Do not implement

    result = " -- THANK ALY AND ARA -- "

    return result, 501, {'Content-Type': 'application/json; charset=utf-8'}


@application.route('/api/<dbname>/<parent_name>/<primary_key>/<target_name>/<target_key>',
                   methods=['GET'])
def get_by_path_key(dbname, parent_name, primary_key, target_name, target_key):
    # Do not implement

    result = " -- THANK ALY AND ARA -- "

    return result, 501, {'Content-Type': 'application/json; charset=utf-8'}


# You can ignore this method.
def handle_error(e, result):
    return "Internal error.", 504, {'Content-Type': 'text/plain; charset=utf-8'}


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.

    logger.debug("Starting HW2 time: " + str(datetime.now()))
    application.debug = True
    application.run(host=_host, port=_port)
