from wtforms.widgets import HTMLString
from wtforms.widgets import html_params


class BoxWidget(object):
	
	def __call__(self, field, **kwargs):

		kwargs.setdefault('id', field.id)

		if 'class' in kwargs:
			kwargs['class'] = kwargs['class']+' spi-form-box'

		kwargs.setdefault('class', 'spi-form-box')

		html = [u'<div %s>' % (html_params(**kwargs))]

		html.append(u'<div>')
		html.append('<ul>')

		for subfield in field:
			html.append(u'<li>%s %s</li>' % (subfield.label, subfield()))

		html.append('</ul>')
		html.append(u'</div>')		
		html.append(u'</div>')
		return HTMLString(u''.join(html))