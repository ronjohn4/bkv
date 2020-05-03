# todo - Create Test Harness
# Load on Start
# Web based page
# Display all Keyvals return
# Allow Instance to be set in UI
# Reload button
# Example of use of one keyval in code

# todo - enforce data types in the UI
# todo - make sure all names are unique within their bag
# todo - add logging
# todo - cascade delete to audit table
# todo - filter bags on current_user

from app import app


if __name__ == "__main__":
    # bag.jinja_env.auto_reload = True
    app.run(port=5000, debug=True)
    # bag.run(host='0.0.0.0')
