#!/usr/bin/env python
# -*- coding: utf-8 -*- 



###################### core mslib #################################

import collections, inspect#, re, time, copy

Ordered_Dict = collections.OrderedDict;

get_method_arguments = lambda f: inspect.getargspec(f).args;

def get_keys(obj): #Assuming obj is list or have .keys method
	return list(range(len(obj))) if type(obj) == list else list(obj.keys());

def run_method(operator, arguments):
	required_args_len = len(get_method_arguments(operator));
	arguments = list(arguments);
	if(len(arguments) < required_args_len):
		arguments += [None]*(required_args_len-len(arguments));
	return operator(*tuple(arguments[:required_args_len]));

def left_fold(operator, array, identity_element):
	for i in get_keys(array):
		identity_element = run_method(operator, (identity_element, array[i], i));
	return identity_element;

identity_fun = lambda x: x;

def get_indexed_list(obj):
	return list((i, obj[i]) for i in range(len(obj))) if type(obj) == list else obj.items();

def mapped(operator, array, filter_operator=None, key_operator=None):
	filter_operator = none_default(filter_operator, value_function(True));
	key_operator = none_default(key_operator, identity_fun);
	operator = none_default(operator, identity_fun);
	return (dict if type(array)==dict else Ordered_Dict)((run_method(key_operator, (i, array[i])), run_method(operator, (array[i], i))) for i in get_keys(array) if(run_method(filter_operator, (array[i], i))));

def mapped_list(operator, array, filter_operator=None, key_operator=None):
	return list(mapped(operator, array, filter_operator, key_operator).values());

def run_if_can(operator, default_value=None, inp=()): #run fun on inp if possible.
	try:
		return operator(*inp) if type(inp) == tuple else operator(inp);
	except:
		return default_value;

def run_if_not_none(operator, default_value = None, inp=None): #run fun on inp if possible.
	return default_value if(inp == None  or operator == None) else run_method(operator, inp);

def get_item(array, keys, default_value = None): #arr can be list or dict | output = arr[key]
	if(type(keys) == list):
		return left_fold(lambda x,y: run_if_can(lambda: (x[0][y], True), (default_value, False)) if x[1] else x, keys, (array, True))[0];
	else:
		key = keys;
		if(type(array) == list):
			return (array[key] if(-len(array) <= key < len(array)) else default_value);
		else:
			return run_if_can(lambda: array[key], default_value);

def has_key(array, key):
	return run_if_can(lambda: get_last(array[key], True), False);

def get_second(x,y):
	return y;

def get_first(x,y):
	return x;

def get_last(*args):
	return args[-1];

def get_second_last(*args):
	return args[-2];

def has_all_keys(array, keys):
	return (sum(not(has_key(array, i)) for i in keys)==0);

def apply_if_true(inp, applier, checker):
	return applier(inp) if(checker(inp)) else inp;

def return_if_valid(inp, invalid_value, validator, if_none_operator=None):
	return (if_none_operator(inp) if if_none_operator != None else inp) if validator(inp) else invalid_value;

def none_default(inp, default_value, is_none=None, if_none_operator=None):
	return return_if_valid(inp, default_value, lambda inp: inp != is_none, if_none_operator);

def soft_set(array, key, value, is_force=False):
	if(type(array) == list):
		if(key > len(array)-1):
			is_force = True;
			array += [None]*(key-len(array)+1);
		if(is_force):
			array[key] = value;
	elif(not(array.has_key(key)) or is_force):
		array[key] = value;
	return array;

def force_set(array, key, value):
	return soft_set(array, key, value, True);

def soft_set_list(array, keys, value=None):
	left_fold(lambda x,y,i: ((soft_set(x, y, {})[y]) if (i<len(keys)-1) else force_set(x, y, value)), keys, array);
	return array;

def soft_merge_once(array, array2, is_force=False):
	return left_fold(lambda x1, yval, y1: soft_set(x1, y1, yval, is_force), array2, array);

def soft_merge(array, *arrays):
	return left_fold(lambda x,y: soft_merge_once(x,y), list(arrays), array);

