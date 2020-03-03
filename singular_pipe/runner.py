from singular_pipe.types import File,InputFile,OutputFile
from singular_pipe.types import IdentFile,CacheFile
# from singular_pipe.types import InputFile,OutputFile,File,TempFile,? ,Path,
from singular_pipe.types import Prefix,InputPrefix,OutputPrefix
from singular_pipe.types import HttpResponse
from singular_pipe.types import IdentAttrDict

from singular_pipe.types import TooManyArgumentsError
import singular_pipe.types

from singular_pipe.base import get_output_files,get_func_name, list_flatten
from singular_pipe.base import job_from_func
import pickle
import os,sys
import shutil
# ,shutil
import json
from itertools import zip_longest
from collections import namedtuple
import collections
_dict = collections.OrderedDict

import inspect


import io
from singular_pipe.hash import hash_nr
import base64
import singular_pipe
# import pkg_resources
from singular_pipe import VERSION,DEFAULT_DIR_LAYOUT
import singular_pipe
import collections
from singular_pipe.types import CantGuessCaller, UndefinedTypeRoutine


from jinja2 import Template, StrictUndefined
def jinja2_format(s,**context):
	return Template(s,undefined=StrictUndefined).render(**context)	
# def ident_changed(ident, ident_file):
# 	ident_dump     = pickle.dumps(ident)
# 	ident_dump_old = open(ident_file,'rb').read() if file_not_empty(ident_file) else b''
# 	return ident_dump != ident_dump_old

# def ident_dump(ident, ident_file, comment=''):
# 	with open(ident_file,'wb') as f:
# 		pickle.dump( ident,  f )


# def _dumps(obj):
def _dumps(obj):
	# f = lambda obj: base64.b64encode(pickle.dumps(obj)).decode('ascii')
	# s = f(obj)
	# x = f(_loads(s))
	# assert x == s,(x,s)
	s = base64.b64encode(pickle.dumps(obj)).decode('ascii')
	return s
def _loads(obj):
	x = base64.b64decode(obj.encode('ascii'))
	return pickle.loads(x)

def ident_load(ident_file,key):	
	ident_dump_old = ''
	try:
		if file_not_empty(ident_file):
			ident_dump_old = json.loads(open(ident_file,'r').read())[key]
			# ident_dump_old = str(json.loads(open(ident_file,'r').read())[key])
	except Exception as e:
		raise e
		print(e)
	return ident_dump_old
def ident_changed(ident, ident_file, key):
	ident_dump = _dumps(ident)
	ident_dump_old = ident_load( ident_file, key )
	return ident_dump != ident_dump_old


def ident_dump(d, ident_file, comment=[],version=VERSION):	
	if isinstance(ident_file, io.IOBase):
		f = ident_file
	else:
		f = open(ident_file,'w')
	with f:
	# with open(ident_file,'w') as f:
		# assert 0
		_d = _dict([
			('version',version),
			# ('comment',comment),
			# ('ident', _dumps(ident) ),
			] + list(_dict(d).items()))

		json.dump(_d,
			f,
			indent=2,
		)
		# collections.OrderedDict
		# pickle.dump( ident,  f )

def _raise(e):
	raise e


def func_orig(func):
	while True:
		if hasattr(func,'__wrapped__'):
			func = func.__wrapped__
		elif hasattr(func,'__func__'):
			func = func.__func__
		else:
			break
	return func


# class Caller( _Caller):

def FakeCode(code):
	# out = (code.co_code, [])
	consts = []
	for const in code.co_consts:
		if isinstance(const, singular_pipe.types.Code):
			consts.append( FakeCode(const) )
		else:
			consts.append( const )
	return FakeCode._codecls( code.co_code, consts)
FakeCode._codecls = _cls= namedtuple('_codecls','co_code co_consts')
_cls.__qualname__ = 'FakeCode._codecls'

class FakeJob(object):
	# code_tree = code_tree
	_codecls = FakeCode._codecls
	def __init__(self,job):
		self.__name__     = job.__name__
		self.__code__     = FakeCode( job.__code__) 
		# self.__code__     = self._codecls( job.__code__.co_code, job.__code__.co_consts)
		self.__qualname__ = job.__qualname__
		self.__module__   = str(job.__module__)
		self._output_type = job._output_type
	# def code_tree(self):


		# self.__code__  = 
		return 

