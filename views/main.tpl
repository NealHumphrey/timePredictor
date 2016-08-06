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
	  		
	  		<h1>Time Predictor</h1>


	  		<!--If you might not have a variable value, you need to check for it or Bottle will crash.-->
	  		<!--other methods - get('variable', 'default_value') and (pagewide) setdefault ('variable', 'defaultValue')-->
	  		%if defined('calendar'):
	  			%start = calendar.days[0].datestamp
	  			%end = calendar.days[-1].datestamp

	  			<p>Calendar: {{calendar}}</p>
	  			<p>From {{start}} to {{end}}</p>
	  			<p>Hours free: {{calendar.potential_time(start,end)}}</p>
	  			<p>Hours overbooked: {{calendar.overbooked_time(start,end)}}</p>


	  			%for day in calendar.days:
	  				<div> {{day.datestamp}}. Working: {{day.working_hours}}, Free: {{day.hours_free()}}, Booked: {{day.hours_booked()}}</div>
	  				<ul>
	  					%for block in day.blocks:
	  						<li> {{block.task.name}}: portion {{block.portion}}, time: {{block.start}}</li>
	  					%end

	  				</ul>
	  			%end

	  		%else:
	  			<p>Variable not found</p>
	  		%end


			</div>
			</div>
		</div>

</body>

</html>