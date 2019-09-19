from flask import render_template, request, current_app

from sites.models.blog import Post
from sites.blueprints.main import main_bp



@main_bp.route('/blogs')
def blog_index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('main/blog/index.html', pagination=pagination, posts=posts)

#创建文章
@main_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    pass