CallerDump = namedtuple('CallerDump',['prefix','config',])
class Caller(object):
	# def 
	@property
	def output_cache_file(self):
		# return self._foo
		return IdentFile( self.config, self.prefix, self.job.__name__, 'cache_pk')
	@property
	def output(self):
		return get_output_files( self.job, self.prefix, self._output_type._typed_fields)
	def get_output_files( self ):		
		res = self.output
		res['_cache_file'] = CacheFile(self.output_cache_file)
		# res += (CacheFile(self.output_cache_file),)
		return list(res.values())

	@classmethod
	def from_input(Caller, job, _input, config):
		if not getattr(job,'_singular_pipe',False):
			job = job_from_func(job)
		_tmp  = []
		_null = namedtuple('_null',[])()
		_zip = lambda: zip_longest(job._input_names, job._input_types, _input,fillvalue=_null)
		_dump = lambda: json.dumps([repr(namedtuple('tuple','argname type input_value')(*x)) for x in _zip()],indent=0,default=repr)
		for n,t,v in _zip():
			if n[0]=='_':
				if v is not _null:
					raise TooManyArgumentsError('{dump}\nToo many arguments specified for {job._origin_code}\n argname started with _ should not have input_value \n'.format(
						dump=_dump(),**locals()))
				else:
					## v is _null, t is default value
					_tmp.append((n,t))
			elif v is _null:
				raise singular_pipe.types.TooFewArgumentsError(
					'{dump}\nToo few arguments specified for {job._origin_code}\n argname started with _ should not have input_value \n'.format(
				dump=_dump(),**locals()))
			else:
				_tmp.append( (n, t(v)) )
		# assert isinstance(_tmp[0]
		_caller = Caller( job, _tmp[:], config)
		return _caller

	def __getstate__(self):
		d = self.__dict__.copy()
		job = self.job
		d['job'] = FakeJob(job)
		# d['returned'] = ('LoadFrom',self.output_cache_file)
		return d

	def __setstate__(self,d):
		self.__dict__ = d

	def __init__(self, job, arg_tuples, config):
		# if not getattr(job,'_singular_pipe',False):
		# 	job = job_from_func(job)		
		self.job = job
		self.__name__ = job.__name__
		self._output_type = job._output_type
		self.arg_tuples = arg_tuples
		self.config = config
		# self.code = (self.f.__code__.co_code)

		# assert isinstance(arg_tuples[0][1], Prefix),(arg_tuples[0])
		# arg_tuples[0] = ('prefix',OutputPrefix(arg_tuples[0][1]))
		assert isinstance(arg_tuples[0][1], File),(arg_tuples[0])
		# arg_tuples[0] = ('prefix', File(arg_tuples[0][1]))

		# _output = job._output_type._typed_fields
		# _output = list(_output) + [CacheFile('_cache')]
		# cls = gunc._output_type = func._output_type = namedtuple('_output_type', list(_output)+['_cache'])
		# cls._typed_fields = _output
		# cls.__module__ = func.__module__
		# cls.__qualname__ = "%s._output_type"%func.__name__		
	@property
	def f(self):
		return func_orig(self.job)
	@property
	def prefix(self):
		return (self.arg_tuples[0][1])
	@property	
	def prefix_named(self):
		return self.prefix+'.%s'%self.__name__
		# '.'.join([self.prefix+]

	
	# def __getstate__
	@property
	def arg_values(self):
		self._arg_values = [v for k,v in self.arg_tuples[:] if not k.endswith('_')]
		return self._arg_values

	def to_ident(self):
		'''
		For pickle.dumps
		'''
		### argument to jobs without prefix
		### argument with name ending with '_' will be discarded in idenitty
		# _job_args = [v for k,v in self.arg_tuples[1:] if not k.endswith('_')]
		# _job_args = [v for k,v in self.arg_tuples[:] if not k.endswith('_')]
		# _job_args = list(zip(*self.arg_tuples[1:])) 
		_input = [
		# (	self.f.__code__.co_code, 
			# self.f.__code__.co_consts),
			self.f.__code__,
			self.arg_values,
		]		
		return _input
	@property
	def dotname(self):
		return "%s.%s"%(inspect.getmodule(self.f).__name__, self.f.__qualname__)
	def to_dict(self):
		'''
		For visualisation / json.dumps
		'''
		f = self.f
		res = collections.OrderedDict([
				('job', repr(f.__code__)),
				('dotname',self.dotname),
				# ('dotname',"%s.%s"%(inspect.getmodule(f).__name__, f.__qualname__)),
				('arg_tuples', collections.OrderedDict([
					(
						k,
						"%s.%s::%s"%(type(v).__module__,type(v).__qualname__, repr(v).strip('"'"'") ),
						# str(type(v))+':'+repr(v).strip('"'"'") ,
						# _raise(Exception())
					) for k,v in self.arg_tuples
					if not k.endswith('_')
					]) ),
				# ('co_code',f.__code__.co_code),
				# ('co_consts',f.__code__.co_consts),
				])
		return res		

	def __repr__(self):
		f = self.f
		return '%s.%s(%s)'%(
			self.__class__.__module__,
			self.__class__.__name__,
			','.join(['%s=%r'%(k,getattr(self,k)) for k in ['dotname','prefix_named']]),
			# self.dotname, self.prefix_named,
			# json.dumps( self.to_dict(),
			# indent=2,default=repr)
			)
	# @property
	# def returned(self):
	# 	return pickle.loads(self.output_cache_file)
	def __call__(self,):
		return self.job(self, *[x[1] for x in self.arg_tuples])
		# return self

	def to_table_node_label(self):
		# node = self
		s = '''
	<		
	<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
	  <TR>
	    <TD ALIGN="LEFT" BGCOLOR="lightblue">attr</TD>
	    <TD ALIGN="LEFT" BGCOLOR="lightblue">type</TD>
	    <TD ALIGN="LEFT" BGCOLOR="lightblue">value</TD>
	  </TR>

	  {# <TR>
	  	<TD ALIGN="LEFT">Prefix</TD>
	    <TD ALIGN="LEFT">{{node.prefix}}</TD>
	  </TR>
	  #}
	  	{% for k,v in [('dotname',node.dotname),('prefix_named', node.prefix_named)] +node.arg_tuples[:] %}
		  <TR>
		  	<TD ALIGN="LEFT">{{k}}</TD>
		  	<TD ALIGN="LEFT">{{v.__class__.__name__}}</TD>
		    <TD ALIGN="LEFT">{{v}}</TD>
		  </TR>
	    {% endfor %}
	</TABLE>
	>
	'''.strip()
		return jinja2_format(s, node=self)
		# return s.format(self=self)
