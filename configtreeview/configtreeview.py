#encoding: utf-8
"""
Copyright (C) 2012 Wesley Hansen
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Contact via email: wes@ridersdiscount.com
"""

__author__ = "Wesley Hansen"
__version__ = "0.1.3.12"
__date__ = "07/6/2012 10:50:22 PM"


import gtk
import sys
import simplejson
import os
import pprint
import copy


class InvalidFilePathError(Exception):pass
class InvalidRendererList(Exception):pass
class ConfigValidationError(Exception):pass

class ConfigTreeView( gtk.TreeView ):
	'''
	A TreeView wrapper that initializes its columns, renderers and properties through
	the use of a configuration structure. This ConfigTreeView is a little different
	from the original design. The TreeView itself handles assigning indices to the
	data model, which is determined by the configuration structure sent in this
	TreeView's init method.
	'''	
	minimum_keys = {'index_names'} #The minimum top-level keys that are required in the config structure
	accepted_keys = {"treeview", "treemodel", "column_order", "macros", "columns"} | minimum_keys#The accepted top-level keys that can be in a config structure	
	def __init__(self, config, debug=False):
		'''
		This treeview is built from a configuration data structure. The configuration
		gives enough information to build all of the TreeView's columns,
		creates headers, create and pack cellrenderers, apply attributes
		and properties to the columns and cellrenderers, and keeps track
		of the indices that the columns require to give to the data model.
		
		:param `config`:
			The configuration structure(a python dict) that will build the underlying
			gtk.TreeView.Check out :doc:`HOW-TO create a config <how_to_config_file>`
			for info on how to build a configuration structure
		'''
		gtk.TreeView.__init__(self)

		self.debug = debug
		#Open json dict
		if isinstance( config, basestring):
			#It's a string, check if it's a valid filepath
			if os.path.exists( config ):
				fp = open(config, 'r')
				fp.seek(0)
				self.config = simplejson.loads( fp.read() )
			else:
				raise InvalidFilePathError( "'%s' is not a valid filepath" % config )
			
		elif isinstance( config, dict ):
			#It's a config dict already, so set self.config
			self.config = dict(config)

		self.macros = None #The macros structure that will be used to set properties
		self.index_map = {}#Maps column names/index variables to an index in a TreeModel row
		self.index_vars = []#A list of all the index variable names--Indices shared by multiple renderers
		self.types = []#The types(in order) as they will be sent to a TreeModel--built by the ConfigTreeView based on the config file setup
		self.args = []#Positional args for a custom ConfigTreeView to handle
		self.kwargs = {}#Keyword args for a custom ConfigTreeView to handle
		self.selection_modes = ('SELECTION_SINGLE', 'SELECTION_NONE', 'SELECTION_BROWSE', 'SELECTION_MULTIPLE')#Acceptable selection modes for a GtkTreeView

	def _apply_config(self):
		'''
		Validate the configuration structure, build the treeview's columns, headers,
		renderers and properties based on the configuration data structure
		'''
		#Validate the config structure
		#1 - Check that the minimum keys to create the treeview are present
		for key in self.minimum_keys:
			if key not in self.config:
				raise ConfigValidationError("Validation Error!: %s is missing from config!!!!"%key)
		#2 - Check that the keys that are present in config are all valid
		for key in self.config:
			if key not in self.accepted_keys:
				raise ConfigValidationError("Validation Error!: %s is not a valid key in config!!!!" % key)
		#3 - Validate index_names
		#	This includes checking for columns that aren't defined in index_names, but are present in "columns"
		#	Also the reverse, a warning is issued if the column is never used
		#		NOTE: this should be intelligent and skip over values that are defined

		#Build the index map--this structure will be a mapping of cellrenderer
		#property names to the index in a TreeModel's row that the property will
		#be stored in.
		self.index_map = copy.deepcopy(self.config.get('index_names', {})) #Need to make deepcopy because we don't want any reference to the original structure.
		
		#Validate the index_map
		for column in self.config.get('columns', {}):
			if column not in self.index_map:
				self.index_map = {}#Reset index_map
				raise ConfigValidationError("Validation Error!: '%s' is defined as a column in the config structure, but it isn't defined in `index_names`!" % column)
		
		for column, value in self.index_map.iteritems():
			if not isinstance(value, basestring) and (isinstance(value, list) or isinstance(value, dict)):
				if column not in self.config.get('columns', {}):
					#Just print a warning that a defined column is never used
					if self.debug: print "Warning!: '%s' is defined as a column in `index_names`, but is never used" % column

		index_names = self.index_map
		if index_names is {}:
			raise KeyError( "`index_names` doesn't exist in the config" )
		for key,value in index_names.iteritems():
			if isinstance( value, dict ):
				value = self._handle_dict_of_types(value)
				self.index_map[key] = value
			elif isinstance( value, list ):
				for idx,item in enumerate(value):
					val = self._handle_dict_of_types(item)
					self.index_map[key][idx] = val
			else:
				value = self._get_type_index(value)
				self.index_vars.append( key )#Update the index_variables list
				self.index_map[key] = value

		#Debugging
		if self.debug:
			print "Okay, successfully created index map, here it is!:"
			pprint.pprint( self.index_map )
			print "*"*50
			print 'Types:'
			pprint.pprint(self.types)

		#Handle args--for custom ConfigTreeViews
		#Check for $index args or kwargs...validate them
		#It's valid if the 'dotted' key evaluates to an actual value
		#in self.index_map
		if self.config.get('treeview', None) is not None:
			args = self.config['treeview'].get('args', [] )
			kwargs = self.config['treeview'].get('kwargs',{} )
			
			for idx,value in enumerate(args):
				if isinstance( value, basestring) and value.startswith('$index.'):
					#Handle index 'dotted' key notation
					value = self._evaluate_dotted_key(value)
					args[idx] = value
			self.args = args
			
			for key,value in kwargs.iteritems():
				if isinstance( value, basestring) and value.startswith('$index.'):
					value = self._evaluate_dotted_key( value )
					kwargs[key] = value
			self.kwargs = kwargs
		self._handle_args( *self.args, **self.kwargs )
		
		#Set Macros
		self.macros = self.config.get('macros', {} )
		
		#Intialize TreeView Properties
		self._init_treeview()
		
		#Initialize TreeViewColumns
		#--This includes its properties
		#--But also a column's renderers, and its properties, and indices
		self._init_treeview_columns()
		
	def _init_treeview_columns(self):
		'''
		Initialize the GtkTreeView's GtkTreeViewColumns. This includes creating a TreeViewColumn,
		with certain properties, creating its CellRenderers, with all of its properties and attribute settings,
		packing the renderers into the column, and then appending the column to the TreeView
		'''
		columns = self.config.get( 'columns', None )
		if columns is not None:
			#Validate that each column name exists in 'columns'
			if self.config.get('column_order', None) is None:
				raise KeyError( "KeyError: `column_order` doesn't exist in config" )
			for name in self.config['column_order']:
				if name not in self.config['columns']:
					raise KeyError("KeyError: '%s' doesn't exist in `columns` of config"% name)

			for name in self.config['column_order']:
				#Create TreeViewColumn
				col = gtk.TreeViewColumn()
				col.set_data('name', name )#Use get_data('name') to determine which column this is
				column = columns[name]
				#Set Macro Properties
				self._set_macros( col, column.get('macros', None ) )
				#Set TreeViewColumn properties
				self._set_properties( col, column.get('properties', None ) )
				#Initialize Renderers
				self._init_renderers( col, column.get('renderers', None ), name )
				#Append Column to the TreeView
				self.append_column( col )
				#Initialize Header
				self._init_header( col, column.get('header', None ) )

	def _init_header( self, col, header ):
		'''
		Initialize the GtkTreeViewColumn's header. If this is a custom widget, import the
		necessary module and classes with the supplied '`module`, `class`, `args`, `kwargs`' 
		keys in the dictionary.  If just 'title' is given, set the title.
		If a class name is given, but 'module' is None, then default to the gtk module.
		if 
		'''
		#Check for title first
		#If both title and a custom widget are supplied, create the title first
		#So if the custom widget doesn't load properly, it will fallback to the title
		if header is not None:
			title = header.get('title', None )
			if title is not None:
				label = gtk.Label()
				label.set_markup( title)
				label.show()
				col.set_widget( label )
		
			#Header widget
			module = header.get( 'module', None )
			moduleclass = header.get( 'class', None )
			skip_header_widget = False
			if module is not None:
				try:#Import the given module
					module = __import__( module, globals(), locals(), [moduleclass], -1 )
					moduleclass = getattr( module, moduleclass)
				except ImportError:#module doesn't exist, fallback to gtk
					if self.debug: print "Warning!: Couldn't import module `%s`, falling back to gtk" % module
					module = gtk
					moduleclass = getattr( module, moduleclass )
				except AttributeError:
					if self.debug: print "Warning!: `%s` is not an attribute of `%s`, falling back to gtk.Label" % (moduleclass, module)
					module = gtk
					moduleclass = getattr(module, 'Label' )
				except:
					if self.debug: print "An unexpected error occured, falling back to gtk.Label"
					module = gtk
					moduleclass = getattr( module, 'Label' )
			else:
				if moduleclass is not None:
					module = gtk
					moduleclass = getattr( module, moduleclass )
				else:
					#Do Nothing here, module and moduleclass are none...so fallback to title
					skip_header_widget = True
				
			if skip_header_widget == False:
				#Get args and kwargs
				#If they're None, then do not pass anything to the constructor
				args = header.get( 'args', None )
				kwargs = header.get('kwargs', None )
				#Create CellRenderer
				widget = None
				if args is None and kwargs is None:
					widget = moduleclass()
				else:
					widget = moduleclass( *args, **kwargs )
			
				col.set_widget( widget )

	def _init_renderers( self, col, renderers, col_name):
		'''
		Determine if the `renderers` key is valid, and attempt to create/pack the renderers into the column
		
		Args:
			col[gtk.TreeViewColumn]: The column to pack a renderer into
			renderers[list or dict]: Information regarding initialization of a gtk.CellRenderer( multiple if a list)
			col_name[str]: Name of the column
		'''
		if renderers is not None:
			if isinstance( renderers, list ):
				if len(renderers) <= 1:
					raise InvalidRendererList( "InvalidRendererList!:  'renderers' cannot be a list of length `%s`"%len(renderers) )
				for idx, renderer in enumerate(renderers):
					key_list = [col_name]
					key_list.append( idx )
					self.__setup_renderer(col, renderer, key_list)
					
			elif isinstance( renderers, dict ):
				key_list = [col_name]
				self.__setup_renderer( col, renderers, key_list )
			else:
				raise ValueError( "ValueError!:  `renderers` must be either of type list or dict, not %s"%type(renderers))

	def __setup_renderer( self, col, renderer, key_list ):
		'''
		Initalize the GtkTreeViewColumn's renderers. This includes setting their properties, adding
		data model attributes and, if necessary, creating them from a custom class, with their
		own args and kwargs.
		Args:
			col[gtk.TreeViewColumn]: The column to pack a renderer into
			renderer[dict]: a structure that defines how to create a gtk.CellRenderer.
			The structure has the following form:
				{
					'pack': 'pack_start',
					'expand': True,
					'module': None,
					'class': 'CellRendererText',
					'args': [],
					'kwargs': {},
					'properties': {
					},
					'macros':[],
					'indices':{
					}
				}
		'''
		if renderer is not None:
			#Determine module and class to use
			module = renderer.get( 'module', None )
			moduleclass = renderer.get( 'class', 'CellRendererText' )
			if module is not None:
				try:
					module = __import__( module, globals(), locals(), [moduleclass], -1 )
					moduleclass = getattr( module, moduleclass)
				except ImportError:
					if self.debug: print "Warning!: Couldn't import module `%s`, falling back to gtk"% module
					module = gtk
					moduleclass = getattr( module, moduleclass )
				except AttributeError:
					if self.debug: print "Warning!: `%s` is not an attribute of `%s`, falling back to gtk.CellRendererText" % (moduleclass, module)
					module = gtk
					moduleclass = getattr(module, 'CellRendererText' )
				except Exception as e:
					if self.debug: print "An unexpected error occured, falling back to gtk.CellRendererText %s" % e
					module = gtk
					moduleclass = getattr( module, 'CellRendererText' )
			else:
				module = gtk
				moduleclass = getattr( module, moduleclass )
					
			#Get args and kwargs
			#If they're None, then do not pass anything to the constructor
			args = renderer.get('args', None)
			kwargs = renderer.get('kwargs', None)
			
			#Create CellRenderer
			cell = None
			if args is None and kwargs is None:
				cell = moduleclass()
			else:
				cell = moduleclass( *args, **kwargs )
				
			#Set Macros
			self._set_macros( cell, renderer.get( 'macros', None ) )
			
			#Set properties
			#These properties will occur on every row
			self._set_properties( cell, renderer.get('properties', None ) )

			#Pack it in the column
			pack = renderer.get('pack', 'pack_start' )
			expand = renderer.get( 'expand', True )
			pack = getattr( col, pack )
			pack(cell, expand)

			#Setup indices
			indices = renderer.get( 'indices', None )
			if indices is not None:
				for attr,index in indices.iteritems():
					value = None#The index of the attribute
					if isinstance( index, bool ):
						if index == True:
							key_list.append( attr )
							value = self._get_index( key_list )
					elif isinstance( index, basestring ):
						value = self._get_index( [index] )
					col.add_attribute( cell, attr, value )

	def _get_index( self, key_list ):
		'''
		Attempts to get the index for the given attribute at the path defined
		in key_list
		Args:
			key_list[list]: A list of the nested indices to access in the index_map
		'''
		index_map = self.index_map
		keys = ""
		for key in key_list:
			keys = keys + "[" + str(key) + "]"
		for idx,index in enumerate(key_list):
			try:
				index_map = index_map[index]
			except KeyError:
				if self.debug: print "KeyError!:  `%s` is not  defined in 'index_names' at %s" % (index, keys)
				raise
			except IndexError:
				if self.debug: print "IndexError!:  `%s` is too large an index in 'index_names' at %s" % (index, keys)
				raise
		return index_map

	def _set_properties( self, widget, properties ):
		'''
		Set the properties of the given `widget` to each of the properties in `properties`
		If the property is invalid, a warning is made, the property is skipped and initialization
		is continued
		'''
		if properties is not None and isinstance( properties, dict ):
			for prop, value in properties.iteritems():
				try:
					widget.set_property( prop, value )
				except TypeError:
					if self.debug: print "Warning: [%s] is not a valid property for `%s`, skipping it." % (prop, widget)

	def _init_treeview(self):
		'''
		Initialize the GtkTreeView's properties and settings. This includes any of the
		gtk.TreeView's properties that can be set with 'treeview.set_property(property, value)'
		as well as some style properties like background color: whether it be a single color, have alternating
		row colors, or possibly an image as the background.
		'''
		struct = self.config.get( 'treeview', None )
		if struct is not None:
			#Set TreeView properties
			self._set_properties( self, struct.get('properties', None ))
			
			#Background stuff
			#Handle Alternating row colors first
			if struct.get( 'bg-even', None) is not None and struct.get( 'bg-odd', None) is not None:
				self._set_alternating_bg(struct['bg-even'], struct['bg-odd'])
			#Or, fallback on a single background color
			elif struct.get( 'bg', None ) is not None:
				self._set_bg( struct['bg'] )
			#Finally, fallback to no background changes(Whatever the default treeview style is)
			else:
				pass
			
			#Selection Mode
			select_mode = struct.get('selection-mode', None )
			if select_mode is not None:
				if select_mode in self.selection_modes:
					selection = self.get_selection()
					selection.set_mode( getattr( gtk, select_mode) )
			
			#Selection Color--The color of the row selection bar
			select_color = struct.get( 'selection-color', None )
			if select_color is not None:
				self.modify_base( gtk.STATE_SELECTED, gtk.gdk.color_parse( select_color ) )

	def _set_alternating_bg( self, even_color, odd_color ):
		'''
		Set the TreeView's background colors to a color scheme that alternates
		every other row. Color scheme is given by `even_color` and `odd_color`.
		'''
		gtk.rc_parse_string( """
		style "alternate_bg_color"{
			GtkTreeView::allow-rules = 1
			GtkTreeView::even-row-color = "%s"
			GtkTreeView::odd-row-color = "%s"
		}
		widget "*alternate_bg_color*" style "alternate_bg_color"
		"""%(even_color, odd_color))
		self.set_rules_hint( True )
		self.set_name( 'alternate_bg_color' )

	def _set_bg( self, color ):
		'''
		Set the TreeView's background colors to a solid color given by `color`.
		'''
		gtk.rc_parse_string( """
		style "bg_color"{
			GtkTreeView::allow-rules = 1
			GtkTreeView::even-row-color = "%s"
		}
		widget "*bg_color*" style "bg_color"
		""" % color)
		self.set_rules_hint( False )
		self.set_name( 'bg_color' )

	def _handle_args( self, *args, **kwargs ):
		'''
		This abstract method is for use with custom classes that inherit :class:`ConfigTreeView`
		that wish to pass custom `args` and `kwargs` to the constructor
		Note: You must override this function in your custom class and
		properly assign the args and kwargs you're trying to grab from the config
		file.
		
		:param `args`:
			Positional arguments passed in typical python fashion.
		:param `kwargs`:
			Keyword arguments passed in typical python fashion.

		'''
		if self.debug:
			print "Args: ",args
			print "Kwargs: ",kwargs		

	def _evaluate_dotted_key( self, value ):
		'''
		Checks for a value at the given indices in self.index_map and returns it.
		If it doesn't find it, then it returns None
		'''
		#Split the index dotted key into parts
		original_value = value
		value = value.replace( "$index.", "" )
		value_list = value.split( '.' )
		#try to traverse
		idx_map = self.index_map
		for index in value_list:
			if index.isdigit():
				idx = int(index)
				try:
					idx_map = idx_map[idx]
				except IndexError:
					if self.debug: print 'IndexError, Not a valid dotted key: `%s` in "%s"'%(idx,original_value)
					raise
			else:
				try:
					idx_map = idx_map[index]
				except KeyError:
					if self.debug: print 'KeyError, Not a valid dotted key: `%s` in "%s"' % (index, original_value )
					raise
		return idx_map

	def _handle_dict_of_types(self, a_dict ):
		'''
		Update each value of the dict with a new index
		'''
		if not isinstance( a_dict, dict ):
			raise TypeError( "TypeError: Multiple CellRenderers can only be represented by a list of dicts in the config file, not a list of '%s'"% a_dict )
		
		for key, value in a_dict.iteritems():
			#print value
			val = self._get_type_index( value )
			a_dict[key] = val
		
		return a_dict
				
	def _get_type_index( self, value ):
		'''
		Update the self.types sequence with the new type
		Returns the available index
		'''
		if isinstance( value, type ):
			pass
			
		elif isinstance( value, basestring ):
			'''
			Attempts to convert a string into a type, if that type is already
			a part of a loaded module( gtk or __builtin__)

			If the value is a string(it came from a JSON config),
			it can either be from module already loaded( gtk.gdk)
			or from __builtin__ as it's just an ordinary type( str, bool...)
			'''
			rfind = value.rfind( '.' )
			module = None
			attr = None
			if rfind != -1:
				#Handle a module in the string name, ex: gtk.gdk.Pixbuf
				module = value[0:rfind]
				attr = value[rfind+1:]
			else:
				module = '__builtin__'
				attr = value
			if module in sys.modules:
				attr = getattr( sys.modules[module], attr)
			else:
				raise TypeError( "Type Error: %s is not a loaded module" % module )
			
			value = attr

		else:
			raise ValueError( "ValueError!: value at config['index_names'][%s] is not a valid value. Looking for a dict, list, string or a valid type"%value )

		#Update the new type
		self.types.append( value )
		return len(self.types)-1

	def _set_macros( self, widget, properties ):
		'''
		Set properties to the `widget` to the macro given
		'''
		if properties is not None:
			for prop in properties:
				if self.macros.get(prop, None ) is not None:
					self._set_properties( widget, self.macros[prop] )
				else:
					if self.debug: print "Warning: [%s] is not a valid macro, ignoring it." % prop

	def get_treemodel(self):
		'''
		Initializes a treemodel that's special for this ConfigTreeView as defined
		in the `treemodel` key of the config structure.
		If there is no `treemodel` defined in the config structure, then a ``GtkListStore``
		is initialized with the types list created from initializing the ConfigTreeView.
		If a custom ``GtkTreeModel`` is defined in the config structure, then it
		must have a function ``_handle_args`` that should assign args and kwargs,
		and also any other post initialization stuff.
		'''
		treemodel_dict = self.config.get('treemodel', {})
		if treemodel_dict.get('module', None) is not None:
			try:
				custom_class = treemodel_dict.get('class', None)
				if custom_class is not None:
					module = __import__(treemodel_dict['module'], globals(), locals(), [custom_class], -1)
					treemodel = getattr(module, custom_class)
							
				else:
					if self.debug: print 'Warning! `class` is empty or None, falling back to GtkListStore'
					treemodel = None
					
			except ImportError:
				if self.debug: print 'CustomTreeModelImportWarning!: module `%s` does not exist!, falling back to GtkListStore.' % treemodel_dict.get('module', '')
				treemodel = None
			except AttributeError:
				if self.debug: print 'CustomTreeModelAttributeWarning!: module `%s` does not have an attribute `%s`, falling back to GtkListStore.' % (treemodel_dict.get('module', ''), treemodel_dict.get('class', ''))
				treemodel = None
			
			if treemodel is None:
				treemodel = gtk.ListStore(*self.types)
			else:
				treemodel = treemodel(*self.types)
				args = treemodel_dict.get('args', [])
				kwargs = treemodel_dict.get('kwargs', {})
				#Handle $index mappings
				for idx, arg in enumerate(args):
					if isinstance(arg, basestring) and arg.startswith('$index.'):
						value = self._evaluate_dotted_key(arg)
						args[idx] = value
			
				for key, value in kwargs.iteritems():
					if isinstance(value, basestring) and value.startswith('$index.'):
						value = self._evaluate_dotted_key(value)
						kwargs[key] = value
			
				try:
					treemodel._handle_args(*args, **kwargs)
				except AttributeError:
					if self.debug: print 'InvalidHandleArgsWarning! Your `%s` doesn\'t have a `_handle_args()` method so your args can not be applied!'
				except Exception as e:
					if self.debug: print 'ErrorHandleArgsWarning! There was an error trying to call _handle_args on the treemodel:\n%s' % e	
				
		else:
			treemodel = gtk.ListStore(*self.types)
		
		return treemodel
			

