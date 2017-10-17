
from msl import *
import string
import re, threading;
import MySQLdb

class Table:
	def __init__(self, table_name):
		self.table_name = table_name;
		self.main_table = None;
		self.where_clause = [];
		self.variables = {};
		self.replacers = {};
		self.joined_tables = [];
		self.is_static = True;
		self.is_dirty = False;
		self.params = Object(select=None, limit=None, order_by=None, group_by=None, suffix="");
		self.primary_key = "id";

	def __str__(self):
		return self.get_query().__str__();

	def __call__(self):
		return self.query_row_limit(self.sql.get_query_result(*self.get_query().get()));

	def __getitem__(self, key):
		return  self.where({self.primary_key: key}).values(limit=1);


	#Private Methods:
	def constrains_to_query(self, constrains, glu = ' AND '):
		if(type(constrains) == Object):
			constrains = constrains.dict();
		if(type(constrains) == dict or type(constrains) == Ordered_Dict):
			(a,b) = left_fold(lambda xx, val, key: get_last(xx[0].append(key+" = {"+key+"}"), (xx[0], force_set(xx[1], key, val))) , constrains, ([],{}));
			return Query(safe_join(glu, a, "true"), b);
		else:
			return Query(constrains) if(type(constrains) == str) else constrains;

	def where_clause_to_query(self, clauses):
		constrains = map(lambda y: self.constrains_to_query(y), clauses);
		combined_query = safe_join(" AND ", map(lambda x: "("+x.query+")", constrains), "true");
		combined_variables = left_fold(lambda x,y: force_merge(x, y.variables), constrains, {});
		combined_replacers = left_fold(lambda x,y: force_merge(x, y.replacers), constrains, {});
		return Query(combined_query, combined_variables, combined_replacers);


	def query_ending_text(self, key, val):
		return '' if(val == None) else {'limit': 'limit ', 'order_by': 'order by ', 'group_by': 'group by '}[key]+str(val);

	def query_row_limit(self, rows):
		return ((rows[0] if len(rows)>0 else None) if(self.params.limit == 1) else rows);



	#Public Methods:


	def print_table(self):
		return "Table({0}, main_table={1}, where_clause={2}, variables={3}, replacers={4}, joined_tables={5}, is_static={6}, is_dirty={7}, params={8} )".format(self.table_name, self.main_table, self.where_clause, self.variables, self.replacers, self.joined_tables, self.is_static, self.is_dirty, self.params);

	def get_query(self, as_table=False):
		table = (Query(self.table_name) if self.main_table == None else (Query("(")+self.main_table.get_query()+")"+self.table_name));
		soft_merge(table.variables, self.variables);
		soft_merge(table.replacers, self.replacers);
		for i in self.joined_tables:
			table += Query(" left join ")+i[0].get_query(True)+" on ("+i[1]+") ";
		if(as_table):
			return table;
		else:
			return Query()+"select "+none_default(self.params.select, "*")+" from "+table+' where '+self.where_clause_to_query(self.where_clause) + safe_join(" ", list(self.query_ending_text(i, self.params[i]) for i in ['group_by', 'order_by', 'limit']), " ") + self.params.suffix;
			

	def copy(self):
		new_table = Table(self.table_name);
		new_table.main_table = self.main_table;
		new_table.where_clause = list(self.where_clause);
		new_table.variables = soft_merge({}, self.variables);
		new_table.replacers = soft_merge({}, self.replacers);
		new_table.joined_tables = list(self.joined_tables);
		new_table.is_static = False;
		new_table.params = Object(self.params.dict());
		return new_table;

	def wrap(self, new_name):
		table = Table(new_name);
		table.is_static = False;
		table.main_table = self;
		return table;

	def get_table(self):
		if(self.is_static):
			return self.copy();
		else:
			return self;

	def add_vars(self, variables={}, replacers={}):
		soft_merge(self.variables, variables);
		soft_merge(self.replacers, replacers);
		return self;

	def join(self, new_table, on, variables={}, replacers={}):
		if(self.is_dirty):
			raise Exception("Join can't be applied on dirty table");
		else:
			table = self.get_table();
			table.add_vars(variables, replacers);
			table.joined_tables.append((new_table, on));
			return table;

	def where(self, where_clause_obj=None, **where_clause):
		table = self.get_table();
		table.is_dirty = True;
		table.where_clause += Help.get_clean_list([where_clause_obj, where_clause], [None, {}]);
		return table;

	def values(self, variables={}, replacers={}, **params):
		table = self.get_table();
		table.is_dirty = True;
		table.add_vars(variables, replacers);
		force_merge(table.params.dict(), params);
		return table;

	def first(self):
		return self.values(limit=1)();

	def view_only_error(self):
		if(self.main_table != None):
			raise Exception("You can't edit a view");

	def set(self, **to_set):
		self.view_only_error();
		query = Query("update ")+self.table_name+" set "+self.constrains_to_query(to_set, ", ")+" where "+self.where_clause_to_query(self.where_clause)+" "+self.query_ending_text("limit", self.params.limit);
		query.add_vars(self.variables, self.replacers);
		return self.sql.run_query(*query.get());

	def insert(self, to_insert, table=None, info={}):#Assumption(all dict of list to_insert must have same keys... or none of row have more keys than first row);
		self.view_only_error();
		if(table != None):
			pass #To be implemented.
		else:
			if(type(to_insert) != list):
				to_insert = [to_insert];
			if(len(to_insert) > 0):
				keys = to_insert[0].keys();
				key_indexes = mapped(get_second, keys, None, get_second);
				changed_to_insert = mapped_list(lambda row,row_index: mapped(None, partial_dict(row, keys, True), None, lambda x: "insert_key_"+str(row_index)+"_"+str(key_indexes[x])), to_insert);

				insert_query_variables = soft_merge({}, *changed_to_insert);

				query = "insert into "+self.table_name+" ("+(",".join(keys))+") values "+(",".join('('+(",".join("{"+x+"}" for x in row))+')' for row in changed_to_insert));
				return self.sql.run_query(query, insert_query_variables);

	def delete(self):
		self.view_only_error();
		if(len(self.where_clause) > 0):
			query = Query("delete from ")+self.table_name+" where "+self.where_clause_to_query(self.where_clause)+" "+self.query_ending_text("limit", self.params.limit);
			query.add_vars(self.variables, self.replacers);
			return self.sql.run_query(*query.get());
		else:
			raise Exception("Danger: Delete Query without any constrains");





