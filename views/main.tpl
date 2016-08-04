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
	  		<!--If you might not have a variable value, you need to check for it or Bottle will crash.-->
	  		<!--other methods - get('variable', 'default_value') and (pagewide) setdefault ('variable', 'defaultValue')-->
	  		%if defined('ending'):
	  			<p>This was your url ending: {{ending}}</p>
	  		%else:
	  			<p>You are visiting the root 'yo' path!</p>
	  		%end

	  		<!--We can also embed Python code in a block-->
	  		<%
	  			test = 'test'
	  			if test == 'test':
	  				test = 'untested'
	  			end
	  		%>

	  		<p>Test: {{test}}</p>

			</div>
			</div>
		</div>

</body>

</html>