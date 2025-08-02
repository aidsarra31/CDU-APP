from flask import Flask, render_template
from prod import prod_bp

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Enregistrement du blueprint
app.register_blueprint(prod_bp)

@app.route('/')
def index():
    return render_template('prod.html')

if __name__ == '__main__':
    app.run(debug=True)
