import logging
from google.appengine.ext import db


class IndexEntryListProperty(db.StringListProperty):
	
	''' Stores a list of keys and relevance/popularity scores. '''
	
	def __init__(self, *args, **kwargs):
		super(IndexEntryListProperty, self).__init__(*args, **kwargs)
		
	
	def make_value_from_datastore(self, value):
				
		decoded_entries = []

		if value is not None:
			for encoded_entry in value:
				split_entry = encoded_entry.split('::')
				
				key = db.Key(split_entry[0])
				
				p_score = split_entry[1].lower().replace('p/','')
				r_score = split_entry[2].lower().replace('r/','')
				f_score = split_entry[3].lower().replace('f/','')
				
						
				decoded_entries.append((key, float(p_score), float(r_score), float(f_score)))
						
		return decoded_entries
		
		
	def validate_list_contents(self, value):
		
		return value
		
			
	def get_value_for_datastore(self, model_instance):
		
		value = self.__get__(model_instance, model_instance.__class__)		

		encoded_index_entries = []		
		for key, p_score, r_score, final_score in value:
			encoded_index_entries.append(str(key)+'::P/'+str(p_score)+'::R/'+str(r_score)+'::F/'+str(final_score))

			
		return encoded_index_entries