import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from sites.models.blog import Category
from sites.blueprints.admin import admin_bp
from sites.blueprints.ajax import ajax_bp
from sites.blueprints.main import main_bp
from sites.blueprints.user import user_bp
from sites.blueprints.auth import auth_bp
from sites.models.user import Role
from sites.extensions import bootstrap, db, login_manager, moment, mail, dropzone, csrf, avatars, whooshee, migrate, ckeditor
from sites.settings import config, basedir

from sites.models.photo import Notification


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('sites')

    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errorhandlers(app)
    register_shell_context(app)
    register_template_context(app)
    register_logging(app)

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
    migrate.init_app(app)
    ckeditor.init_app(app)


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ajax_bp, url_prefix='/ajax')

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
            categories = Category.query.filter_by(author_id=current_user.id).order_by(Category.name).all()
        else:
            notification_count = None
            categories = None
        return dict(notification_count=notification_count, categories=categories)


def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_fount(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

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
        Role.init_role()
        click.echo('初始化数据库')


def register_logging(app):
    # app.logger.setLevel(logging.INFO)
    class RequestFormatter(logging.Formatter):
        def format(self,record):
            record.url = request.url
            record.remote_addr = request.remote_addr

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir,'logs/sites.log'), maxBytes=10*1024*1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)


    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=['MAIL_USERNAME'],
        subject='personal-web site Error',        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    if not app.debug:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(mail_handler)