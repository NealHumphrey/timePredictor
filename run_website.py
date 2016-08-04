#Bottle provies a simpe server that can run Python code and connect it to a website. 
#Unlike Django and others, there's no database or other full-stack components, making it useful for quick display-based tools.

#Import the stuff we need first:
from bottle import route, run, template, view, debug
#Obviously you can import other modules here.


#Run arbitrary code
my_var = {'foo': 200, 'bar': 'This comes after bar!'}
print("I'm succesfully running Bottle!")

#Tell Bottle what pages to create

#The most simple version
@route('/hello')
def hello():
    return 'Hello World'

#Bottle uses templates. Templates are saved in /views and named filename.tpl
@route('/yo')
def yo():
    return template('main')

#You can create dynamic URLs. Use <> in the @route and bind it in the function definition.
@route('/yo/<ending>')
def yo(ending):
	#and we can pass arbitrary variables to the template
    return template('main', ending = ending, my_page_var = 21, other_var = my_var) 

#An alternative definition method that allows you to return a dictionary
@route('/')
@view('example_template')
def main():
	return dict(my_var=my_var)


#When it's all set up, run the 
run(host='localhost', port=8080, debug=True)
#not sure why, can't get reloader to work. This would be via reloader=True. Restart the server if you edit this file.
#TODO - remove the debug call in production!