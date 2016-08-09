<!DOCTYPE html>
<html>
<meta charset="utf-8">
<header>
	% include('header.tpl')
</header>


<!--Optional on-page styles-->
<style>

.time-summary{
	font-size:1.5em;
	margin-bottom:0px;
}
.calendar-duration{
	font-size:1.2em;
	font-style:italic;
	color:rgb(160,160,160);
}

.hours-ok{
	/*change nothing*/
}

.hours-over{
	color:rgb(212,80,80);
}


.well {
	padding:3px;
	min-height:300px;

	-webkit-box-flex: 1;
    -moz-box-flex: 1;
    -webkit-flex: 1;
    -ms-flex: 1;
    flex: 1;
}

.well.working {
	background:rgb(255,255,255);
}

.well.vacation {
	background:rgb(235,235,235);
}
.calendar-row{
	
    display: -webkit-flexbox;
    display: -ms-flexbox;
    display: -webkit-flex;
    display: flex;
}
.workblock{
	width:100%;
	min-height:70px;
	padding:3px;
	margin: 1px 0px 1px 0px;

	-webkit-border-radius: 10px;
	-moz-border-radius: 10px;
	border-radius: 10px;
	
	border:1px solid #9E9E99;
	background:rgba(193,227,186,0.7);

	display: -webkit-box;
    display: -moz-box;
}

.workblock.block-ok{
	/*change nothing*/
}

.workblock.block-over{
	background:rgba(227,141,141,0.7);
}

.project-name{
	font-size: 0.8em;
	font-style: italic;
	color: rgb(120,120,120);
}
.task-name{
	/*change nothing*/
}


</style>



