#Bottle provies a simpe server that can run Python code and connect it to a website. 
#Unlike Django and others, there's no database or other full-stack components, making it useful for quick display-based tools.

#Import the stuff we need first:
import os
from bottle import route, run, template, view, debug, default_app
from app.main import sample, slice_calendar
from datetime import datetime
#Obviously you can import other modules here.

application = default_app()

#Run arbitrary code
sample_calendar = sample()


@route('/sample')
def sample():
	return template('main', calendar=sample_calendar) 

@route('/')
def main():
	return template('main') 

@route('/<start>/<end>')
def sliced(start,end):
	start = datetime.strptime(start, '%Y-%m-%d').date()
	end = datetime.strptime(end, '%Y-%m-%d').date()
	sliced_calendar = slice_calendar(sample_calendar,start,end)
	return template('main', calendar=sliced_calendar)

#Examples:
#The most simple version
@route('/hello')
def hello():
    return 'Hello World'


run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

#Version used for running locally:
#run(host='localhost', port=8080, debug=True, reloader=True, interval=3)

#TODO - remove the debug call in production!