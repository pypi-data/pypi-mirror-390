"""FlaskIt - Modern Flask Framework"""

from flaskit.app import FlaskIt, create_app
from flaskit.routing import Route
from flaskit.data_loader import get_data, all_data
from flaskit.discord import discord, colors as discord_colors
from flaskit.watch import watch

# Réexporter les fonctions Flask courantes
from flask import (
    request, jsonify, redirect, url_for, 
    session, flash, abort, make_response,
    send_file, send_from_directory
)

__version__ = '0.2.4'
__all__ = [
    'FlaskIt',
    'create_app',
    'Route',
    'get_data',
    'all_data',
    'discord',
    'discord_colors',
    'watch',
    'request',
    'jsonify',
    'redirect',
    'url_for',
    'session',
    'flash',
    'abort',
    'make_response',
    'send_file',
    'send_from_directory',
]