<!--Main body of the content here-->
<body>
	
		<!--main body-->
		<div class="container-fluid">

			<div class="row">
			<div class="col-xs-12 col-sm-12"><!--id="container-sub-wrapper"-->
	  		
	  		<h1>Time Predictor</h1>


	  		<!--If you might not have a variable value, you need to check for it or Bottle will crash.-->
	  		<!--other methods - get('variable', 'default_value') and (pagewide) setdefault ('variable', 'defaultValue')-->
	  		%if defined('calendar'):
	  			%if len(calendar.days) == 0:
	  				<p>No days available</p>
	  			%else:
	  				%date_format = '%a, %b %d'
		  			%start = calendar.days[0].datestamp
		  			%end = calendar.days[-1].datestamp

		  			<p class="calendar-duration">{{start.strftime(date_format)}} to {{end.strftime(date_format)}} ({{len(calendar.days)}} days)</p>
	  				
	  				<div style="margin-bottom:20px">
  						%booked_days = round(calendar.normal_booked_time(start,end) / 8, 1)
  						%free_days = round(calendar.potential_time(start,end) / 8, 1)
  						%overbooked_days = round(calendar.overbooked_time(start,end) / 8, 1)
  						%total_days = round(calendar.working_hours(start,end) / 8, 1)
  						%percent_booked = round(booked_days / (total_days),2) * 100

	  						<p class="time-summary">Booked: {{(booked_days)}} out of {{(total_days)}} ({{percent_booked}} %)</p>
		  					<p class="time-summary" style="text-indent: 20px;">plus overbooked: {{ overbooked_days }} days</p>
		  					<p class="time-summary">Time free: {{free_days}} days</p>
		  					
			  		</div>

		  			<div class="calendar-row"><!--the first one-->
		  			%for day_counter, day in enumerate(calendar.days):
		  				%width = 1*(100/7)
		  				%well_style = "working" if day.working_hours > 0 else "vacation"
	  					<div class="well {{well_style}}" style="width:{{width}}%; float:left">
			  				<div> 
			  					{{day.datestamp.strftime(date_format)}}.<br>
			  					{{day.working_hours}} working
			  					%free_style = "hours-ok" if day.hours_free() >=0 else "hours-over"
			  						(<span class="{{free_style}}">
			  							{{day.hours_free()}} free
			  						</span>
			  						, {{day.hours_booked()}} booked)<br> 
			  				</div>

			  					<!--Print each work block-->
			  					%for block_counter, block in enumerate(day.blocks):
			  						%block_style = "block-ok" if block_counter < day.working_hours else "block-over" #remember block_counter starts at 0, so using < instead of <=
			  						<div class="workblock {{block_style}}"> 
			  							<span class="task-name">{{block.task.name}} ({{block.portion}})</span><br>
			  							<span class="project-name">{{block.task.project}}</span>
			  						</div>
			  					%end

		  				</div>
			  			%if 6 == (day_counter % 7) or day_counter == len(calendar.days):
			  				</div><!--ending the calendar_row-->
			  				<div class="clearfix"></div>
			  			%end
			  			%if 6 == (day_counter % 7):
			  				<div class="calendar-row"><!--only start new ones if needed-->
			  			%end
	  				%end			
	  			%end
	  		%else:

	  			<p>Choose a starting week:</p>
	  				<ul>
	  					<li><a href='/2016-08-15/2016-11-07'/a>Week of Aug 15</a></li>
						<li><a href='/2016-08-22/2016-11-14'/a>Week of Aug 22</a></li>
						<li><a href='/2016-08-29/2016-11-21'/a>Week of Aug 29</a></li>
						<li><a href='/2016-09-05/2016-11-28'/a>Week of Sep 5</a></li>
						<li><a href='/2016-09-12/2016-12-05'/a>Week of Sep 12</a></li>
						<li><a href='/2016-09-19/2016-12-12'/a>Week of Sep 19</a></li>
						<li><a href='/2016-09-26/2016-12-19'/a>Week of Sep 26</a></li>
						<li><a href='/2016-10-03/2016-12-26'/a>Week of Oct 3</a></li>
						<li><a href='/2016-10-10/2017-01-02'/a>Week of Oct 10</a></li>
						<li><a href='/2016-10-17/2017-01-09'/a>Week of Oct 17</a></li>
						<li><a href='/2016-10-24/2017-01-16'/a>Week of Oct 24</a></li>
						<li><a href='/2016-10-31/2017-01-23'/a>Week of Oct 31</a></li>
						<li><a href='/2016-11-07/2017-01-30'/a>Week of Nov 7</a></li>
						<li><a href='/2016-11-14/2017-02-06'/a>Week of Nov 14</a></li>
						<li><a href='/2016-11-21/2017-02-13'/a>Week of Nov 21</a></li>
						<li><a href='/2016-11-28/2017-02-20'/a>Week of Nov 28</a></li>
						<li><a href='/2016-12-05/2017-02-27'/a>Week of Dec 5</a></li>
						<li><a href='/2016-12-12/2017-03-06'/a>Week of Dec 12</a></li>
						<li><a href='/2016-12-19/2017-03-13'/a>Week of Dec 19</a></li>
						<li><a href='/2016-12-26/2017-03-20'/a>Week of Dec 26</a></li>
						<li><a href='/2017-01-02/2017-03-27'/a>Week of Jan 2</a></li>
						<li><a href='/2017-01-09/2017-04-03'/a>Week of Jan 9</a></li>
						<li><a href='/2017-01-16/2017-04-10'/a>Week of Jan 16</a></li>
						<li><a href='/2017-01-23/2017-04-17'/a>Week of Jan 23</a></li>
						<li><a href='/2017-01-30/2017-04-24'/a>Week of Jan 30</a></li>
						<li><a href='/2017-02-06/2017-05-01'/a>Week of Feb 6</a></li>
						<li><a href='/2017-02-13/2017-05-08'/a>Week of Feb 13</a></li>
						<li><a href='/2017-02-20/2017-05-15'/a>Week of Feb 20</a></li>
						<li><a href='/2017-02-27/2017-05-22'/a>Week of Feb 27</a></li>
						<li><a href='/2017-03-06/2017-05-29'/a>Week of Mar 6</a></li>
						<li><a href='/2017-03-13/2017-06-05'/a>Week of Mar 13</a></li>
					</ul>
	  			<!--start.strftime(date_format)-->
	  		%end


			</div>
			</div>
		</div>

</body>

</html>