"""Application factory for the local study-materials lab."""

from pathlib import Path

from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / "lab.sqlite"),
        DEBUG=False,
        TESTING=False,
    )
    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    from app.main import bp as main_bp
    from app.reflected import bp as reflected_bp
    from app.stored import bp as stored_bp
    from app.dom import bp as dom_bp

    for blueprint in (main_bp, reflected_bp, stored_bp, dom_bp):
        app.register_blueprint(blueprint)

    # TV2 will supply app.db.init_app; stage 1 does not open/create a database.
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        # Keep protocol headers, including Allow, from Werkzeug's response.
        response = error.get_response()
        response.set_data(render_template("errors/405.html"))
        response.content_type = "text/html; charset=utf-8"
        return response

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    return app
