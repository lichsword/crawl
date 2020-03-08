import os

import tornado.iostream
import tornado.template
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


class DownloadHandler(AdminOnlyMixin, tornado.web.StaticFileHandler):

    def initialize(self):
        self.root = "."
        super(DownloadHandler, self).initialize()

    def get(self, path=None, include_body=True):
        self.set_header("Content-Type", "application/octet-stream")
        super(DownloadHandler, self).get(path, include_body)


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


class ViewUserHandler(AdminOnlyMixin, tornado.web.RequestHandler):
    """Handler for user view."""

    def get(self, username):
        user = userdb.get_user_info(username)
        if not user:
            raise tornado.web.HTTPError(404)

        user_saves = self._get_saves_for_user(user.username)
        self.render("user.html",
                    config=config,
                    user=user,
                    user_saves=user_saves)

    def _get_save_dirs(self):
        try:
            crawl_base_dir = os.path.join(config.chroot, 'crawl-master')
            return [
                (subdir, os.path.join(crawl_base_dir, subdir, 'saves'))
                for subdir in os.listdir(crawl_base_dir)
                if os.path.isdir(subdir)
            ]
        except AttributeError:
            return [('trunk', 'saves')]

    def _get_saves_for_user(self, username):
        saves = [
            (name, os.path.join(d, username+'.cs'))
            for name, d in self._get_save_dirs()
        ]
        return [(name, save) for name, save in saves if os.path.isfile(save)]
