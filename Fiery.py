import sys
import os
sys.path.append(os.path.dirname(__file__))	# needed to find isodate
import sublime, sublime_plugin
from .models import fhirelementfactory
from .models import fhirdate


class FieryCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		i = 0
		for sel in self.view.sel():
			resource_type = self.view.substr(sel)
			model = fhirelementfactory.FHIRElementFactory.instantiate(resource_type, None)
			if model is not None and 'Element' != model.resource_name:
				indent = '  '			# only whitespace is supported!
				yml = resource_type + "\n" + self.yml_for_resource(model, indent)
				yml = yml.replace("\n", "\n{}".format(self.take_indent_at(sel)))
				yml = self.apply_document_line_endings(yml)
				self.view.replace(edit, sel, yml)
				i += 1
		
		self.view.end_edit(edit)
		if i > 1:
			sublime.status_message("{} resources inserted".format(i))
		elif i > 0:
			sublime.status_message("1 resource inserted")
		else:
			sublime.status_message("No valid resource names highlighted".format(i))
	
	def yml_for_resource(self, resource, indent='  '):
		""" Create a string representation, using unix line breaks with the
		given indent indenting one level. """
		props = []
		for prop in resource.elementProperties():
			row_key = prop[1]
			if 'contained' == row_key:
				continue
			
			row_val = ''
			p_type = prop[2]
			p_array = prop[3]
			
			if str == p_type:
				row_val = '""'
			elif bool == p_type:
				row_val = 'False'
			elif fhirdate.FHIRDate == p_type:
				row_val = '2001-01-01'
			elif hasattr(p_type, 'elementProperties'):
				if 'Extension' == p_type.resource_name or 'Meta' == p_type.resource_name:
					continue
				row_val = p_type.resource_name
			
			row_val = '*'+row_val if prop[5] else row_val
			row = row_key+":\n"+indent+indent+'- '+row_val if p_array else row_key+': '+row_val
			props.append(row)
		
		# apply indent to all line breaks
		if len(props) > 0:
			props[0] = indent+props[0]
		return ("\n"+indent).join(props)
	
	def take_indent_at(self, sel):
		(row, col) = self.view.rowcol(sel.begin())
		indent_region = self.view.find('^\s+', self.view.text_point(row, 0))
		if self.view.rowcol(indent_region.begin())[0] == row:
			return self.view.substr(indent_region)
		return ''
	
	def apply_document_line_endings(self, string):
		""" Input string must have unix line endings. """
		line_endings = self.view.line_endings().lower()
		if 'windows' == line_endings:
			string = string.replace("\n", "\r\n")
		elif 'mac' == line_endings:
			string = string.replace("\n", "\r")
		return string

