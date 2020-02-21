from flask import Blueprint, Response, render_template, request, jsonify, redirect, url_for
from flask_babel import gettext

from base.models import Msg, User
from init import db
from util import config, session_util
import base64

base_bp = Blueprint('base', __name__)


def is_valid_cid(cid):
    import re
    return True if re.match("^[0-9A-Za-z_\-.]+$", cid) else False

@base_bp.route('/subscribe/<string:client_id>', methods=['GET'])
def subscribe(client_id):
    if not is_valid_cid(client_id):
        return ""
    import os
    link = config.prepare_link_dir()
    link_file = "%s/%s"%(link, client_id)
    if not link or not os.path.exists(link_file):
        return ""
    s = ''
    with open(link_file, 'r') as fd:
        s = fd.read()
    return base64.encodebytes(s.encode()).decode().strip()

@base_bp.route('/')
def index():
    if session_util.is_login():
        return redirect(url_for('v2ray.index'))
    from init import common_context
    return render_template('index.html',
                           login_title=config.get_login_title(),
                           **common_context)


@base_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user is not None:
        session_util.login_success(user)
        return jsonify(Msg(True, gettext('login success')))
    return jsonify(Msg(False, gettext('username or password wrong')))


@base_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session_util.logout()
    return redirect(url_for('base.index'))


@base_bp.route('/robots.txt')
def robots():
    return Response('User-agent: *\n' + 'Disallow: /', 200, headers={
        'Content-Type': 'text/plain'
    })


def init_user():
    if User.query.count() == 0:
        db.session.add(User('admin', 'admin'))
        db.session.commit()


init_user()
