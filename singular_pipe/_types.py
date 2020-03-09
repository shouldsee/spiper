# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from path import Path
import glob
from collections import namedtuple
import os
from orderedattrdict import AttrDict
import json
import re
from singular_pipe._header import list_flatten,list_flatten_strict,rgetattr

import singular_pipe
import sys
singular_pipe._types = sys.modules[__name__]


def DirtyKey(s):
	return re.sub('[^0-9a-zA-Z_]','_',s)	


Code = type((lambda:None).__code__)

class TooManyArgumentsError(RuntimeError):
	pass
class TooFewArgumentsError(RuntimeError):
	pass
# class NotEnoughArgumentsError(RuntimeError):
# 	pass
class TooFewDefaultsError(RuntimeError):
	pass


class CantGuessCaller(Exception):
	pass
class UndefinedTypeRoutine(Exception):
	pass

class OverwriteError(Exception):
	pass

class UndefinedRoutine(Exception):
	pass


class IdentAttrDict(AttrDict):
	pass



class cached_property(object):
    """
    Descriptor (non-data) for building an attribute on-demand on first use.
    Source: https://stackoverflow.com/a/4037979
    """
    def __init__(self, factory):
        """
        <factory> is called such: factory(instance) to build the attribute.
        """
        self._attr_name = factory.__name__
        self._factory = factory

    def __get__(self, instance, owner):
        # Build the attribute.
        attr = self._factory(instance)
        # Cache the value; hide ourselves.
        setattr(instance, self._attr_name, attr)
        return attr

class PicklableNamedTuple(object):
	pass

# if 0:
	def __getstate__(self,):
		d = self.__dict__.copy()
		del d['cls']
		return d
	def __setstate__(self,d):
		self.__dict__ = d
		self.cls = namedtuple(d['name'], d['fields'])
	def __init__(self,name,fields):
		self.name = 'myData'
		self.cls = namedtuple(self.name,fields)
		self.fields = self.cls._fields
	def __call__(self,*a,**kw):
		v = self.cls(*a,**kw)
		# if len(v)>=3:
		# 	import pdb;pdb.set_trace()
		return AttrDict(v._asdict())

def Default(x):
	'''
	A dummy "class" mocked with a function
	'''
	return x

class _BaseFunction(object):
	pass



class NodeFunction(_BaseFunction):
	named = 1
	pass

# class SingleFileNodeFunction(NodeFunction):
# 	named = 0

# def SingleFileNode(func):
# 	func._type = SingleFileNodeFunction
# 	# UnnamedNodeFunction
# 	return func


def Node(func):
	func._type = NodeFunction
	return func

class FlowFunction(_BaseFunction):
	named = 1
	pass

def Flow(func):
	func._type = FlowFunction
	return func





_os_stat_result_null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
def os_stat_safe(fname):
	if os.path.isfile(fname):
		return os.stat(fname)
	else:
		return _os_stat_result_null

class Depend(Path):
	'''
	Abstract Dependency
	'''
	pass

class PrefixedNode(Depend):
	def get_prefix_pointer(self, dir_layout):
		idFile = IdentFile( dir_layout, self, [] , '_prefix_pointer')		
		suc = 0
		res = None
		if idFile.exists():
			with open(idFile,'r') as f:
				s = json.load(f)[0]
				# s = f.read()
				suc = 1
				res = Prefix(idFile.dirname()/s).expand()

		return suc,res

	def callback_output(self, caller, name):
		# pass
		fn = self
		idFile = IdentFile( caller.dir_layout, fn, [] , '_prefix_pointer')
		with open(idFile,'w') as f:
			json.dump( [ caller.prefix_named.relpath(idFile.dirname())], f)

	def fileglob(self, g, strict,filter=1):
		res = [File(x) for x in glob.glob("%s%s"%(self,g))]
		if filter:
			res = [x  for x  in res
			if not x.endswith('.outward_edges') and not x.endswith('.outward_edges_old') and not x.endswith('._prefix_pointer')
			and not x.endswith('.mock')
			]
		if strict:
			assert len(res),'(%r,%r) expanded into nothing!'% (self,g)
		# return [File(str(x)) for x in glob.glob("%s%s"%(self,g))]
		return res

			# f.write( self.relpath(idFile.dirname()) )
# tups =(prefix_job, self.DIR/'root','/tmp/pjob',)
# job = force_run(*tups)

class File(PrefixedNode):
	def __init__(self,*a,**kw):
		super(File,self).__init__(*a,**kw)
	def to_ident(self,):
		stat = os_stat_safe(self)
		res = (self, stat.st_mtime, stat.st_size)
		return res
	def expanded(self):
		return [self]



class TempFile(File):
	def __init__(self,*a,**kw):
		super(TempFile,self).__init__(*a,**kw)
	pass

class InputFile(File):
	def __init__(self,*a,**kw):
		super(InputFile,self).__init__(*a,**kw)
	pass

class OutputFile(File):
	def __init__(self,*a,**kw):
		super(OutputFile,self).__init__(*a,**kw)
	pass

