'''
author: Vinhthuy Phan
date: 11/27/2011
version: 0.1
'''
import re
import os

DEBUG = False
OpenBracket, ClosedBracket = '__ocb__', '__ccb__'
NoEndTags = ['area','base','br','col','command','embed','hr','img','input','link','meta','param','source']
IdRe = '[a-zA-Z_]\w*'
PythonControl = ['def','for','if','elif','else','while']

# -------------------------------------------------------------------------- #
class OrderedHash(object):
	def __init__(self):
		self.data = [] # self.data[index] = (key, code, data)
		self.hash = {} # self.hash[key] = index in self.data where key is stored
					
	def save(self, key, value, tabs, _type):
		if _type not in ['code','html']:
			raise Exception("type must be either 'code' or 'data'")
		
		value = '\t'*tabs + value + '\n'
		if key not in self.hash:
			self.hash[key] = len(self.data)
			if _type=='code':	self.data.append( [key,value,''] )
			else: 				self.data.append( [key,'',value] )
		else:
			item = self.data[self.hash[key]]
			if _type=='code': item[1] += value
			else: item[2] += value

	def compile(self):
		for i, v in enumerate(self.data):
			self.data[i] = (v[0], compile(v[1],'<string>','exec'), v[2])

	def __iter__(self):
		self.index = -1
		return self

	def next(self):
		if self.index==len(self.data)-1: raise StopIteration
		self.index += 1
		return self.data[self.index]

	def __str__(self):
		return self.hash.__str__() + '\n' + self.data.__str__()


