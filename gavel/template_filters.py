from gavel import app
from humanize import naturaltime
import markdown
import html
from markupsafe import Markup

@app.template_filter('utcdatetime_local')
def _jinja2_filter_datetime_local(datetime):
    if datetime is None:
        return 'None'
    return naturaltime(datetime)

@app.template_filter('utcdatetime_epoch')
def _jinja2_filter_datetime_epoch(datetime):
    if datetime is None:
        return 0
    return datetime.strftime('%s')

@app.template_filter('markdown')
def _jinja2_filter_markdown(text):
    if text is None:
        return ''
    # Escape HTML to prevent XSS attacks before processing markdown
    escaped_text = html.escape(text)
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['nl2br'])
    html_output = md.convert(escaped_text)
    # Return as safe markup to prevent double-escaping
    return Markup(html_output)
