import os
from flask import Flask, render_template, send_from_directory, request
from dotenv import load_dotenv
from app.python.posts.postPageGenerator import PostPageGenerator
from app.python.posts.comment import Comment
from app.python.posts.post import Post
from app.python.gallery.galleryController import GalleryController
from app.python.gallery.image import Image
from PIL import Image as IMG
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from . import dbex
#from app.db import get_db

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}'.format(
    user=os.getenv('POSTGRES_USER'),
    passwd=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('POSTGRES_HOST'),
    port=5432,
    table=os.getenv('POSTGRES_DB'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class UserModel(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"



#app.config['DATABASE'] = os.path.join(os.getcwd(), 'flask.sqlite')
#db.init_app(app)

postGenerator = PostPageGenerator()
galleryGenerator = GalleryController()

UPLOAD_FOLDER = '../app/static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html', title="Gamer Fellowship", url=os.getenv("URL"))

@app.route('/blog')
def blog():
    postIndex = postGenerator.postIndex
    commentIndex = postGenerator.commentIndex
    post = postGenerator.posts[postIndex] if postIndex > -1 and postIndex < len(postGenerator.posts) else Post()
    comment = postGenerator.postComments[commentIndex] if commentIndex > -1 and commentIndex < len(postGenerator.postComments) else Comment()

    #Template
    postCategory = post.postCategory
    postTitle = post.postTitle
    postDate = post.postDate
    postBody = post.postBody
    commentAuthor = comment.commentAuthor
    commentDate = comment.commentDate
    commentBody = comment.commentBody
    LikeCount = post.postLikeCount
    currentComment = commentIndex + 1
    totalComments = len(postGenerator.postComments)

    title = post.postTitle
    return render_template('blogEntry.html', postCategory = postCategory, 
    postTitle = title, postDate = postDate, postBody = postBody, commentAuthor = commentAuthor,\
    commentDate = commentDate, commentBody = commentBody, LikeCount = LikeCount, currentComment = currentComment, totalComments = totalComments )

@app.route("/nextPost")
def loadNextPost():
    postIndex = postGenerator.postIndex
    postIndex = postIndex + 1 if postIndex  + 1 < len(postGenerator.posts) else 0
    postGenerator.postIndex = postIndex
    postGenerator.obtainPostCommentInfo()
    return blog()

@app.route("/prevPost")
def loadPrevPost():
    postIndex = postGenerator.postIndex
    postIndex = postIndex - 1 if postIndex  -1 > -1 else len(postGenerator.posts) - 1
    postGenerator.postIndex = postIndex
    postGenerator.obtainPostCommentInfo()
    return blog()

@app.route("/nextComment")
def loadNextComment():
    commentIndex = postGenerator.commentIndex
    commentIndex = commentIndex + 1 if commentIndex  + 1 < len(postGenerator.postComments) else 0
    postGenerator.commentIndex = commentIndex
    return blog()

@app.route("/prevComment")
def loadPrevComment():
    commentIndex = postGenerator.commentIndex
    commentIndex = commentIndex - 1 if (commentIndex  -1) > -1 else len(postGenerator.postComments) - 1
    postGenerator.commentIndex = commentIndex
    return blog()

@app.route("/giveLove")
def giveLove():
    postIndex = postGenerator.postIndex
    post = postGenerator.posts[postIndex]
    postGenerator.DB.addALike(post)
    postGenerator.posts[postIndex].postLikeCount += 1
    return blog()


@app.route("/commentForm", methods=["GET", "POST"])
def addCommentForm():
    return render_template("addComment.html")

@app.route("/postForm", methods=["GET", "POST"])
def addPostForm():
    return render_template("addPost.html")

@app.route("/createComment", methods=["GET", "POST"])
def createComment():
    author = request.form["commentAuthor"]
    date = request.form["commentDate"]
    body = request.form["commentBody"]
    arrayIndex = len(postGenerator.postComments)
    commentToAdd = Comment(arrayIndex, author, body, date, -1)
    postGenerator.addComment(commentToAdd)
    return blog()

@app.route("/createPost", methods = ["GET", "POST"])
def createPost():
    title = request.form["postTitle"]
    category = request.form["postCategory"]
    date = request.form["postDate"]
    body = request.form["postBody"]
    arrayIndex = len(postGenerator.postComments)
    postToAdd = Post(arrayIndex, -1, title, body, category, date)
    postGenerator.addPost(postToAdd)
    return blog()

@app.route("/character")
def character():
    return render_template('character.html', title="About Us", url=os.getenv("URL"))

@app.route("/gallery")
def gallery():
    imageIndex = galleryGenerator.imageIndex
    galleryImage = galleryGenerator.images[imageIndex] if imageIndex > -1 and imageIndex < len(galleryGenerator.images) else Image()
    print(imageIndex)
    #Template
    imageFile = galleryGenerator.formatter.decode_img(galleryImage.imageFile)
    if imageFile != None:
        
        imageTitle = galleryImage.imageTitle
        imageDescription = galleryImage.imageDescription
        imageFile.save('C:\\Users\\angel\\OneDrive\\Desktop\\MLH\\3.3.1.3-flask-blog' + 'app\\static\\img\\galleryImageTemplate.jpg')
  
    else:
        print("NOPE")


    return render_template('gallery.html', imageTitle = imageTitle, imageDescription = imageDescription,
            currentImage = imageIndex + 1, totalImages = len(galleryGenerator.images))

@app.route("/nextImage")
def loadNextImage():
    imageIndex = galleryGenerator.imageIndex
    imageIndex = imageIndex + 1 if (imageIndex  + 1) < len(galleryGenerator.images) else 0
    galleryGenerator.imageIndex = imageIndex
    return gallery()

@app.route("/prevImage")
def loadPrevImage():
    imageIndex = galleryGenerator.imageIndex
    imageIndex = imageIndex - 1 if (imageIndex  - 1) > -1  else len(galleryGenerator.images) - 1
    galleryGenerator.imageIndex = imageIndex
    return gallery()

@app.route("/imageForm", methods=["GET", "POST"])
def addImageForm():
    return render_template('addImage.html')

@app.route('/health')
def health():
    return "Works"

@app.route("/createImage", methods=["GET", "POST"])
def createImage():
    title = request.form["imageTitle"]
    description = request.form["imageDescription"]
    file = request.files['file']
    
    encoded_file = galleryGenerator.formatter.encode_img(IMG.open(file))
    imageToAdd = Image(-1,encoded_file,title,description)
    galleryGenerator.addImage(imageToAdd)
    return gallery()

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif UserModel.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."

        if error is None:
            new_user = UserModel(username, generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return f"User {username} created successfully"
        else:
            return error, 418

    return render_template('register.html', title="Register")


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        user = UserModel.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            return "Login Successful", 200
        else:
            return error, 418

    
    
    return render_template('login.html', title="Login")