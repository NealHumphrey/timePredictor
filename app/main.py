"""
Summary Notes:
	App creates a calendar, which is a list of day objects
	Each day has 'working_hours', the hours available for doing work
	Tasks are components that have an estimated time to complete.
	The tool automatically breaks Tasks into Blocks. These are assigned to lists in both Days in the calendar and to the original Task they were generated from. 

	Calendar then can be sent to the view.

	Current status:
	-create_calendar and load_tasks both just create dummy data - need to load from a file
	-prioritize tasks not yet implemented
	-need to load start/end dates from the URL dynamically (i.e. run_website needs to call a function with two date arguments)
	-Nothing in the view is implemented yet - just a text output
	-Times are not dealt with at all (but they are stored for blocks and tasks)

"""






from datetime import timedelta, datetime, time, date
from collections import deque

#Just a handy tool for making random objects
class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)



def ex():
	return 2

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

		#summary properties assigned to Task class
		Task.allTasks.append(self)

	def __repr__(self):
		return 'Task{name: %r, project: %r, hours_needed: %r}' % (self.name, self.project, self.hours_needed)

	def clear_blocks(self):
		self.blocks = []



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

# Break a task into blocks, and assign these blocks to the calendar as soon as possible.
# For each day, if hours_free > block_size, create a block and assign it to that day.
# For any task time that remains on task.end, add it to the deadline day. This will overbook the day.
# Task hours that need to be assigned are those not yet completed (hours_needed - hours_done)
# 	task: a Task object
#	calendar: an ordered list of Day objects
#	start: 
def assign_blocks(task,calendar,start):
	print("Entering task {}".format(task.name))

	block_size = 1 #hour(s)
	hours_to_assign = task.hours_needed - task.hours_done
	hours_assigned = 0

	#This will be incremented when each portion is created.
	portion=1

	# if not empty, we assume this has already been run; haven't handled re-running appropriately so we will instead throw an error
	if len(task.blocks) > 0:
		raise Exception("task.blocks already populated - don't want to duplicate the blocks")
	
	#TODO log warning if start date is earlier than task.start. But, allow behavior and require caller to use start appropriately.


	for d in calendar.days:
		print(d.datestamp)

		#Go to the next day if it's not the start date
		if d.datestamp < start:
			print("continuing")
			continue

		print("calculating")
		while hours_to_assign > hours_assigned:
			#Just fill the available hours in the day, unless today is the deadline. On the deadline we can overbook the day.
			if d.hours_free() >= block_size or task.end.date() <= d.datestamp:
				b = Block(start=datetime.combine(d.datestamp, time(9,0)), duration=block_size, task=task, portion=portion)		
				hours_assigned += b.duration
				
				print("portion: {}".format(portion))

				portion += 1

				task.blocks.append(b)
				d.blocks.append(b)
			else:
				break #assign the hours to the next day

		if hours_assigned >= hours_to_assign:
			break #no need to look at the rest of the days


	#handle error - ran out of days in calendar (should add a list at the end of the calendar)






# Takes a list of tasks and sorts the list so that they can be passed through the assign_blocks routine
# 	Priority:
#		1) Time constrained - 
#			hours_available= total working hours available in the calendar between task start and end dates
#			hours_needed = time remaining in task
#			The smallest (hours_available - hours_needed) get top priority (i.e. must happen on specific days)
#			
#		2) end - if time constrained is the same, do the one with the earliest deadline first
#		3) start - finally, do the one with earliest start date first. 
def prioritize_tasks(tasks, calendar):
	print("Potential time: {}".format(calendar.potential_time(date(2016,9,6),date(2016,9,7))))

	return tasks

#Returns a list of tasks loaded from a data source (CSV file)
#this will need to load the data from the CSV or other file
#TODO only sample data creation for now
def load_tasks(data):
	sample_task = Task(name='My Task', start = datetime(2016,9,6,9,30), end = datetime(2016,9,8,10,30), hours_needed=15, hours_done=0, completed=False, project='Test Project', notes='no notes')
	tasks = [sample_task]

	second_task = Task(name='Second Task', start = datetime(2016,9,7,9,30), end = datetime(2016,9,7,10,30), hours_needed=9, hours_done=0, completed=False, project='Test Project', notes='my note')
	tasks.append(second_task)

	specific_task = Task(name="Specific",start=datetime(2016,9,7,13,0),end=datetime(2016,9,7,14,0),hours_needed=1)
	tasks.insert(0,specific_task)

	return tasks

def create_calendar(data, start):
	pass
	#parse the data to get date and available hours
	#make a list of ordered days starting with start (a date)
	#if start is not in the data, throw error
	#if there are any gaps in the data, create filler days with working_hours = 0


	#for now just make a sample calendar to use
	calendar = Calendar()
	calendar.days = create_week_september_5()

	#some extra sample code
	day = Day(datestamp=date(2016,9,12), working_hours=8)
	calendar.days.append(day)

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

	print('-----------')

	cal = create_calendar(1,1)
	print(cal)
	tasks = load_tasks('nodata')
	tasks = prioritize_tasks(tasks,cal)

	print(tasks)

	for t in tasks:
		assign_blocks(task=t, calendar=cal, start=t.start.date())

	print("Available time: {}".format(cal.potential_time(date(2016,9,6),date(2016,9,7))))
	print("Overbooked time: {}".format(cal.overbooked_time(date(2016,9,6),date(2016,9,7))))

	return cal
	
if __name__ == '__main__':
	sample()

		

#example: students = [ Student( score, gender ) for score, gender in <some-data-source> ]