# DEFAULT_DIR_LAYOUT = 'clean'
def force_run(job, *args,**kw):
	'''
	Run a jobs regardless of whether it has a valid cache
	'''
	return cache_run(job,*args,force=True,**kw)
	_input = args
	res = job(*_input)
	return res
def cache_check(job, *args,**kw):
	'''
	Check whether there is a valid cache for this job
	'''
	return cache_run(job,*args,check_only=True,**kw)
def cache_check_changed(job, *args,  check_changed=1,**kw):
	return cache_run(   job,  *args, check_changed=check_changed,**kw)

def cache_run_verbose(job,*args, verbose=1, **kw):
	return cache_run(job,*args,verbose=verbose,**kw)
def cache_run(job, *args,
	config = DEFAULT_DIR_LAYOUT,
	# config = 'flat',	
	check_only=False, check_changed=False, force=False,verbose=0
	):

	'''
	return: job_result
		Check whether a valid cache exists for a job receipe.
		Load cache as result if so, otherwise recalculate the job.

	##### we want to avoid re-calculating the output if they already exist and is intact
	##### this is done by storing an identity information on disk 
	##### this identity information is calculated from the outputted files
	##### which could be md5sum or timestamp		
	'''
	func_name = get_func_name()
	prefix = args[0]


	###### the _input is changed if one of the func.co_code/func.co_consts/input_args changed
	###### the prefix is ignored in to_ident() because it would point to a different ident_file
	#####  Caller.from_input() would also cast types for inputs
	_input = args
	_caller = Caller.from_input(job, _input, config)
	_input  = [_caller.to_ident()]	
	# print(_dump()) if verbose>=2 else None
	print(repr(_caller)) if verbose >= 3 else None

	input_ident_file =  IdentFile(config, prefix, job.__name__, 'input_json' )
	output_ident_file=  IdentFile(config, prefix, job.__name__, 'output_json' )
	# output_cache_file=  IdentFile(config, prefix, job, 'cache_pk')
	output_cache_file=  _caller.output_cache_file
	File(input_ident_file).dirname().makedirs_p()

	#### calculate output files
	### cast all files all as prefix
	### here we add cache_file as a constitutive output.
	_output = _caller.get_output_files()
	# _output = get_output_files( job, prefix, job._output_type._typed_fields) + (CacheFile(output_cache_file),)
	# print('[out1]',_output)

	input_ident_changed  = ident_changed( get_identity( _input, ), input_ident_file, 'ident')
	output_ident_changed = ident_changed( get_identity( _output, ), output_ident_file,'ident')		
	use_cache = not input_ident_changed and not output_ident_changed
	if check_only:
		return use_cache
	if check_changed:
		if check_changed >=2:
			input_ident = get_identity(_input)
			input_ident_old = _loads(json.load(open(input_ident_file,'r'))['ident'])
			output_ident = get_identity(_output)
			output_ident_old = _loads(json.load(open(output_ident_file,'r'))['ident'])
			import pdb; pdb.set_trace();
		return (input_ident_changed, output_ident_changed)

	if verbose:
		print('[{func_name}]'.format(**locals()),
			json.dumps([
			('job_name',job.__name__),
			('input_ident_changed', int(input_ident_changed)),
			('output_ident_chanegd',int(output_ident_changed))]
				,separators='_=').replace('"','')
			)
		if verbose >= 2:
			import pdb; pdb.set_trace()

	if check_only:
		return bool(use_cache)		

	if force:
		use_cache = False

	if use_cache:
		with open(output_cache_file,'rb') as f: result = pickle.load(f)

	else:
		result = _caller()
		for k,v in _caller.output.items():
			func = getattr( v,'callback_output',lambda *x:None)
			func(_caller,k)
			# method(_caller)
			# if hasattr(x,'callback_output'):
			# 	x.output_callback(_caller)				
		with open(output_cache_file,'wb') as f: pickle.dump(result, f)
		# ident_dump( result, output_cache_file, )
		_input_ident  = get_identity( _input)
		_output_ident = get_identity(_output)

		ident_dump( [
			('comment',[[repr(x) for x in _output],_output_ident]),
			('output_dump', _dumps(_output)),
			('ident', _dumps(_output_ident))
			], output_ident_file,
			)
			 # comment = [[repr(x) for x in _output],get_identity(_output)] ) ### outputs are all
		ident_dump(
			[
				('comment',  _caller.to_dict()),
				('caller_dump',  _dumps( _caller)),
				('ident',_dumps(_input_ident)),

			],
			input_ident_file)
		# ident_dump( _input_ident  , input_ident_file,  comment = (_caller.to_dict(),  _dumps( _caller)))

		#### add edge_file to inputs 
		### add input and output ident to outward_pk
		outward_dir_list = get_outward_json_list( _input, config)
		for outward_dir in outward_dir_list:
			outward_edge_file = outward_dir.makedirs_p() / str( hash_nr( _input_ident ) ) +'.%s.json'%job.__name__
			# ident_dump( _input_ident,  outward_edge_file, comment=_caller.to_dict() )			

			ident_dump(
				[
					('comment',  _caller.to_dict()),
					('caller_dump',  _dumps( _caller)),
					('ident',_dumps(_input_ident)),
				],
				outward_edge_file)			
			# ident_dump( _input_ident  , outward_edge_file,  comment = (_caller.to_dict(), _dumps(_caller) ) )

			# ident_dump( (_caller, get_identity(_caller.to_ident())), 
			# 	outward_edge_file, comment=_caller.to_dict() )			

		#### remove edge_file of outputs
		outward_dir_list = get_outward_json_list( _output, config)
		for outward_dir in outward_dir_list:
			shutil.move(outward_dir.makedirs_p() , (outward_dir+'_old').rmtree_p())
			outward_dir = outward_dir.makedirs_p() 


	return result


