from blog_app import app, db, mail
from flask import render_template, session, flash, redirect, url_for, request,jsonify, g
from blog_app.models import User, Post, Like, Comment, Suggesstion
from blog_app.forms import SignUpForm, LoginForm, NewPost, CommentForm, UpdatePostForm, ReplyForm, SuggesstionForm,UpdateAccountForm
from blog_app.email import send_email
from flask_mail import Message
from blog_app.token import generate_token, confirm_token
from flask_login import login_user, login_required, current_user, logout_user
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url





@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = generate_token(form.email.data)
        verify_url = url_for('verify_email',token=token, _external=True)
        html = render_template('verify_email.html', confirm_url=verify_url)
        subject = "Please confirm your email"
        send_email(form.email.data,subject, html)
        flash("An Email has been sent to your email please verify your account!!",
              category="success")
        return redirect(url_for('home'))
    return render_template("signup.html", title='Sign Up', form=form)


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account Updated', category='success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)



@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@admin.com":
            user = User.query.filter_by(email=form.email.data).first()
            password_correct = user.password == form.password.data
            if password_correct:
                login_user(user)
                if current_user.is_authenticated:
                    flash("Login Successfull", category="success")
                    return redirect(url_for('dashboard'))
                else:
                    flash("Incorrct Credentials",category='danger')
                    return redirect(url_for('login'))
        else:
            user = User.query.filter_by(email=form.email.data).first()
            password_correct = user.password == form.password.data
            if password_correct:
                login_user(user)
                if current_user.is_authenticated:
                    flash("Login Successfull", category="success")
                    return redirect(url_for('dashboard'))
            else:
                flash("Incorrct Credentials",category='danger')
                return redirect(url_for('login'))
            

    return render_template('login.html', title='Login', form=form)


@app.route("/verify-email/<token>",methods=['GET','POST'])
def verify_email(token):
    try:
        email = confirm_token(token)
    except:
        flash("Link is invalid", category='danger')

    user = User.query.filter_by(email=email).first_or_404()

    if user.verified:
        flash("Account already verified",category='success')
        return redirect(url_for('login'))
    else:
        user.verified = True
        db.session.add(user)
        db.session.commit()
        flash("You account has been verified",category='success')
        return redirect(url_for('login'))
    

