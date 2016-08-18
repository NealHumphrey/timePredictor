"""
Summary Notes:
	App creates a calendar, which is a list of day objects
	Each day has 'working_hours', the hours available for doing work
	Tasks are components that have an estimated time to complete.
	The tool automatically breaks Tasks into Blocks. These are assigned to lists in both Days in the calendar and to the original Task they were generated from. 

	Calendar then can be sent to the view.

	Current status:
	-load_tasks correctly pulls from Google Sheets, but need to parse the date
	
	-prioritize tasks not yet implemented
	-Nothing in the view is implemented yet - just a text output
	-Times are not dealt with at all (but they are stored for blocks and tasks)

"""







from datetime import timedelta, datetime, time, date
from collections import deque #not used currently?
from operator import attrgetter
from ast import literal_eval
import pandas as pd
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#Configure logging
logging_filename = "logs/app.log"
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)

####
#Utility functions
####
#Just a handy tool for making random objects
class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def str_to_bool(s):
    if s.lower() == 'true':
         return True
    elif s.lower() == 'false':
         return False
    else:
        logging.warning("Couldn't parse string '{}' properly. Returning False.".format(s))
        return False



def ex():
	return 2


####
#Classes used in the app
####

#Make day objects. Copy paste this to initialize:
	# x = Day(datestamp=date(YYYY,M,D), working_hours = 0)
class Day(object):
	def __init__(self, datestamp, working_hours):
		self.datestamp = datestamp
		self.working_hours = working_hours

		#properties to be added later
		self.blocks = []
	#override the default print/string method
	def __repr__(self):
		return (
				"Day{datestamp:" + str(self.datestamp) + 
				", len(blocks): " + str(len(self.blocks)) + 
				", working_hours:" + str(self.working_hours) + "}"
				)

	# Returns the number of hours available to do work, based on the blocks assigned to this day
	# if hours_free is negative, it indicates overbooked time
	def hours_free(self):
		hours = self.working_hours
		for b in self.blocks:
			hours = hours - b.duration
		return hours

	def hours_booked(self):
		hours = 0
		for b in self.blocks:
			hours += b.duration
		return hours

class Block(object):
	def __init__(self, start, duration, task, portion):
		self.start = start 				#a datetime
		self.duration = duration
		self.task = task
		self.portion = portion			#portion is an iterator for all blocks in a task

		task.blocks.append(self)

	def __repr__(self):
		return (
				"Block{" + str(self.start) + 
				", duration: " + str(self.duration) + 
				", task:" + str(self.task) + 
				", portion: " + str(self.portion) + "}" 
				)

class Task(object):
	allTasks = []

	#to use: x = Task(name="",start=,end=,hours_needed=)
	def __init__(self, name, start, end, hours_needed, hours_done=0, completed=False, project='', notes=''):
		self.name = name
		self.start = start
		self.end = end
		self.hours_needed = hours_needed
		self.hours_done = hours_done
		self.completed = completed
		self.project = project
		self.notes = notes

		#properties to be added later
		self.blocks = []
		self.calendar_potential_time = 0 #Calculated in task prioritization based on the calendar. Number of working hours between start and end dates
		self.time_constraint = 0 #Calculated in task prioritization. difference between potential_time and hours_remaining

		#summary properties assigned to Task class
		Task.allTasks.append(self)

	def __repr__(self):
		return 'Task{name: %r, project: %r, hours_needed: %r, time_constraint: %r, end: %r}\n' % (self.name, self.project, self.hours_needed, self.time_constraint, self.end)

	def clear_blocks(self):
		self.blocks = []

	def hours_remaining(self):
		
		if self.completed == True:
			hours = 0
		else:
			hours = self.hours_needed - self.hours_done
		return hours

class Calendar(object):
	def __init__(self):
		self.days = [] #blank list to hold days objects

	def __repr__(self):
		return "Calendar{days(count): %r}" % (len(self.days))

	# Calculate the time available in the calendar for doing tasks between two dates. Ignores overbooked time.
	def potential_time(self, start, end):
		working_hours = 0

		for d in self.days:
			if d.datestamp >= start and d.datestamp <= end:
				working_hours += max(0,d.hours_free())

		return working_hours

	#Sums up just the overbooked times between two dates.
	def overbooked_time(self, start, end):
		working_hours = 0

		for d in self.days:
			if d.datestamp >= start and d.datestamp <= end:
				working_hours += abs(min(0,d.hours_free()))

		return working_hours

	def normal_booked_time(self, start, end):
		working_hours = 0
		for d in self.days:
			if d.datestamp >= start and d.datestamp <= end:
				working_hours += d.working_hours if (d.hours_booked() > d.working_hours) else d.hours_booked()

		return working_hours

	def working_hours(self, start, end):
		working_hours = 0
		for d in self.days:
			if d.datestamp >= start and d.datestamp <= end:
				working_hours += d.working_hours
		return working_hours

