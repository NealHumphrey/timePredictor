<!DOCTYPE html>
<html>
<meta charset="utf-8">
<header>
	% include('header.tpl')
</header>


<!--Optional on-page styles-->
<style>

</style>



<!--Main body of the content here-->
<body>
	
		<!--main body-->
		<div class="container">

			<div class="row">
			<div class="col-xs-12 col-sm-12"><!--id="container-sub-wrapper"-->
	  		
	  		<h1>This is a title</h1>
	  		<h2>This title is smaller</h2>
	  		<p>You can output variables onto this page</p>
	  		<p>The dictionary: {{my_var}}</p>
	  		<p>The 'foo' variable: {{my_var['foo']}}</p>
	  		<p>The 'bar' variable: {{my_var['bar']}}</p>
	  		<p>Don't forget, this syntax won't work: my_var.foo</p>


			</div>
			</div>
		</div>

</body>

</html>