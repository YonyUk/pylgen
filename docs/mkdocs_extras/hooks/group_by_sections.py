import os
from typing import Dict, List
from mkdocs.plugins import event_priority

@event_priority(200)
def on_config(config):
    nav = config.get('nav', [])
    if not nav:
        return config

    sections_deep = {}

    def compute_section_deeps(sections:List[Dict[str,List | str]],deep=1):

        for section in sections:
            _,content = list(section.items())[0]

            if isinstance(content,str):
                sections_deep[content] = deep
            else:
                compute_section_deeps(content,deep+1)

    compute_section_deeps(nav)

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
        f.write('{% set _ = ns.sections_deep.update({\n')
        for path, deep in sections_deep.items():
            normalized = path.replace('\\', '/')
            f.write(f"    {repr(normalized)}: {deep},\n")
        f.write('}) %}\n')

    return config