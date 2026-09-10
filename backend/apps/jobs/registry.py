from apps.pipeline import handlers

HANDLERS = {
    "parse-import": handlers.parse_import,
    "generate-context": handlers.generate_context_job,
}