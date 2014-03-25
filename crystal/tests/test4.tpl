html
	head
		title {title or "Index Page"}
	body
		ul.outside
			div#one 
				mytag#two
					p#three.sure
						something.yes

			- for I in range(10):
				- if I > 5:
					- for J in range(2):
						- if J%2:
							li Odd = {I},{J}
						- else:
							li Even = {I},{J}
		Done
		div#footer Copyright 2011