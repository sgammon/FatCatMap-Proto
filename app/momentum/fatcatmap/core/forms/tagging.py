import logging
from tipfy.ext.wtforms import fields
from momentum.fatcatmap.models.search import *
from momentum.fatcatmap.models.content import ContentItemCategory


class TagListField(fields.TextField):
	

	def process_data(self, value):
		if value is not None:
			tags = db.get(value)
			result = []
			for tag in tags:
				result.append(tag.value)
			value = ', '.join(result)
		self.data = value
		
	def process_formdata(self, value):

		results = []
		
		for item in value[0].split(','):
			item = item.lstrip().rstrip().replace(' ', '-')
			t = UserTag.get_by_key_name(item)
			if t is None:
				t = UserTag(key_name=item, value=item)
				t.put()
			results.append(t.key())
			
		self.data = results

		
class CategoryListField(fields.SelectField):


	def process_data(self, value):
		if value is not None:
			value = str(value.key())
		self.data = value
		

	def process_formdata(self, value):
		self.data = db.Key(value[0])