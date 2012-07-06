==============
ConfigTreeView
==============
	This is an implementation of a GtkTreeView in python(using pygtk) that
	allows for easy, fast, and dynamic setting up of a TreeView, its
	TreeViewColumns and CellRenderers. This ConfigTreeView can create a TreeView
	with all its properties initialized through the use of a simple config-type
	file. This config file can be in a python dictionary format, or even read
	in from a JSON object.
	
The Why (Why use a ConfigTreeView?)
===================================
	* The ConfigTreeView was designed in such a way to abstract the developer
	  from having to set up indices for how a ListStore row of data should look.
	  The config file creates an easy way to do it and allows you to supply a
	  row of data in python dict form(or a JSON) while initializing all the
	  properties, columns, cell renderers that could possbily be used in
	  creating a TreeView.
	
	* Eliminates the several lines of code it takes to initialize a TreeView.
	  A TreeView is a very useful but also very complicated widget in the gtk 
	  arsenal and this implementation takes away that complication.
	
	* Useful for data sets that could change frequently without having
	  to go in and change the code.--This is actually the use case that I ran
	  into at my place of work that inspired me to create the ConfigTreeView. We
	  have an application that many people use in the office that is connected
	  to a server. The application gets all of the data from the server and 
	  displays it in a GtkTreeView but the data could change in the near future
	  as we may need to display new columns or different formats of data in the
	  same TreeView so we wanted a system set in place that could allow for us 
	  to change the data the server was sending without having to go in and
	  change the code in the clients(i.e. the TreeView) in order to properly
	  display the newly changed data. With a ConfigTreeView you can do just
	  this: the server can supply a config structure to initialize the clients,
	  eliminating the need for changing the client code.

How to use it
=============
	* It's easy! All you need to do is create a config file(either as a python
	  dict in a .py file or as a JSON file). 
	* Then with a config file, you're ready to create a ConfigTreeView::
	
		from config_treeview import ConfigTreeView
		#Import the config structure(it's a python dict named config)
		from myconfigfile import config
		#Create a ConfigTreeView using config as the configuration structure
		treeview = ConfigTreeView(config)
		#Apply the config structure to finish initalizing the TreeView
		treeview._apply_config()

For more information
====================
Check out the documentation in the source in the `html/` directory starting with 
`index.html`

or visit the docs: http://packages.python.org/configtreeview/
