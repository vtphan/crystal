html
	head
		title {title or "Index Page"}
	body
		div#header {header or "Default Header"}
		p
			- if True:
				This is True.
			- else:
				This is False.
		ul
			- for i in range(10):
				li Item {i}

		div#footer Copyright 2011