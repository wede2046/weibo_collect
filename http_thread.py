#encoding:utf8
import urllib2
import cookielib
import lxml.html
import re
import sys
import time
import mysql.connector
import threading
import redis
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")
#获取cookie,并将保存在变量中的cookie打印出来
def Cookie():
    #声明一个CookieJar对象来保存cookie
    cookie = cookielib.CookieJar()
    #创建cookie处理器
    handler = urllib2.HTTPCookieProcessor(cookie)
    #构建opener
    opener = urllib2.build_opener(handler)
    #创建请求
    res = opener.open('http://weibo.com/p/1005055173399462/info?mod=pedit_more&reason=&retcode=')
    for item in cookie:
        print 'name:' + item.name + '-value:' + item.value

#将cookie保存在文件中
def saveCookie():
    #设置保存cookie的文件
    filename = 'C:\\2.txt'
    #声明一个MozillaCookieJar对象来保存cookie，之后写入文件
    cookie = cookielib.MozillaCookieJar(filename)
    #创建cookie处理器
    handler = urllib2.HTTPCookieProcessor(cookie)
    #构建opener
    opener = urllib2.build_opener(handler)
    #创建请求
    res = opener.open('http://weibo.com/p/1005055173399462/info?mod=pedit_more&reason=&retcode=')
    #保存cookie到文件
    #ignore_discard的意思是即使cookies将被丢弃也将它保存下来
    #ignore_expires的意思是如果在该文件中cookies已经存在，则覆盖原文件写入
    cookie.save(ignore_discard=True,ignore_expires=True)

#从文件中获取cookie并且访问(我们通过这个方法就可以打开保存在本地的cookie来模拟登录)

