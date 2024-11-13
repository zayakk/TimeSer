from django.http.response import JsonResponse
from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from backend.settings import sendMail, sendResponse ,disconnectDB, connectDB, resultMessages,generateStr

# Odoogiin tsagiig duuddag service
def dt_gettime(request):
    jsons = json.loads(request.body) # request body-g dictionary bolgon avch baina
    action = jsons["action"] #jsons-s action-g salgaj avch baina
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {"action":"gettime"}
    
    # response:
    # {
    #     "resultCode": 200,
    #     "resultMessage": "Success",
    #     "data": [
    #         {
    #             "time": "2024/11/06, 07:53:58"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "gettime",
    #     "curdate": "2024/11/06 07:53:58"
    # }
    
    respdata = [{'time':datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}]  # response-n data-g beldej baina. list turultei baih
    resp = sendResponse(request, 200, respdata, action)
    # response beldej baina. 6 keytei.
    return resp
# dt_gettime

#login service
def dt_login(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    # print(action)
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {
    #     "action": "login",
    #     "uname": "ganzoo@mandakh.edu.mn",
    #     "upassword":"73y483h4bhu34buhrbq3uhbi3aefgiu"
    # }
    
    # response:
    # {
    #     "resultCode": 1002,
    #     "resultMessage": "Login Successful",
    #     "data": [
    #         {
    #             "uname": "ganzoo@mandakh.edu.mn",
    #             "fname": "Ganzo",
    #             "lname": "U",
    #             "lastlogin": "2024-11-06T15:57:52.996+08:00"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "login",
    #     "curdate": "2024/11/06 07:58:10"
    # }
    try:
        uname = jsons['uname'].lower() # get uname key from jsons
        upassword = jsons['upassword'] # get upassword key from jsons
    except: # uname, upassword key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3006, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        
        # Hereglegchiin ner, password-r nevtreh erhtei (isverified=True) hereglegch login hiij baigaag toolj baina.
        query = F"""SELECT COUNT(*) AS usercount, MIN(fname) AS fname, MAX(lname) AS lname FROM t_user 
                WHERE uname = '{uname}' 
                AND isverified = True 
                AND upassword = '{upassword}' 
                AND isbanned = False """ 
        #print(query)
        cursor.execute(query) # executing query
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        print(respRow)
        cursor.close() # close the cursor. ALWAYS

        if respRow[0]['usercount'] == 1: # verified user oldson uyd login hiine
            cursor1 = myConn.cursor() # creating cursor1
            
            # get logged user information
            query = F"""SELECT uid, uname, fname, lname, lastlogin
                    FROM t_user 
                    WHERE uname = '{uname}' AND isverified = True AND upassword = '{upassword}'"""
            
            cursor1.execute(query) # executing cursor1
            columns = cursor1.description # 
            # print(columns, "tuples")
            respRow = [{columns[index][0]:column for index, 
                column in enumerate(value)} for value in cursor1.fetchall()] # respRow is list. elements are dictionary. dictionary structure is columnName : value
            # print(respRow)
            
            uid = respRow[0]['uid'] #
            uname = respRow[0]['uname'] # 
            fname = respRow[0]['fname'] #
            lname = respRow[0]['lname'] #
            lastlogin = respRow[0]['lastlogin'] #

            respdata = [{'uid': uid,'uname':uname, 'fname':fname, 'lname':lname, 'lastlogin':lastlogin}] # creating response logged user information
            resp = sendResponse(request, 1002, respdata, action) # response beldej baina. 6 keytei.

            query = F"""UPDATE t_user 
                    SET lastlogin = NOW()
                    WHERE uname = '{uname}' AND isverified = True AND upassword = '{upassword}'"""
            
            cursor1.execute(query) # executing query cursor1
            myConn.commit() # save update query database
            cursor1.close() # closing cursor1
            
        else: # if user name or password wrong 
            data = [{'uname':uname}] # he/she wrong username, password. just return username
            resp = sendResponse(request, 1004, data, action) # response beldej baina. 6 keytei.
    except:
        # login service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [] # hooson data bustaana.
        resp = sendResponse(request, 5001, respdata, action) # standartiin daguu 6 key-tei response butsaana
        
    finally:
        disconnectDB(myConn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
#dt_login

def dt_register(request):
    jsons = json.loads(request.body) # get request body
    action = jsons["action"] # get action key from jsons
    # print(action)
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {
    #     "action": "register",
    #     "uname": "ganzoo@mandakh.edu.mn",
    #     "upassword":"a9b7ba70783b617e9998dc4dd82eb3c5",
    #     "lname":"Ganzo",
    #     "fname":"U"
    # }
    
    # response:
    # {
    #     "resultCode": 200,
    #     "resultMessage": "Success",
    #     "data": [
    #         {
    #             "uname": "ganzoo@mandakh.edu.mn",
    #             "lname": "U",
    #             "fname": "Ganzo"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "register",
    #     "curdate": "2024/11/06 07:59:23"
    # }
    try :
        uname = jsons["uname"].lower() # get uname key from jsons and lower
        lname = jsons["lname"].capitalize() # get lname key from jsons and capitalize
        fname = jsons["fname"].capitalize() # get fname key from jsons and capitalize
        upassword = jsons["upassword"] # get upassword key from jsons
    except:
        # uname, upassword, fname, lname key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3007, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try:
        conn = connectDB() # database holbolt uusgej baina
        cursor = conn.cursor() # cursor uusgej baina
        # Shineer burtguulj baigaa hereglegch burtguuleh bolomjtoi esehiig shalgaj baina
        query = F"SELECT COUNT(*) AS usercount FROM t_user WHERE uname = '{uname}' AND isverified = True"
        # print (query)
        cursor.execute(query) # executing query
        # print(cursor.description)
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        print(respRow)
        cursor.close() # close the cursor. ALWAYS

        if respRow[0]["usercount"] == 0: # verified user oldoogui uyd ajillana
            cursor1 = conn.cursor() # creating cursor1
            # Insert user to t_user
            query = F"""INSERT INTO t_user(uname, lname, fname, upassword, isverified, isbanned, createddate, lastlogin) 
                        VALUES('{uname}','{lname}','{fname}', '{upassword}',
                        False, False, NOW(), '1970-01-01') 
            RETURNING uid"""
            print(query)
            
            cursor1.execute(query) # executing cursor1
            uid = cursor1.fetchone()[0] # Returning newly inserted (uid)
            print(uid, "uid")
            conn.commit() # updating database
            
            token = generateStr(20) # generating token 20 urttai
            query = F"""INSERT INTO t_token(uid, token, tokentype, tokenenddate, createddate) VALUES({uid}, '{token}', 'register', NOW() + interval \'1 day\', NOW() )""" # Inserting t_token
            print(query)
            cursor1.execute(query) # executing cursor1
            conn.commit() # updating database
            cursor1.close() # closing cursor1
            
            subject = "User burtgel batalgaajuulah mail"
            bodyHTML = F"""<a target='_blank' href=http://localhost:8000/user?token={token}>CLICK ME</a>
            
            """
            sendMail(uname,subject,bodyHTML)
            
            action = jsons['action']
            # register service success response with data
            respdata = [{"uname":uname,"lname":lname,"fname":fname}]
            resp = sendResponse(request, 200, respdata, action) # response beldej baina. 6 keytei.
        else:
            action = jsons['action']
            respdata = [{"uname":uname,"fname":fname}]
            resp = sendResponse(request, 3008, respdata, action) # response beldej baina. 6 keytei.
    except (Exception) as e:
        # register service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [{"aldaa":str(e)}] # hooson data bustaana.
        resp = sendResponse(request, 5002, respdata, action) # standartiin daguu 6 key-tei response butsaana
        
    finally:
        disconnectDB(conn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
# dt_register

# Nuuts ugee martsan bol duudah service
def dt_forgot(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    # print(action)
    resp = {}
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {
    #     "action": "forgot",
    #     "uname": "ganzoo@mandakh.edu.mn"
    # }
    
    # response: 
    # {
    #     "resultCode": 3012,
    #     "resultMessage": "Forgot password huselt ilgeelee",
    #     "data": [
    #         {
    #             "uname": "ganzoo@mandakh.edu.mn"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "forgot",
    #     "curdate": "2024/11/06 08:00:32"
    # }
    try:
        uname = jsons['uname'].lower() # get uname key from jsons
    except: # uname key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3016, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        # hereglegch burtgeltei esehiig shalgaj baina. Burtgelgui, verified hiigeegui hereglegch bol forgot password ajillahgui.
        query = f"""SELECT COUNT(*) AS usercount, MIN(uname) AS uname , MIN(uid) AS uid
                    FROM t_user
                    WHERE uname = '{uname}' AND isverified = True"""
        cursor.execute(query) # executing query
        cursor.description
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        # print(respRow)
        
        
        if respRow[0]['usercount'] == 1: # verified hereglegch oldson bol nuuts ugiig sergeehiig zuvshuurnu. 
            uid = respRow[0]['uid']
            uname = respRow[0]['uname']
            token = generateStr(25) # forgot password-iin token uusgej baina. 25 urttai
            query = F"""INSERT INTO t_token(uid, token, tokentype, tokenenddate, createddate) 
            VALUES({uid}, '{token}', 'forgot', NOW() + interval \'1 day\', NOW() )""" # Inserting forgot token in t_token
            cursor.execute(query) # executing query
            myConn.commit() # saving DB
            
            # forgot password verify hiih mail
            subject = "Nuuts ug shinechleh"
            body = f"<a href='http://localhost:8000/user?token={token}'>Martsan nuuts ugee shinechleh link</a>"
            sendMail(uname, subject, body)
            
            # sending Response
            action = jsons['action']
            respdata = [{"uname":uname}]
            resp = sendResponse(request,3012,respdata,action )
            
        else: # verified user not found 
            action = jsons['action']
            respdata = [{"uname":uname}]
            resp = sendResponse(request,3013,respdata,action )
            
    except Exception as e: # forgot service deer dotood aldaa garsan bol ajillana.
        # forgot service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [{"error":str(e)}] # hooson data bustaana.
        resp = sendResponse(request, 5003, respdata, action) # standartiin daguu 6 key-tei response butsaana
    finally:
        cursor.close() # close the cursor. ALWAYS
        disconnectDB(myConn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
# dt_forgot

# Nuuts ugee martsan uyd resetpassword service-r nuuts ugee shinechilne
def dt_resetpassword(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    # print(action)
    resp = {}
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    #  {
    #     "action": "resetpassword",
    #     "token":"145v2n080t0lqh3i1dvpt3tgkrmn3kygqf5sqwnw",
    #     "newpass":"MandakhSchool"
    # }
    
    # response:
    # {
    #     "resultCode": 3019,
    #     "resultMessage": "martsan nuuts ugiig shinchille",
    #     "data": [
    #         {
    #             "uname": "ganzoo@mandakh.edu.mn"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "resetpassword",
    #     "curdate": "2024/11/06 08:03:25"
    # }
    try:
        newpass = jsons['newpass'] # get newpass key from jsons
        token = jsons['token'] # get token key from jsons
    except: # newpass, token key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3018, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        
        # Tuhain token deer burtgeltei batalgaajsan hereglegch baigaa esehiig shalgana. Neg l hereglegch songogdono esvel songogdohgui. Token buruu, hugatsaa duussan bol resetpassword service ajillahgui.
        query = f"""SELECT COUNT (t_user.uid) AS usercount
                , MIN(uname) AS uname
                , MAX(t_user.uid) AS uid
                , MAX(t_token.tokenid) AS tokenid
                FROM t_user INNER JOIN t_token
                ON t_user.uid = t_token.uid
                WHERE t_token.token = '{token}'
                AND t_user.isverified = True
                AND t_token.tokenenddate > NOW()"""
        cursor.execute(query) # executing query
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        # print(respRow)
        if respRow[0]['usercount'] == 1: # token idevhtei, verified hereglegch oldson bol nuuts ugiig shinechlehiig zuvshuurnu.
            uid = respRow[0]['uid']
            uname = respRow[0]['uname']
            tokenid = respRow[0] ['tokenid'] 
            token = generateStr(40) # shine ajilladaggui token uusgej baina. 40 urttai. 
            query = F"""UPDATE t_user SET upassword = '{newpass}'
                        WHERE t_user.uid = {uid}""" # Updating user's new password in t_user
            cursor.execute(query) # executing query
            myConn.commit() # saving DB
            
            query = F"""UPDATE t_token 
                SET token = '{token}'
                , tokenenddate = '1970-01-01' 
                WHERE tokenid = {tokenid}""" # Updating token and tokenenddate in t_token. Token-iig idevhgui bolgoj baina
            cursor.execute(query) # executing query
            myConn.commit() # saving DB             
            
            # sending Response
            action = jsons['action']
            respdata = [{"uname":uname}]
            resp = sendResponse(request,3019,respdata,action )
            
        else: # token not found 
            action = jsons['action']
            respdata = []
            resp = sendResponse(request,3020,respdata,action )
            
    except Exception as e: # reset password service deer dotood aldaa garsan bol ajillana.
        # reset service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [{"error":str(e)}] # aldaanii medeelel bustaana.
        resp = sendResponse(request, 5005, respdata, action) # standartiin daguu 6 key-tei response butsaana
    finally:
        cursor.close() # close the cursor. ALWAYS
        disconnectDB(myConn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
#dt_resetpassword

# Huuchin nuuts ugee ashiglan Shine nuuts ugeer shinechleh service
def dt_changepassword(request):
    jsons = json.loads(request.body) # get request body
    action = jsons['action'] # get action key from jsons
    # print(action)
    resp = {}
    
    # url: http://localhost:8000/user/
    # Method: POST
    # Body: raw JSON
    
    # request body:
    # {
    #     "action": "changepassword",
    #     "uname": "ganzoo@mandakh.edu.mn",
    #     "oldpass":"a1b2c3d4",
    #     "newpass":"a1b2"
    # }
    
    # response: 
    # {
    #     "resultCode": 3022,
    #     "resultMessage": "nuuts ug amjilttai soligdloo ",
    #     "data": [
    #         {
    #             "uname": "ganzoo@mandakh.edu.mn",
    #             "lname": "U",
    #             "fname": "Ganzo"
    #         }
    #     ],
    #     "size": 1,
    #     "action": "changepassword",
    #     "curdate": "2024/11/06 08:04:18"
    # }
    try:
        uname = jsons['uname'].lower() # get uname key from jsons
        newpass = jsons['newpass'] # get newpass key from jsons
        oldpass = jsons['oldpass'] # get oldpass key from jsons
    except: # uname, newpass, oldpass key ali neg ni baihgui bol aldaanii medeelel butsaana
        action = jsons['action']
        respdata = []
        resp = sendResponse(request, 3021, respdata, action) # response beldej baina. 6 keytei.
        return resp
    
    try: 
        myConn = connectDB() # database holbolt uusgej baina
        cursor = myConn.cursor() # cursor uusgej baina
        # burtgeltei batalgaajsan hereglegchiin nuuts ug zuv esehiig shalgaj baina. Burtgelgui, verified hiigeegui, huuchin nuuts ug taarahgui hereglegch bol change password ajillahgui.
        query = f"""SELECT COUNT(uid) AS usercount ,MAX(uid) AS uid
                    ,MIN(uname) AS uname
                    ,MIN (lname) AS lname
                    ,MAX (fname) AS fname
                    FROM t_user
                    WHERE uname='{uname}'  
                    AND isverified=true
                    AND upassword='{oldpass}'"""
        cursor.execute(query) # executing query
        columns = cursor.description #
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
        # print(respRow)
        if respRow[0]['usercount'] == 1: # Burtgeltei, batalgaajsan, huuchin nuuts ug taarsan hereglegch oldson bol nuuts ugiig shineer solihiig zuvshuurnu.
            uid = respRow[0]['uid']
            uname = respRow[0]['uname']
            lname = respRow[0]['lname']
            fname = respRow[0]['fname']
            
            query = F"""UPDATE t_user SET upassword='{newpass}'
                        WHERE uid={uid}""" # Updating user's new password using uid in t_user
            cursor.execute(query) # executing query
            myConn.commit() # saving DB
            
            # sending Response
            action = jsons['action']
            respdata = [{"uname":uname, "lname": lname, "fname":fname}]
            resp = sendResponse(request, 3022, respdata, action )
            
        else: # old password not match
            action = jsons['action']
            respdata = [{"uname":uname}]
            resp = sendResponse(request, 3023, respdata, action )
            
    except Exception as e: # change password service deer dotood aldaa garsan bol ajillana.
        # change service deer aldaa garval ajillana. 
        action = jsons["action"]
        respdata = [{"error":str(e)}] # hooson data bustaana.
        resp = sendResponse(request, 5006, respdata, action) # standartiin daguu 6 key-tei response butsaana
    finally:
        cursor.close() # close the cursor. ALWAYS
        disconnectDB(myConn) # yamarch uyd database holbolt uussen bol holboltiig salgana. Uchir ni finally dotor baigaa
        return resp # response bustaaj baina
# dt_changepassword

@csrf_exempt # method POST uyd ajilluulah csrf
def checkService(request): # hamgiin ehend duudagdah request shalgah service
    if request.method == "POST": # Method ni POST esehiig shalgaj baina
        try:
            # request body-g dictionary bolgon avch baina
            jsons = json.loads(request.body)
        except:
            # request body json bish bol aldaanii medeelel butsaana. 
            action = "no action"
            respdata = [] # hooson data bustaana.
            resp = sendResponse(request, 3003, respdata) # standartiin daguu 6 key-tei response butsaana
            return JsonResponse(resp) # response bustaaj baina
            
        try: 
            #jsons-s action-g salgaj avch baina
            action = jsons["action"]
        except:
            # request body-d action key baihgui bol aldaanii medeelel butsaana. 
            action = "no action"
            respdata = [] # hooson data bustaana.
            resp = sendResponse(request, 3005, respdata,action) # standartiin daguu 6 key-tei response butsaana
            return JsonResponse(resp)# response bustaaj baina
        
        # request-n action ni gettime
        if action == "gettime":
            result = dt_gettime(request)
            return JsonResponse(result)
        # request-n action ni login bol ajillana
        elif action == "login":
            result = dt_login(request)
            return JsonResponse(result)
        # request-n action ni register bol ajillana
        elif action == "register":
            result = dt_register(request)
            return JsonResponse(result)
        # request-n action ni forgot bol ajillana
        elif action == "forgot":
            result = dt_forgot(request)
            return JsonResponse(result)
        #requestiin action resetpassword-r ajillna
        elif action == "resetpassword":
            result = dt_resetpassword(request)
            return JsonResponse(result)
        #requestiin action changepassword-r ajillna
        elif action == "changepassword":
            result = dt_changepassword(request)
            return JsonResponse(result)
        # request-n action ni burtgegdeegui action bol else ajillana.
        else:
            action = "no action"
            respdata = []
            resp = sendResponse(request, 3001, respdata, action)
            return JsonResponse(resp)
    
    # Method ni GET esehiig shalgaj baina. register service, forgot password service deer mail yavuulna. Ene uyd link deer darahad GET method-r url duudagdana.
    elif request.method == "GET":
        # url: http://localhost:8000/users?token=erjhfbuegrshjwiefnqier
        # Method: GET
        # Body: NONE
        
        # request body: NONE
        
        # response:
        # {
        #     "resultCode": 3011,
        #     "resultMessage": "Forgot password verified",
        #     "data": [
        #         {
        #             "uid": 33,
        #             "uname": "ganzoo@mandakh.edu.mn",
        #             "tokentype": "forgot",
        #             "createddate": "2024-10-16T11:21:57.455+08:00"
        #         }
        #     ],
        #     "size": 1,
        #     "action": "forgot user verify",
        #     "curdate": "2024/11/06 08:06:25"
        # }
        
        token = request.GET.get('token') # token parameteriin utgiig avch baina.
        
        if (token is None):
            action = "no action" 
            respdata = []  # response-n data-g beldej baina. list turultei baih
            resp = sendResponse(request, 3015, respdata, action)
            return JsonResponse(resp)
            # response beldej baina. 6 keytei.
            
            
        try: 
            conn = connectDB() # database holbolt uusgej baina
            cursor = conn.cursor() # cursor uusgej baina
            
            # gadnaas orj irsen token-r mur songoj toolj baina. Tuhain token ni idevhtei baigaag mun shalgaj baina.
            query = F"""
                    SELECT COUNT(*) AS tokencount
                        , MIN(tokenid) AS tokenid
                        , MAX(uid) AS uid
                        , MIN(token) token
                        , MAX(tokentype) tokentype
                    FROM t_token 
                    WHERE token = '{token}' 
                            AND tokenenddate > NOW()"""
            # print (query)
            cursor.execute(query) # executing query
            # print(cursor.description)
            columns = cursor.description #
            respRow = [{columns[index][0]:column for index, 
                column in enumerate(value)} for value in cursor.fetchall()] # respRow is list and elements are dictionary. dictionary structure is columnName : value
            # print(respRow)
            uid = respRow[0]["uid"]
            tokentype = respRow[0]["tokentype"]
            tokenid = respRow[0]["tokenid"]
            
            if respRow[0]["tokencount"] == 1: # Hervee hargalzah token oldson baival ajillana.
                #tokentype ni 3 turultei. (register, forgot, login) 
                # End register, forgot hoyriig shagaj uzehed hangalttai. Uchir ni login type ni GET method-r hezee ch orj irehgui.
                if tokentype == "register": # Hervee tokentype ni register bol ajillana.
                    query = f"""SELECT uname, lname, fname, createddate 
                            FROM t_user
                            WHERE uid = {uid}""" # Tuhain neg hunii medeelliig avch baina.
                    cursor.execute(query) # executing query
                    
                    columns = cursor.description #
                    respRow = [{columns[index][0]:column for index, 
                        column in enumerate(value)} for value in cursor.fetchall()]
                    uname = respRow[0]['uname']
                    lname = respRow[0]['lname']
                    fname = respRow[0]['fname']
                    createddate = respRow[0]['createddate']
                    
                    # Umnu uname-r verified bolson hereglegch baival tuhain uname-r dahin verified bolgoj bolohgui. Iimees umnu verified hereglegch oldoh yosgui. 
                    query  = f"""SELECT COUNT(*) AS verifiedusercount 
                                , MIN(uname) AS uname
                            FROM t_user 
                            WHERE uname = '{uname}' AND isverified = True"""
                    cursor.execute(query) # executing query
                    columns = cursor.description #
                    respRow = [{columns[index][0]:column for index, 
                        column in enumerate(value)} for value in cursor.fetchall()]
                    
                    if respRow[0]['verifiedusercount'] == 0:
                        
                        # verified user oldoogui tul hereglegchiin verified bolgono.
                        query = f"UPDATE t_user SET isverified = true WHERE uid = {uid}"
                        cursor.execute(query) # executing query
                        conn.commit() # saving database
                        
                        token = generateStr(30) # huuchin token-oo uurchluh token uusgej baina
                        # huuchin token-g idevhgui bolgoj baina.
                        query = f"""UPDATE t_token SET token = '{token}', 
                                    tokenenddate = '1970-01-01' WHERE tokenid = {tokenid}"""
                        cursor.execute(query) # executing query
                        conn.commit() # saving database
                        
                        # token verified service-n response
                        action = "userverified"
                        respdata = [{"uid":uid,"uname":uname, "lname":lname,
                                    "fname":fname,"tokentype":tokentype
                                    , "createddate":createddate}]
                        resp = sendResponse(request, 3010, respdata, action) # response beldej baina. 6 keytei.
                    else: # user verified already. User verify his or her mail verifying again. send Response. No change in Database.
                        action = "user verified already"
                        respdata = [{"uname":uname,"tokentype":tokentype}]
                        resp = sendResponse(request, 3014, respdata, action) # response beldej baina. 6 keytei.
                elif tokentype == "forgot": # Hervee tokentype ni forgot password bol ajillana.
                    
                    query = f"""SELECT uname, lname, fname, createddate FROM t_user
                            WHERE uid = {uid} AND isverified = True""" # Tuhain neg hunii medeelliig avch baina.
                    cursor.execute(query) # executing query
                    columns = cursor.description #
                    respRow = [{columns[index][0]:column for index, 
                        column in enumerate(value)} for value in cursor.fetchall()]
                    
                    uname = respRow[0]['uname']
                    lname = respRow[0]['lname']
                    fname = respRow[0]['fname']
                    createddate = respRow[0]['createddate']
                    
                    # forgot password check token response
                    action = "forgot user verify"
                    respdata = [{"uid":uid,"uname":uname,  "tokentype":tokentype
                                , "createddate":createddate}]
                    resp = sendResponse(request, 3011, respdata, action) # response beldej baina. 6 keytei.
                else:
                    # token-ii turul ni forgot, register ali ali ni bish bol buruu duudagdsan gej uzne.
                    # login-ii token GET-r duudagdahgui. 
                    action = "no action"
                    respdata = []
                    resp = sendResponse(request, 3017, respdata, action) # response beldej baina. 6 keytei.
                
            else: # Hervee hargalzah token oldoogui bol ajillana.
                # token buruu esvel hugatsaa duussan . Send Response
                action = "notoken" 
                respdata = []
                resp = sendResponse(request, 3009, respdata, action) # response beldej baina. 6 keytei.
                
        except:
            # GET method dotood aldaa
            action = "no action" 
            respdata = []  # response-n data-g beldej baina. list turultei baih
            resp = sendResponse(request, 5004, respdata, action)
            # response beldej baina. 6 keytei.
        finally:
            cursor.close()
            disconnectDB(conn)
            return JsonResponse(resp)
    
    # Method ni POST, GET ali ali ni bish bol ajillana
    else:
        #GET, POST-s busad uyd ajillana
        action = "no action"
        respdata = []
        resp = sendResponse(request, 3002, respdata, action)
        return JsonResponse(resp)
