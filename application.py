#Bottle provies a simpe server that can run Python code and connect it to a website. 
#Unlike Django and others, there's no database or other full-stack components, making it useful for quick display-based tools.

#Import the stuff we need first:
from flask import Flask, jsonify, render_template, request
from app.main import sample, slice_calendar
from datetime import datetime
#Obviously you can import other modules here.

app = Flask(__name__)

#Run arbitrary code
sample_calendar = sample()


@app.route('/sample')
def sample():
	return render_template('main.html', calendar=sample_calendar) 

@app.route('/')
def main():
	return render_template('main.html') 

@app.route('/<start>/<end>')
def sliced(start = None, end=None):
	start = datetime.strptime(start, '%Y-%m-%d').date()
	end = datetime.strptime(end, '%Y-%m-%d').date()
	sliced_calendar = slice_calendar(sample_calendar,start,end)
	return render_template('main.html', calendar=sliced_calendar)


if __name__ == '__main__':
    print("Running in browser...")
    app.run(host="0.0.0.0")
