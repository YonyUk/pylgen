import os
from typing import Dict, List
from mkdocs.plugins import event_priority
from pathlib import Path
import logging

logger = logging.getLogger(f"mkdocs.hooks.{__name__}")

@event_priority(200)
def on_config(config):
    nav = config.get('nav', [])
    if not nav:
        return config

    sections_deep  = {}   # path -> deep
    sections_name  = {}   # path -> sección contenedora
    sections_title = {}   # path -> título de página (label del nav)

    def walk(sections, deep=1, parent_section=""):
        for section in sections:
            for label, content in section.items():
                if isinstance(content, str):
                    normalized = content.replace('\\', '/')
                    effective_section = label if deep == 1 else parent_section
                    sections_deep[normalized]  = deep
                    sections_name[normalized]  = effective_section
                    sections_title[normalized] = label
                    if deep > 1:
                        base = normalized.rsplit('/', 1)[-1]
                        if base not in sections_deep:
                            sections_deep[base]  = deep
                            sections_name[base]  = effective_section
                            sections_title[base] = label
                else:
                    walk(content, deep + 1, label)

    walk(nav)

    template_dir = None
    for plugin in config.get('plugins', []):
        if hasattr(plugin, 'config') and plugin.__class__.__name__ == 'TocMdPlugin':
            template_dir = plugin.config.get('template_dir_path')
            break
    if template_dir is None:
        template_dir = 'docs/mkdocs_extras/templates'

    os.makedirs(template_dir, exist_ok=True)
    out_path = os.path.join(template_dir, '_nav_map.j2')

    with open(out_path, 'w', encoding='utf-8') as f:
        for var_name, data in (
            ('sections_deep',  sections_deep),
            ('sections_name',  sections_name),
            ('sections_title', sections_title),
        ):
            f.write(f'{{% set _ = ns.{var_name}.update({{\n')
            for k, v in data.items():
                f.write(f"    {repr(k)}: {repr(v)},\n")
            f.write('}) %}\n')

    return config

GENERATED_FILES = {
    "table_of_contents.md",
    "_nav_map.j2"
}

def on_serve(server, config, builder):
    docs_dir = Path(config.docs_dir).resolve()

    # 1. Localizar el handler que vigila docs_dir
    try:
        handler = next(
            handlers.copy().pop()
            for watch, handlers in server.observer._handlers.items()
            if Path(watch.path).resolve() == docs_dir
        )
    except StopIteration:
        logger.warning("ON_SERVE: watcher for docs_dir not found")
        return server

    # 2. Envolver el callback original
    original_callback = handler.on_any_event

    def callback_wrapper(event):
        src = getattr(event, "src_path", None)
        if src:
            name = Path(src).name
            if name in GENERATED_FILES:
                return  # descartar el evento silenciosamente
        return original_callback(event)

    # 3. Sustituir el callback en el handler ya existente
    handler.on_any_event = callback_wrapper

    logger.info("ON_SERVE: filter for generated files activated")
    return server