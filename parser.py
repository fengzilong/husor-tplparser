#!/usr/bin/python
# -*- coding:gbk -*-
# author : feng_zilong@163.com
# filename : parser.py

import sys, os
import datetime
import string
import urllib, urllib2
import cPickle as p

def getMembers():
	memberUrl = 'https://gist.githubusercontent.com/fengzilong/316c010ecd46fa18252e/raw/b3ef3b75cee74f46af2d3e8b2d90473cf6e77d9f/member'
	html = urllib2.urlopen(memberUrl).read()
	html = html.decode('utf-8').encode('gbk')
	htmldict = eval(html)
	return htmldict

def getAuthor():
	author = ''
	needRemoteFetch = 0
	confpath = os.getcwd() + '\\conf'

	#如果存在配置文件
	if os.path.exists(confpath):
		filehandler = open(confpath, 'r')
		try:
			data = p.load(filehandler)
			#如果dict中存在键author
			if data.has_key('author'):
				author = data['author']
			#如果dict中不存在键author
			else:
				needRemoteFetch = 1
		except:
			pass
		finally:
			filehandler.close()
	#如果不存在配置文件
	else:
		needRemoteFetch = 1

	if needRemoteFetch:
		print '载入中，请稍等...\r',
		members = getMembers()
		print '请输入对应的序号:'
		memberOptions = ''
		for index, member in enumerate(members):
			memberOptions += str(index) + ' : ' + member['name'] + '\n'

		memberIdx = int(raw_input(memberOptions))

		try:
			author = members[memberIdx]['name'] + '<' + members[memberIdx]['email'] + '>'
		except:
			print '下标越界'
			author = ''

		if not author == '':
			print '已记录<下次将自动使用，如需修改，请删除同目录下的conf文件>\n'
			dumpdata = {'author' : author}
			#记录
			filehandler = open('conf', 'w')
			try:
				p.dump(dumpdata, filehandler)
			except:
				print '写入配置时出错'
	
	return author

def checkExist(path):
	needProcess = 0
	
	if os.path.exists(path):
		try:
			needProcess = {'y' : 1, 'n' : 0}[raw_input(os.path.split(path)[1] + '已存在，需要覆盖么(y/n)')]
		except Exception, e:
			raise
	else:
		needProcess = 1

	if not needProcess:
		sys.exit(0)

def getFormatDate(*args):
	if len(args) == 0:
		sep = ''
	else:
		sep = args[0]
	now = datetime.datetime.now()
	return now.strftime('%Y' + sep + '%m' + sep + '%d')

class Tpl(string.Template):
	"""模板"""
	delimiter = '@'
	idpattern = '[A-Z]+'
	html = '<!DOCTYPE html>\n<html>\n	<head>\n		<meta charset="utf-8">\n		<meta name="description" content="中国首家专业的母婴特卖网站,以1-7折超低折扣对上千家童装、童鞋、玩具、用品等品牌进行限时特卖,每天十点开抢,100%正品,全国包邮,7天无理由退货。" />\n		<meta name="keywords" content="母婴特卖,母婴商城,童装,童鞋,玩具,贝贝" />\n		<meta content="yes" name="apple-mobile-web-app-capable" />\n		<meta content="telephone=no" name="format-detection" />\n		<meta content="email=no" name="format-detection" />\n		<meta content="black" name="apple-mobile-web-app-status-bar-style">\n		<title>@TITLE</title>\n		<link rel="stylesheet" href="/build/css/@PATH@FILENAME.debug.css?t=@DATE" media="all" />\n		<script type="text/javascript" src="/assets/libs/zepto.min.js?t=@DATE"></script>\n	</head>\n	<body>\n        \n		<script type="text/javascript" src="/build/js/@PATH@FILENAME.debug.js?t=@DATE"></script>\n	</body>\n</html>\n'
	js = '/**\n * @desc    @TITLE\n * @author  @AUTHOR\n * @date    @DATE\n */\n\n;(function($){\n    var lib = window.lib;\n\n    \n	\n})(Zepto);\n'
	less = '// @desc    @TITLE\n// @author  @AUTHOR\n// @date    @DATE\n\n@charset "utf-8";\n\n@import "../../../../lib/veryless/very.less";\n@import "../../common/itemlistBox.less";\n@import "../../common/navbar.less";\n@import "../../common/footer.less";\n@import "../../common/downloadBar.less";\n\n.reset();\n.global();\n.navbar();\n.button();\n\nbody {\n	.user-select-none();\n}\n\n.loading {\n	color: #999;\n	line-height: 1.2rem;\n	font-size: .6rem;\n	text-align: center;\n}\n\n.footer();\n.downloadBar();\n'
	