def force_merge(array, *arrays): #general Extension of python's Dict.update method.
	return left_fold(lambda x,y: soft_merge_once(x,y, True), list(arrays), array);

def is_all_true(array):
	return sum(array) == len(list(array));

def is_any_true(array):
	return sum(array) >= 1;

def if_else(a, b=None, c=None):
	return (b if a else c);

def value_function(value):
	return lambda: value;

def if_else_methods(a, b=None, c=None):
	b = none_default(b, value_function(None));
	c = none_default(c, value_function(None));
	return (b() if a else c());

def if_else_list(bool_list, value_list):
	for i in range(len(bool_list)):
		if(bool_list[i]):
			return value_list[i];
	return value_list[-1];

def partial_dict(array, keys, fill_missing_key=False, missing_key_value=None): # partial keys: output is a Ordered_Dict, in same order as key is.
	if(fill_missing_key):
		return mapped(lambda x: run_if_can(lambda: array[x], missing_key_value), keys, None, lambda x: keys[x]);
	else:
		return mapped(lambda x: array[x], keys, lambda x: has_key(array, x), lambda x: keys[x]);
	

def partial_list(array, keys, fill_missing_key=False, missing_key_value=None):
	return partial_dict(array, keys, fill_missing_key, missing_key_value).values();

def get_element_index(array, element, inlist_checker=None, not_found_index=-1):
	if(inlist_checker==None):
		inlist_checker = lambda x,y: x==y;
	return left_fold(lambda y,x,i: (i if (y==not_found_index and inlist_checker(x,element)) else y), array, not_found_index);

def append(array, element):
	return get_last(array.append(element), array);

def append_unique(array, element, inlist_checker=None):
	element_index = get_element_index(array, element, inlist_checker);
	if(element_index == -1):
		array.append(element);
		return len(array)-1;
	else:
		return element_index;

def remove(array, element):
	return get_last(run_if_can(lambda: array.remove(element)), array);

def key_mapper(array, key_mapping):
	return mapped(identity_fun, array, None, lambda x: get_item(key_mapping, x, x));

def mixed_list(array):
	return left_fold(lambda x,y: x+y, array, []);




def indexify(data, key_list=[], is_unique = False, is_pop = True, depth=0):
	if(len(data) == 0):
		return Ordered_Dict();
	elif(type(data[0]) == list):
		indexify_list = lambda data, depth=0: (data if (depth <= 0) else mapped(lambda v: indexify_list(v, depth=depth-1), left_fold(lambda x,y: get_last(soft_set(x, y[0], []), x[y[0]].append(y[1:]), x) , data, {})));
		return indexify_list(data, depth);
	else:
		list_or_row = lambda x: x[0] if is_unique else x;
		indexify_dict = lambda data, key_list: (list_or_row(data) if (len(key_list) == 0) else mapped(lambda v: indexify_dict(v, key_list[1:]), left_fold(lambda x,y: get_last(soft_set(x, y[key_list[0]], []), x[y[key_list[0]]].append( get_last(y.pop(key_list[0]) if is_pop else None, y) ), x), data, Ordered_Dict())));
		return indexify_dict(data, key_list);


##########################  core helper Classes  ###############################

import string;


class Object:
	def __init__(self, initial_value=None, **kwargs):
		self.__dict__ = force_merge(none_default(initial_value, Ordered_Dict()), kwargs);

	def __call__(self, key):
		return self.__dict__[key];

	def __setitem__(self, key, val):
		self.__dict__[key] = val;
		return self.__dict__[key];

	def __getitem__(self, key):
		return self.__dict__[key];

	def __str__(self):
		return dict(self.__dict__).__str__();

	def dict(self):
		return self.__dict__;


class Safe_Format(object):
	def __init__(self, **kw):
		self.dict = kw

	def __getitem__(self, name):
		return self.dict.get(name, '{%s}' % name);

	def format(self, inp):
		return string.Formatter().vformat(inp, [], self);



#########################  os methods  #####################################################

import os

def read_file_pipe(file_pipe, reader=None):
	data=file_pipe.read() if reader == None else reader(file_pipe);
	file_pipe.close();
	return data;

def write_file_pipe(file_pipe, data):
	file_pipe.write(data);
	file_pipe.close();

