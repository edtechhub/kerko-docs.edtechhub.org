import logging
from logging.config import dictConfig

# Set root logger to log to sys.stderr.
# Note: this must be set before the Flask app gets created.
# Ref: https://flask.palletsprojects.com/en/1.1.x/logging/#basic-configuration
dictConfig(
    {
        'version': 1,
        'formatters':
            {
                'default':
                    {
                        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                    }
            },
        'handlers':
            {
                'wsgi':
                    {
                        'class': 'logging.StreamHandler',
                        'stream': 'ext://flask.logging.wsgi_errors_stream',
                        'formatter': 'default'
                    }
            },
        'root':
            {
                'level': 'INFO',
                'handlers': ['wsgi']
            },
    }
)


def init_app(app):
    root = logging.getLogger()
    if app.config.get('LOGGING_HANDLER') == 'syslog':
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler(app.config.get('LOGGING_ADDRESS', '/dev/log'))
        syslog_handler.setFormatter(
            logging.Formatter(
                app.config.get(
                    'LOGGING_FORMAT', '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
                )
            )
        )
        root.addHandler(syslog_handler)
    if 'LOGGING_LEVEL' in app.config:
        root.setLevel(app.config['LOGGING_LEVEL'])
