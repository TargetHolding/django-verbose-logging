import logging
import io

from django.views.debug import ExceptionReporter
from django.template import Context, Template


LOG_TEMPLATE_500 = \
"""{{ request.META.REQUEST_METHOD }} {{ request.build_absolute_uri }} on {{server_time|date:"c"}}
{% if template_info %}
Template error:
  In template {{ template_info.name }}, error at line {{ template_info.line }}
  {{ template_info.message }}{% for source_line in template_info.source_lines %}{% ifequal source_line.0 template_info.line %}
  {{ source_line.0 }} : {{ template_info.before }} {{ template_info.during }} {{ template_info.after }}
  {% else %}
  {{ source_line.0 }} : {{ source_line.1 }}
  {% endifequal %}{% endfor %}{% endif %}{% if lastframe %}
FRAMES:{% for frame in frames %}
  in {{ frame.function|escape }}(...){% for var in frame.vars|dictsort:"0" %}
    - {{ var.0|safe }} = {{ var.1|safe }}{% endfor %}{% endfor %}
{% endif %}{% if request.user.username %}USERNAME: {{ request.user.username }}
{% endif %}{% if request.GET %}GET:{% for k, v in request.GET.items %}
- {{ k }} = {{ v|stringformat:"r" }}{% endfor %}
{% endif %}{% if request.POST %}POST:{% for k, v in filtered_POST.items %}
- {{ k }} = {{ v|stringformat:"r" }}{% endfor %}
{% endif %}{% if request.FILES %}FILES:{% for k, v in request.FILES.items %}
- {{ k }} = {{ v|stringformat:"r" }}{% endfor %}
{% endif %}{% if request.COOKIES %}COOKIES:{% for k, v in request.COOKIES.items %}
- {{ k }} = {{ v|stringformat:"r" }}{% endfor %}
{% endif %}"""

class Formatter(logging.Formatter):
	def format(self, record):
		try:
			request = record.request
		except AttributeError:
			return super().format(record=record)

		if record.exc_info:
			exc_info = record.exc_info
		else:
			exc_info = (None, record.getMessage(), None)

		reporter = ExceptionReporter(request, is_email=False, *exc_info)
		t = Template(LOG_TEMPLATE_500, name='Log 500 template')
		c = Context(reporter.get_traceback_data(), autoescape=False, use_l10n=False)
		
		frames = []
		
		for frame in c['frames']:
			fvars = (
				(k, str(v)
					.replace('&amp;', '&')
					.replace('&lt;', '<')
					.replace('&gt;', '>')
					.replace('&quot;', '"')
					.replace("&#39;", '\'')
				)
				for (k, v) in frame['vars']
			)
			
			frame['vars'] = [
				(k, "'<WSGIRequest ...>'")
				if str(v).startswith("'<WSGIRequest")
				else (k, v)
				for (k, v) in fvars
			]
			
			frames.append(frame)
		
		formatted = t.render(c)
		
		divider = '-' * 80 + '\n'

		message = io.StringIO()
		message.write(divider)
		message.write(super().format(record=record))
		message.write('\n')
		message.write(formatted)
		message.write(divider)

		return message.getvalue()