def read_file(file_name, reader=None):
	return read_file_pipe(open(file_name), reader);

def write_file(fn, data, mode='w'):
	return write_file_pipe(open(fn, mode), data);

def run_linux_command(command):
	return read_file_pipe(os.popen(command));


##########  helper methods ##################################################


def safe_split(st, spliter = '-'):
	return return_if_valid(st.split(spliter), [], lambda x: x!=[""]);

def float_safe(x, default_value = 0):
	return run_if_can(lambda: float(x), default_value);

def int_safe(x, default_value = 0):
	return run_if_can(lambda: int(x), int(float_safe(x, default_value)));


def replace_all(inp, replacing_array):
	return left_fold(lambda s, ar, br: s.replace(br, ar), replacing_array, inp);


def clean_string(s):
	return unicode(s).encode('ascii', 'ignore')

def unicode_dict_to_str(inp):
	if(type(inp) == unicode):
		return clean_string(inp);
	elif(type(inp) == Ordered_Dict or type(inp) == dict):
		return mapped(lambda x: unicode_dict_to_str(x), inp, None, lambda x: clean_string(x));
	elif(type(inp) == list):
		return map(unicode_dict_to_str, inp);
	else:
		return inp;

def safe_join(glu, array, default_value=''):
	return glu.join(list(str(x) for x in array)) if len(array) > 0 else default_value;


def update_object(obj, updating_dict):
	for i in updating_dict:
		obj.__dict__[i] = updating_dict[i];
	return obj;



#################### json, csv methods ######################################

import json, csv

def json2str(inp):
	return json.dumps(inp, default=lambda x: x.dict());

def str2json(inp, error_value = None): #dl = []
	return run_if_can(lambda: unicode_dict_to_str(json.loads(inp, object_pairs_hook=Ordered_Dict)), error_value);


#################### Helping Class ######################################

import socket, re, itertools; #os, 

