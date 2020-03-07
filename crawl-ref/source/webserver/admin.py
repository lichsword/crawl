import tornado.web

import config
import userdb
import ws_handler


class AuthRequiredMixin(object):
    def initialize(self, *args, **kwargs):
        pass

    def get_current_user(self):
        cookie = self.get_cookie('login').replace('%20', ' ')
        username, token = cookie.split()
        try:
            token = long(token)
        except ValueError:
            token = None
        if (token, username) not in ws_handler.login_tokens:
            raise tornado.web.HTTPError(404)

        return userdb.get_user_info(username)


class AdminOnlyMixin(AuthRequiredMixin):
    def get_current_user(self):
        user = super(AdminOnlyMixin, self).get_current_user()
        if not user.is_admin:
            raise tornado.web.HTTPError(404)
        return user


class AdminHandler(AdminOnlyMixin, tornado.web.RequestHandler):
    """Handler for main admin panel."""

    def get(self):
        self.render("admin.html",
                    config=config,
                    rebuild_targets=self._get_rebuild_targets())

    def _get_rebuild_targets(self):
        dedup_games = {}
        for game_id, game in config.games.items():
            if game['crawl_binary'] not in dedup_games:
                dedup_games[game['crawl_binary']] = game_id

        return {
            game_id: config.games[game_id]['name']
            for game_id in dedup_games.values()
        }

