html
	head
	meta (equiv="UTF-8" lang="en")
	script (type="text/javascript" src="js/jquery.js")
	title {title or "Index.html"}
	body
		div#title
			{page_title or "Welcome..."}
		div#content
			{content or "There is nothing to show."}
		div#footer
			@block footer
				Not yet implemented.
				ul.foot
					- for i in range(3):
						li {i} is in footer
			Copyright 2011
