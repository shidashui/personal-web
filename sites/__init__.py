import os

import click
from flask import Flask, render_template
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from sites.extensions import bootstrap, db, login_manager, moment, mail, dropzone, csrf, avatars, whooshee
from sites.settings import config

from sites.models.photo import Notification


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('CoderShui')

    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errorhandlers(app)
    register_shell_context(app)
    register_template_context(app)

    return app


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    dropzone.init_app(app)
    csrf.init_app(app)
    avatars.init_app(app)
    whooshee.init_app(app)


def register_blueprints(app):
    # app.register_blueprint(main_bp)
    # app.register_blueprint(user_bp, url_prefix='/user')
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(admin_bp, url_prefix='/admin')
    # app.register_blueprint(ajax_bp, url_prefix='/ajax')
    pass

def register_shell_context(app):
    # @app.shell_context_processor
    # def make_shell_context():
    #     return dict(db=db, User=User, Role=Role, Permission=Permission,Photo=Photo,Tag=Tag,Collect=Collect,
    #                 Follow=Follow, Notification=Notification)
    pass


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        if current_user.is_authenticated:
            notification_count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
        else:
            notification_count = None
        return dict(notification_count=notification_count)


def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_fount(e):
        return  render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return  render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 500




def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='先删除后创建')
    def initdb(drop):
        if drop:
            click.confirm('此操作会删除数据库，确认？',abort=True)
            db.drop_all()
            click.echo('删除表')
        db.create_all()
        click.echo('初始化数据库')