import os

from flask import render_template, request, current_app, flash, redirect, url_for, send_from_directory
from flask_ckeditor import upload_fail, upload_success
from flask_login import current_user

from sites.extensions import db
from sites.forms.blog import CategoryForm, PostForm
from sites.models.blog import Post, Category, PostComment
from sites.blueprints.main import main_bp
from sites.utils import allowed_file


@main_bp.route('/blogs')
def blog_index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('main/blog/index.html', pagination=pagination, posts=posts)


#文章分类
@main_bp.route('/category/new', methods=['GET', 'POST'])
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        user = current_user._get_current_object()
        category = Category(name=name, author=user)
        db.session.add(category)
        db.session.commit()
        flash('已创建分类', 'success')
        # return redirect(url_for(''))
    return render_template('main/blog/new_category.html', form=form)

#创建文章
@main_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        author = current_user._get_current_object()
        post = Post(title=title,body=body, category=category, author=author)
        db.session.add(post)
        db.session.commit()
        flash('文章已创建', 'success')
        return redirect(url_for('.show_post', post_id=post.id))
    return render_template('main/blog/new_post.html', form=form)

#ckeditor图片上传
@main_bp.route('/blog_img', methods=['POST'])
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('只允许图片')
    f.save(os.path.join(current_app.config['BLOG_UPLOAD_PATH'], f.filename))
    url = url_for('.get_ck_image', filename=f.filename)
    return upload_success(url, f.filename)

@main_bp.route('/blog_img/<path:filename>')
def get_ck_image(filename):
    return send_from_directory(current_app.config['BLOG_UPLOAD_PATH'], filename)


#文章显示
@main_bp.route('/post/<int:post_id>', methods=['GET','POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)

    # page = request.args.get('page', 1, type=int)
    # per_page = current_app.config['ALBUMY_COMMENT_PER_PAGE']
    # pagination = PostComment.query.with_parent(post).filter_by(reviewed=True).order_by(PostComment.timestamp.asc()).paginate(page,per_page)
    # comments = pagination.items
    return render_template('main/blog/post.html', post=post)