class Help:
	@staticmethod
	def __init__(xlrd):
		Help.xlrd = xlrd;

	@staticmethod
	def function(method):
		return method();
		

	@staticmethod
	def get_my_ip():
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("www.iitd.ac.in",80))
		myip=s.getsockname()[0];
		s.close()
		return myip;

	@staticmethod #untested Method yet
	def socket_send(s, msg):
		return s.send(("%010d" % (len(msg),))+msg);

	@staticmethod
	def get_clean_list(array, invalid_values=None):
		invalid_values = none_default(invalid_values, [None]*len(array));
		return mapped_list(None, array, lambda x, xx: x != invalid_values[xx]);


	@staticmethod #untested Method yet
	def socket_recv(s):
		num_to_recv = run_if_can(lambda: int(s.recv(10)), 0);
		need_to_recv = num_to_recv;
		datasofar = "";
		while(need_to_recv > 0):
			recved = s.recv(need_to_recv);
			need_to_recv-=len(recved);
			datasofar+=recved;
		return datasofar;


	@staticmethod #untested Method yet
	def print_tree(xl, tabseprate='\t', depth = -1):
		if type(xl) == list :
			return mixl(map(lambda x: print_tree(x, tabseprate, depth+1), xl));
		elif(xl != '') :
			return [tabseprate*depth+str(xl)];
		else:
			return [];

	@staticmethod
	def cleanpath(path, clean_start=True, clean_end=True):
		if(clean_start and len(path)>0 and path[0]=='/'):
			path=path[1:];
		if(clean_end and len(path)>0 and path[-1]=='/'):
			path=path[:-1];
		return path;

	@staticmethod
	def list_files(folder_path, include_hidden=False):
		return filter(lambda x: (include_hidden or get_item(x,0) != '.'), os.listdir(folder_path));

	@staticmethod
	def list_file_recursive(folder_path, include_hidden = False):
		folder_path = Help.cleanpath(folder_path, clean_start=False)+"/";
		all_files = Help.list_files(folder_path, include_hidden);
		return list(folder_path+i for i in all_files if os.path.isfile(folder_path+i))+left_fold(lambda x,y: x+y, list(Help.list_file_recursive(folder_path+i, include_hidden) for i in all_files if not(os.path.isfile(folder_path+i)) ), []);

	@staticmethod
	def list_dir(folder_path):
		folder_path = Help.cleanpath(folder_path, clean_start=False)+"/";
		return list(i for i in os.listdir(folder_path) if not(os.path.isfile(folder_path+i)));


	@staticmethod
	def read_xls(file_name): #Not tested Yet.
		if (type(file_name) == str or type(file_name) == unicode):
			wb = Help.xlrd.open_workbook(file_name);
		else:
			wb = Help.xlrd.open_workbook(file_contents=file_name.read());
		return list(list(list(s.cell(i,j) for j in xrange(s.ncols)) for i in xrange(s.nrows)) for s in wb.sheets());


	@staticmethod
	def read_csv(file_name):
		return read_file(file_name, lambda csv_file: list(list(row) for row in csv.reader(csv_file)));

	@staticmethod
	def write_log(file_name, log_label, data):
		fd = open(file_name, 'a');
		fd.write(log_label+": "+ Time.now()+ "\n"+str(data)+"\n-------------\n");
		fd.close();

	@staticmethod
	def write_csv(file_name, data_array): #For List of (Row List)
		fd = open(file_name, 'wb');
		csvw = csv.writer(fd);
		mapped_list(lambda i: csvw.writerow(i), data_array);
		fd.close();

	@staticmethod
	def write_csv_dict(file_name, data, key_mapping={}, preference_order=[]): #For list of (Row Dict)
		if(len(data) == 0):
			Help.write_csv(file_name, [['']]);
		else:
			keys = Help.sort_by_preference(data[0].keys(), preference_order);
			Help.write_csv(file_name, [mapped_list(lambda x: get_item(key_mapping, x, x), keys)]+mapped_list(lambda row: partial_dict(row, keys).values(), data));



	@staticmethod
	def sort_by_preference(array, preference_order=[]):
		preferences = mapped_list(lambda x: get_element_index(preference_order, x, not_found_index=len(array)+len(preference_order)), array);
		return partial_dict(array, sorted(get_keys(array), cmp=lambda x,y: return_if_valid(preferences[x].__cmp__(preferences[y]), x.__cmp__(y), lambda z: z!=0))).values();


	@staticmethod #not tested yet
	def group_list(array, gap=1):
		outp = [];
		for i in array:
			if (outp == [] or (outp[-1][0] + outp[-1][1]*gap != i)):
				outp.append([i, 1]);
			else:
				outp[-1][1]+=1;
		return outp;


	# tested till here.

	@staticmethod
	def clean_split(ss):
		return re.sub("[^a-zA-Z0-9]+", " ", ss.lower()).strip().split();


	@staticmethod
	def clean_file_name(name):
		return re.sub("[-.]", "_", re.sub("[^a-zA-Z0-9_-]", "", name));


	@staticmethod
	def fixed_str_len(st, fixed_length, padding_string = ' ', extend_if_short=True, truncate_if_long=True):
		if(len(st) == fixed_length):
			return st;
		if(len(st) > fixed_length and truncate_if_long):
			return st[:fixed_length-3]+" ..";
		if(len(st) < fixed_length and extend_if_short):
			diff = fixed_length-len(st);
			return padding_string*(diff - diff/2) + st + padding_string*(diff/2);
		return st;


#################### Time Class ######################################

from time import mktime
import datetime;


