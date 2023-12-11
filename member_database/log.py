import logging
from logging.handlers import SMTPHandler, TimedRotatingFileHandler


def setup_logging(app):
    if not app.debug and app.config["MAIL_SERVER"]:
        if app.config["MAIL_USE_SSL"]:
            app.logger.warning("SSL not supported by logging.SMTPHandler")
            return

        credentials = None
        if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
            credentials = (
                app.config["MAIL_USERNAME"],
                app.config["MAIL_PASSWORD"],
            )

        secure = None
        if app.config["MAIL_USE_TLS"]:
            secure = ()

        mail_handler = SMTPHandler(
            mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            fromaddr=app.config["MAIL_SENDER"],
            toaddrs=app.config["ADMIN_MAIL"],
            subject="PeP Database Failure",
            credentials=credentials,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if app.config.get("LOG_FILE"):
        handler = TimedRotatingFileHandler(app.config["LOG_FILE"], when="midnight")
        formatter = logging.Formatter(
            fmt="%(asctime)s|%(levelname)s|%(name)s|%(message)s",
            datefmt="%Y-%m-%dT%H:%M:%s",
        )
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
