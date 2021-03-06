set -e
### install package first
python3 build-readme.py

NAME=spiper
VERSION=`python3 -c "import setup; print(setup.config['version'])"`
echo [docing]$VERSION
#mkdir _build_docs; cp -rft _build_docs
ODIR=`realpath $PWD`
DIR=../singular_pipe_docs
DIR=`realpath $DIR`
mkdir -p $DIR
cp -rfl $NAME examples scripts *.md -t $DIR
cp -rfl docs/* -t $DIR
sphinx-build -b html $DIR $DIR/_build

rm -rf $DIR/_push
git clone --branch gh-pages https://github.com/shouldsee/$NAME $DIR/_push
cp -rfT $DIR/_build $DIR/_push
cd $DIR/_push
git add .; git commit . -m docs-$VERSION; git push origin gh-pages

cd $ODIR
exit 0

# git checkout master
# git commit docs -mdocs || echo no_commit
# rm -rf ./_docs
# cp -rfT docs _docs
# git checkout gh-pages

# sphinx-build -b html _docs _html
# cp -lfr _html/* -t .
# cp -lfr _html/ -T ../singular_pipe_docs
# git add .; git commit . -m docs; git push origin gh-pages
# git checkout master -f
# #mv html/* .
# #git checkout 