class Parser():
	"""文件内容解析"""
	htmltpl = Tpl(Tpl.html)
	jstpl = Tpl(Tpl.js)
	lesstpl = Tpl(Tpl.less)
	
	def __init__(self, htmlpath, jspath, lesspath, filename, folder, author, title):
		self.htmlpath = htmlpath
		self.jspath = jspath
		self.lesspath = lesspath
		self.filename = filename
		self.folder = folder
		self.author = author
		self.title = title
		self.date = getFormatDate()
		self.datesep = getFormatDate('-')
	
	
	def process(self):
		#创建文件
		self.writeHtml()
		self.writeJs()
		self.writeLess()

		#打开文件
		self.openfiles()
		
		print '完成'

	#写入html模板
	def writeHtml(self):
		filehandler = open(self.htmlpath, 'w')
		htmlcontent = self.htmltpl.safe_substitute({'TITLE' : self.title, 'PATH' : self.folder, 'FILENAME' : self.filename, 'DATE' : self.date})
		htmlcontent = htmlcontent.decode('gbk').encode('utf8')
		try:
			filehandler.write(htmlcontent)
		finally:
			filehandler.close()

	#写入js模板
	def writeJs(self):
		path, filename = os.path.split(self.jspath)
		
		#目标文件夹不存在，则创建
		if not os.path.exists(path):
			os.makedirs(path)
		
		filehandler = open(self.jspath, 'w')
		jscontent = self.jstpl.safe_substitute({'TITLE' : self.title, 'AUTHOR' : self.author, 'DATE' : self.datesep})
		jscontent = jscontent.decode('gbk').encode('utf8')
		try:
			filehandler.write(jscontent)
		finally:
			filehandler.close()

	#写入less模板
	def writeLess(self):
		path, filename = os.path.split(self.lesspath)
		
		#目标文件夹不存在，则创建
		if not os.path.exists(path):
			os.makedirs(path)
		
		filehandler = open(self.lesspath, 'w')
		lesscontent = self.lesstpl.safe_substitute({'TITLE' : self.title, 'AUTHOR' : self.author, 'DATE' : self.datesep})
		lesscontent = lesscontent.decode('gbk').encode('utf8')
		try:
			filehandler.write(lesscontent)
		finally:
			filehandler.close()

	def openfiles(self):
		os.system('start ' + self.htmlpath)
		os.system('start ' + self.lesspath)
		os.system('start ' + self.jspath)

if __name__ == '__main__':
	print '-' * 29, '\nName  : FED generator\n', 'Author: feng_zilong@163.com\n', '-' * 29

	#作者名
	author = getAuthor()

	#文件名
	filename = raw_input('输入文件名: ')
	htmlpath = os.getcwd() + '\\demo\\' + filename + '.html'

	#在html中的位置
	folder = raw_input('在html中的路径: ')
	folder = folder.strip('\\/')
	if not folder == '':
		osfolder = folder + os.path.sep
		folder = folder + '/'
	else:
		osfolder = folder

	#js文件及less文件路径
	jspath = os.getcwd() + '\\src\\js\\pages\\' + osfolder + filename + '.js'
	lesspath = os.getcwd() + '\\src\\less\\pages\\' + osfolder + filename + '.less'

	#检查文件是否已存在
	checkExist(htmlpath)
	checkExist(jspath)
	checkExist(lesspath)

	#html文件标题及js&less描述
	title = raw_input('请输入html标题: ')

	#生成解析器实例并调用
	parser = Parser(htmlpath, jspath, lesspath, filename, folder, author, title)
	parser.process()
	
	raw_input()