def file_not_empty(fpath):  
    '''
    Source: https://stackoverflow.com/a/15924160/8083313
    '''
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0



def _get_outward_json_file(ele, config=DEFAULT_DIR_LAYOUT):
	if isinstance(ele, Prefix):
		if config == 'clean':
			f = File( ele ).dirname()/'_singular_pipe'/ele.basename()+'.outward_edges'
		elif config == 'flat':
			f = File( ele + '.outward_edges')
	elif isinstance(ele, File):
		if isinstance(ele, CacheFile):
			config = 'flat' ### override config
		if config == 'clean':
			f = File(ele).dirname()/'_singular_pipe'/ele.basename()+'.outward_edges'
		elif config == 'flat':
			f = File( ele + '.outward_edges')	
	else:
		f = None
	return f


def get_outward_json_list(lst, config, out = None,verbose=0,):
	if out is None:
		out = []
	for ele in list_flatten(lst):
		f = _get_outward_json_file(ele, config)
		out.append(f) if f is not None else None
	return out 
	# return get_files(lst, *a, target = 'outward', **kw)
def get_identity(lst, out = None, verbose=0, strict=0):
	'''
	Append to file names with their mtime and st_size
	'''
	this = get_identity
	assert out is None
	out = []
	debug = 0
	verbose = 0
	# assert isinstance(lst, (tuple, list)),(type(lst), lst)
	flist = list_flatten(lst)
	# print('[lst]',lst,'\n[flist]',flist)
	for ele in flist:
		if  isinstance(ele, Prefix):
			res = ele.fileglob("*", ele is InputPrefix)
			###### exclude outward_edges for DIR_LAYOUT=flat
			res = [x for x in res if x not in [ ele+'.outward_edges', ele+'.outward_edges_old']]
			print('[expanding]\n  %r\n  %r'%(ele,res)) if verbose else None
			res = get_identity( res, None, verbose, strict)
			out.append( res)

		elif isinstance(ele, (File, HttpResponse, )):
			print('[identing]%r'%ele) if verbose else None
			res = ele.to_ident() #### see types.File, use (mtime and st_size) to identify
			# stat = os_stat_safe(ele)
			# res = (ele, stat.st_mtime, stat.st_size)
			out.append(res)	

		elif hasattr(ele, 'to_ident'):
			assert 0,'call to_ident() yourself before passing into get_files()'
			#### Caller.to_ident()
			ele = ele.to_ident()
			res = get_identity(ele, None, verbose, strict)
			out.append( res)
		elif isinstance(ele,singular_pipe.types.Code):
			res = (ele.co_code, get_identity(ele.co_consts, None, verbose, strict))
			out.append(res)
			print('[identing]%s,%s'%(ele.co_code,ele.co_consts)) if verbose else None

			if debug:
				# res = (ele.co_code, [get_identity([x], [], verbose, strict) for x in ele.co_consts])
				# print([ele.co_consts)
				print(json.dumps([(type(x),x) for x in ele.co_consts],default=repr,indent=2))
				# for x in ele.co_consts
				# print(res[1])
				print(len(res[1]),list(zip(ele.co_consts,res[1:])))
				if any([isinstance(x,singular_pipe.types.Code) for x in ele.co_consts]):
					assert 0
		else:
			if strict:
				raise UndefinedTypeRoutine("get_identity(%s) undefined for %r"%(type(ele),ele))
			out.append(ele)
	return out