# Break a task into blocks, and assign these blocks to the calendar as soon as possible.
# For each day, if hours_free > block_size, create a block and assign it to that day.
# For any task time that remains on task.end, add it to the deadline day. This will overbook the day.
# Task hours that need to be assigned are those not yet completed (hours_needed - hours_done)
# 	task: a Task object
#	calendar: an ordered list of Day objects
#	start: 
def assign_blocks(task,calendar,start):
	logging.info("Assigning task {}".format(task.name))

	block_size = 1 #hour(s)
	hours_to_assign = task.hours_remaining()
	hours_assigned = 0

	#This will be incremented when each block is created.
	portion=1

	# if not empty, we assume this has already been run; haven't handled re-running appropriately so we will instead throw an error
	if len(task.blocks) > 0:
		raise Exception("task.blocks already populated - don't want to duplicate the blocks")
	
	#'Completed' field has precedence over the hours_to_assign amount
	if task.completed == True:

		logging.info('{} skipped because completed = {}'.format(task.name, task.completed))
		return

	for d in calendar.days:
		#Go to the next day if it's not the start date
		if d.datestamp < start:
			continue

		while hours_to_assign > hours_assigned:
			#Just fill the available hours in the day, unless today is the deadline. On the deadline we can overbook the day.
			if d.hours_free() >= block_size or task.end.date() <= d.datestamp:
				b = Block(start=datetime.combine(d.datestamp, time(9,0)), duration=block_size, task=task, portion=portion)		
				hours_assigned += b.duration
				portion += 1

				task.blocks.append(b)
				d.blocks.append(b)
			else:
				break #assign the hours to the next day

		if hours_assigned >= hours_to_assign:
			break #no need to look at the rest of the days if everything is assigned


	logging.info("{}: {} portions created".format(task.name, (portion-1))) #last increment does not apply to the total portions count

	#handle error - ran out of days in calendar (should add a list at the end of the calendar)

# Takes a list of tasks and sorts the list so that they can be passed through the assign_blocks routine
# 	Priority:
#		1) Time constrained - 
#			Calendar.potential_time(start,end) = total working hours available in the calendar between task start and end dates
#			Task.hours_remaining = time remaining in task
#			The smallest (hours_available - hours_needed) get top priority (i.e. must happen on specific days)
#			
#		2) end - if time constrained is the same, do the one with the earliest deadline first
#		3) start - finally, do the one with earliest start date first. 
def prioritize_tasks(tasks, calendar):
	
	for t in tasks:
		t.calendar_potential_time = calendar.potential_time(t.start.date(),t.end.date()) #task is datetime. potential_time takes date
		t.time_constraint = t.calendar_potential_time - t.hours_remaining()

	
	#Use stable sort property to implement multi-level sort. Lowest priority first.
	sorted_tasks = sorted(tasks, key=attrgetter('start'))
	sorted_tasks = sorted(sorted_tasks, key=attrgetter('end'))
	sorted_tasks = sorted(sorted_tasks, key=attrgetter('time_constraint'))

	#For comparison
	logging.info('Before sort')
	logging.info(tasks)
	logging.info('After sort')
	logging.info(sorted_tasks)

	return sorted_tasks

#Returns a list of tasks loaded from a data source (CSV file)
#this will need to load the data from the CSV or other file
#TODO only sample data creation for now
def load_tasks(data_id):
	print('Loading Tasks....')

	spreadsheet_date_format='%A, %B %d, %Y'

	#Configure Google Sheets credentials
	scope = ['https://spreadsheets.google.com/feeds']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

	#open the notebook
	gc = gspread.authorize(credentials)
	notebook = gc.open_by_key(data_id)


	#worksheets = sheetbook.worksheets() #a list of all worksheets in a spreadsheet
	#worksheet_count = worksheet.row_count
	#worksheet_headers = worksheet.row_values(1) #returns list of values in a row
	
	worksheet = notebook.get_worksheet(0) #get worksheet by index number
	worksheet_values = worksheet.get_all_values()

	#Create Task objects for each row
	row_index = 1
	tasks = []
	for row in worksheet_values:
		#skip the headers
		if row_index == 1:
			row_index += 1
			continue 
		task = Task(name = str(row[0]), 
					start = datetime.strptime(row[1],spreadsheet_date_format),		#TODO need to convert to datetime format (parse string)
					end = datetime.strptime(row[2],spreadsheet_date_format),
					hours_needed = float(row[3]), 
					hours_done = float(row[4]), 
					completed = str_to_bool(row[5]), 
					project = str(row[6]), 
					notes = str(row[7]))
		
		tasks.append(task)
		row_index += 1

	return tasks

