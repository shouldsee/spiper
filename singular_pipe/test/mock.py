import unittest2
from path import Path
import singular_pipe
from singular_pipe.test.graph import tarball_main
from singular_pipe.types import LoggedShellCommand,File
from singular_pipe.runner import mock_run,cache_run
from pprint import pprint
class Case(unittest2.TestCase):
	def test_mock_overwrite(self):
		# assert 0
		prefix = None
		if prefix is None:
			prefix = File('/tmp/singular_pipe.symbolic/root')
			
		prefix.dirname().rmtree_p()	
		_d = singular_pipe.rcParams.copy()
		singular_pipe.rcParams['dir_layout'] = 'clean'

		tarball_main( mock_run, prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
		 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
		 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt.old.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd.old.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz.old.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd.old.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz.old.mock')]


		# tarball_main( lambda *a:cache_run(*a,check_changed=2), prefix)
		tarball_main( cache_run, prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
	 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz')]

		tarball_main( mock_run , prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
	 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz')]



		with open((prefix + '.gen_files.out_txt'),'w') as f:
			f.write('100'*2000)
		tarball_main( mock_run , prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
	 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
	 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt.old.mock'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd.old.mock'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz.old.mock')]


		tarball_main( cache_run, prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
		 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz')]

		# res = LoggedShellCommand(['ls -lhtr',prefix+'*'])
		# .fileglob('*'),])
		# print(res)
		# prefix
		# tarball_main( mock_run , prefix)
		# assert 0
		# (prefix.dirname()/'root.tarball_dangerous_cache.tar_gz').touch()
		# self.assertRaises(singular_pipe._types.OverwriteError, tarball_main, mock_run, prefix)
		singular_pipe.rcParams.update(_d)



'''
Symbolic run construct .outward_edges, .input_json and .output_json as usual 
but skip the creation of actual output files.
A symbolic node is a node with all output_files being empty
'''
import singular_pipe
from singular_pipe.types  import Node,Flow
from singular_pipe.types  import Path, File, Prefix
from singular_pipe.types  import HttpResponse, HttpResponseContentHeader
from singular_pipe.types  import LoggedShellCommand
from singular_pipe.runner import mock_run
from singular_pipe.graph  import get_downstream_tree, plot_simple_graph
import random
def random_seq(self, prefix, seed = int, L = int, _output=['seq']):
	random.seed(seed)
	with open(self.output.seq,'w') as f:
		f.write('>random_sequence\n')
		buf = ''
		for i in range(L):
			buf += 'ATCG'[int(random.random()*4)]
		f.write(buf+'\n')
	return self


def transcribe(self, prefix, input = File, _output=['fasta']):
	with open(input,'r') as fi:
		with open(self.output.fasta,'w') as fo:
			fo.write(fi.read().replace('T','U'))
	return self

@Node
def mutate(self, prefix, input=File,   _seed = 0, _output=['fasta']):
	random.seed(_seed)
	with open(input,'r') as fi:
		with open(self.output.fasta,'w') as fo:
			buf = list(fi.read())
			random.shuffle(buf)
			fo.write(''.join(buf))
	return self

@Flow
def workflow(self, prefix, seed =int , L=int, 
	_output = [
	File('log'),
	]):
	_ = '''
	A workflow is not a Node()
	'''
	print('\n[Flow running] mock=%s'%getattr(self.runner.func,'__name__','None'))
	### [ToDo] (func, prefix) must be unique within each workflow
	# self.data = {}
	curr = self.runner(random_seq, prefix,  seed,  L)
	curr1 = self.config_runner(tag='temp')(random_seq, prefix, 0, 100)
	curr = self.runner(transcribe, prefix,  curr.output.seq,)
	curr = self.runner(mutate,     prefix,  curr.output.fasta)
	stdout = LoggedShellCommand(['ls -lhtr',prefix.dirname()],).rstrip()
	return self


from singular_pipe.types import Caller,DirtyKey,rgetattr
import shutil
def copy_file(self, prefix, input=File, _output=['backup'] ):
	shutil.copy2(input, self.output.backup+'.temp')
	shutil.move(self.output.backup+'.temp', self.output.backup)


@Flow
def backup(self, prefix, flow = Caller, _output=[]):
	key = 'subflow.random_seq.output.seq'
	self.config_runner(tag=DirtyKey(key))(copy_file, prefix, rgetattr(flow,key))
	key = 'subflow.random_seq_temp.output.seq'
	self.config_runner(tag=DirtyKey(key))(copy_file, prefix, rgetattr(flow,key))
	key = 'subflow.transcribe.output.fasta'
	self.config_runner(tag=DirtyKey(key))(copy_file, prefix, rgetattr(flow,key))
	key = 'subflow.mutate.output.fasta'
	self.config_runner(tag=DirtyKey(key))(copy_file, prefix, rgetattr(flow,key))
	return self

# def backup(self,prefix, input_prefix=Preifx, 
# 	random_seq ):

import json
from singular_pipe.runner import cache_run,force_run,is_mock_file,get_changed_files
from singular_pipe.shell import LoggedShellCommand
from singular_pipe.types import File,CacheFile

def main(self,
	prefix = None):
	if prefix is None:
		prefix = Path('/tmp/singular_pipe.symbolic/root')
		prefix.dirname().rmtree_p()
	print('\n...[start]%r'%prefix)
	from pprint import pprint
	fs = get_changed_files(workflow, prefix, 1, 100, verbose=0)
	exp = [
	  File('/tmp/singular_pipe.symbolic/root.workflow.log'),
	  File('/tmp/singular_pipe.symbolic/root.random_seq.seq'),
	  File('/tmp/singular_pipe.symbolic/root.random_seq_temp.seq'),
	  File('/tmp/singular_pipe.symbolic/root.transcribe.fasta'),
	  File('/tmp/singular_pipe.symbolic/root.mutate.fasta'),
	  ]
	assert sorted(fs) == sorted(exp),pprint(list(zip(sorted(fs),sorted(exp))))




	res  = cache_run( workflow, prefix, 1, 100,verbose=0)

	File('/tmp/singular_pipe.symbolic/root.workflow.log').touch()
	fs = get_changed_files(workflow,prefix, 1 ,100 ,verbose=1)
	assert fs == [
	  File('/tmp/singular_pipe.symbolic/root.workflow.log'),
 	],fs

	fs = get_changed_files(backup, prefix, res, verbose = 0, )
	assert fs == [File('/tmp/singular_pipe.symbolic/root.copy_file_subflow_random_seq_output_seq.backup'),
 File('/tmp/singular_pipe.symbolic/root.copy_file_subflow_random_seq_temp_output_seq.backup'),
 File('/tmp/singular_pipe.symbolic/root.copy_file_subflow_transcribe_output_fasta.backup'),
 File('/tmp/singular_pipe.symbolic/root.copy_file_subflow_mutate_output_fasta.backup')],pprint(fs)



	# print('[fs1]')
	# pprint(fs)

	res2 = cache_run(backup, prefix, res, verbose = 0)
	fs = get_changed_files(backup, prefix, res, verbose = 0)
	print('[fs2]')
	assert fs==[],pprint(fs)
	# res  = mock_run( workflow, prefix, 2, 100,verbose=1)
	# File('/tmp/singular_pipe.symbolic/root.transcribe.fasta').touch()

	res  = mock_run( workflow, prefix, 2, 100,verbose=0)
	fs = get_changed_files(backup, prefix, res, verbose = 0)
	print('[fs3]')
	assert fs==[File('/tmp/singular_pipe.symbolic/root.copy_file_subflow_random_seq_output_seq.backup'),
 File('/tmp/singular_pipe.symbolic/root.copy_file_subflow_transcribe_output_fasta.backup'),
 File('/tmp/singular_pipe.symbolic/root.copy_file_subflow_mutate_output_fasta.backup')],pprint(fs)
	# assert 0


	exp = [
	  File('/tmp/singular_pipe.symbolic/root.workflow.log'),
	  File('/tmp/singular_pipe.symbolic/root.random_seq.seq'),
	  # File('/tmp/singular_pipe.symbolic/root.random_seq_temp.seq'),
	  File('/tmp/singular_pipe.symbolic/root.transcribe.fasta'),
	  File('/tmp/singular_pipe.symbolic/root.mutate.fasta'),
	  ]
	fs = get_changed_files(workflow,prefix, 2 ,100 ,verbose=1)
	assert fs == exp,pprint((fs,exp))

	print('\n...[Done]')
	stdout = LoggedShellCommand(['ls -lhtr',prefix.dirname()],).rstrip()
	print(stdout)	
	of1 = res.subflow.mutate.output.fasta
	of2 = res['subflow']['mutate']['output']['fasta'] 
	of3 = res.get_subflow('mutate').get_output('fasta')
	assert of1 is of2 is of3	
	print(of3)

	#### this is more visually pleasant 
	tree = get_downstream_tree( [Prefix(prefix+'.random_seq.seq')], strict=0)	
	### render with graphviz
	fn = Path('assets/%s.mock.dot'%__file__).basename(); fn =fn.realpath()
	g = plot_simple_graph(tree,None,0)
	g.render( fn,format='svg'); print('[see output]%s'%fn)

	res = force_run( workflow, prefix, 1, 100 )
	tree = get_downstream_tree( [Prefix(prefix+'.random_seq.seq')], strict=0)	
	fn = Path('assets/%s.real.dot'%__file__).basename(); fn =fn.realpath()
	g = plot_simple_graph(tree,None,0)
	g.render( fn,format='svg'); print('[see output]%s'%fn)
Case.test_tag = main

if __name__ == '__main__':
	main()
