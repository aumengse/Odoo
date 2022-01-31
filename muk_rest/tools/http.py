###################################################################################
#
#    Copyright (c) 2017-today MuK IT GmbH.
#
#    This file is part of MuK REST API for Odoo
#    (see https://mukit.at).
#
#    MuK Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used
#    (executed, modified, executed after modifications) if you have
#    purchased a valid license from MuK IT GmbH.
#
#    The above permissions are granted for a single database per purchased
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using its
#    resources), but without copying any source code or material from the
#    Software. You may distribute those modules under the license of your
#    choice, provided that this license is compatible with the terms of the
#    MuK Proprietary License (For example: LGPL, MIT, or proprietary licenses
#    similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###################################################################################


import json
import base64
import urllib
import importlib
import functools
import logging
import traceback
import sys

from urllib.parse import urlencode, quote_plus
from urllib.parse import urlparse, urlunparse, parse_qs
from werkzeug.exceptions import HTTPException, Unauthorized, Forbidden

from odoo import http, api, conf, exceptions, registry, SUPERUSER_ID
from odoo.tools import ustr, config
from odoo.http import request, route

from odoo.addons.muk_rest.tools import common
from odoo.addons.muk_rest.tools.encoder import RecordEncoder
from odoo.addons.muk_rest.exceptions.http import RestModuleNotInstalled, NoDatabaseFound

_logger = logging.getLogger(__name__)


def build_route(route):
    param_routes = route
    if not isinstance(route, list):
        param_routes = [route]
    api_routes = []
    for item in param_routes:
        api_routes.append('{}{}'.format(common.BASE_URL, item))
    return api_routes


def clean_query_params(query, clean_db=True, clean_debug=True):
    cleaned_params = {}
    parsed_url = urlparse(query)
    params = parse_qs(parsed_url.query)
    for key, value in params.items():
        invalid_param_check = any(
            param and not set(param) <= common.SAFE_URL_CHARS or \
                common.INVALID_HEX_PATTERN.search(param) or \
                (clean_debug and key == 'debug') or \
                (clean_db and key == 'db')
            for param in value
        )
        if not invalid_param_check and not ():
            cleaned_params[key] = value
    parsed_url = parsed_url._replace(
        query=urlencode(cleaned_params, True)
    )
    return urlunparse(parsed_url)

    
def make_json_response(data, headers=None, cookies=None, encoder=RecordEncoder):
    json_headers = {} if headers is None else headers
    json_headers[common.CONTENT_TYPE_HEADER] = common.JSON_CONTENT_TYPE
    json_data = json.dumps(data, sort_keys=True, indent=4, cls=encoder)
    return request.make_response(json_data, headers=json_headers, cookies=cookies)


def ensure_db(httprequest, session, params):
    database = params.get('db', '').strip()
    if database and database not in http.db_filter([database]):
        database = None
    if not database and session.db and http.db_filter([session.db]):
        database = session.db
    if not database:
        database = http.db_monodb(httprequest)
    if not database:
        raise NoDatabaseFound()
    session.db = database
    
    
def ensure_database(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ensure_db(
            http.request.httprequest, 
            http.request.session, 
            http.request.params
        )
        return func(*args, **kwargs)
    return wrapper


def ensure_rest_module(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with registry(http.request.session.db).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            if 'muk_rest' not in env['ir.module.module']._installed() and \
                    not config.get('test_enable', False):
                raise RestModuleNotInstalled()
        return func(*args, **kwargs)
    return wrapper


def rest_route(routes=None, **kw):
    cors_config = config.get('rest_default_cors', False)
    default_params = dict(cors=cors) if cors_config else dict()
    fixed_params = dict(auth='none', csrf=False, save_session=False, rest=True)
    return route(route=routes, **{**default_params, **kw, **fixed_params})
    
    
@common.monkey_patch(http.Root)
def get_request(self, httprequest):
    if common.BASE_URL in httprequest.base_url:
        return http.HttpRequest(httprequest)  
    return get_request.super(self, httprequest)   
