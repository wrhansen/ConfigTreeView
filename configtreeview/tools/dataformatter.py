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
__date__ = "04/24/2012 02:13:18 PM"


from collections import Mapping

class DataFormatter():
	"""
	TreeView data coming from the server will come in list of dicts. Each dict represents
	a row in the treeview. Each key-path in the dict corresponds to an index as defined
	in the index_map of a ConfigTreeView.
	Example index_map( mapping a column hierachy to an index in the TreeView row):
	::

		{'address': {'markup': 6},
		 'cell-bg-index': 10,
		 'comments': {'markup': 7},
		 'contact': {'markup': 3},
		 'market': {'pixbuf': 5},
		 'name': {'markup': 11},
		 'payment': [{'markup': 8}, {'markup': 9}],
		 'placed': {'markup': 4},
		 'shipping': {'markup': 2},
		 'status': [{'markup': 0}, {'markup': 1}]
		}

	Sample data(Key-paths will have the same hierarchy as the index_map:
	::

		{
		  'market': {'pixbuf': 'images/pixbufs/my_image.png'},
		  'name': {'markup': 'Wesley Hansen'},
		  'cell-bg-index': 'blue',
		  'address':{'markup': '2336 112th Avenue'}
		}

	As you can see, the data coming from the server will share the same hierarchy, as this
	is important to determine which column/renderer and, ultimately, the index in a row to insert
	the data into.

	The DataFormatter will take care of this, creating a simple API to do it. It will be able
	to, taking in an index_map and a types list(these things are taken from a ConfigTreeView),
	take in data and generate formatted rows, which are ready for either appending to a liststore,
	or some other post-formatting function.
	"""
	def __init__(self, index_map, types ):
		'''
		Create a new data formatter with the given *index_map* and *types*
		
		:param index_map:
			A `dict` that maps a key location to an index in the types list	
		:param types:
			A `list` of types that describe what data types, and the order
			with which, a row of data for this `gtk.TreeView`'s TreeModel is
			expecting
		    
		'''
		self.index_map = index_map
		self.types = types

	def get_new_row(self):
		'''
		Returns an empty list with the correct length a *gtk.TreeModel* with the
		given *index_map* (from the constructor) expects.
		
		Example: if the index_map contained 4 different values of type str, then
		this function would return: [None, None, None, None]
		'''
		return [None]*len( self.types)
	
	def get_rows_deprecated(self, data):
		'''
		Yields formatted rows of data where `data` is a list of dicts, where each dict's
		key-path has a valid value in index_map...if it doesn't, a warning is printed out,
		and that value is skipped in that row
		NOTE: This function is deprecated, use get_rows() instead
		'''
		for row in data:#Each row
			#Create a new empty row
			new_row = self.get_new_row()
			key_map = [] #A list of all key-paths for a row
			
			#Generate key_map
			self._generate_key_paths(row, [],key_map )
			
			#Get index
			for item in key_map:
				index = self._get_index( item[0] )
				#Try to insert value into the row
				if index is not None:
					try:
						new_row[index] = item[1]
					except IndexError:
						print "IndexError!: '%s' is too large an index in new_row" %(index)

			yield new_row#Yield the newly formatted row

	def get_rows(self, data ):
		'''
		Yields formatted rows of data where `data` is a list of dicts, where each dict's
		key-path has a valid value in index_map...if it doesn't a warning is printed out,
		and that value is skipped in that row.
		
		:param data:
			The data, whose structure is a list of dicts, as described
			by the `index_map`.

		'''
		for row in data:
			new_row = self.get_new_row()
			
			for item in self.treeZip(row, self.index_map):
				try:
					new_row[item[1]] = item[0]
				except IndexError:
					print "Warning: IndexError: '%s' is too large an index for a row" %item[1] 
			yield new_row


	def treeZip(self, data, index_map):
		'''
		Iterates data and index_map to yield tuples of their values at 
		each key in data that is in index_map
		
		treeZip function courtesy of ninjagecko from StackOverflow
		'''
		if isinstance(data,Mapping) and isinstance(index_map,Mapping):
		    assert set(data) <= set(index_map)
		    for k,v1 in data.items():
		        v2 = index_map[k]
		        for tuple in self.treeZip(v1,v2):
		            yield tuple
		elif isinstance( data, list) and isinstance( index_map, list ):
			for idx,item in enumerate(data):
				v1 = item
				v2 = index_map[idx]
				for tuple in self.treeZip(v1, v2):
					yield tuple
		else:
		    yield (data,index_map)

	def _get_index( self, key_list ):
		'''
		Attempts to get the index at the given key-path defined in `key-list`.
		Raises an error if the path doesn't exist in the index_map
		'''
		index_map = self.index_map
		keys = ""
		for key in key_list:
			keys = keys + "[" + str(key) + "]"
		for idx,index in enumerate(key_list):
			try:
				index_map = index_map[index]
			except KeyError:
				print "KeyError!:  `%s` is not  defined in 'index_map' at %s" % (index, keys)
				index_map = None
				break
			except IndexError:
				print "IndexError!:  `%s` is too large an index in 'index_map' at %s" % (index, keys)
				index_map = None
				break
		return index_map		

	def _generate_key_paths(self, value, key_list,key_map ):
		'''
		Recursively iterate through a dictionary's values,
		and generate the key-path it creates to traverse down to the actual value.
		Append this (key-path,value) tuple to the key_map
		'''
		new_list = [item for item in key_list]
		if isinstance( value, dict):
			#Handle list
			for key, val in value.iteritems():
				new_list.append( key)
				self._generate_key_paths( val, new_list, key_map )
				new_list = [item for item in key_list]

		elif isinstance( value, list ):
			#Handle list
			for idx,item in enumerate(value):
				new_list.append( idx )	
				self._generate_key_paths( item, new_list, key_map )
				new_list = [item for item in key_list]
		else:
			#Handle data--reached farthest point you can go
			#So just append (key-path, value) to key_map
			key_map.append((new_list, value ) )
			

