

html (lang="en")

	This is before comment
	# This is a comment

	head
		meta (equiv="UTF-8" lang="en")
		script (type="text/javascript" src="js/jquery.js")
		script (type="text/javascript")
			<!--
				var SESSIONURL = "";
				var SECURITYTOKEN = "1321027914-7225cb5939c5de725381b9001779a241f07ae124";
				var IMGDIR_MISC = "images/misc";
				var IMGDIR_BUTTON = "images/buttons";
				var vb_disable_ajax = parseInt("0", 10);
				var SIMPLEVERSION = "413";
				var BBURL = "http://abc.com/test";
			// -->
		meta  (http-equiv="Content-Type", content="text/html; charset=UTF-8")

	body
		div#header This is my header
		div#main
			p.content
				Text begins with a capitalized letter.
				Another line.
				> to enter text with lower case, start with a ">"
				ul.list
					li One
					li Two
					ul
						li Nested one
						li Nested two
					li Three
		div#footer Copyright 2011