# import pickle
class Prefix(PrefixedNode):
	def __init__(self,*a,**kw):
		super(Prefix, self).__init__(*a,**kw)
	def callback_output(self, caller, name):
		super().callback_output(caller, name)
		fs = self.fileglob('*',strict=1)
		for fn in fs:
			idFile = IdentFile( caller.dir_layout, fn, [] , '_prefix_pointer')
			with open(idFile,'w') as f:
				json.dump( [ self.relpath(idFile.dirname())], f)
				# f.write(self.relpath(idFile.dirname()))
		return 
	def expaneded(self):
		return self.fileglob('*',0)

class InputPrefix(Prefix):
	def __init__(self,*a,**kw):
		super( InputPrefix,self).__init__(*a,**kw)

class OutputPrefix(Prefix):
	def __init__(self,*a,**kw):
		super( OutputPrefix,self).__init__(*a,**kw)

job_result = namedtuple(
	'job_result',
	[
	'OUTDIR',
	'cmd_list',
	'output']
	)


def IdentFile(dir_layout, prefix, job_name, suffix):
	if isinstance(prefix, CacheFile):
		dir_layout = 'flat'
	prefix = Prefix(prefix)
	# if  callable(job_name):
	# 	import pdb;pdb.set_trace();
	if dir_layout == 'clean':
		pre_dir = prefix.dirname()
		pre_base = prefix.basename()
		lst = ['{pre_dir}/_singular_pipe/{pre_base}'.format(**locals()),
				job_name,suffix]
		# input_ident_file = '{pre_dir}/_singular_pipe/{pre_base}.{job_name}.{suffix}'.format(**locals())
	elif dir_layout == 'flat':
		lst = [prefix,job_name,suffix]
	else:
		assert 0,("dir_layout",dir_layout)
		# input_ident_file = '{prefix}.{job_name}.{suffix}'.format(**locals())
	input_ident_file = '.'.join(list_flatten_strict(lst))
	return File(input_ident_file)


class CacheFile(OutputFile):
	pass


from collections import OrderedDict as _dict
import requests
import json
# class HttpCheckLengthResult(object):
class HttpResponse(object):
	'''
	Github tarball/master often take minutes to update itself
	'''
	headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
	}
	def __init__(self, method,url,**kwargs):
		self.method = method
		self.url = url
		kwargs.setdefault('headers', self.headers)
		self.kwargs =kwargs
	def __repr__(self):
		return "%s(%s)"%(
			self.__class__.__name__,
			json.dumps(
				_dict([(k,getattr(self,k)) for k in ['method','url']]),
				default=repr,separators=',=')
			)

	##### Evaluate this response only once during the lifespan of this object
	@cached_property
	# @property
	def response(self):
		x = requests.request( self.method, self.url, **self.kwargs)
		return x

	@property
	def text(self):
		return self.response.text

	def to_ident(self,):
		x = self.response
		d0=  self.__dict__.copy()
		d0.pop('response', None)

		d = x.headers.copy()
		via =  d.get('via','')
		if 'varnish' in via:
			d['header_ident'] = d.get('etag', None)
		if d['header_ident'] is None:
			d['header_ident'] = d.get('content-length', None)
		if d['header_ident'] is None:
			d['header_ident'] = d.get('content-disposition', None)
		if d['header_ident'] is None:
			if not x.text:
				raise Exception('HTTP header is not informative!%s'%json.dumps(x.headers,indent=2))
		# hd = _dict()
		# hd['clen'] =  d.get('Content-Length', None)
		# hd['cdisp'] = d.get('Content-Disposition',None)
		# hd['ctype'] = d.get('Content-Type', None)
		# assert hd['clen'] or hd['cdisp'], hd

		# return [ sorted(d0.items()), ('_header_ident',list(hd.values())), ('_text',x.text)]
		return [ sorted(d0.items()), ('_header_ident',d['header_ident']), ('_text',x.text)]



class HttpResponseContentHeader(HttpResponse):
	def __init__(self,url,**kwargs):
		super().__init__('head', url,**kwargs)


def lstrip(x,s):
	if x.startswith(s):
		x = x[len(s):]
	return x
def PythonModule(package_path, version = None):
	'''
	Tries to parse package specificaion
	'''

	assert version is None
	err = UndefinedRoutine('PythonModule(%r)'%((package_path)))
	if '@' in package_path:
		package_name, url = package_path.split('@',1)
		if url.startswith('http'):
			extras = HttpResponseContentHeader(url)
		elif url.startswith('file://'):
			extras = File(lstrip(url, 'file://'))
		else:
			raise err
		mod = _PythonModule(package_name, url, extras)
	else:
		raise err
	return mod