@app.route("/new-post", methods=['GET','POST'])
@login_required
def new_post():
    form = NewPost()
    if form.validate_on_submit():
        if form.attachment.data:
            picture_url = upload(form.attachment.data)['url']
            post = Post(title=form.title.data,content=form.content.data,attachement=picture_url,user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("New Post Created Successfully it will be live once its verified by the Admins",category='success')
            return redirect(url_for('dashboard'))
        if not form.attachment.data:
            post = Post(title=form.title.data,content=form.content.data,attachement=None,user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("New Post Created Successfully it will be live once its verified by the Admins",category='success')
            return redirect(url_for('dashboard'))

    return render_template("newpost.html",form=form)
    

@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    form = CommentForm()
    posts = Post.query.all()
    if form.validate_on_submit():
        if request.method == 'POST':
            user_id = current_user.id
            parent_id = request.form.get('post-id')
            parent_type = request.form.get('parent-type')
            comment = Comment(content=form.comment.data,user_id=user_id,parent_id=parent_id,parent_type=parent_type)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('dashboard.html',title=current_user.username,posts=posts, form=form,Comments=Comment,Likes=Like,Users=User,suggestions=Suggesstion)
                                                                                                 
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/give-suggesstion/<int:userId>/<int:postId>", methods=['POST','GET'])
@login_required
def give_suggesstion(userId, postId):
    form = SuggesstionForm()
    post = Post.query.get(postId)
    suggestions = Suggesstion.query.filter_by(post_id = postId).all()
    if form.validate_on_submit():
        suggestion = form.suggesstion.data
        data = Suggesstion(user_id=current_user.id, post_id=postId, content=suggestion)
        db.session.add(data)
        db.session.commit()
        print(suggestion)
        return redirect(url_for('give_suggesstion', userId=current_user.id, postId=postId))
    return render_template("give_suggesstion.html",post=post, form=form, suggestions=suggestions,comments=Comment)


@app.route("/reject-suggesstion/<int:sId>/<int:userId>/<int:postId>")
@login_required
def reject_suggesstion(sId, userId, postId):
    data = Suggesstion.query.filter_by(s_id=sId, user_id=userId, post_id=postId).first()
    comments = Comment.query.filter_by(parent_id=sId, parent_type='suggestion').all()
    for c in comments:
        db.session.delete(c)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('give_suggesstion',userId=userId, postId=postId))


@app.route("/like", methods=['POST'])
@login_required
def like():
    if request.method == "POST":
        postId = int(request.form.get('postId'))
        userId = int(request.form.get('userId'))
        parentType = request.form.get('parentType')
        isLiked = Like.query.filter_by(user_id=userId,parent_id=postId,parent_type=parentType).first()
        if not isLiked:
            liked = Like(user_id=userId,parent_id=postId,parent_type=parentType)
            db.session.add(liked)
            db.session.commit()
            likes_count = len(Like.query.filter_by(parent_id=postId,parent_type="post").all())
            return jsonify({"mess":"hello", 'isLiked':True, "likesCount": likes_count})
        
        if isLiked:
            Like.query.filter_by(user_id=userId,parent_id=postId,parent_type=parentType).delete()
            db.session.commit()
            likes_count = len(Like.query.filter_by(parent_id=postId,parent_type="post").all())
            return jsonify({"mess":"bye", "isLiked":False, "likesCount": likes_count})

        
        


@app.route("/delete/<int:postId>")
@login_required
def delete_post(postId):
    post = Post.query.get(postId)
    comments = Comment.query.filter_by(parent_id=postId).all()
    likes = Like.query.filter_by(parent_id=postId).all()
    for comment in comments:
        db.session.delete(comment)

    for like in likes:
        db.session.delete(like)

    db.session.delete(post)
    db.session.commit()
    flash("Post Deleted Successfully", category='success')
    return redirect(url_for('dashboard'))


@app.route("/update-post/<int:postId>",methods=['GET','POST'])
@login_required
def update_post(postId):
    form = UpdatePostForm()
    post = Post.query.get_or_404(postId)
    
    
    if form.validate_on_submit():
        if form.attachment.data:
            picture_url = upload(form.attachment.data)['url']
            post.attachement = picture_url
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post Updated Successfully",category='success')
        return redirect(url_for('dashboard'))
    
    form.title.data = post.title
    form.content.data = post.content

    return render_template('update_post.html',title='Update Post', form=form)


@app.route("/reply/<int:parentId>/<string:parentType>/<int:postId>",methods=['GET','POST'])
@login_required
def reply(parentId,parentType,postId):
    comment = Comment.query.filter_by(comment_id=parentId).first()
    suggestion = Suggesstion.query.filter_by(s_id = parentId).first()

    if parentType == 'comment':
        data = comment
    elif parentType == 'suggestion':
        data = suggestion
    form = ReplyForm()
    if form.validate_on_submit():
        print(form.reply.data)
        newReply = Comment(user_id=current_user.id, parent_id=parentId,parent_type=parentType,content=form.reply.data)
        db.session.add(newReply)
        db.session.commit()
        flash("Replied Successfully",category="success")
        if parentType == 'comment':
            return redirect(url_for('dashboard'))
        elif parentType == 'suggestion':
            return redirect(url_for('give_suggesstion',userId=current_user.id, postId=postId))

    return render_template('reply.html', title='Reply', form=form,comment_content = data.content)


@app.route("/delete-reply/<int:id>/<int:parentId>/<string:parentType>/<string:postId>", methods=['POST',"GET"])
def delete_reply(id, parentId, parentType,postId):
    comment = Comment.query.filter_by(comment_id=id, parent_id=parentId, parent_type=parentType).first()
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('give_suggesstion',userId=current_user.id, postId=postId))


@app.route("/approve-post",methods=["POST"])
def approve_post():
    if request.method=="POST":
        if int(request.form.get('postId')):
            postId = int(request.form.get('postId'))
            post = Post.query.get(postId)
            if post.approved:
                post.approved = False
                db.session.commit()
                return jsonify({"approved":False})
            elif not post.approved:
                post.approved = True
                db.session.commit()
                return jsonify({"approved":True})
    return redirect(url_for('dashboard'))


@app.route("/update-user-role",methods=["POST"])
def update_user_role():
    if request.method == "POST":
        if request.form:
            userId  = int(request.form.get('userId'))
            userRole = request.form.get('role')
            user = User.query.get(userId)
            user.role = userRole
            db.session.commit()
            return jsonify({"role":user.role})
    return redirect(url_for('dashboard'))

