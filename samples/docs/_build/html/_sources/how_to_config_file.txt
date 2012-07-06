.. how-to-config-file-label:

============================
HOW-TO: Create a config file
============================

This document details everything you need to know about creating a config file
for use with a ConfigTreeView. First I'll say a few things about how a config
file is made.

Making a config file
--------------------
	
		-The config file is represented as a dictionary in python. Because of
		this, you can either create a python dict in a separate .py file or
		create one on the fly within your code...OR...you can create the dict
		in a JSON document...and simply give the path to the JSON file in the
		constructor to the ConfigTreeView where you'd supply the python dict
		normally.
	
	
Basic Structure
---------------
	
		-Here's a look at the top-level keys in the config dict:
		::
		
			{
				"treeview": {},
				"treemodel": {},
				"index_names":{},
				"column_order":[],
				"macros": {},
				"columns":{}
			}
		
-----------------------------
The *treeview* key(optional):
-----------------------------

The *treeview* key(this key is not required, unless you're setting properties):
	This key sets up everything dealing with initializing the TreeView container.
	This includes setting gtk properties, some style options and also supplying
	custom positional and/or keyword arguments to your custom ConfigTreeView.
	
		example:
		::
		
			{
				"treeview": {
					"properties": {
						"rules-hint": True,
						"headers-clickable": True
					},
					"args": [],
					"kwargs": {},
					"bg": "green",
					"bg-even": "red",
					"bg-odd": "yellow",
					"selection-mode": "SELECTION_SINGLE",
					"selection-color": "blue"
				}
			}

	The *properties* key defines gtk properties for the TreeView as found in the
	pygtk documentation: http://www.pygtk.org/docs/pygtk/class-gtktreeview.html
	Any of the properties listed here can be defined in the "properties" key.
	An entry in the *properties* dict takes the following form:
	
		::
		
			"gtk-property-name": "value"
	
	Note: if the value is not a native python type(ex: a gtk object),
	this is not currently supported if you define the config file in 
	a JSON as primitive types...but only a few properties are
	like that. If you need to use these types, consider it good practice
	to define the config structure in it's own python module. Then you can
	import all the modules you need.

	
	The *args* and *kwargs* keys let you define positional(args) and keyword(kwargs)
	to a custom ConfigTreeView prototype. This works in the same fashion as passing
	any positional([]) and keyword({}) args to an object in python. A common use/need for
	this arises when you need your custom treeview to know the index of an attribute
	that was defined in the config file. The config file makes this easy with the
	use of the *$index* dotted-key string.
	
	An example of an $index key:  `$index.cell_bg_set`
	Supplying the above $index key in either args or kwargs will set that
	parameter as the index of 'cell_bg_set'( as defined in *index_names*) in
	the data model.
	Values supplied to *args* and *kwargs* are passed through the 'handle_args'
	function in the ConfigTreeView which should be overridden when you create
	your own custom ConfigTreeView.
	
	The *bg*, *bg-even*, and *bg-odd* keys are style options that I've added that
	allow you to change the background colors of a TreeView. *bg* by itself
	changes the background to a single color...color can either be a gtk-accepted
	string name(ex: "blue") or it can be a hexidecimal string(ex: "#FF0078").
	If you wish to have your ConfigTreeView with two colors, alternating per row,
	supply the *bg-even* and *bg-odd* colors instead. Note: *bg-even* and *bg-odd*
	must be supplied together or you'll get errors when you try to apply your
	config.
	A GTK Note: These color options change the underlying GtkStyle which is 
	determined by the users theme. You should try to stay away from using this
	and respect a user's theme choices...but if you're in a controlled environment
	or it's for personal use, then it's okay to change these styles as you see fit.
	
	The *selection-mode* key allows you to set the mode of the GtkTreeSelection.
	This is limited to these values: 
	(SELECTION_NONE, SELECTION_SINGLE, SELECTION_BROWSE, SELECTION_MULTIPLE)
	
	The *selection-color* key allows you to change the color of the selection bar
	in the TreeView. This bar is what highlights a row you've just clicked on.
	The value for this key follows the same guidelines as *bg*, *bg-even* and *bg-odd*
	Note: This too should only be used in a controlled environment, because you
	should respect the user's choice of theme.

------------------------------
The *treemodel* key(optional):
------------------------------
	
	This optional key defines a TreeModel instance that is required to properly
	manage and store the data so that it can be displayed by your ``ConfigTreeView``.
	When a call to ``ConfigTreeView.get_treemodel()`` is made, the information
	for the TreeModel to create is grabbed from this key's structure:
	
		.. code:: python
		
			{
				#Config stuff here...
				"treemodel": {
					"module": "chronicle.gui.tools.image_loader",
					"class": "ImageStore",
					"args": ["$index.market.pixbuf"],
					"kwargs":{},
				}
				#More config stuff here...
			}
	
	* The *"module"* key is a string that points to the location of the
	  module that you need to import in order to create an instance of the
	  custom TreeModel you need to use.
	* The *"class"* key is a string that is the name of the custom TreeModel that
	  will be instantiated. Note: This class must be an instance of a `GtkTreeModel`
	  or the instantiation will fail and fallback to a `GtkListStore`.
	* The *"args"* key is a list of all the positional arguments you want to
	  send to the TreeModel's *_handle_args()* method. This method should be
	  present in your TreeModel custom implementation if you need to pass any
	  arguments to it that will be handled before data rows are appended to the
	  model.
	* The *"kwargs"* key is a dict of keyword arguments you to send to the TreeModel's
	  *_handle_args()* method. The same rules apply to this key as to the *"args"* key.

	It is important to note that if this key is not supplied, or there is any
	kind of error in importing, initializing, or running the custom implementation
	defined in this structure--the ConfigTreeView will fallback and initialize
	a `GtkListStore` with the proper *types* and return that instead when *get_treemodel()*
	is called.
	

--------------------------------
The *index_names* key(required):
--------------------------------

	This required key defines how your data structure will look, as
	well as defining the types for each member of a row of data. It essentially
	defines what attributes a row of data needs, and the types for each attribute.
	An example:
	
	::
	
		{
		  "index_names":{
			  "record_open_bool": bool,
			  "order_status":{
				  "markup": str,
			  },
			  "column_one":[
				  {"markup": str, "cell-background":str},
				  {"pixbuf": "gtk.gdk.Pixbuf"}
			  ]
		  }
		}
		

	The top level keys within the *index_names* dict are names that you
	give to columns, or names that you give to a variable. And the values at
	these keys result in a type for that value later on.
	
	In the above example the "record_open_bool" key is an example
	of how you'd define a variable. A 'variable' in the config file is
	a value that you want an index for in the data model, but it is used by
	more than one CellRenderer. You'll see how this is applied when the *columns*
	structure is detailed later on.
	
	The *order_status* key in the above example is for a column named *order_status*
	that has a single CellRenderer that wishes to create an index for "markup" with
	a type of 'str'.
	
	The *column_one* key in the above example is for a column named *column_one*
	that has two CellRenderers. The first CellRenderer defines a "markup" property
	of type str and a "cell-background" property of type str. And the second
	CellRenderer defines a "pixbuf" property of type "gtk.gdk.Pixbuf".
	
	Note: when creating *$index* args to pass to "treeview.args/kwargs" you can
	define any value within the *index_names* dict by using dotted-key-notation.
	Examples:
	::
	
		"$index.record_open_bool"
		"$index.order_status.markup"
		"$index.column_one.0.markup"
		"$index.column_one.1.pixbuf"

----------------------------------
The *column_order* key( required):
----------------------------------

	This required key defines the order you want the columns to be appended to
	the ConfigTreeView.
	Example:
	::
	
		"column_order": ["order_status", "column_one"]
	
	
	The column names are the same as the columns that you define in *index_names*
	and also *columns*.

---------------------------
The *macros* key(optional):
---------------------------
	This key lets you define a set of properties that you wish to use multiple
	times throughout the config file. This feature is added only as a convenience
	to make the config structure cleaner looking by removing some redundancies.
	Example:
	
	::
	
		{
			"macros":{
				"cell-text-default":{
					"font": "Lucida Sans 8",
					"foreground": "green",
				}
			}
		}	

	In the above example, a macro named "cell-text-default" was defined that
	sets properties "font" and "foreground". These properties must be valid
	GtkProperties for whatever widget you end up defining them for( TreeViewColumn
	or CellRenderer)
	
	In the next section, *columns*, you'll see how to set a macro that's been
	defined.

----------------------------
The *columns* key(required):
----------------------------

	This required key lets you define the columns, by name, that you want to
	create for this ConfigTreeView. The name must be the same name as defined
	in *index_names*.
	Example:
	
	::

		"columns":{
			"column_one":{
			},
			"order_status"{
			}
		}


	Example of "column_one" column:
	::
	
		"column_one":{
			"header":{
				"title": "Column1",
				"module": None,
				"class": "Button",
				"args": [],
				"kwargs": {},
			},
			"macros": ["cell-text-default"],
			"properties"{
				"resizable": True,
				"visible": True,
				"max-width": 100,
			},
			"renderers":[]
		}

		
	The *header* key is where you define anything about this column's header.
	If you just want text in the header, then supply the *title* key. You may
	wish to put a widget up there which you can do by supplying the 'module',
	'class', 'args', and 'kwargs' keys for the class you want.
	Note: if module isn't supplied, it's defaulted to the gtk module. And if
	class isn't supplied, it's defaulted to gtk.Label.
	
	The *macros* key is where you set the macros that you already defined
	in the *macros* top-level-key. This is simply done by supplying
	the name of the macro(s) you wish to use in a list as is demonstrated
	in the above example.
	
	The *properties* key is where you define any properties that you want
	to set for the particular column. This follows the same guidelines as
	the *properties* key in the *treeview* top-level key.
	TreeViewColumn properties: 
	http://www.pygtk.org/docs/pygtk/class-gtktreeviewcolumn.html

-------------------	
Defining Renderers:
-------------------
	The *renderers* key is where you define what CellRenderers will go
	into a given column and also what properties and indices the renderer
	will have.
	Example:
	
	::
	
		"column_one":{
			"renderers":[
				{
					"pack": "pack_start",
					"expand": "True",
					"module": None,
					"class": "CellRendererText",
					"args": [],
					"kwargs": {},
					"properties":{
						"height": 25,
						"xpad": 5,
						"font": "Times New Roman 13"
					},
					"indices": {
						"markup": True,
						"cell-background-set": "record_open_bool"
					}
				}
				{
					"class": "CellRendererPixbuf",
					"indices": {
						"pixbuf": True,
						"cell-background-set": "record_open_bool"
					}
				}
			]
		}

	
	If a column has a single CellRenderer, then you define the *renderers*
	key as a dict({}), but if a column has multiple CellRenderers, you define
	the *renderers* key as a list([]) containing dicts where each dict
	is a CellRenderer
	
	From the above example you see a CellRenderer is defined as:
		The *pack* key defines how the CellRenderer will be added to the TreeViewColumn.
		Accepted values are: "pack_start" and "pack_end". If this key isn't supplied,
		it defaults to "pack_start".
		
		The *expand* key defines whether or not the CellRenderer will expand to
		the size the TreeViewColumn supplies. True or False. If key isn't supplied,
		it defaults to True.
		
		The *module*, *class*, *args*, and *kwargs* keys are used to supply
		a custom CellRenderer. If these keys aren't supplied, it's defaulted to
		a gtk.CellRendererText
		
		The *properties* key is where you define any properties that you want
		to set specifically for this CellRenderer. This follows the same guidelines
		as the *properties* key in the *treeview* top-level key.
		CellRendererProperties: http://www.pygtk.org/pygtk2tutorial/sec-CellRenderers.html
		
		The *indices* key is where you define what CellRenderer properties you
		want controlled by the data model. You already defined the types and
		size of the structure, this is where you request an index in the data
		model for the given property.
		These properties are also the same properties that you can define
		in the *properties* key, but when they're defined as an index, the value
		of the property is defined by the data model for each row.
		
		In the above example, the first CellRenderer dict defines two properties:
		"markup" and "cell-background-set". When you're just requesting a new index,
		a value of True is passed...but when you're setting that value to another
		value( granted the value is defined in *index_names*) then you're simply
		pointing that property to an index that is shared by multiple renderers.
		
	

	
