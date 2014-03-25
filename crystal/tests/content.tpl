@extends base.tpl 

- page_title = 'Main Content'

- footer =
	Footer defined in content.tpl
	- for i in ['apple', 'orange']:
		li fruit: {i}

p.main-content
	p
		This is main content defined in content.tpl.

	p
		Second line.
		Third line.

	Items
	ul.list
		- for i in range(4):
			li Item {i}.