# -------------------------------------------------------------------------- #
class Template(object):
	def __init__(self, thing, _type='__str__', _dir='', _base_dir=''):
		self.dir = _dir
		self.base_dir = _base_dir
		self.var_id = -1
		self.line = ''
		self.default_vars = {}
		self.local_cxt = {OpenBracket:'{', ClosedBracket:'}'}
		self.data = OrderedHash()

		self.lines = self.extract_lines(thing, _type)

		# check for base.tpl
		if self.lines and self.lines[0].startswith('@extends '):
			self.base_tpl = re.split('\s', self.lines.pop(0).strip())[-1]
			self.base_context = self.extract_context(self.base_tpl)
			self.base_tpl = os.path.join(_base_dir, self.base_tpl)
		else:
			self.base_tpl = None
			self.base_context = None

		# begin parsing
		self.parse(0,0,self.context,'')

		if self.base_tpl:
			self.lines = self.extract_lines(self.base_tpl, '__file__')
			self.parse(0,0,self.base_context,'')

		if not DEBUG:
			self.data.compile()
		else: 
			for block,code,html in self.data:
				print '---block:',block,'\n---code---\n',code,'\n---data---\n',html

	# ---------------------------------------------------------------------- #
	def extract_context(self, name):
		name = name.rsplit('/',1)[-1]
		name = name.rsplit('.',1)[0]
		return name.replace('.','_').replace('-','_')

	def extract_lines(self, thing, _type):
		if _type=='__str__': 
			text = thing
			self.context = '__str__'
		elif _type=='__file__':
			with open(os.path.join(self.dir,thing)) as f:
				text = f.read()
			self.context = self.extract_context(thing)
		else:
			raise Exception('crystal template: type must __str__ or __file__')
		text = re.sub(r'\{(?=\s)', '{'+OpenBracket+'}', text)
		text = re.sub(r'(?<=\s)\}', '{'+ClosedBracket+'}', text)
		return [l for l in text.splitlines() if l.strip() and l.strip()[0]!='#']

	# ---------------------------------------------------------------------- #
	def render(self, **dct):
		dct.update(self.local_cxt)
		for k,v in self.default_vars.items():
			dct.setdefault(k,v)
		for block, code, html in self.data:
			if DEBUG:
				print '='*20, 'execing', block
			exec(code, {}, dct)
			dct[block] = html.format(**dct)

		if DEBUG:
			print 'Base template:', self.base_tpl, self.base_context
		return dct.get(self.base_context, dct.get(self.context, ''))

	# ---------------------------------------------------------------------- #
	def parse(self, text_tabs=0, code_tabs=0, block='__default__', code_block=''):
		''' parse all well-indented blocks at level t '''
		tabs = self.next_tabs()

		if tabs > text_tabs: 
			raise Exception('Unexpected indent', tabs, text_tabs, code_tabs, self.line)
		elif tabs < text_tabs or tabs<0: return
		if not self.next_line(): return

		tag, processed_text, start_of_block = self.parse_one_line(tabs)

		if tag == '-':
			new_var = code_block or self.new_var()
			if not code_block:
				self.data.save(block, '{'+new_var+'}', tabs, 'html')
				self.data.save(block, new_var+"=''", code_tabs, 'code')
			self.data.save(block, processed_text, code_tabs, 'code')
			if start_of_block:
				self.parse(text_tabs+1, code_tabs+1, block, new_var)
		elif tag == '__compound_assignment__':
			self.data.save(block, processed_text+"=''", code_tabs, 'code')
			self.parse(text_tabs+1, code_tabs, block, processed_text)
		elif tag == '__block__':
			_v = self.new_var()
			self.data.save(block, '{'+processed_text+'}', tabs, 'html')
			self.data.save(block, _v+"=''", code_tabs, 'code')
			self.parse(text_tabs+1, code_tabs, block, _v)
			_c = 'if "{blk}" not in vars(): {blk}={v}'.format(blk=processed_text,v=_v)
			self.data.save(block, _c, code_tabs, 'code')
		else:
			t = code_tabs if code_block else text_tabs
			self.save_text(processed_text, t, block, code_block)
			if start_of_block:
				if tag == 'script':
					while self.next_tabs() > tabs:
						self.save_text(self.lines.pop(0), t, block, code_block)
				else:
					self.parse(text_tabs+1, code_tabs, block, code_block)
				self.save_text('</'+tag+'>', t, block, code_block)

		while True:
			go_on, adj = self.should_continue(tabs)
			if not go_on: return
			self.parse(text_tabs+adj, code_tabs+adj, block, code_block)

	# ---------------------------------------------------------------------- #
	def save_text(self, text, tabs, block, code_block=''):
		# Replace expressions with dummy variables
		res = re.findall(r'\{([^\{\}]+)\}', text)
		for e in [i for i in res if i==i.strip() and not self.valid_id(i)]:
			self.extract_default_vars(e)
			var = self.new_var()
			t = tabs if code_block else 0
			self.data.save(block, '{var}={e};'.format(var=var, e=e), t, 'code')
			text = text.replace('{'+e+'}', '{'+var+'}')

		# If inside a code block, text might be reformatted.
		if not code_block:
			self.data.save(block, text, tabs, 'html')
		else:
			text = self.format_vars(text, tabs)
			self.data.save(block, code_block+"+="+text, tabs, 'code')

	# ---------------------------------------------------------------------- #
	def should_continue(self, tabs):
		next_tabs = self.next_tabs()
		if next_tabs == -1: return False, 0
		if next_tabs == tabs: return True, 0
		if next_tabs+1 == tabs and re.match(r'\-\s+(else|elif)', self.lines[0].strip()):
			return True, -1
		return False, 0

	# ---------------------------------------------------------------------- #
	def parse_one_line(self, tabs):
		''' returns tag, processed_text, start_of_block '''
		# Python code/block starts with -
		if self.line[0] == '-': 
			code = self.line[1:].strip()
			m = re.match(r'([a-zA-Z_]\w*)\s*=$', code)
			if m: 
				return '__compound_assignment__', m.groups()[0], True
			control = re.split('\W', code, 1)[0]
			return '-', code, control in PythonControl
		
		# parsing a block
		if self.line.startswith('@block '):
			b = self.line[7:].strip()
			if not re.match(r'[a-zA-Z_]\w*', b): 
				raise Exception('syntax error', self.line)
			return '__block__', b, False

		# A tag starts with uncapitalized letters.  
		# Regular texts' first letter must be capitalized; Escape character is >
		if not self.line[0].isalpha() or self.line[0].isupper():
			if self.line[0] == '>': return '', self.line[1:].strip(), False
			return '', self.line.strip(), False

		# Tag rule: tag#id.class (optional_attributes="values") other-things
		res = re.split(r'\s+' ,self.line, 1)
		first, the_rest = res[0], res[1].strip() if len(res)==2 else ''
		m = re.match(r'(\w+)((#[\w-]+)*)((\.[\w-]+)*)$', first)
		if not m: 
			raise Exception('syntax error', self.line)
		tag, _id, _class = m.groups()[0], m.groups()[1], m.groups()[3]
		
		attributes = ''
		if _id or _class:
			attributes = ' '+self.format_id_class(_id, _class)
		
		m = re.match('\((\w+="[^"]+"\s+)*\w+="[^"]+"\)', the_rest)
		if m:
			attributes += ' '+m.group()[1:-1]
			the_rest = the_rest[len(m.group()):]

		if tag in NoEndTags: 
			return tag, '<'+tag+attributes+' />', False

		if the_rest or tabs==self.next_tabs():
			return tag, '<'+tag+attributes+'>'+the_rest+'</'+tag+'>', False
		
		return tag, '<'+tag+attributes+'>', True

	# ---------------------------------------------------------------------- #

	def extract_default_vars(self, expr):
		vs = [ (i,None) for i in re.split(r'\s+or\s+', expr) if self.valid_id(i) ]
		self.default_vars.update( dict(vs) )

	def valid_id(self, x): return re.match(r'[a-zA-Z_]\w*$', x)

	def format_vars(self, line, tabs):
		res = re.findall(r'\{([^\{\}]+)\}', line)
		var = [ i for i in set(res) if i==i.strip() and self.valid_id(i) ]

		args = ','.join([ '{x}={x}'.format(x=i) for i in set(var) ])
		if not args: return "'''{tabs}{line}\n'''".format(tabs='\t'*tabs,line=line)
		return "'''{tabs}{line}\n'''.format({args})".format(tabs='\t'*tabs,line=line,args=args)

	def format_id_class(self, _id='', _class=''):
		if _id: _id = 'id="{_id}"'.format(_id=_id.replace('#',' ').strip())
		if _class: _class = 'class="{_cl}"'.format(_cl=_class.replace('.', ' ').strip())
		return (_id + ' ' + _class).strip()
		
	def next_line(self):
		''' Returns if end-of-file, num of tabs '''
		if not self.lines: return False
		self.line = self.lines.pop(0).strip()
		return True

	def next_tabs(self):
		''' peek at number of tabs in the first unparsed line '''
		if not self.lines: return -1
		return 0 if self.lines[0][0]!='\t' else len(re.match('\t+',self.lines[0]).group())

	def new_var(self, prefix='__var__'):
		self.var_id += 1
		return prefix + str(self.var_id)

# -------------------------------------------------------------------------- #

if __name__ == '__main__':
	import os
	for dir_paths, dir_names, file_names in os.walk('./tests'):
		ff = [ os.path.join(dir_paths,e) for e in file_names if e.endswith('.tpl') ]
		ff = sorted(ff, key=os.path.getmtime, reverse=True)
		for f in ff:
			print 'Start processing ', f
			template = Template(f, _type='__file__', _base_dir='./tests')
			context = dict(title="Title Passed from Outside", )
			print '\nresult....\n', template.render(**context)
			print '\n\n', raw_input('Enter to continue... '), '\n', '-'*80


