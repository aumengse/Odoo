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
import logging
import traceback
import threading
import werkzeug

from odoo import api, models, tools, http, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.http import request, Response

from odoo.addons.muk_rest.tools import common, security
from odoo.addons.muk_rest.tools.http import ensure_db
from odoo.addons.muk_rest.tools.common import parse_exception
from odoo.addons.muk_rest.tools.encoder import RecordEncoder
from odoo.addons.muk_rest.exceptions.http import RestModuleNotInstalled

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    
    _inherit = 'ir.http'
    
    @classmethod
    def _rest_update_request(cls, endpoint, args):
        cls._handle_debug()
        request.is_rest = True
        request.is_frontend = False
        request.website_routing = False
        request.session.logout(keep_db=False)
        request.set_handler(endpoint, args, 'none')
        
    @classmethod 
    def _rest_ensure_database(cls):
        ensure_db(request.httprequest, request.session, request.params)
        threading.current_thread().dbname = request.session.db
        
    @classmethod 
    def _rest_ensure_module(cls):
        env = api.Environment(request.cr, SUPERUSER_ID, {})
        if 'muk_rest' not in env['ir.module.module']._installed() and \
                not tools.config.get('test_enable', False):
            raise RestModuleNotInstalled()
        
    @classmethod 
    def _rest_authenticate_request(cls, routing, params):
        env = api.Environment(request.cr, SUPERUSER_ID, {})
        user = None

        def update_request(user):
            request.uid = user.id
            request.disable_db = False
            request.session.login = user.login
            request.session.uid = user.id
            request.session.get_context()
            threading.current_thread().uid = user.id
            return user
        
        with env['res.users']._assert_can_auth():
            if common.ACTIVE_BASIC_AUTHENTICATION:
                user = security.verify_basic_request()
            if not user and common.ACTIVE_OAUTH1_AUTHENTICATION:
                user = security.verify_oauth1_request(routing, params)
            if not user and common.ACTIVE_OAUTH2_AUTHENTICATION:
                user = security.verify_oauth2_request(routing, params)
        if not user:
            raise werkzeug.exceptions.Unauthorized()
        return update_request(user)

    @classmethod
    def _dispatch(cls):
        try:
            rule, args = cls._match(request.httprequest.path)
            endpoint_routing_values = rule.endpoint.routing
        except Exception:
            return super(IrHttp, cls)._dispatch()

        if endpoint_routing_values.get('rest', False):
            try:
                cls._rest_update_request(rule.endpoint, args)
                
                if endpoint_routing_values.get('ensure_db', False) or \
                        endpoint_routing_values.get('ensure_module', False) or \
                        endpoint_routing_values.get('protected', False):
                    cls._rest_ensure_database()
                
                if endpoint_routing_values.get('ensure_module', False) or \
                        endpoint_routing_values.get('protected', False):    
                    cls._rest_ensure_module()
                    
                if endpoint_routing_values.get('protected', False):    
                    cls._rest_authenticate_request(
                        endpoint_routing_values, 
                        {**args, **request.params}
                    )
                
                if request.params.get('with_context', False):
                    ctx = getattr(request.session, 'context', {})
                    ctx.update(common.parse_value(request.params['with_context'], {}))
                    request.session.context = ctx
                    request.context = ctx
                    
                if request.params.get('with_company', False):
                    ctx = getattr(request.session, 'context', {})
                    with_company_id = int(request.params['with_company'])
                    allowed_company_ids = ctx.get('allowed_company_ids', [])
                    if with_company_id in allowed_company_ids:
                        allowed_company_ids.remove(with_company_id)
                    allowed_company_ids.insert(0, with_company_id)
                    ctx.update({'allowed_company_ids': allowed_company_ids})
                    request.session.context = ctx
                    request.context = ctx
        
                response = request.dispatch()
                if isinstance(response, Exception):
                    raise response
                if isinstance(response, werkzeug.wrappers.BaseResponse) and \
                        response.content_type != 'application/json' and \
                        response.status_code != 200:
                    message = {
                        'message': response.status,
                        'code': response.status_code,
                        'content': response.get_data(as_text=True).splitlines()
                    }
                    return Response(json.dumps(message, indent=4, cls=RecordEncoder), 
                        content_type='application/json', status=response.status_code
                    )         
                return response
            except Exception as exc:
                return cls._handle_exception(exc)
        return super(IrHttp, cls)._dispatch()

    @classmethod
    def _handle_exception(cls, exception):
        if not bool(getattr(request, 'is_rest', False)):
            return super(IrHttp, cls)._handle_exception(exception)
        error_message = parse_exception(exception)
        try:
            super(IrHttp, cls)._handle_exception(exception)
        except Exception as exc:
            logging.exception('Restful API Error', exc_info=exc)
        return Response(json.dumps(error_message, indent=4, cls=RecordEncoder), 
            content_type='application/json', status=error_message.get('code', 500)
        )