def getCookie(cnx,proxy_ip,proxy_no,seq,th,reds):
    #创建一个MozillaCookieJar对象
    cookie = cookielib.MozillaCookieJar()
    #从文件中的读取cookie内容到变量
    cookie.load('C:\\2.txt',ignore_discard=True,ignore_expires=True)
    #打印cookie内容,证明获取cookie成功
    #for item in cookie:
       # print 'name:' + item.name + '-value:' + item.value
    #利用获取到的cookie创建一个opener
    #handler = set()
    handler=urllib2.HTTPCookieProcessor(cookie)
    handler1=urllib2.ProxyHandler({"http" : proxy_ip+":"+proxy_no})
    opener = urllib2.build_opener(handler,handler1)

    urllib2.install_opener(opener)


    add_weib = ("INSERT INTO `test`.`weibo3` ( `weibo_id`, `name`, `addr`, `sex`, `sexs`, `love`, `bri`, `xuexin`, `blogadd`,"
                "    `domain`, `info`, `reg`, `conn`, `work`, `tab`, `vip`, `level`, `foce`, `fan`, `wcount`, `touaddr`,`school`,`from`,`img`) "
                "VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s ,%s,%s,%s);")
    #接受数据字典

        #1005055238215899
        #100605169254465
    seq_end = seq +10
    start_time = datetime.datetime.now()
    #print start_time
    for user_id in  range(seq,seq_end):
        #print user_id
        try:
            end_time = datetime.datetime.now()
            if (end_time - start_time).seconds > 200:
                print "太慢了。。。。。。。。。。。。。。"+str(seq)
                break
            res = opener.open('http://weibo.com/p/'+str(user_id)+'/info')
            #res = opener.open('http://weibo.com/p/1005056224533255/info')
            html_s = res.read()
            doc = lxml.html.fromstring(html_s)
            #print html_s
            #break
            numList = doc.xpath('//script/text()')
            data_dic = {}
            tab_list = ''
            for i in  numList:
                doc = lxml.html.fromstring(i)
                numList1 = doc.xpath('//span/text()')
                numLisImg = doc.xpath("//img[@medalcard]/@title")
                numListCom = doc.xpath("//div/@title")
                conn = ""
                school = ""
                #认证标示
                if len(numListCom) > 0:
                    data_dic['comp'] =  numListCom[0].encode('utf-8').replace('\\"','') .replace(',',' ').replace('，',' ')
                #print numList_comp
                #h获取标示
                img = ''
                if len(numLisImg) > 0:
                    for u in numLisImg:
                        if len(u) > 0:
                            img += u.encode('utf-8').replace('\\"','') + "|"
                    data_dic['img']  = img
                #获取公司
                numListwork = doc.xpath("//a[@href]/text()")
                tmplistwork = ''
                for u in range(0,len(numListwork)):
                    if re.match(r"\S+\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t ", numListwork[u]) or re.match(r"\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t ", numListwork[u]):
                        tmplistwork += numListwork[u].encode('utf-8').replace('\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t','').replace('\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t \\t\\t\\t\\t\\t\\t\\t\\t\\t\\t','').replace('\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t \\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t ','').replace('\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t','').replace('\\t\\t\\t\\t\\t\\t\\t\\t\\t\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\r\\n        \\t\\t\\t\\t\\t\\t\\r\\n        \\t\\t\\t\\t\\t\\r\\n        \\t\\t\\t\\t\\t\\r\\n\\t\\t\\t\\t\\t\\t\\r\\n\\t\\t\\t\\t\\t\\r\\n\\t\\t\\t\\t\\r\\n\\t\\t\\t\\r\\n\\t\\t\\t','') + "|"
                    #print u.encode('utf-8')
                data_dic['work'] = tmplistwork
                #print data_dic.get('work','')
                numListconn = doc.xpath("//span/text()|//a/text()")

                for u in range(0, len(numListconn)):
                    #print "00"+numListconn[u]
                    if re.match(ur"\S+\s+\S+年\)\\t\\t\\t\\t\\t\\t\\t\\t\\t", numListconn[u]):
                        numListconn[u].encode('utf-8')
                    elif re.match(ur"\S+\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t$", numListconn[u]):
                        if re.match(ur"大学：*",numListconn[u]):
                            school += "大学："
                            stop1 = 2
                            while re.match(ur"\S+\s+\S+年\)\\t\\t\\t\\t\\t\\t\\t\\t\\t", numListconn[u+stop1]):
                                school += numListconn[u+stop1].encode('utf-8').replace('\\t\\t\\t\\t\\t\\t\\t\\t\\t',' ')
                                stop1 += 2
                            school += "|"
                        elif re.match(ur"小学：*",numListconn[u]):
                            stop1 = 2
                            school += "小学："
                            while re.match(ur"\S+\s+\S+年\)\\t\\t\\t\\t\\t\\t\\t\\t\\t", numListconn[u+stop1]):
                                school += numListconn[u+stop1].encode('utf-8').replace('\\t\\t\\t\\t\\t\\t\\t\\t\\t',' ')
                                stop1 += 2
                            school += "|"
                        elif re.match(ur"初中：*", numListconn[u]):
                            school += "初中："
                            stop1 = 2
                            while re.match(ur"\S+\s+\S+年\)\\t\\t\\t\\t\\t\\t\\t\\t\\t", numListconn[u+stop1]):
                                school += numListconn[u+stop1].encode('utf-8').replace('\\t\\t\\t\\t\\t\\t\\t\\t\\t',' ')
                                stop1 += 2
                            school += "|"
                        elif re.match(ur"海外：*", numListconn[u]):
                            school += "海外："
                            stop1 = 2
                            while re.match(ur"\S+\s+\S+年\)\\t\\t\\t\\t\\t\\t\\t\\t\\t", numListconn[u+stop1]):
                                school += numListconn[u+stop1].encode('utf-8').replace('\\t\\t\\t\\t\\t\\t\\t\\t\\t',' ')
                                stop1 += 2
                            school += "|"
                        elif re.match(ur"高中：*", numListconn[u]):
                            school += "高中："
                            stop1 = 2
                            while re.match(ur"\S+\s+\S+年\)\\t\\t\\t\\t\\t\\t\\t\\t\\t", numListconn[u+stop1]):
                                school += numListconn[u+stop1].encode('utf-8').replace('\\t\\t\\t\\t\\t\\t\\t\\t\\t',' ')
                                stop1 += 2
                            school += "|"
                        #print numListconn[u].encode('utf-8')
                        # print u.encode('utf-8')
                #联系信息

                for t in range(0,len(numList1)):
                    if numList1[t] == u"昵称：":
                        data_dic['nname'] =  numList1[t+1].replace('\\r','').replace('\\t','').replace('\\n','')
                    elif numList1[t] == u"所在地：":
                        data_dic['addr'] = numList1[t+1].replace('\\r','').replace('\\t','').replace('\\n','')
                    elif numList1[t] == u"性别：":
                        data_dic['sex'] = numList1[t+1].replace('\\r','').replace('\\t','').replace('\\n','')
                    elif re.match(ur"性取向*", numList1[t]):
                        data_dic['sexu'] =  numList1[t+1].replace('\\r','').replace('\\t','').replace('\\n','')
                    elif re.match(ur"感情状况*", numList1[t]):
                        data_dic['love'] = numList1[t+1].replace('\\r','').replace('\\t','').replace('\\n','')
                    elif re.match(ur"生日*", numList1[t]):
                        if re.match(ur"\d+年", numList1[t+1]):
                            data_dic['bri'] =  numList1[t+1].replace('\\r','').replace('\\t','').replace('\\n','')
                    elif re.match(ur"注册时间*", numList1[t]):
                        data_dic['reg_time'] =  numList1[t+1].replace('\\r','').replace('\\t','').replace('\\n','').replace(' ','')
                    elif re.match(ur"\s当前等级*", numList1[t]):
                        data_dic['lv'] =  numList1[t+1].replace(' ','')
                    elif re.match(ur"简介*", numList1[t]):
                        data_dic['info'] = numList1[t + 1].replace('\\r','').replace('\\t','').replace('\\n','').replace(' ','')
                    elif re.match(ur"血型*", numList1[t]):
                        data_dic['xuexin'] = numList1[t + 1].replace('\\r','').replace('\\t','').replace('\\n','').replace(' ','')
                    elif re.match(ur"QQ*", numList1[t]):
                        conn += "QQ:" + numList1[t + 1].replace('\\r','').replace('\\t','').replace('\\n','').replace(' ','') +"|"
                    elif re.match(ur"MSN*", numList1[t]):
                        conn += "MSN:" +numList1[t + 1].replace('\\r','').replace('\\t','').replace('\\n','').replace(' ','')+"|"
                    elif re.match(ur"邮箱*", numList1[t]):
                        conn += "邮箱:" + numList1[t + 1].replace('\\r','').replace('\\t','').replace('\\n','').replace(' ','')+"|"
                    elif re.match(ur"简介*", numList1[t]):
                        print numList1[t + 1].replace('\\r','').replace('\\t','').replace('\\n','').replace(' ','')
                numList_domain = doc.xpath('//span/a/text()')
                url1=''
                numList_img = doc.xpath("//img/@src")
               # print numList_img
                for it in numList_img:
                    #print it
                    if re.match(r"\S+tva\S+",it):
                        data_dic["touimg"] = it.replace('\\','').replace('\"','')
                        #print "22"+it
                for u in numList_domain:
                    if re.match(r"http*",u):
                        url1 = u.replace('\\r','').replace('\\t','').replace('\\n','').replace('\\','')
                        break
                numList_tab = doc.xpath('//em/text()')
                for ti in range(0,len(numList_tab)-1):
                    if re.match(r"\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t*",numList_tab[ti]):
                        tmp = numList_tab[ti].replace('\\r','').replace('\\t','').replace('\\n','').replace(' ','') + '|'
                        tab_list += tmp
                        #print numList_tab[ti]
                        #print ti.encode('utf-8')
                    #print u"\u6252\u76ae\u65b0\u664b\u7f51\u7ea2".encode('utf-8')
                numList_weibo = doc.xpath('//strong/text()')
                if len(numList_weibo) == 3:
                    data_dic['foce'] = numList_weibo[0]
                    data_dic['fan'] = numList_weibo[1]
                    data_dic['doc_count'] = numList_weibo[2]
            if len(data_dic) > 2:
                #add_weib = (
               # "INSERT INTO `test`.`weibo` ( `weibo_id`, `name`, `addr`, `sex`, `sexs`, `love`, `bri`, `xuexin`, `blogadd`,"
                #"    `domain`, `info`, `reg`, `conn`, `work`, `tab`, `vip`, `level`, `foce`, `fan`, `wcount`, `touaddr`) "
                weibo_data = ()
                print str(seq)+"-----------------"+str(user_id)
                weibo_data = str(user_id)+"!@!"+str(data_dic.get('nname','') )+"!@!"+str(data_dic.get('addr','') )+"!@!"+ str(data_dic.get('sex','') )+"!@!"+str(data_dic.get('sexu','') )+"!@!"+str(data_dic.get('love','') )+"!@!"+str(data_dic.get('bri','') )+"!@!"+str(data_dic.get('xuexin','') )+"!@!"+''+"!@!"+str(url1)+"!@!"+str(data_dic.get('info','') )+"!@!"+str(data_dic.get('reg_time', '') )+"!@!"+conn+"!@!"+str(data_dic.get('work','') )+"!@!"+str(tab_list)+"!@!"+str(data_dic.get('comp','') )+"!@!"+str(data_dic.get('lv','') )+"!@!"+str(data_dic.get('foce','') )+"!@!"+ str(data_dic.get('fan','') )+"!@!"+str(data_dic.get('doc_count','') )+"!@!"+str(data_dic.get('touimg',''))+"!@!"+str(school)+"!@!"+"36_01"+"!@!"+data_dic.get('img','')
                            #'+ ',' + str(data_dic.get('reg_time','')+ ',' + str(data_dic.get('lv','')+ ',' + str(data_dic.get('foce','')+ ',' + str(data_dic.get('fan','')+ ',' + str(data_dic.get('doc_count','') +  ','+str(tab_list)+','+ str(url1)+','+str(data_dic.get('img','')+','+str(data_dic.get('work','')+','+ str(data_dic.get('comp','')+','+conn+','+data_dic.get('xuexin','')+','+school +','++ "\n")
                #w_str =str(user_id) + ',' + data_dic.get('nname','') + ',' + data_dic.get('addr','') + ',' + data_dic.get('sex','')+ ',' + data_dic.get('sexu','')+ ',' + data_dic.get('love','')+ ',' + data_dic.get('bri','')+ ',' + data_dic.get('reg_time','')+ ',' + + ',' + data_dic.get('foce','')+ ',' + data_dic.get('fan','')+ ',' + data_dic.get('doc_count','') +  ','+str(tab_list)+','+ str(url1)+','+data_dic.get('img','')+','+data_dic.get('work','')+','+ data_dic.get('comp','')+','+conn+','+data_dic['xuexin']+','+school +','+data_dic.get('info','')+ "\n"
               # print weibo_data
                th.lpush("getdate", weibo_data)

                # cursor = cnx.cursor()
                # cursor.execute(add_weib, weibo_data)
                # cnx.commit()
                # cursor.close()
        except Exception, e:
            print str(seq)
            print e
            #cnx.rollback()
            reds.rpush("seq", seq)
            break
    th.lpush("tmp_ip_list", proxy_ip+":"+proxy_no)