def create_calendar(data_path, start, end):
	#parse the data to get date and available hours
	#make a list of ordered days starting with start (a date)
	#if start is not in the data, throw error
	#if there are any gaps in the data, create filler days with working_hours = 0

	#data validation
	if isinstance(start, date) is False or isinstance(end, date) is False:
		raise ValueError('start and end must be of the type datetime.date')
	if start > end:
		raise ValueError('start must be before end')
	if isinstance(data_path,str) is False: 
		raise ValueError('data_path must be a string')

	#Read calendar info into a pandas dataframe
	calendar_data = pd.read_csv(data_path,parse_dates=['date'])
	calendar_sorted = calendar_data.sort_values(by='date')
	#convert from a Pandas Timestamp to a datetime.date() object for consistency with the rest of the time objects
	calendar_sorted['date'] = [date.date() for date in calendar_sorted['date']]
 	
 	#Calendar object is returned by the function
	calendar = Calendar()

	#Create Day objects and append them to the Calendar.days[]
	for row in calendar_sorted.itertuples():
		if row.date < start or row.date > end:
			continue

		#Append sufficient 'filler' days if there is a gap in the calendar file. Assume 0 working hours if day is not listed.
		if len(calendar.days) == 0:
			yesterday = None 
		else:
			yesterday = calendar.days[-1].datestamp
		if yesterday:
			currentDate = yesterday + timedelta(days=1)
			while currentDate < row.date:
				day = Day(datestamp=currentDate, working_hours=0)
				calendar.days.append(day)
				currentDate = currentDate + timedelta(days=1)
				logging.info("Adding filler day {}".format(calendar.days[-1]))

		#Append the date from the data file
		day = Day(datestamp=row.date, working_hours=row.working_hours)
		calendar.days.append(day)

	#Check some stats to make sure the calendar is as expected
	if len(calendar.days) == 0:
		raise ValueError("No dates added - check that start and end dates are in the data source")
	if calendar.days[-1].datestamp != end:
		raise ValueError("Last date does not match end date - check that data source has sufficient data for the time period selected")


	#Show the calendar in the log file
	logging.info("Calendar generated ({} days included)".format(len(calendar.days)))
	logging.info("First 10 days of calendar:")
	for i in range(min(10,len(calendar.days))):
		logging.info(calendar.days[i])
	
	return calendar
                                                                                                                       
########################
#create some sample data
def create_week_september_5():
	week = []
	for d in range(5,12):
		datestamp = date(2016,9,d)
		if d < 10:
			working_hours = 8
		else:
			working_hours = 0

		day = Day(datestamp,working_hours)
		week.append(day)
	return week


#########################
def sample():
	logging.info('------------------------')
	logging.info('Starting sample() module')

	tasks = load_tasks(data_id='1q7F6Ie2ZGBZ7OsogyHQjMTrHsK27E473zEwRgAfWaEg')

	#Create the calendar
	start = date.today()
	#initialize end, then set it to the latest end date from task
	end = date.today()		
	for t in tasks:
		if t.end.date() > end:
			end = t.end.date()
	cal = create_calendar('data/calendar.csv',start,end)


	sorted_tasks = prioritize_tasks(tasks,cal)

	for t in sorted_tasks:
		assign_blocks(task=t, calendar=cal, start=t.start.date())

	return cal

def slice_calendar(calendar, start, end):

	sliced_calendar = Calendar()

	for d in calendar.days:
		if d.datestamp >= start and d.datestamp <= end:
			sliced_calendar.days.append(d)

	return sliced_calendar


print(__name__)
if __name__ == '__main__':
	#sample()
	pass
		

#example: students = [ Student( score, gender ) for score, gender in <some-data-source> ]