##################################################
##################################################
##################################################
#### the following computes closures on the DAG ##
#### aka upstream/downstream


# from singular_pipe.graph import file_to_node
def file_to_node(obj, strict, config,):
	'''
	One can only guess the prefix by removing the suffix
	'''
	err = CantGuessCaller("Cannot guess the Caller() for %r"%obj) 

	# res = obj.rsplit('.',2)
	# if len(res)!=3:
	# 	return (_raise(err) if strict else None)
	# prefix, job_name, suffix = res 

	suc, prefix_named = obj.get_prefix_pointer(config)
	if suc:
		prefix, job_name = prefix_named.split('.',1)
		succ = 1
	else:
		return (_raise(err) if strict else None)

	input_ident_file =  IdentFile(config, prefix, job_name, 'input_json' )
	output_ident_file = IdentFile(config, prefix, job_name, 'output_json' )
	lst = _loads(json.load(open(output_ident_file,'r'))['ident'])  ##[FRAGILE]
	obj_ident = get_identity([obj])[0]
	'''
	[IMPLEMENT]
	strict=1 should detect a identity change
	contained in output_ident_file() -> Tracked
	not contained in output_ident_file() -> Dangling/Untracked
	'''
	if obj_ident in lst:
		x = _loads(json.load(open(input_ident_file,'r'))['caller_dump'])
	else:
		return (_raise(err) if strict else None)
	return x