# 为线程定义一个函数
def print_time( threadName, delay):
   count = 0
   time.sleep(delay)
   # print "%s: %s" % ( threadName, time.ctime(time.time()) )

def getredis_conn():
    r = redis.Redis(host="22.222.22.22",port=6379,db=0)
    return  r

def getseq_conn():
    r = redis.Redis(host="22.222.22.22",port=46379,db=0)
    return  r

def dbcon():
    cnx = mysql.connector.connect(user='root', database='test', host='22.222.22.22', port=33062, password='password')
    return cnx

#查询结束标志
def get_seq(cnx):
    date_sql = ("select seq from seq_red")
    update_sql = ("UPDATE seq_red set seq = seq+10")
    try:
        cnxu = cnx.cursor()
        cnxu.execute(date_sql)
        seq = cnxu.fetchone()[0]
        cnxu.execute(update_sql)
        cnx.commit()
        cnxu.close()
        return seq
    except Exception, e:
        print"获取序列出错"+e
        cnx.rollback()
        return 0
#获取redis队列
def getseq_red(reds):
    seq = reds.brpop(["seq"], timeout=100)
    return seq

#查询结束标志
def get_end(cnx):
    date_sql = ("select fl from end_flag")
    try:
        cnxu = cnx.cursor()
        cnxu.execute(date_sql)
        flag = cnxu.fetchone()[0]
        cnxu.close()
        return flag
    except Exception, e:
        print e
        return 0
