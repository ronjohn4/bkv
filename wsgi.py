from app import app


if __name__ == "__main__":
    # bag.jinja_env.auto_reload = True
    app.run(port=5000, debug=True)
    # bag.run(host='0.0.0.0')
