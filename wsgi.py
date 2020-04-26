# todo - Create Test Harness
# Load on Start
# Web based page
# Display all Keyvals return
# Allow Instance to be set in UI
# Reload button
# Example of use of one keyval in code

# Todo - Expose API for pull by app (json response(
# todo - enforce data types in the UI
# todo - default cursor position on form load

from app import app


if __name__ == "__main__":
    # bag.jinja_env.auto_reload = True
    app.run(port=5000, debug=True)
    # bag.run(host='0.0.0.0')
