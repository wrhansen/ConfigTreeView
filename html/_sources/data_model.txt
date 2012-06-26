=========================
More About ConfigTreeView
=========================

	The ``ConfigTreeView`` is an implementation of ``GtkTreeView`` that has its widgets,
	their properties, and attributes set via a configuration structure. Because
	of the nature and design of this config structure, a very simple, intuitive,
	and flexible data model has been created that both define the look and feel
	of the treeview, but also explicitly detail the shape and look of the data
	that the ``ConfigTreeView`` is expecting.
	
	The ``ConfigTreeView``'s  data model is indirectly defined in the ``index-names``
	key in the config structure. This key has a dictionary as its value that
	looks something like this:
	
		.. code:: python
		
			{
			  'cell-bg-index': bool,
			  'market':{'pixbuf': "gtk.gdk.Pixbuf"},
			  'status':[{'markup':str},{'markup':str}],
			  'name':{'markup':str},
			  'address':{'markup':str},
			  'contact':{'markup':str},
			  'payment':[{'markup':str}, {'markup':str}],
			  'shipping':{'markup':str},
			  'comments':{'markup':str},
			  'placed':{'markup':str},
			  'id': str,
			}

	Each inner-level key represents a new index of the defined type in a data row
	that will eventually be inserted into a GtkTreeModel.

The Data Model
==============

	The ConfigTreeView data model refers to what structure the incoming data must
	look like in order for the data to be properly formatted and displayed. The data
	model is indirectly defined by the ``index-names`` dictionary defined in the
	configuration structure. What this means is that the ``index-names`` dictionary is also
	the same structure that the data model should follow, replacing the types that
	were defined for the actual values at that particular index. An example data
	structure for a single row of data following the data model defined above:
	
		.. code:: python
		
			{
			  'cell-bg-index': True,
			  'market':{'pixbuf': "/images/market1.png"},
			  'status':[{'markup': "Current Status"},{'markup': "Shipped"}],
			  'name':{'markup': "Darth Vader"},
			  'address':{'markup': "The Death Star"},
			  'contact':{'markup': "867-5309"},
			  'payment':[{'markup': "Visa"}, {'markup': "$100.00"}],
			  'shipping':{'markup': "Shipped"},
			  'comments':{'markup': "No comments"},
			  'placed':{'markup': "2012-06-19 12:08:33PM"},
			  'id': "123435252335",
			}
			
	But the data model also is a little more flexible than this. There may come
	a time when you don't want to display all information for a row. With this
	data model you only need to define the indices that you plan on using. So
	a more minimal row of data could look like this:
	
		.. code:: python
		
			{
			  'name': {'markup': "Darth Vader"},
			  'address': {'markup': "The Death Star"},
			  'status': [{'markup': "Current Status"}, {'markup': "Shipped"}]
			}