if 0:
	def get_downstream_nodes(obj, level = -1, strict= 1, config=DEFAULT_DIR_LAYOUT, target='node', flat=1):
		return _get_downstream_targets( obj, level, strict, config, target, flat)

	def get_downstream_files(obj, level = -1, strict= 1, config=DEFAULT_DIR_LAYOUT, target='file', flat=1):
		return _get_downstream_targets( obj, level, strict, config, target, flat)

	def get_downstream_targets(obj, level = -1, strict= 1, config=DEFAULT_DIR_LAYOUT, target='all', flat=1):
		return  _get_downstream_targets( obj, level, strict, config, target, flat)


	def _get_downstream_targets(obj, level, strict, config, target, flat):
		'''
		List downstream files depending on this object
		'''
		this = _get_downstream_targets

		#### cast input_obj to a list of downstream nodes
		nodes = []

		# if isinstance(obj,File):
		# 	suc, res = obj.get_prefix_pointer(config)
		# 	obj = res if suc else obj
		# 	### if a File has _prefix_pointer, cast it back to Prefix

		if isinstance(obj, (File,Prefix)):
			for outward_file in _get_outward_json_file(obj, config).glob('*.json'):
				buf = json.load(open(outward_file,'r'))
				x_ident = _loads(buf['ident'])
				try:
					_ = '''[TBC] fragile '''
					x  =_loads(buf['caller_dump'])
					input_ident_file  = IdentFile(config, x.prefix, x.job.__name__, 'input_json')
					x2 = _loads(json.load(open(input_ident_file,'r'))['ident'])
				except:
					x2 = ''
				x1 = x_ident
				if x1 == x2:
					nodes += [x]
					pass
				else:
					if strict==1:
						buf = json.dumps([outward_file,obj,x.prefix,],indent=2,default=repr)
						raise Exception('Broken edge exists between nodes. set get_downstream_nodes(strict=0) to auto-remove outdated edge files %s'%buf)
					elif strict == -1:
						os.unlink(outward_file)
					else:
						buf = json.dumps([outward_file,obj,x.prefix,],indent=2,default=repr)
						if 0:
							print('[SKIPPING]Outdated %s'%buf)
						pass
		elif isinstance(obj, Caller):
			nodes += [obj]
		else:
			raise UndefinedTypeRoutine("%r not defined for type:%s %r"%(this.__code__, type(obj),obj))

		assert target in ['file','node','all'],(target,)
		output_list = []
		for x in nodes:
			if target in ['file','all']:
				out    = [x, []]
				if target == 'all':
					pass
				else:
					out[0] = []


				output_list += [out]
				# output_list += [(x.get_output_files(),out)]
				for of in x.get_output_files():
					down = [] 
					if level!=0:
						down[:] = _get_downstream_targets( of, min(-1,level-1), strict, config, target, flat)
					out[1].append((of,down))


			elif target =='node':
				out    = []
				output_list += [(x,out)]

				if level!=0:
					for of in x.get_output_files():
						out += [_get_downstream_targets( of, min(-1,level-1), strict, config, target, flat)]

		if flat:
			output_list = list_flatten(output_list)
		return output_list



	#### upstream
	def get_upstream_files(obj, level = -1, strict= 1, config=DEFAULT_DIR_LAYOUT, target='file', flat=1):
		return _get_upstream_targets( obj, level, strict, config, target, flat)

	def get_upstream_nodes(obj, level = -1, strict= 1, config=DEFAULT_DIR_LAYOUT, target='node', flat=1):
		return _get_upstream_targets( obj, level, strict, config, target, flat)



	def _get_upstream_targets(obj, level, strict, config, target, flat):

		####
		assert strict==0,'strict == 1 not implmented'
		assert target in ['node','file','all'],target
		this = _get_upstream_targets
		nodes = []
		output_list = []
		if isinstance(obj, (Prefix,File)):
			'''
			Try to get Caller of a dangling file
			'''
			x = file_to_node(obj, strict, config, )
			if x is not None:
				nodes += [x]
		elif isinstance(obj, HttpResponse):
			# nodes += [SourceNode('SOURCE')]
			output_list += [obj]
		elif isinstance(obj, Caller):
			nodes += [obj]
		else:
			raise UndefinedTypeRoutine("%r not defined for type:%s %r"%(this.__code__, type(obj),obj))

		for node in nodes:
			out = []
			files = [x for x in node.arg_values[1:] if isinstance(x,(File,Prefix))]
			if target == 'node':
				output_list += [[node, out]]
			elif target =='file':
				output_list += [[files, out]]
			if level == 0:
				pass
			else:
				out[:] = [ _get_upstream_targets( f, min(level-1,-1), strict, config, target,flat) for f in files]


		if flat:
			output_list = list_flatten(output_list)
		return output_list


