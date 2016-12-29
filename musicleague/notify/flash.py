from flask import flash


def flash_info(message):
    flash(message, "info")


def flash_success(message):
    flash(message, "success")


def flash_warning(message):
    flash(message, "warning")


def flash_error(message):
    flash(message, "danger")
