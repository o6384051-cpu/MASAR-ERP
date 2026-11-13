app_name = "masar_erp"
app_title = "MASAR ERP"
app_publisher = "MASAR"
app_description = "Arabic-ready multi-company ERP extensions"

# Keep this app additive: do not override ERPNext accounting controllers.
# Chat records and their linked files are visible only to room members.
has_permission = {
    "MASAR Chat Room": "masar_erp.permissions.chat_room_has_permission",
    "MASAR Chat Message": "masar_erp.permissions.chat_message_has_permission",
    "File": "masar_erp.permissions.file_has_permission",
}

permission_query_conditions = {
    "MASAR Chat Room": "masar_erp.permissions.chat_room_query",
    "MASAR Chat Message": "masar_erp.permissions.chat_message_query",
}