class Time:
	@staticmethod
	def __init__(pytz):
		Time.pytz = pytz;
		Time.formats = {
			"standard": "%d-%m-%Y %I:%M:%S %p", 
			"cool": "%d-%m-%Y %I:%M:%S %p", 
			"time": "%I:%M:%S %p", 
			"date-time": "%d-%m-%Y %I:%M:%S %p", 
			"date": "%d-%m-%Y", 
		};
		if(pytz != None):
			Time.local_time_zone = run_if_can(lambda: pytz.timezone("Asia/Calcutta"));
		else:
			Time.local_time_zone = None;

	@staticmethod
	def now(format=None, format_type="date-time"):
		if(format_type == None and format == None):
			return Time.get_time_now();
		else:
			return Time.string(None, format, format_type);

	@staticmethod
	def string(time_at=None, format=None, format_type="date-time"):
		format = none_default(format, Time.formats[format_type]);
		return Time.int_to_str(time_at, format);


	@staticmethod
	def get_time_now():
		return int(mktime(datetime.datetime.now(Time.local_time_zone).timetuple()));

	@staticmethod
	def int_to_object(x):
		return datetime.datetime.fromtimestamp(x);

	@staticmethod
	def int_to_str(time_at = None, time_format=None):
		return Time.int_to_object(none_default(time_at, Time.get_time_now())).strftime(none_default(time_format, Time.formats['standard']));

	# @staticmethod
	# def str_time(time_at = None):
	# 	return Time.int_to_str(time_at, Time.default_time);

	# @staticmethod
	# def str_date(time_at = None):
	# 	return Time.int_to_str(time_at, Time.default_date);

	# @staticmethod
	# def str_date_time(time_at = None):
	# 	return Time.int_to_str(time_at, Time.default_date_time);

	@staticmethod
	def parse_format(time_string, time_format, error_time = None): #times: time_string
		return run_if_can(lambda: int(mktime(datetime.datetime.strptime(time_string.strip(), time_format).timetuple())), error_time);

	@staticmethod
	def str_to_int(time_string, error_time = 0): #times: time_String
		time_string = re.sub('\s+', ' ', time_string).strip();
		# formates = (['']+['%d-%m-']*['%y', '%Y'])*[' ']*['', '%I:%M:%S %p', '%H:%M:%S', '%I:%M %p', '%H:%M']
		possible_formats = ['', ' %I:%M:%S %p', ' %H:%M:%S', ' %I:%M %p', ' %H:%M', '%d-%m-%y ', '%d-%b-%y', '%d-%b-%Y', '%d-%m-%y %I:%M:%S %p', '%d-%m-%y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d-%m-%y %I:%M %p', '%d-%m-%y %H:%M', '%d-%m-%Y ', '%d-%m-%Y %I:%M:%S %p', '%d-%m-%Y %H:%M:%S', '%d-%m-%Y %I:%M %p', '%d-%m-%Y %H:%M', '%d/%m/%y ', '%d/%m/%y %I:%M:%S %p', '%d/%m/%y %H:%M:%S', '%d/%m/%y %I:%M %p', '%d/%m/%y %H:%M', '%d/%m/%Y ', '%d/%m/%Y %I:%M:%S %p', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %I:%M %p', '%d/%m/%Y %H:%M'];
		return none_default(left_fold(lambda x,y: Time.parse_format(time_string, y.strip()) if x == None else x, possible_formats, None), error_time);

	@staticmethod
	def get_time_at_day_start(time_at=None):
		time_at = none_default(time_at, Time.get_time_now());
		return Time.str_to_int(Time.get_date_string(time_at));

	@staticmethod
	def get_date_string(time_at=None):
		return Time.int_to_str(time_at, "%d-%m-%Y");

	@staticmethod
	def date_to_int(d, m, y):
		return Time.str_to_int(str(d)+"-"+str(m)+"-"+str(y));





class Encoding:
	#to be done: Create proper structure for Encoding class, having multiple encoding schema, 2way encoding, 1way encoding, secrate keys, etc. Ability to extend it using decoraters, class extensions. create document for it.
	def msencode(inp):
		return "".join(i if i.isalnum() else ("#"+hex(ord(i))[2:].zfill(2)) for i in inp);

	def msdecode(inp):
		outp = "";
		i=0;
		while(i < len(inp)):
			if(inp[i] != "#"):
				outp += inp[i];
				i+=1;
			else:
				outp += chr(int(inp[i+1:i+3], 16));
				i+=3;
		return outp;

	def encode2(self, inp):
		return ''.join((chr(ord('a') + ord(i)/16)+chr(ord('a') + ord(i)%16)) for i in inp);

	def decode2(self, inp):
		outp="";
		st=0;
		for i in range(len(inp)):
			if( i%2==0 ):
				st=(ord(inp[i])-ord('a'))*16;
			else:
				st+=(ord(inp[i])-ord('a'));
				if(0<=st<=255):
					outp+=chr(st);
		return outp;