# 创建两个线程
try:
    #数据库链接
    conn = dbcon()
    #redisl链接
    reds = getredis_conn()
    thread_list = []
    alive_count = 0
    seq_red = getseq_conn()
    while True:
        end_flag = get_end(conn)
        # 1--检查是否结束标志
        if end_flag == 0:
            print "开始"
            # 2--检查进程数
            alive_count = 0
            for th in thread_list:
                if th.is_alive():
                    alive_count=alive_count+1
            print "技术"
            print "活的线程数------------------------------------------------------"+str(alive_count)
            if alive_count > 500:
                print "线程超阀等"
                time.sleep(600)


            ex_in_flag = 0
            for i in range(10):

                # #3--获取代理信息
                #print "代理"
                proxy_h = reds.blpop(["oklist"], timeout=1)
                #print "代理"+str(proxy_h)
                #      #4--获取当前序列
                seq = getseq_red(seq_red)
                print seq
                if int(seq[1]) != 0 and  len(str(proxy_h)) != 4 :
                    #print seq
                    #print proxy_h
                    proxy_ip = proxy_h[1].split(":")[0]
                    proxy_no = proxy_h[1].split(":")[1]
                    iseq = int(seq[1])
                    ths =threading.Thread(target=getCookie,args=(conn,proxy_ip,proxy_no,iseq,reds,seq_red),name="t.%d" % i)
                    ths.start()
                    thread_list.append(ths)
                else:
                    ex_in_flag = 1
                    break
            #判断获取s是否成功
            if ex_in_flag == 0:
                print "线程创建完成，休息"
                time.sleep(10)
            else:
                print "取不到【seq】火拿不到代理有问题"
                break
        else:
            print "手工结束有问题"
            break
   # for i in range(0,100):
   #      #3--获取代理信息
   #      #4--获取当前序列
   #      thread.start_new_thread(getCookie,(conn, "117.187.42.34", "8888", 1005051656000001,"t1"))
   #  time.sleep(30)
except Exception, e:
   print e

 

