from flask import Flask, render_template, send_file

from src.web_app.charts import get_main_image

app = Flask(__name__)


@app.route('/')
def main():
    """Entry point; the view for the main page"""
    return render_template('main.html')


@app.route('/main_image.png')
def main_image():
    img = get_main_image()
    return send_file(img, mimetype='image/png', cache_timeout=0)


if __name__ == '__main__':
    app.run()