class Query:
	def __init__(self, query='', variables={}, replacers={}):
		if(type(query) == str):
			self.query = query;
			self.variables = dict(variables);
			self.replacers = dict(replacers);
		else:
			self.query = query.query;
			self.variables = dict(query.variables);
			self.replacers = dict(query.replacers);

	def __str__(self):
		return string.Formatter().vformat(self.query, [], Safe_Format(**soft_merge({}, self.variables, self.replacers)));

	def add(self, query2):
		self.query += query2.query;
		force_merge(self.variables, query2.variables);
		force_merge(self.replacers, query2.replacers);
		return self;

	def add_vars(self, variables={}, replacers={}):
		force_merge(self.variables, variables);
		force_merge(self.replacers, replacers);

	def get(self):
		return [string.Formatter().vformat(self.query, [], Safe_Format(**soft_merge({}, self.replacers))), self.variables];

	def __copy__(self):
		return Query(self);

	def __add__(self, query2):
		if(type(query2)==str):
			self.query += query2;
			return self;
		else:
			return self.add(query2);



class Sqlary:
	def __init__(self, db_data):
		self.db = None;
		self.cursor = None;
		self.lock = threading.Lock();
		self.lockedby = None;
		self.db_data = db_data;

		############ Sqlary Part 2 ################

		self.tables = {};
		self.table_configs = {};
		self.column = Object(
			int = lambda x='': ("int", x), 
			string = lambda x: ("string", x), 
			json = lambda x=2000: ("json",x), 
			time = lambda **params: ("time", params), 
			other = lambda x: ("other", x), 
		);

	def acquire_lock(self):
		self.lock.acquire();
		self.lockedby = threading.current_thread().name;

	def release_lock(self):
		self.lockedby = None;
		self.lock.release();

	def init_db(self):
		db_data = self.db_data;
		if(self.db == None and self.cursor == None):
			self.db = MySQLdb.connect(host=db_data["host"], user=db_data["username"], passwd=db_data["password"], db=db_data["database"]);
			self.cursor = self.db.cursor(MySQLdb.cursors.DictCursor);

	def commit_db(self):
		if(self.db != None):
			self.acquire_lock();
			self.db.commit();
			self.release_lock();

	def close_db(self):
		self.commit_db();
		map(lambda x:x.close() if x!=None else None, [self.cursor, self.db]);

	def rquery(self, query, dkeys={}):
		return query.format(**mapped(lambda x,y: "%("+y+")s", dkeys));

	def run_query(self, query, variables={}):
		self.acquire_lock();
		if(type(variables) == Object):
			variables = variables.dict();
		else:
			variables = dict(variables);
		self.init_db();
		self.cursor.execute(self.rquery(query, variables), variables);
		outp = (self.cursor.lastrowid);
		self.release_lock();
		return outp;

	def get_query_result(self, query, variables={}):
		self.acquire_lock();
		self.init_db();
		self.cursor.execute(self.rquery(query, variables), dict(variables));
		s_feilds = mapped_list(lambda x: x[0], list(self.cursor.description));
		outp = mapped_list(lambda x: partial_dict(x, s_feilds), list(self.cursor));
		self.release_lock();
		return outp;



	##########  Sqlary Part 2 ######


	def table(self, table_name):
		return self.tables[table_name];


	def add_table_configs(self, table_configs):
		def conv_column_config(column_config, column_name):
			soft_merge(column_config, dict(
				primary_key = False, 
				search_key = False, 
				validator = None, 
				insert_cast = None, 
				select_cast = None, 
				name = column_name, 
				disp_name = column_name.title(), 
			));
			if(type(column_config['type']) == str):
				column_config['type'] = self.column.other(column_config['type']);
			return column_config;

		def conv_table_config(table_config):
			table_config['columns'] = mapped(conv_column_config, table_config['columns']);
			keys = dict((x, get_item(mapped_list(get_second, table_config['columns'], lambda y: y[x]), 0)) for x in ['primary_key', 'search_key']);
			keys['search_key'] = none_default(keys['search_key'], keys['primary_key']);
			table_config['columns'] = partial_dict(table_config['columns'], Help.sort_by_preference(table_config['columns'].keys(), Help.get_clean_list(partial_list(keys, ['primary_key', 'search_key']))));
			force_merge(table_config, keys);
			return table_config;

		force_merge(self.table_configs, mapped(conv_table_config, table_configs));
		for i in table_configs:
			self.tables[i] = Table(i);



	def delete_tables(self, table_name=None, my_table_only=True, delete_all=False, ignored_tables=[]):
		to_delete = list(i for i in list(i.values()[0] for i in self.get_query_result("show tables")) if ((i not in ignored_tables) and (delete_all or table_name == i) and (not(my_table_only) or self.table_configs.has_key(i))));
		list(self.run_query("drop table if exists "+x) for x in to_delete);
		print "Deleted: ", to_delete;
		return to_delete;

		


	def create_tables(self, table_name=None, drop_old_columns=False):
		table_names = [table_name] if table_name != None else self.table_configs.keys();
		tables_in_db = mapped_list(lambda x: x.values()[0], self.get_query_result("show tables"));
		def column_query_str(column):
			column_type = column['type'][0];
			if(column_type == 'int'):
				return column['name']+" int "+column['type'][1];
			elif(column_type == 'string'):
				return column['name']+" varchar("+str(column['type'][1])+")";
			elif(column_type == 'json'):
				return column['name']+" varchar("+str(column['type'][1])+")";
			elif(column_type == 'time'):
				return column['name']+" int ";
			elif(column_type == 'other'):
				return column['name']+" "+column['type'][1];

		for table_name in table_names:
			table = self.table_configs[table_name];
			table_columns = table['columns'];
			if(table_name in tables_in_db):
				columns_in_db = mapped_list(lambda x: x['Field'], self.get_query_result("show columns from "+table_name));
				for (i, column) in table_columns.items():
					if(i not in columns_in_db):
						alter_query = "alter table "+table_name+" add column "+column_query_str(column);
						print alter_query;
						self.run_query(alter_query);
						print "Altered..Added";
				for i in columns_in_db:
					if(drop_old_columns and not(table_columns.has_key(i))):
						alter_query = "alter table "+table_name+" drop column "+i;
						print alter_query;
						self.run_query(alter_query);
						print "Altered.. Deleted";
			else:
				create_table_query = "create table if not exists "+table_name+" ("+", ".join(list(column_query_str(column) for (i,column) in table_columns.items())+([] if table['primary_key']==None else ["primary key ("+table['primary_key']+") "]))+")";
				print create_table_query;
				self.run_query(create_table_query);
				print "Created !";



	def pre_insert(self, table_name, row_obj):
		error_code = [None, ""];
		table_columns = self.table_configs[table_name]['columns'];
		for i in row_obj:
			if(not(table_columns.has_key(i))):
				error_code[0] = "invalid_column";
				error_code[1] = i+" : Invalid Column"
				break;
			if(table_columns[i]['validator'] != None):
				validator_response = table_columns[i]['validator'](row_obj[i]);
				if(not(validator_response[0])):
					error_code[0] = "validator_error";
					error_code[1] = table_columns[i]['disp_name']+": "+validator_response[1];
					break;
			column_type = table_columns[i].type[0];
			if(table_columns[i]['insert_cast'] != None):
				row_obj[i] = table_columns[i]['insert_cast'](row_obj[i]);
			if(column_type == "string"):
				row_obj[i] = str(row_obj[i]);
			if(column_type == "json"):
				row_obj[i] = json.dumps(row_obj[i]);
			if(column_type == "time"):
				row_obj[i] = Time.get_time_now();

			if(column_type in ["string", "json"]):
				if(len(row_obj[i]) > table_columns[i].type[0]):
					error_code[0] = "string_overflow";
					error_code[1] = i+" : String Size Overflow";
					break;
		return (row_obj, error_code[0], error_code[1]);



	def post_select(self, table_name, row_obj):
		table_columns = self.table_configs[table_name]['columns'];
		for i in row_obj:
			column_type = table_columns[i].type[0];
			if(column_type == "json"):
				row_obj[i] = run_if_can(json.loads(row_obj[i], object_pairs_hook=Ordered_Dict), {});
			if(table_columns[i]['select_cast'] != None):
				row_obj[i] = table_columns[i]['select_cast'](row_obj[i]);
		return row_obj;






