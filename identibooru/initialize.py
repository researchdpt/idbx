
import identibooru, logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from time import strftime
import traceback

# Pages
import identibooru.views.base

# Search
import identibooru.views.search

# Auth
import identibooru.views.register
import identibooru.views.login
import identibooru.views.logout
import identibooru.views.change_password
import identibooru.views.change_options

# Users
import identibooru.views.user

#Run the main app...
if __name__ == '__main__':
    identibooru.app.run(threaded=True)