from singular_pipe._pickler import get_version as get_package_version
from singular_pipe._shell import _shellcmd
import sys,importlib
import pkg_resources
import json
# PIP_BIN = 'pip3'
class _PythonModule(object):
	'''
	pip.main()? https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program
	'''
	def __init__(self, package_name, url, extras):
		self.package_name = package_name
		# self._resp = HttpResponseContentHeader(url)
		self.url = url
		# self.version = version
		self.extras = extras
	def __repr__(self):
		return ("{self.__class__.__name__}"
		"(package_name={self.package_name!r},"
		"url={self.url!r},"
		"extras={self.extras!r}"
		# "version={self.version!r}"
		")").format(**locals())


	def to_ident(self):
		res = sorted(self.__dict__.items())
		# res = _dict(self.__dict__)
		# res = list_flatten(res)
		return res

	@property
	def egg_info(self):
		verbose=0
		fn = ''
		try:
			dist = pkg_resources.get_distribution(self.package_name)
			fn = Path( dist.egg_info )
		except pkg_resources.DistributionNotFound as e:
			if verbose:
				print(e)
		return Path(fn)

	@property
	def ident_file(self):
		if self.egg_info: 
			return self.egg_info / 'URL_RESPONSE_HEADER'
		else:
			return ''


	def get_installed_ident(self, ):
		# ident = ''
		fn = self.ident_file
		# ident = []
		ident = ''
		if fn and fn.isfile(): 
			with open( fn,'r') as f:
				ident = f.read()
				# try:
				# 	ident = json.loads(f)
				# except:
				# 	pass
		return ident
	def dumps(self, x):
		x = get_identity( x,strict=1)
		return json.dumps( x,indent=2)

	def is_compatible(self):
		# return 0 

		#### Use content header to check whether is compatible
		installed_ident   =  self.get_installed_ident()
		self_ident        =  self.dumps([self])
		# from pprint import pprint
		# pprint(json.loads(self_ident))
		# pprint(json.loads(installed_ident))
		# print('[eq]', json.loads(self_ident) == json.loads(installed_ident))
		return self_ident == installed_ident

		# # return self.to_ident() == self.installed_ident()

		# # if installed_ident != self.get_
		# # get_package_ident(self.package_name, 0)
		# # installed_version = get_package_version(self.package_name, 0)
		# if self.version is None:
		# 	return bool( installed_version)
		# if self.version.startswith('>='):
		# 	val = installed_version[2:] >= self.version
		# elif self.version.startswith('<='):
		# 	val = installed_version[2:] <= self.version
		# elif self.version.startswith('=='):
		# 	val = installed_version[2:] == self.version
		# else:
		# 	assert 0,(self.versoin, installed_version)
		# return val

	def is_installed(self):
		'''
		If get_package_version did not return
		'''
		version = get_package_version(self.package_name, 0)
		return 0

	def is_loaded(self):
		return self.package_name in sys.modules

	# def __getattr__(self, key):
	# 	'''
	# 	Get module attribute if not 
	# 	'''


	def loaded(self):
		verbose = 0
		PIP_BIN = [sys.executable,'-m','pip',]
		if not self.is_loaded():
			# print(self.ident_file)
			# print(self.is_compatible())
			if not self.is_compatible():
				'''
				Overwrite the local installation by default
				'''
				print('[installing]',self.package_name,'@',self.url)
				self.egg_info.rmtree_p()

				CMD = [
				[PIP_BIN,'uninstall','-y',self.package_name,';'],
				# CMD = [ 
				PIP_BIN,'install','-vvv', '--user',
				self.package_name+'@'+self.url,
				]
				suc, stdout, stderr = _shellcmd(CMD, 1, 0, 'utf8', None, None, None, 1)
				assert self.egg_info.isdir(),'Installation of given url did not create a valid egg_info directory:\nurl={self.url}\negg_info={self.egg_info}'.format(**locals())
				
				print(stdout) if verbose>=2 else None
				with open(self.ident_file,'w') as f:
					f.write(self.dumps([self]))
			mod = importlib.import_module(self.package_name)
		else:
			mod = sys.modules[self.package_name]
		return mod

class PythonFunction(object):
	def __init__(self, *args):
		if len(args)==3:
			package_path, package_version, function_name = args
		if len(args)==2:
			package_path, function_name = args
			package_version = None
		self.module = PythonModule(package_path, package_version)
		self.function_name = function_name
	def __repr__(self):
		return ("{self.__class__.__name__}"
		"("
			"function_name={self.function_name!r},"
			"module={self.module!r}"
		")").format(**locals())
	def loaded(self):
		mod = self.module.loaded()
		return getattr( mod, self.function_name)

	def to_ident(self):
		return sorted(self.__dict__.items())

import json
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
			# assert 0,'call to_ident() yourself before passing into get_files()'
			#### Caller.to_ident()
			res = ele.to_ident()
			res = get_identity( res, None, verbose, strict)
			out.append( res)

		elif isinstance(ele,singular_pipe._types.Code):
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
				if any([isinstance(x,singular_pipe._types.Code) for x in ele.co_consts]):
					assert 0
		elif isinstance(ele, (str,type(None),int,)):
			out.append(ele)
		else:
			if strict:
				raise UndefinedTypeRoutine("get_identity(%s) undefined for %r"%(type(ele),ele))
			out.append(ele)
	return out


# class Static(object):
# 	def __init__(self,a):
# 		pass