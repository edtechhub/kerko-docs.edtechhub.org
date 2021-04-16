from flask_assets import Bundle, Environment


scss_styles = Bundle(  # pylint: disable=invalid-name
    'src/app/scss/styles.scss',
    filters='libsass',
    depends='**/*.scss',
    output='build/css/styles.css',
)
css_styles = Bundle(  # pylint: disable=invalid-name
    scss_styles,
    filters='autoprefixer6',
    output='dist/css/styles.css',
)
css_min_styles = Bundle(  # pylint: disable=invalid-name
    scss_styles,
    filters='autoprefixer6,cleancss',
    output='dist/css/styles.min.css',
)
common_js = Bundle(  # pylint: disable=invalid-name
    'src/vendor/jquery/jquery.min.js',
    'src/vendor/popper.js/popper.min.js',
    'src/vendor/bootstrap/index.js',
    'src/vendor/bootstrap/util.js',
    'src/vendor/bootstrap/collapse.js',  # For navbar.
    'src/vendor/bootstrap/alert.js',
    'src/vendor/bootstrap/button.js',
    'src/vendor/bootstrap/dropdown.js',
    'src/vendor/bootstrap/modal.js',
    'src/vendor/bootstrap/tab.js',
    filters='jsmin',
    output='dist/js/common.min.js',
)
search_js = Bundle(  # pylint: disable=invalid-name
    'kerko/kerko/js/search.js',
    filters='jsmin',
    output='dist/js/search.min.js',
)
item_js = Bundle(  # pylint: disable=invalid-name
    'kerko/kerko/js/item.js',
    filters='jsmin',
    output='dist/js/item.min.js',
)
print_js = Bundle(  # pylint: disable=invalid-name
    'kerko/kerko/js/print.js',
    filters='jsmin',
    output='dist/js/print.min.js',
)


class EnvironmentWithBundles(Environment):
    """
    An assets environment that registers its own bundles.

    Registering the bundles at `init_app` time lets it refer to the app config.
    """

    def init_app(self, app):
        super().init_app(app)
        if app.config['ASSETS_DEBUG']:
            assets.register('css_styles', css_styles)
        else:
            assets.register('css_styles', css_min_styles)
        assets.register('common_js', common_js)
        assets.register('search_js', search_js)
        assets.register('item_js', item_js)
        assets.register('print_js', print_js)


assets = EnvironmentWithBundles()  # pylint: disable=invalid-name
