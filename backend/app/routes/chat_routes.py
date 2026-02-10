"""Thin chat routes – URL mapping only, delegates to controllers."""
from flask import Blueprint
from backend.app.controllers.chat_controller import (
    handle_chat,
    handle_get_history,
    handle_get_history_by_device,
    handle_reset_history,
    handle_reset_all,
)

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('', methods=['POST'])
def chat():
    return handle_chat()


@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    return handle_get_history(session_id)


@chat_bp.route('/history/device/<device_token>', methods=['GET'])
def get_chat_history_by_device(device_token):
    return handle_get_history_by_device(device_token)


@chat_bp.route('/reset', methods=['DELETE'])
def reset_chat_history():
    return handle_reset_history()


@chat_bp.route('/reset-all', methods=['DELETE'])
def reset_all_chat_history():
    return handle_reset_all()
