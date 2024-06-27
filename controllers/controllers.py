from odoo import http
from odoo.http import request
import odoo.addons.web.controllers.home as main
from odoo.service import security
import string
import secrets


class AutoLoginHome(main.Home):

    @http.route("/web/login", type="http", auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        if request.session.is_new:
            alphabet = string.ascii_letters + string.digits
            login = "".join(secrets.choice(alphabet) for _ in range(8))
            lang_id = request.env["res.lang"].sudo().with_context(active_test=False).search(
                [("iso_code", "=", request.best_lang)], limit=1)
            lang_id.active = True
            user_id = request.env["res.users"].sudo().create({
                "name": login,
                "login": login,
                "lang": lang_id.id,
                "company_ids": request.env["res.company"].sudo().search([], limit=1).ids,
                "company_id": request.env["res.company"].sudo().search([], limit=1).id,
            })
            request.session.uid = user_id.id
            request.env.registry.clear_cache()
            request.session.session_token = security.compute_session_token(request.session, request.env)
            return request.redirect(self._login_redirect(user_id.id, redirect=redirect))
        return super().web_login(redirect=redirect, **kw)
