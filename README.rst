Crystal
=======

A pythonic, simple template engine.

Example
-------

html
	title This is a page title
	body
		h1#page-title First Page
		h2 Subtitle
		p.para
			This is a paragraph

	footer#footer
      Copyright @2012


Results in

<html>
	<title>This is a page title</title>
	<body>
		<h1 id="page-title">First Page</h1>
		<h2>Subtitle</h2>
		<p class="para">
			This is a paragraph
		</p>
		<footer id="footer">
			Copyright @2012
		</footer>
	</body>
</html>
