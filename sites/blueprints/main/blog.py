from flask import render_template, request, current_app, flash, redirect
from flask_login import current_user

from sites.extensions import db
from sites.forms.blog import CategoryForm
from sites.models.blog import Post, Category
from sites.blueprints.main import main_bp



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
    pass