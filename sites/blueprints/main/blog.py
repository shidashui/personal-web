import os

from flask import render_template, request, current_app, flash, redirect, url_for, send_from_directory, abort
from flask_ckeditor import upload_fail, upload_success
from flask_login import current_user, login_required

from sites.decorators import permission_required,confirm_required
from sites.forms.main import CommentForm
from sites.extensions import db
from sites.forms.blog import CategoryForm, PostForm
from sites.models.blog import Post, Category, PostComment
from sites.blueprints.main import main_bp
from sites.utils import allowed_file,flash_errors


@main_bp.route('/blogs')
@login_required
def blog_index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('main/blog/index.html', pagination=pagination, posts=posts)


#文章分类
@main_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('只允许图片')
    f.save(os.path.join(current_app.config['BLOG_UPLOAD_PATH'], f.filename))
    url = url_for('.get_ck_image', filename=f.filename)
    return upload_success(url, f.filename)

@main_bp.route('/blog_img/<path:filename>')
@login_required
def get_ck_image(filename):
    return send_from_directory(current_app.config['BLOG_UPLOAD_PATH'], filename)


#文章显示
@main_bp.route('/post/<int:post_id>', methods=['GET','POST'])
@login_required
def show_post(post_id):
    post = Post.query.get_or_404(post_id)

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_COMMENT_PER_PAGE']
    pagination = PostComment.query.with_parent(post).order_by(PostComment.timestamp.asc()).paginate(page,per_page)
    comments = pagination.items

    comment_form = CommentForm()
    return render_template('main/blog/post.html', post=post, pagination=pagination, comment_form=comment_form, comments=comments)


#设置评论功能
@main_bp.route('/set-post-comment/<int:post_id>', methods=['POST'])
@login_required
def set_post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)

    if post.can_comment:
        post.can_comment = False
        flash('已禁止评论', 'info')
    else:
        post.can_comment = True
        flash('可以评论', 'info')
    db.session.commit()
    return redirect(url_for('.show_post', post_id=post_id))

#新评论
@main_bp.route('/post/<int:post_id>/comment/new', methods=['POST'])
@login_required
@permission_required('COMMENT')
def new_post_comment(post_id):
    post = Post.query.get_or_404(post_id)

    page = request.args.get('page', 1, type=int)
    form = CommentForm()
    if form.validate_on_submit():
        body = form.body.data
        author = current_user._get_current_object()
        comment = PostComment(body=body, author=author, post=post)

        replied_id = request.args.get('reply')
        if replied_id:
            comment.replied = PostComment.query.get_or_404(replied_id)
            #提醒功能
        db.session.add(comment)
        db.session.commit()
        flash('已评论', 'success')

    flash_errors(form)
    return redirect(url_for('.show_post', post_id=post_id, page=page))


#举报评论
@main_bp.route('/report/post_comment/<int:comment_id>', methods=['POST'])
@login_required
@confirm_required
def report_post_comment(comment_id):
    comment = PostComment.query.get_or_404(comment_id)
    comment.flag += 1
    db.session.commit()
    flash('已举报评论', 'success')
    return redirect(url_for('.show_post', post_id=comment.post_id))

#评论回复
@main_bp.route('/reply/post_comment/<int:comment_id>',methods=['POST'])
@login_required
@permission_required('COMMENT')
def reply_post_comment(comment_id):
    comment = PostComment.query.get_or_404(comment_id)
    return redirect(url_for('.show_post', post_id = comment.post_id, reply=comment_id, author=comment.author.name)+'#comment-form')

#删除评论
@main_bp.route('/delete/post_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_post_comment(comment_id):
    comment = PostComment.query.get_or_404(comment_id)
    if current_user != comment.author and current_user != comment.post.author:
        abort(403)

    db.session.delete(comment)
    db.session.commit()
    flash('已删除评论', 'info')
    return redirect(url_for('.show_post', post_id=comment.post_id))