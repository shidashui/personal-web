import os

from flask import render_template, request, current_app, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import func

from sites.extensions import db
from sites.models import Photo, Tag, Collect, Notification, Follow, User
from sites.decorators import confirm_required, permission_required
from sites.utils import rename_image, resize_image, redirect_back

from sites.blueprints.main import main_bp


#获取正在关注用户的图片显示在首页
#通过连表查询
#连表查询性能要优于子查询


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
        pagination = Photo.query.join(Follow, Follow.followed_id == Photo.author_id) \
                        .filter(Follow.follower_id == current_user.id) \
                        .order_by(Photo.timestamp.desc()).paginate(page, per_page)
        photos = pagination.items
    else:
        pagination = None
        photos = None
    tags=Tag.query.join(Tag.photos).group_by(Tag.id).order_by(func.count(Photo.id).desc()).limit(10)
    return render_template('main/index.html', pagination=pagination, photos=photos, tags=tags, Collect=Collect)

@main_bp.route('/explore')
def explore():
    photos = Photo.query.order_by(func.random()).limit(12)
    return render_template('main/explore.html', photos=photos)


@main_bp.route('/upload', methods=['GET','POST'])
@login_required                 #验证登陆状态
@confirm_required               #验证确认状态
@permission_required('UPLOAD')  #验证权限
def upload():
    # print(request.files)
    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')           #获取文件
        filename = rename_image(f.filename)     #生成随机文件名
        f.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename))    #保存文件
        filename_s = resize_image(f, filename, current_app.config['ALBUMY_PHOTO_SIZE']['small'])
        filename_m = resize_image(f, filename, current_app.config['ALBUMY_PHOTO_SIZE']['medium'])
        photo = Photo(
            filename=filename,
            filename_s=filename_s,
            filename_m=filename_m,
            author=current_user._get_current_object()
        )
        db.session.add(photo)
        db.session.commit()
    return render_template('main/upload.html')





#提醒中心
@main_bp.route('/notifications')
@login_required
def show_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_NOTIFICATION_PER_PAGE']
    notifications = Notification.query.with_parent(current_user)
    filter_rule = request.args.get('filter')
    if filter_rule == 'unread':
        notifications = notifications.filter_by(is_read=False)

    pagination = notifications.order_by(Notification.timestamp.desc()).paginate(page, per_page)
    notifications = pagination.items
    return render_template('main/notifications.html', pagination=pagination,notifications=notifications)

@main_bp.route('/notifications/read/all', methods=['POST'])
@login_required
def read_all_notification():
    for notification in current_user.notifications:
        notification.is_read = True
    db.session.commit()
    flash('全部已读', 'success')
    return redirect(url_for('.show_notifications'))


@main_bp.route('/notification/read/<int:notification_id>', methods=['POST'])
@login_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if current_user != notification.receiver:
        abort(403)

    notification.is_read = True
    db.session.commit()
    flash('已读', 'success')
    return redirect(url_for('.show_notifications'))


#全局搜索
@main_bp.route('/search')
def search():
    q = request.args.get('q', '')
    if q == '':
        flash('请输入内容','warning')
        return redirect_back()

    category = request.args.get('category', 'photo')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_SEARCH_RESULT_PER_PAGE']
    if category == 'user':
        pagination = User.query.whooshee_search(q).paginate(page, per_page)
    elif category == 'tag':
        pagination = Tag.query.whooshee_search(q).paginate(page, per_page)
    else:
        pagination = Photo.query.whooshee_search(q).paginate(page, per_page)
    results = pagination.items
    return render_template('main/search.html', q=q, results=results, pagination=pagination, category=category)