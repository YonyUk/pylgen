# ==============================================
# GOOGLE SEARCH CONSOLE VERIFICATION
# ==============================================

def add_google_verification(app, pagename, templatename, context, doctree):
    # Este es el meta tag que Google necesita para verificar el sitio
    meta_tag = '<meta name="google-site-verification" content="WY0eAxGSQVsrz78bXP9Efi4kzl6UXmljaZ51YnEyHDQ" />'
    # Lo añadimos a la cabecera (head) de todas las páginas
    context['metatags'] = context.get('metatags', '') + meta_tag

def setup(app):
    app.connect('html-page-context', add_google_verification)