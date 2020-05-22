# todo - enforce data types in the UI
# todo - make sure all names are unique within their bag
# todo - add logging
# todo - cascade delete to audit table
# todo - filter bags on current_user


from app import app


if __name__ == "__main__":
    app.run(port=5000, debug=True)
