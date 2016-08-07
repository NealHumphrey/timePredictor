#Bottle provies a simpe server that can run Python code and connect it to a website. 
#Unlike Django and others, there's no database or other full-stack components, making it useful for quick display-based tools.

#Import the stuff we need first:
from bottle import route, run, template, view, debug
from app.main import sample, slice_calendar
from datetime import datetime
#Obviously you can import other modules here.


#Run arbitrary code
sample_calendar = sample()


#An alternative definition method that allows you to return a dictionary
@route('/sample')
def main():
	return template('main', calendar=sample_calendar) 


@route('/<start>/<end>')
def sliced(start,end):
	start = datetime.strptime(start, '%Y%m%d').date()
	end = datetime.strptime(end, '%Y%m%d').date()
	sliced_calendar = slice_calendar(sample_calendar,start,end)
	return template('main', calendar=sliced_calendar)

#Examples:
#The most simple version
@route('/hello')
def hello():
    return 'Hello World'


#When it's all set up, run the page.
run(host='localhost', port=8080, debug=True, reloader=True, interval=3)
#TODO - remove the debug call in production!