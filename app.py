import os,sys
import math
import traceback
from flask_pymongo import PyMongo, pymongo
from pymongo import MongoClient
from bson import ObjectId
from flask import Flask, request, render_template, json, redirect, url_for, escape, session
#from datetime import timedelta, datetime
import datetime
#from datetime import datetime
import time
from isoweek import Week
from bson import json_util

from helperFunctions import *

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'cisco-regression-tool'

# Global Parameters
projectroot = os.path.dirname(os.path.abspath(__file__))
backupDir = os.path.join(projectroot, 'backup')
app.config['BACKUP_FOLDER'] = backupDir


@app.route('/login', methods=['post', 'get'])
def login():
    user_validation = ''
    error_list=[]
    login_status = 0
    if request.method == 'POST':
        try:
            user_id = request.form['user_id'].strip()
            regression_token = request.form['regression_token'].strip()
            entity_collection = db_connection()
            login_status = entity_collection.users.find({'_id': ObjectId(regression_token),'user_id':user_id}).count()
            if login_status >0:
                session['regression-tool-username'] = user_id.strip()
                return redirect(url_for('home'))
            else:
                user_validation='Please enter correct username, regression token.'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            user_validation='Please enter correct username, regression token.'

    return render_template('login.html',user_validation = user_validation, error = error_list)


@app.route('/logout')
def logout():
   session.pop('regression-tool-username', None)
   return redirect(url_for('login'))

@app.route('/')
@app.route('/home', methods=['post', 'get'])
def home():
    home_menu = 'class=active'
    test_area_menu = ''
    reports_menu = ''
    input_success = ''
    test_areas_list = []
    error_list = []
    user_message = ''
    ri_score_list = ''
    if request.method == 'POST':
        try:
            entity_collection = db_connection()
            biller = request.form['biller'].strip().lower()
            payment_status = request.form['payment_status'].strip().lower()
            bill_amount = float(request.form['bill_amount'].strip())            
            bill_date = datetime.datetime.strptime(request.form['bill_date'].strip(),"%m/%d/%Y")
            due_date = datetime.datetime.strptime(request.form['due_date'].strip(),"%m/%d/%Y")            
            form_input_array = {'payment_status':payment_status,'biller': biller.lower(),'bill_amount': bill_amount,'bill_date': bill_date,'due_date': due_date,'created_on':datetime.datetime.now()}
            entity_collection.dues.insert(form_input_array)
            input_success='New due inserted successfully'
            ri_score_list=entity_collection.dues.find({}).sort('due_date',pymongo.ASCENDING)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
    else:
        try:
            entity_collection = db_connection()
            ri_score_list=entity_collection.dues.find({}).sort('due_date',pymongo.ASCENDING)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})

    if 'ri-score-user-message' in session:
        user_message = session['ri-score-user-message']
        session.pop('ri-score-user-message', None)

    if 'regression-tool-username' in session:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        return render_template('home.html', dues_list = ri_score_list,
        input_success = input_success, error = error_list, timestr = timestr, user_message = user_message,
        home_menu = home_menu, test_area_menu = test_area_menu, reports_menu = reports_menu,loggedin_user = session['regression-tool-username'])
    else:
        return redirect(url_for('login'))
		
@app.route('/calendar', methods=['post', 'get'])
def calendar():
    home_menu = 'class=active'
    test_area_menu = ''
    reports_menu = ''
    input_success = ''
    test_areas_list = []
    error_list = []
    user_message = ''
    ri_score_list = ''
    if request.method == 'POST':
        try:
            entity_collection = db_connection()
            biller = request.form['biller'].strip().lower()
            payment_status = request.form['payment_status'].strip().lower()
            bill_amount = float(request.form['bill_amount'].strip())            
            bill_date = datetime.datetime.strptime(request.form['bill_date'].strip(),"%m/%d/%Y")
            due_date = datetime.datetime.strptime(request.form['due_date'].strip(),"%m/%d/%Y")            
            form_input_array = {'payment_status':payment_status,'biller': biller.lower(),'bill_amount': bill_amount,'bill_date': bill_date,'due_date': due_date,'created_on':datetime.datetime.now()}
            entity_collection.dues.insert(form_input_array)
            input_success='New due inserted successfully'
            ri_score_list=entity_collection.dues.find({}).sort({"due_date":1})
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
    else:
        try:
            entity_collection = db_connection()
            ri_score_list=entity_collection.dues.find({}).sort({'due_date':1})
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})

    if 'ri-score-user-message' in session:
        user_message = session['ri-score-user-message']
        session.pop('ri-score-user-message', None)

    if 'regression-tool-username' in session:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        return render_template('home.html', dues_list = ri_score_list,
        input_success = input_success, error = error_list, timestr = timestr, user_message = user_message,
        home_menu = home_menu, test_area_menu = test_area_menu, reports_menu = reports_menu,loggedin_user = session['regression-tool-username'])
    else:
        return redirect(url_for('login'))		
        
@app.route('/ri-score-edit', methods=['post', 'get'])
def ri_score_edit():
    home_menu = ''
    test_area_menu = 'class=active'
    reports_menu = ''
    error_list=[]
    edit_db_result = ''
    user_message = ''
    editable_ri_score = ''
    riscore_date = ''
    if request.method == 'GET' and 'regression-tool-username' in session:
        try:
            tid = request.args['tid']
            entity_collection = db_connection()
            edit_db_result = entity_collection.ri_score.find({'_id': ObjectId(tid)})
            if edit_db_result.count() == 0 :
                user_message = 'Record is not in database'
            else:
                for item in edit_db_result:
                    editable_ri_score = item
                    riscore_date = item['riscore_date'].strftime("%m/%d/%Y")                    
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})

    if 'regression-tool-username' in session:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        return render_template('ri-score-edit.html', timestr = timestr, editable_ri_score = editable_ri_score, riscore_date=riscore_date, user_message = user_message, loggedin_user = session['regression-tool-username'], error = error_list, home_menu = home_menu, test_area_menu = test_area_menu, reports_menu = reports_menu)
    else:
        return redirect(url_for('login'))


@app.route('/ri-score-remove', methods=['post', 'get'])
def ri_score_remove():
    error_list=[]
    if request.method == 'GET' and 'regression-tool-username' in session:
        try:
            tid = request.args['del_id']
            entity_collection = db_connection()
            db_result=entity_collection.ri_score.remove({'_id': ObjectId(tid)})
            session['ri-score-user-message'] = 'RI Score data deleted successfully'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            session['ri-score-user-message'] = error_list
    return redirect(url_for('home'))


@app.route('/test-area-management', methods=['post', 'get'])
def test_area_management():
    ri_scores_menu = ''
    our_team_menu = ''
    home_menu = ''
    test_area_menu = 'class=active'
    reports_menu = ''
    input_success = ''
    error_list=[]
    test_areas_list = []
    user_message = ''
    notOwner = []
    if request.method == 'POST':
        try:
            test_area = request.form['test_area'].strip()
            entity_collection = db_connection()
            check_duplicate_result = entity_collection.test_area.find({'test_area':test_area.lower()})
            if check_duplicate_result.count() == 0 :
                user_id = request.form['user_id'].strip()
                form_input_array = {'test_area': test_area.lower(),'user_id': user_id,'used_status':0,'owner':1}
                entity_collection.test_area.insert(form_input_array)
                session['test-area-user-message']='Test area added successfully'
            else:
                session['test-area-user-message']='Duplicate record, Test area already exist.'

            #db_areas_list=entity_collection.test_area.find({'$or': [{'user_id':session['regression-tool-username']}, {'user_id':'jthanisl'}]})
            db_areas_list=entity_collection.test_area.find({})
            for item in db_areas_list:
                test_areas_list.append(item)
                if item['user_id'] == session['regression-tool-username'] and item['owner'] ==0:
                    notOwner.append(item['test_area'])
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
    else:
        try:
            entity_collection = db_connection()
            db_areas_list=entity_collection.test_area.find({})
            for item in db_areas_list:
                test_areas_list.append(item)
                if item['user_id'] == session['regression-tool-username'] and item['owner'] ==0:
                    notOwner.append(item['test_area'])
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})

    if 'test-area-user-message' in session:
        user_message = session['test-area-user-message']
        session.pop('test-area-user-message', None)

    if 'regression-tool-username' in session:
        return render_template('test-area-management.html',user_message = user_message,
        loggedin_user = session['regression-tool-username'],
        test_areas_list = test_areas_list,
        input_success = input_success, notOwner = notOwner,
        error = error_list, home_menu = home_menu, ri_scores_menu = ri_scores_menu, test_area_menu = test_area_menu, our_team_menu = our_team_menu, reports_menu = reports_menu)
    else:
        return redirect(url_for('login'))


@app.route('/test-area-remove', methods=['post', 'get'])
def test_area_remove():
    error_list=[]
    if request.method == 'GET' and 'regression-tool-username' in session:
        try:
            tid = request.args['tid']
            entity_collection = db_connection()
            db_result=entity_collection.test_area.remove({'_id': ObjectId(tid)})
            session['test-area-user-message'] = 'Test area deleted successfully'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            session['test-area-user-message'] = error_list
    return redirect(url_for('test_area_management'))

@app.route('/test-area-edit', methods=['post', 'get'])
def test_area_edit():
    ri_scores_menu = ''
    our_team_menu = ''
    home_menu = ''
    test_area_menu = 'class=active'
    reports_menu = ''
    error_list=[]
    edit_db_result = ''
    user_message = ''
    editable_test_area = ''
    if request.method == 'GET' and 'regression-tool-username' in session:
        try:
            tid = request.args['tid']
            entity_collection = db_connection()
            edit_db_result = entity_collection.test_area.find({'_id': ObjectId(tid),'user_id':session['regression-tool-username']})
            if edit_db_result.count() == 0 :
                user_message = 'Record is not in database'
            else:
                for item in edit_db_result:
                    editable_test_area = item
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})

    if 'regression-tool-username' in session:
        return render_template('test-area-management-edit.html', editable_test_area = editable_test_area, user_message = user_message, 
        loggedin_user = session['regression-tool-username'], error = error_list, home_menu = home_menu, test_area_menu = test_area_menu, 
        reports_menu = reports_menu, ri_scores_menu = ri_scores_menu, our_team_menu = our_team_menu)
    else:
        return redirect(url_for('login'))

@app.route('/test-area-update', methods=['post', 'get'])
def test_area_update():
    error_list=[]
    update_db_result = ''
    if request.method == 'POST' and 'regression-tool-username' in session:
        try:
            edit_id = request.form['edit_id']
            edit_test_area = request.form['test_area'].strip()
            update_data={'test_area':edit_test_area.lower()}
            entity_collection = db_connection()
            update_db_result = entity_collection.test_area.update({'_id': ObjectId(edit_id),'user_id':session['regression-tool-username']},{'$set':update_data})
            if update_db_result['nModified'] == 1:
                session['test-area-user-message'] = 'Test area modified successfully.'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            session['test-area-user-message'] = error_list
    return redirect(url_for('test_area_management'))

@app.route('/test-area-copy', methods=['post', 'get'])
def test_area_copy():
    error_list=[]
    update_db_result = ''
    if request.method == 'GET' and 'regression-tool-username' in session:
        try:
            copy_id = request.args['cid'].strip()
            toBeCopy_test_area = ''
            #print("Logged User : ",session['regression-tool-username'] )
            #print("copy_id : ",copy_id )
            entity_collection = db_connection()
            copy_db_result = entity_collection.test_area.find({'_id': ObjectId(copy_id)})
            for item in copy_db_result:
                toBeCopy_test_area = item['test_area'].strip()
            existing_result = entity_collection.test_area.find({'test_area': toBeCopy_test_area.lower(),'user_id':session['regression-tool-username']}).count()
            #print("copy_db_result.count() : ",copy_db_result)
            if existing_result == 0 :
                form_input_array = {'test_area': toBeCopy_test_area.lower(),'user_id': session['regression-tool-username'],'used_status':0,'owner':0}
                entity_collection.test_area.insert(form_input_array)
                session['test-area-user-message']='Test area copied successfully'
            else:
                session['test-area-user-message']='Test area already exist under your userID'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            session['test-area-user-message'] = error_list
    return redirect(url_for('test_area_management'))


@app.route('/reports_old', methods=['post', 'get'])
def reports_old():
    w = Week(2011, 20)
    #print("Week %s starts on %s" % (w, w.monday()))
    lastWeekWithYr = Week.thisweek()-1
    lastWeekWeekNumber = lastWeekWithYr.week
    lastWeekStartsOn = lastWeekWithYr.monday()
    lastWeekEndsWith = lastWeekWithYr.sunday()
    #print("nextWeekWeekNumber : %s , nextWeekWithYr : %s, nextWeekStartsOn : %s" % (nextWeekWeekNumber,nextWeekWithYr,nextWeekStartsOn))
    currentWeekNumber = Week.thisweek().week
    currentWeekWithYr = Week.thisweek()
    currentWeekStartsOn = currentWeekWithYr.monday()
    #print("currentWeekNumber : %s , currentWeekWithYr : %s, currentWeekStartsOn : %s" % (currentWeekNumber,currentWeekWithYr,currentWeekStartsOn))
    nextWeekWithYr = Week.thisweek()+1
    nextWeekWeekNumber = nextWeekWithYr.week
    nextWeekStartsOn = nextWeekWithYr.monday()
    #print("nextWeekWeekNumber : %s , nextWeekWithYr : %s, nextWeekStartsOn : %s" % (nextWeekWeekNumber,nextWeekWithYr,nextWeekStartsOn))
    timestr = time.strftime("%Y%m%d-%H%M%S")
    error_list=[]
    home_menu = ''
    test_area_menu = ''
    reports_menu = 'class=active'
    latest_score_data = []
    platform_wise_score_breakup = {}
    previous_score_data = []
    search_dd_platform = []
    search_dd_version = []
    search_dd_sub_version = []
    loggedin_user = ''
    data_series = []
    cdets_info_slice = []
    component_wise = []
    severity_wise = []
    trend_xaxis_data = []
    trend_yaxis_data = []
    trend_chart_main_title = 'Trend Chart : Platform Wise'
    trend_chart_legends = 1
    trend_chart_new_legends = 1 
    test_areas_for_breakup = {}
    trend_chart_width = 0
    trend_chart_categories = []
    trend_chart_score_data = [] 

    if request.method == 'POST':
        try:
            entity_collection = db_connection()
# Start:Getting form values to search
            platform = request.form['platform'].strip().lower()
            version = request.form['version'].strip().lower()
            sub_version = request.form['sub_version'].strip().lower()
            selected_platform = platform
            selected_version = version
            selected_sub_version = sub_version
# End:Getting form values to search
            existing_platforms = entity_collection.ri_score.distinct("platform")
            existing_versions = entity_collection.ri_score.distinct("version")
#-----------------------------------------------------------------------------------------------------------------------------------------------
# all + value + none or all + value + all
#-----------------------------------------------------------------------------------------------------------------------------------------------
            if (platform=="" or platform=="all") and version!="" and version!="all" and (sub_version=="" or sub_version=="all"):
                trend_chart_main_title = "Regression Score Trend ( %s )"%(version.upper())
                distinct_subversions_db = entity_collection.ri_score.distinct('sub_version',{'version':version})
                distinct_platforms_db = entity_collection.ri_score.distinct('platform',{'version':version})

                for iteminSubVersions in distinct_subversions_db:
                    trend_yaxis_score = []
                    for platform_idx,item_platform in enumerate(distinct_platforms_db):
                        if item_platform.upper() not in trend_xaxis_data:
                            trend_xaxis_data.append(item_platform.upper())
                            
                        print("Query Parameters - platform: %s, version: %s, sub version: %s"%(item_platform.lower(),version.lower(),iteminSubVersions.lower()))
                        trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':version.lower(), 'sub_version':iteminSubVersions.lower()}).sort([("riscore_date", -1)]).limit(1)
                        print("trend_chart_db_result.count() : ",trend_chart_db_result.count())                     
                        if trend_chart_db_result.count() > 0 :
                            for idx,item in enumerate(trend_chart_db_result):
                                trend_yaxis_score.insert(platform_idx,float(item['score']))
                                trend_chart_width +=1
                        else:
                            trend_yaxis_score.insert(platform_idx,'null')
                            trend_chart_width +=1
                            
                    legend_title = version+'('+iteminSubVersions+')'                        
                    trend_yaxis_data.append({'name':legend_title,'data':trend_yaxis_score,
                                             'dataLabels': {'enabled': 'true','rotation':-90, 'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                            'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})
                                                            
                #For new chart==================================================================================================  
                distinct_platforms_db = entity_collection.ri_score.distinct('platform',{'version':version})
                for platform_idx,item_platform in enumerate(distinct_platforms_db):
                    subversions_label = []              
                    trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':version.lower()}).sort([("riscore_date",1)])
                    if trend_chart_db_result.count() > 0 :
                        for idx,item in enumerate(trend_chart_db_result):
                            subversions_label.append(item['sub_version'])
                            trend_chart_score_data.append(float(item['score']))                                                     

                    trend_chart_categories.append({
                                                'name': item_platform.upper(), # Versions 
                                                'categories': subversions_label # Sub Versions
                                              }) 
                                             

#-----------------------------------------------------------------------------------------------------------------------------------------------
# all + value + value
#-----------------------------------------------------------------------------------------------------------------------------------------------
            elif platform=="all" and version!="" and version!="all" and sub_version!="" and sub_version!="all":
                trend_chart_main_title = "Regression Score Trend ( %s, %s )"%(version.upper(),sub_version.lower())
                trend_chart_legends = 0
                distinct_subversions_db = []
                distinct_subversions_db.append(sub_version)
                distinct_platforms_db = entity_collection.ri_score.distinct('platform',{'version':version,'sub_version':sub_version})
                for iteminSubVersions in distinct_subversions_db:
                    trend_yaxis_score = []
                    for platform_idx,item_platform in enumerate(distinct_platforms_db):
                        if item_platform.upper() not in trend_xaxis_data:
                            trend_xaxis_data.append(item_platform.upper())

                        trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':version.lower(), 'sub_version':iteminSubVersions.lower()})
                        if trend_chart_db_result.count() > 0 :
                            for idx,item in enumerate(trend_chart_db_result):
                                trend_yaxis_score.insert(platform_idx,float(item['score']))
                        else:
                            trend_yaxis_score.insert(platform_idx,'null')

                    trend_yaxis_data.append({'name':version+'('+iteminSubVersions+')','data':trend_yaxis_score,
                                             'dataLabels': {'enabled': 'true','rotation':-90, 'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                            'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})
                                                            
                #For new chart==================================================================================================  
                distinct_platforms_db = entity_collection.ri_score.distinct('platform',{'version':version,'sub_version':sub_version.lower()})
                for platform_idx,item_platform in enumerate(distinct_platforms_db):             
                    subversions_label = []              
                    trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':version.lower(),'sub_version':sub_version.lower()}).sort([("riscore_date",1)])
                    if trend_chart_db_result.count() > 0 :
                        for idx,item in enumerate(trend_chart_db_result):
                            subversions_label.append(sub_version.lower())
                            trend_chart_score_data.append(float(item['score']))                                                     

                    trend_chart_categories.append({
                                                'name': item_platform.upper()+' - '+version, # Versions 
                                                'categories': subversions_label # Sub Versions
                                              })                                                            
#Trend chart Filter 1---------------------------------------------------------------------------------------------------------------------------
# none + all + none/all
#-----------------------------------------------------------------------------------------------------------------------------------------------
# all + all + none or all + all + all 
#-----------------------------------------------------------------------------------------------------------------------------------------------
            elif platform=="" and ( version=="all" or version=="") and ( sub_version=="" or sub_version=="all") :
                if version=="all" and sub_version=="all":
                    trend_chart_main_title = "Regression Score Trend ( All Versions, All Sub Versions )"
                elif version=="all" and sub_version=="all":
                    trend_chart_main_title = "Regression Score Trend ( All Versions )"
                elif version=="" and sub_version=="all":
                    trend_chart_main_title = "Regression Score Trend ( All Sub Versions )"
                nolegends = []
                distinct_subversions_db = entity_collection.ri_score.distinct("sub_version")
                distinct_versions_db = entity_collection.ri_score.distinct("version",{'sub_version':{'$in':distinct_subversions_db}})

                for iteminSubVersions in distinct_subversions_db:
                    for version_idx,item_version in enumerate(distinct_versions_db):
                        trend_yaxis_score = []
                        for platform_idx,item_platform in enumerate(existing_platforms):

                            if item_platform.upper() not in trend_xaxis_data:
                                trend_xaxis_data.append(item_platform.upper())

                            trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':item_version.lower(), 'sub_version':iteminSubVersions.lower()})
                            if trend_chart_db_result.count() > 0 :
                                for idx,item in enumerate(trend_chart_db_result):
                                    trend_yaxis_score.insert(version_idx,float(item['score']))
                                    #trend_chart_width +=1
                            else:
                                trend_yaxis_score.insert(version_idx,'null')
                        legend_title = item_version+'('+iteminSubVersions+')'
                        trend_yaxis_data.append({'name':legend_title,'data':trend_yaxis_score,
                                                 'dataLabels': {'enabled': 'true','rotation':-90,'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                                'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})
                        nolegends.append(legend_title)
                unique_bars = list(set(nolegends))
                print("len(unique_bars) : ",len(unique_bars))
                trend_chart_width = len(unique_bars)*3
#Trend chart Filter 2---------------------------------------------------------------------------------------------------------------------------
# none/all + all/none + value
            elif ( platform=="" or platform=="all" ) and ( version=="all" or version=="" ) and sub_version!="" and sub_version!="all":
                if version=="all":
                    trend_chart_main_title = "Regression Score Trend ( All Versions with %s )"%(sub_version.lower())
                elif platform=="all":
                    trend_chart_main_title = "Regression Score Trend ( All Platforms with %s )"%(sub_version.lower())
                else:
                    trend_chart_main_title = "Regression Score Trend ( %s )"%(sub_version.lower())
                distinct_versions_db = entity_collection.ri_score.distinct("version",{'sub_version':sub_version.lower()})
                distinct_platform_db = entity_collection.ri_score.distinct("platform",{'sub_version':sub_version.lower()})
                for version_idx,item_version in enumerate(distinct_versions_db):
                    trend_yaxis_score = []
                    for platform_idx,item_platform in enumerate(distinct_platform_db):

                        if item_platform.upper() not in trend_xaxis_data:
                            trend_xaxis_data.append(item_platform.upper())

                        latest_score_trend_db = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':item_version.lower(),'sub_version':sub_version.lower()}).sort([("riscore_date", -1)]).limit(1)
                        if latest_score_trend_db.count() > 0 :
                            for idx,item in enumerate(latest_score_trend_db):
                                score = float(item['score'])
                                trend_yaxis_score.insert(platform_idx,score)
                                sub_version = item['sub_version']
                        else:
                            trend_yaxis_score.insert(platform_idx,'null')


                    trend_yaxis_data.append({'name':item_version+'('+sub_version+')','data':trend_yaxis_score,
                                         'dataLabels': {'enabled': 'true','rotation':-90,'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                        'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})

#Trend chart Filter 3---------------------------------------------------------------------------------------------------------------------------
# all + none + none
            elif platform!="" and platform=="all" and version=="" and sub_version=="":
                trend_chart_main_title = "Regression Score Trend ( Platform Wise Latest Score )"
                trend_chart_legends = 0
                #for version_idx,item_version in enumerate(existing_versions):
                trend_yaxis_score = []
                for platform_idx,item_platform in enumerate(existing_platforms):
                    latest_score_trend_db = entity_collection.ri_score.find({'platform':item_platform.lower()}).sort([("riscore_date", -1)]).limit(1)
                    if latest_score_trend_db.count() > 0 :
                        for idx,item in enumerate(latest_score_trend_db):
                            score = float(item['score'])
                            trend_yaxis_score.insert(platform_idx,score)
                            version = item['version']
                            sub_version = item['sub_version']
                            xaxis_value = item_platform.upper()+'-'+version.upper()+'-'+sub_version.lower()
                            if xaxis_value not in trend_xaxis_data:
                                trend_xaxis_data.append(xaxis_value)
                    else:
                        trend_yaxis_score.insert(platform_idx,'null')


                trend_yaxis_data.append({'name':item_platform.upper(),'data':trend_yaxis_score,
                                     'dataLabels': {'enabled': 'true','rotation':-90,'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                    'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})
                                                    
                #For new chart==================================================================================================  
                distinct_platforms_db = entity_collection.ri_score.distinct('platform')
                trend_chart_new_legends = 1 
                for platform_idx,item_platform in enumerate(distinct_platforms_db):
                    distinct_versions_db = entity_collection.ri_score.distinct('version',{'platform':item_platform.lower()})
                    trend_chart_categories_temp = []                    
                    for version_idx_idx,item_version in enumerate(distinct_versions_db):                
                        subversions_label = []              
                        trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':item_version.lower()}).sort([("riscore_date",-1)])
                        if trend_chart_db_result.count() > 0 :
                            for idx,item in enumerate(trend_chart_db_result):
                                subversions_label.append(item['sub_version'])
                                trend_chart_score_data.append(float(item['score'])) 
                                                        
                        trend_chart_categories_temp.append({
                                                    'name': item_version.upper(), # Versions 
                                                    'categories': subversions_label # Sub Versions
                                                  })
                    trend_chart_categories.append({
                                                    'name': item_platform.upper(), # Versions 
                                                    'categories': trend_chart_categories_temp # Sub Versions
                                                  })                                                    

#-----------------------------------------------------------------------------------------------------------------------------------------------
# value + none + none or value + none + all or value + all + none or value + all + all
#-----------------------------------------------------------------------------------------------------------------------------------------------
            elif platform!="" and platform!="all" and ( version=="" or version=="all" ) and ( sub_version=="" or sub_version=="all" ):
                trend_chart_main_title = "Regression Score Trend ( %s )"%(platform.upper())
                distinct_subversions_db = entity_collection.ri_score.distinct("sub_version",{'platform':platform.lower()})
                distinct_versions_db = entity_collection.ri_score.distinct("version",{'platform':platform.lower()})
            
                for iteminSubVersions in distinct_subversions_db:
                    trend_yaxis_score = []
                    for version_idx,item_version in enumerate(distinct_versions_db):
                        if item_version.upper() not in trend_xaxis_data:
                            trend_xaxis_data.append(item_version.upper())

                        trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':item_version.lower(), 'sub_version':iteminSubVersions.lower()}).sort([("riscore_date", -1)]).limit(1)
                        if trend_chart_db_result.count() > 0 :
                            for idx,item in enumerate(trend_chart_db_result):
                                trend_yaxis_score.insert(version_idx,float(item['score']))
                                trend_chart_width +=1                               
                        else:
                            trend_yaxis_score.insert(version_idx,'null')
                            trend_chart_width +=1

                    trend_yaxis_data.append({'name':iteminSubVersions,'data':trend_yaxis_score,
                                             'dataLabels': {'enabled': 'true','rotation':-90,'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                            'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})
                #For new chart==================================================================================================  

                for version_idx,item_version in enumerate(distinct_versions_db):
                    subversions_label = []              
                    trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':item_version.lower()}).sort([("riscore_date",1)])
                    if trend_chart_db_result.count() > 0 :
                        for idx,item in enumerate(trend_chart_db_result):
                            subversions_label.append(item['sub_version'])
                            trend_chart_score_data.append(float(item['score']))                                                     

                    trend_chart_categories.append({
                                                'name': item_version.upper(), # Versions 
                                                'categories': subversions_label # Sub Versions
                                              })                                                            

#-----------------------------------------------------------------------------------------------------------------------------------------------
# value + value + none or value + value + all
#-----------------------------------------------------------------------------------------------------------------------------------------------
            elif platform!="" and platform!="all" and version!="" and version!="all" and ( sub_version=="" or sub_version=="all"):
                if sub_version=="all":
                    trend_chart_main_title = "Regression Score Trend ( %s, %s, All Sub Versions )"%(platform.upper(),version)
                else:
                    trend_chart_main_title = "Regression Score Trend ( %s, %s )"%(platform.upper(),version)

                trend_chart_legends = 0
                #distinct_subversions_db = entity_collection.ri_score.distinct("sub_version",{'platform':platform.lower(),'version':version.lower()})
                distinct_subversions_db_new = entity_collection.ri_score.find({'platform':platform.lower(),'version':version.lower()},{'sub_version':1,'_id':0,'riscore_date':1}).sort([("riscore_date", 1)])
                sub_versions_array = []
                for dsdb_item in distinct_subversions_db_new:
                    sub_versions_array.append(dsdb_item['sub_version'])
                #print_json_format(sub_versions_array)
                #distinct_svs = list(set(sub_versions_array))
                #print_json_format(distinct_svs)
                if len(sub_versions_array)>0:
                    trend_yaxis_score = []
                    for idx_subversion,iteminSubVersions in enumerate(sub_versions_array):
                        if iteminSubVersions.upper() not in trend_xaxis_data:
                            trend_xaxis_data.append(iteminSubVersions.upper())

                        trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':version.lower(), 'sub_version':iteminSubVersions.lower()})
                        if trend_chart_db_result.count() > 0 :
                            for idx,item in enumerate(trend_chart_db_result):
                                trend_yaxis_score.insert(idx_subversion,float(item['score']))
                                trend_chart_width +=1
                        else:
                            trend_yaxis_score.insert(idx_subversion,'null')
                            trend_chart_width +=1


                    trend_yaxis_data.append({'name':iteminSubVersions,'data':trend_yaxis_score,
                                             'dataLabels': {'enabled': 'true','rotation':-90,'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                            'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})
                else:
                    trend_yaxis_data.append({'data':[]})
                    
                #For new chart==================================================================================================  
                trend_chart_categories = []
                trend_chart_score_data = []                             
                subversions_label = []              
                trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':version.lower()}).sort([("riscore_date",1)])
                if trend_chart_db_result.count() > 0 :
                    for idx,item in enumerate(trend_chart_db_result):
                        subversions_label.append(item['sub_version'])
                        trend_chart_score_data.append(float(item['score']))                              

                trend_chart_categories.append({
                                            'name': platform.upper()+' - '+version.upper(), # Versions 
                                            'categories': subversions_label # Sub Versions
                                          })                    

#End5-----------------------------------------------------------------------------------------------------------------------------------------------
#Trend chart Filter 6---------------------------------------------------------------------------------------------------------------------------
# value + none/all + value
            elif platform!="" and platform!="all" and ( version=="" or version=="all" ) and sub_version!="" and sub_version!="all":
                trend_chart_main_title = "Regression Score Trend ( %s, %s )"%(platform.upper(),sub_version.lower())
                distinct_versions_db = entity_collection.ri_score.distinct("version",{'platform':platform.lower(),'sub_version':sub_version.lower()})
                trend_chart_legends = 0
                if len(distinct_versions_db)>0:
                    trend_yaxis_score = []
                    for version_idx,item_version in enumerate(distinct_versions_db):
                        if item_version.upper() not in trend_xaxis_data:
                            trend_xaxis_data.append(item_version.upper())

                        trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':item_version.lower(), 'sub_version':sub_version.lower()})
                        if trend_chart_db_result.count() > 0 :
                            for idx,item in enumerate(trend_chart_db_result):
                                trend_yaxis_score.insert(version_idx,float(item['score']))
                        else:
                            trend_yaxis_score.insert(version_idx,'null')

                    trend_yaxis_data.append({'name':item_version,'data':trend_yaxis_score,
                                             'dataLabels': {'enabled': 'true','rotation':-90,'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                            'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})
                else:
                    trend_yaxis_data.append({'data':[]})
#End6-----------------------------------------------------------------------------------------------------------------------------------------------
#Trend chart Filter 7 ( value + value + value )-----------------------------------------------------------------------------------------------------
# value + value + value
            elif platform!="" and platform!="all" and version!="" and version!="all" and sub_version!="" and sub_version!="all":
                trend_chart_main_title = "Regression Score Trend ( %s, %s, %s )"%(platform.upper(),version.lower(),sub_version.lower())
                trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':version.lower(), 'sub_version':sub_version.lower()})
                trend_chart_legends = 0
                if trend_chart_db_result.count()>0:
                    trend_yaxis_score = []
                    xaxis_label_custom = "%s - %s - %s"%(platform.upper(),version.upper(),sub_version.lower())
                    for idx,item in enumerate(trend_chart_db_result):
                        trend_yaxis_score.insert(idx,float(item['score']))

                    if xaxis_label_custom not in trend_xaxis_data:
                        trend_xaxis_data.append(xaxis_label_custom)

                    trend_yaxis_data.append({'name':xaxis_label_custom,'data':trend_yaxis_score,
                                             'dataLabels': {'enabled': 'true','rotation':-90,'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                            'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})
                else:
                    trend_yaxis_data.append({'data':[]})
                #For new chart==================================================================================================
                trend_chart_new_legends = 0             
                trend_chart_categories = []
                trend_chart_score_data = []                             
                trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':version.lower(),'sub_version':sub_version.lower()}).sort([("riscore_date",1)])
                if trend_chart_db_result.count() > 0 :
                    for idx,item in enumerate(trend_chart_db_result):
                        trend_chart_score_data.append(float(item['score']))                              

                    
#End7-----------------------------------------------------------------------------------------------------------------------------------------------

            query_str_array = []
            if selected_platform!="" and selected_platform!="all":
                query_str_array.append({'platform':selected_platform.lower()})
            if selected_version!="" and selected_version!="all":
                query_str_array.append({'version':selected_version.lower()})
            if selected_sub_version!="" and selected_sub_version!="all":
                query_str_array.append({'sub_version':selected_sub_version.lower()})
# Making where condition for mongodb
            query_str = formQueryString(query_str_array)

# Latest score data based on filter

            latestDataByPlatforms = []
            previousDataByPlatforms = []
            if platform!="" and platform!="all":
                latest_score_by_platforms = entity_collection.ri_score.find(query_str).sort([("riscore_date", -1)]).limit(1)
                for item in latest_score_by_platforms:
                    latestDataByPlatforms.append(item)
                previous_score_by_platforms = entity_collection.ri_score.find(query_str).sort([("riscore_date", -1)]).skip(1).limit(1)
                for item in previous_score_by_platforms:
                    previousDataByPlatforms.append(item)
            elif platform=="" or platform=="all":
                for platform_idx,item_platform in enumerate(existing_platforms):
                    query_str['platform']=item_platform
                    latest_score_by_platforms = entity_collection.ri_score.find(query_str).sort([("riscore_date", -1)]).limit(1)
                    for item in latest_score_by_platforms:
                        latestDataByPlatforms.append(item)
                    previous_score_by_platforms = entity_collection.ri_score.find(query_str).sort([("riscore_date", -1)]).skip(1).limit(1)
                    for item in previous_score_by_platforms:
                        previousDataByPlatforms.append(item)

            for idx,item in enumerate(latestDataByPlatforms):
                latest_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})
                platform_wise_score_breakup.update({item['platform'].lower():[{'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score']),'test_area':item['test_area']}]})
# Previous week score data for table
            for idx,item in enumerate(previousDataByPlatforms):
                previous_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})
# Previous week score data for table

# Bug details for table, component wise count, severity wise count ( unique bug ids based on filter )


            query_str = formQueryString(query_str_array)
            form_input_data = entity_collection.ri_score.find(query_str)
            all_bugids = []
            cdets_info = []
            for idx,item in enumerate(form_input_data):
                cdets_array =  get_cdets_count(item['test_area'])
                for item in cdets_array:
                    all_bugids.append(item)

            cdets_info = entity_collection.bug_data.find({"Identifier":{"$in":all_bugids}})

            distinct_components = []
            distinct_severity = []
            for item in cdets_info:
                cdets_info_slice.append(item)
                distinct_components.append(item['Component'].lower())
                distinct_severity.append(item['Severity'].lower())

            for item in list(set(distinct_components)):
                component_wise.append({ 'name': item, 'y':distinct_components.count(item)})

            for item in list(set(distinct_severity)):
                severity_wise.append({ 'name': item, 'y':distinct_severity.count(item)})
#-------------------------------------------------------------------------------------------------------------------------------
# Platform Wise table
#-------------------------------------------------------------------------------------------------------------------------------
            #test_areas_for_breakup = {}
            for pwsb_key,pwsb_item in platform_wise_score_breakup.items():
                platform_wise_breakup = []
                ddts_info = []
                bug_ids_for_breakup = []
                test_area_array = pwsb_item[0]['test_area']
                score = pwsb_item[0]['score']
                version = pwsb_item[0]['version']
                sub_version = pwsb_item[0]['sub_version']
                for testarea in test_area_array:
                    test_area_name_db = entity_collection.test_area.find({'_id':ObjectId(testarea['test_area_id'])},{'_id':0,'test_area':1})
                    for area_name in test_area_name_db:
                        test_area_name = area_name['test_area']
                    platform_wise_breakup.append({'area_score':testarea['score'],'area_name':test_area_name,'ddts':testarea['cdets'],'impact':testarea['comments']})
                    if testarea['cdets']:
                        bug_ids_for_breakup.append(testarea['cdets'])

                ddts_info = entity_collection.bug_data.find({"Identifier":{"$in":bug_ids_for_breakup}})

                test_areas_for_breakup.update({pwsb_key:{'break_up':platform_wise_breakup,'ddts':ddts_info}})

#-------------------------------------------------------------------------------------------------------------------------------
# Bug details for table ( unique bug ids based on filter )
# Currently available platform,version,and sub version for drop down filter search form         
            search_dd_platform = entity_collection.ri_score.distinct("platform")
            
            if selected_platform!="" and selected_platform!="all" and selected_version!="" and selected_version!="all":          
                search_dd_version = entity_collection.ri_score.distinct("version",{'platform':selected_platform.lower()})
                search_dd_sub_version = entity_collection.ri_score.distinct("sub_version",{'platform':selected_platform.lower(),'version':selected_version.lower()})            
            elif selected_platform!="" and selected_platform!="all" and selected_version!="" and selected_version=="all":          
                search_dd_version = entity_collection.ri_score.distinct("version",{'platform':selected_platform.lower()})
                search_dd_sub_version = entity_collection.ri_score.distinct("sub_version",{'platform':selected_platform.lower()})               
            elif selected_platform!="" and selected_platform!="all" and selected_version=="":            
                search_dd_version = entity_collection.ri_score.distinct("version",{'platform':selected_platform.lower()})
            elif selected_platform=="all" and selected_version!="" and selected_version!="all":          
                search_dd_version = entity_collection.ri_score.distinct("version")
                search_dd_sub_version = entity_collection.ri_score.distinct("sub_version",{'version':selected_version.lower()})                 
            elif selected_platform=="all" and selected_version=="":          
                search_dd_version = entity_collection.ri_score.distinct("version")
                 
            #search_dd_version = entity_collection.ri_score.distinct("version")
            #search_dd_sub_version = entity_collection.ri_score.distinct("sub_version")
            
# Currently available platform,version,and sub version for drop down filter search form
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})

        if 'regression-tool-username' in session:
            loggedin_user = session['regression-tool-username']

        return render_template('reports.html', home_menu = home_menu,
                               test_area_menu = test_area_menu, reports_menu = reports_menu, error = error_list,
                               latest_score_data = latest_score_data, previous_score_data = previous_score_data,
                               selected_platform = selected_platform,
                               selected_version = selected_version,
                               selected_sub_version = selected_sub_version,
                               search_dd_platform = set(list(search_dd_platform)),
                               search_dd_version = set(list(search_dd_version)),
                               search_dd_sub_version = set(list(search_dd_sub_version)),
                               timestr = lambda: int(round(time.time() * 1000)),
                               cdets_info = cdets_info_slice,
                               component_wise = component_wise,
                               severity_wise = severity_wise,
                               loggedin_user = loggedin_user, trend_xaxis_data = trend_xaxis_data, trend_yaxis_data = trend_yaxis_data,
                               trend_chart_main_title = trend_chart_main_title, trend_chart_legends = trend_chart_legends,
                               platform_wise_score_breakup = platform_wise_score_breakup,
                               test_areas_for_breakup = test_areas_for_breakup,trend_chart_width = trend_chart_width*43,
                               trend_chart_categories = trend_chart_categories, trend_chart_new_legends = trend_chart_new_legends,
                               trend_chart_score_data = trend_chart_score_data,trend_chart_width_new = len(trend_chart_score_data)*33
                               ,categories_rotation=0)                            
#Reports page initially without filter from search form
    else:
        try:
            entity_collection = db_connection()
            existing_platforms = entity_collection.ri_score.distinct("platform")
            existing_version = entity_collection.ri_score.distinct("version")
#---------------------------------------------------------------------------------------------------
            latestDataByPlatforms = []
            previousDataByPlatforms = []
            for platform_idx,item_platform in enumerate(existing_platforms):
                latest_score_by_platforms = entity_collection.ri_score.find({'platform':item_platform.lower()}).sort([("riscore_date", -1)]).limit(1)
                for idx,item in enumerate(latest_score_by_platforms):
                    latestDataByPlatforms.append(item)

                previous_score_by_platforms = entity_collection.ri_score.find({'platform':item_platform.lower()}).sort([("riscore_date", -1)]).skip(1).limit(1)
                for idx,item in enumerate(previous_score_by_platforms):
                    previousDataByPlatforms.append(item)
#---------------------------------------------------------------------------------------------------
# Start: For trend chart
            trend_chart_main_title = "Regression Score Trend ( Platform and version wise latest score )"
            trend_chart_legends = 0
            #for version_idx,item_version in enumerate(existing_versions):
            trend_yaxis_score = []
            for platform_idx,item_platform in enumerate(existing_platforms):

                latest_score_trend_db = entity_collection.ri_score.find({'platform':item_platform.lower()}).sort([("riscore_date", -1)]).limit(1)
                if latest_score_trend_db.count() > 0 :
                    for idx,item in enumerate(latest_score_trend_db):
                        score = float(item['score'])
                        trend_yaxis_score.insert(platform_idx,score)
                        version = item['version']
                        sub_version = item['sub_version']
                        xaxis_value = item_platform.upper()+'-'+version.upper()+'-'+sub_version.lower()
                        if xaxis_value not in trend_xaxis_data:
                            trend_xaxis_data.append(xaxis_value)
                else:
                    trend_yaxis_score.insert(platform_idx,'null')
                    sub_version = ""


            trend_yaxis_data.append({'name':item_platform.upper(),'data':trend_yaxis_score,
                                 'dataLabels': {'enabled': 'true','rotation':-90,'color': '#FFFFFF','align': 'right','format': '{point.y:.1f}',
                                                'y': 5,'style': {'fontSize': '13px','fontFamily': 'Verdana, sans-serif'}}})
                                                
            #For new chart==================================================================================================  
            distinct_platforms_db = entity_collection.ri_score.distinct('platform')
            trend_chart_new_legends = 1 
            for platform_idx,item_platform in enumerate(distinct_platforms_db):
                distinct_versions_db = entity_collection.ri_score.distinct('version',{'platform':item_platform.lower()})
                trend_chart_categories_temp = []                    
                for version_idx_idx,item_version in enumerate(distinct_versions_db):                
                    subversions_label = []              
                    trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':item_version.lower()}).sort([("riscore_date",-1)]).limit(1)
                    if trend_chart_db_result.count() > 0 :
                        for idx,item in enumerate(trend_chart_db_result):
                            subversions_label.append(item['sub_version'])
                            trend_chart_score_data.append(float(item['score'])) 
                                                    
                    trend_chart_categories_temp.append({
                                                'name': item_version.upper(), # Versions 
                                                'categories': subversions_label # Sub Versions
                                              })
                trend_chart_categories.append({
                                                'name': item_platform.upper(), # Versions 
                                                'categories': trend_chart_categories_temp # Sub Versions
                                              })                                                

# End: For trend chart

            #print("currentWeekStartsOn : ",datetime.datetime.combine(currentWeekStartsOn, datetime.datetime.min.time()))
            #ri_score_data_from = datetime.datetime.combine(lastWeekStartsOn, datetime.datetime.min.time())
            #ri_score_data_to= datetime.datetime.combine(lastWeekEndsWith, datetime.datetime.min.time())
            all_bugids = []
            cdets_info = []
            #form_input_data = entity_collection.ri_score.find({'riscore_date':{'$gte':ri_score_data_from,'$lte':ri_score_data_to}})
            for idx,item in enumerate(latestDataByPlatforms):
                data_series.append({item['riscore_date'].strftime("%m/%d/%Y"):float(item['score'])})
                cdets_array =  get_cdets_count(item['test_area'])
                for item in cdets_array:
                    all_bugids.append(item)

            for idx,item in enumerate(previousDataByPlatforms):
                previous_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})

            for idx,item in enumerate(latestDataByPlatforms):
                latest_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})
                platform_wise_score_breakup.update({item['platform'].lower():[{'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score']),'test_area':item['test_area']}]})

            cdets_info = entity_collection.bug_data.find({"Identifier":{"$in":all_bugids}})
            distinct_components = []
            distinct_severity = []
            for item in cdets_info:
                cdets_info_slice.append(item)
                distinct_components.append(item['Component'].lower())
                distinct_severity.append(item['Severity'].lower())

            for item in list(set(distinct_components)):
                component_wise.append({ 'name': item, 'y':distinct_components.count(item)})

            for item in list(set(distinct_severity)):
                severity_wise.append({ 'name': item, 'y':distinct_severity.count(item)})

#-------------------------------------------------------------------------------------------------------------------------------
# Platform Wise table
#-------------------------------------------------------------------------------------------------------------------------------
            #test_areas_for_breakup = {}
            for pwsb_key,pwsb_item in platform_wise_score_breakup.items():
                platform_wise_breakup = []
                ddts_info = []
                bug_ids_for_breakup = []
                test_area_array = pwsb_item[0]['test_area']
                score = pwsb_item[0]['score']
                version = pwsb_item[0]['version']
                sub_version = pwsb_item[0]['sub_version']
                for testarea in test_area_array:
                    test_area_name_db = entity_collection.test_area.find({'_id':ObjectId(testarea['test_area_id'])},{'_id':0,'test_area':1})
                    for area_name in test_area_name_db:
                        test_area_name = area_name['test_area']
                    platform_wise_breakup.append({'area_score':testarea['score'],'area_name':test_area_name,'ddts':testarea['cdets'],'impact':testarea['comments']})
                    if testarea['cdets']:
                        bug_ids_for_breakup.append(testarea['cdets'])

                ddts_info = entity_collection.bug_data.find({"Identifier":{"$in":bug_ids_for_breakup}})

                test_areas_for_breakup.update({pwsb_key:{'break_up':platform_wise_breakup,'ddts':ddts_info}})

#-------------------------------------------------------------------------------------------------------------------------------

            search_dd_platform = entity_collection.ri_score.distinct("platform")
            search_dd_version = []
            search_dd_sub_version = []
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})

        if 'regression-tool-username' in session:
            loggedin_user = session['regression-tool-username']

        return render_template('reports.html', home_menu = home_menu,
                               test_area_menu = test_area_menu, reports_menu = reports_menu, error = error_list,
                               latest_score_data = latest_score_data, previous_score_data = previous_score_data,
                               selected_platform = "",
                               selected_version = "",
                               selected_sub_version = "",
                               search_dd_platform = set(list(search_dd_platform)),
                               search_dd_version = set(list(search_dd_version)),
                               search_dd_sub_version = set(list(search_dd_sub_version)),
                               timestr = lambda: int(round(time.time() * 1000)),
                               data_series = data_series, cdets_info = cdets_info_slice,
                               component_wise = component_wise,
                               severity_wise = severity_wise,
                               platform_wise_score_breakup = platform_wise_score_breakup,
                               loggedin_user = loggedin_user, trend_xaxis_data = trend_xaxis_data, trend_yaxis_data = trend_yaxis_data,
                               trend_chart_main_title = trend_chart_main_title, trend_chart_legends = trend_chart_legends,
                               test_areas_for_breakup = test_areas_for_breakup,
                               trend_chart_categories = trend_chart_categories,trend_chart_new_legends = trend_chart_new_legends,
                               trend_chart_score_data = trend_chart_score_data,categories_rotation=-45)

#------------------------------------------------------------------------------------------------------------------------
@app.route('/reports_new')
def reports_new():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    error_list=[]
    home_menu = ''
    test_area_menu = ''
    reports_menu = 'class=active'
    latest_score_data = []
    platform_wise_score_breakup = {}
    previous_score_data = []
    search_dd_platform = []
    search_dd_version = []
    search_dd_sub_version = []
    loggedin_user = ''
    cdets_info_slice = []
    component_wise = []
    severity_wise = []
    trend_chart_main_title = 'Trend Chart : Platform Wise'
    trend_chart_legends = 1
    trend_chart_new_legends = 1 
    test_areas_for_breakup = {}
    trend_chart_width = 0
    trend_chart_categories = []
    trend_chart_score_data = []
    try:
        entity_collection = db_connection()
        distinct_platforms_db = entity_collection.ri_score.distinct("platform")
        existing_version = entity_collection.ri_score.distinct("version")
        trend_chart_main_title = "Regression Score Trend ( Platform and version wise latest score )"
        trend_chart_legends = 0     
        trend_chart_new_legends = 1     
        #---------------------------------------------------------------------------------------------------
        all_bugids = []
        for platform_idx,item_platform in enumerate(distinct_platforms_db):
            latest_score_by_platforms = entity_collection.ri_score.find({'platform':item_platform.lower()}).sort([("riscore_date", -1)]).limit(1)
            for idx,item in enumerate(latest_score_by_platforms):
                latest_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})
                platform_wise_score_breakup.update({item['platform'].lower():[{'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score']),'test_area':item['test_area']}]})
                cdets_array =  get_cdets_count(item['test_area'])
                for item in cdets_array:
                    all_bugids.append(item)                
                

            previous_score_by_platforms = entity_collection.ri_score.find({'platform':item_platform.lower()}).sort([("riscore_date", -1)]).skip(1).limit(1)
            for idx,item in enumerate(previous_score_by_platforms):
                previous_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})
                                 
#Start:Trend Chart Related==================================================================================================
        #for platform_idx,item_platform in enumerate(distinct_platforms_db):
            distinct_versions_db = entity_collection.ri_score.distinct('version',{'platform':item_platform.lower()})
            trend_chart_categories_temp = []                    
            for version_idx_idx,item_version in enumerate(distinct_versions_db):                
                subversions_label = []              
                trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':item_version.lower()}).sort([("riscore_date",-1)]).limit(1)
                if trend_chart_db_result.count() > 0 :
                    for idx,item in enumerate(trend_chart_db_result):
                        subversions_label.append(item['sub_version'])
                        trend_chart_score_data.append(float(item['score'])) 
                                                
                trend_chart_categories_temp.append({
                                            'name': item_version.upper(), # Versions 
                                            'categories': subversions_label # Sub Versions
                                          })
            trend_chart_categories.append({
                                            'name': item_platform.upper(), # Versions 
                                            'categories': trend_chart_categories_temp # Sub Versions
                                          })                                   
#End:Trend Chart Related==================================================================================================
        cdets_info = []
        cdets_info = entity_collection.bug_data.find({"Identifier":{"$in":all_bugids}})
        distinct_components = []
        distinct_severity = []
        for item in cdets_info:
            cdets_info_slice.append(item)
            distinct_components.append(item['Component'].lower())
            distinct_severity.append(item['Severity'].lower())

        for item in list(set(distinct_components)):
            component_wise.append({ 'name': item, 'y':distinct_components.count(item)})

        for item in list(set(distinct_severity)):
            severity_wise.append({ 'name': item, 'y':distinct_severity.count(item)})

#-------------------------------------------------------------------------------------------------------------------------------
# Platform Wise table
#-------------------------------------------------------------------------------------------------------------------------------
        for pwsb_key,pwsb_item in platform_wise_score_breakup.items():
            platform_wise_breakup = []
            ddts_info = []
            bug_ids_for_breakup = []
            test_area_array = pwsb_item[0]['test_area']
            score = pwsb_item[0]['score']
            version = pwsb_item[0]['version']
            sub_version = pwsb_item[0]['sub_version']
            for testarea in test_area_array:
                test_area_name_db = entity_collection.test_area.find({'_id':ObjectId(testarea['test_area_id'])},{'_id':0,'test_area':1})
                for area_name in test_area_name_db:
                    test_area_name = area_name['test_area']
                platform_wise_breakup.append({'area_score':testarea['score'],'area_name':test_area_name,'ddts':testarea['cdets'],'impact':testarea['comments']})
                if testarea['cdets']:
                    bug_ids_for_breakup.append(testarea['cdets'])

            ddts_info = entity_collection.bug_data.find({"Identifier":{"$in":bug_ids_for_breakup}})
            test_areas_for_breakup.update({pwsb_key:{'break_up':platform_wise_breakup,'ddts':ddts_info}})
#-------------------------------------------------------------------------------------------------------------------------------
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
        tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
        error_list.append({'Exception type and value':etype_value})
        error_list.append({'File name and line number':tb1})

    if 'regression-tool-username' in session:
        loggedin_user = session['regression-tool-username']

    return render_template('reports_new.html', home_menu = home_menu,test_area_menu = test_area_menu, reports_menu = reports_menu,
                           error = error_list,
                           latest_score_data = latest_score_data, previous_score_data = previous_score_data,
                           selected_platform = "",
                           selected_version = "",
                           selected_sub_version = "",
                           search_dd_platform = distinct_platforms_db,
                           search_dd_version = [],
                           search_dd_sub_version = [],
                           timestr = timestr,
                           cdets_info = cdets_info_slice,
                           component_wise = component_wise,
                           severity_wise = severity_wise,
                           platform_wise_score_breakup = platform_wise_score_breakup,
                           loggedin_user = loggedin_user,
                           trend_chart_main_title = trend_chart_main_title, trend_chart_legends = trend_chart_legends,
                           test_areas_for_breakup = test_areas_for_breakup,
                           trend_chart_categories = trend_chart_categories,trend_chart_new_legends = trend_chart_new_legends,
                           trend_chart_score_data = trend_chart_score_data,categories_rotation=-45)
                           
#------------------------------------------------------------------------------------------------------------------------
@app.route('/reports')
def reports():
    ri_scores_menu = ''
    our_team_menu = ''
    home_menu = ''
    test_area_menu = ''
    reports_menu = 'class=active'
    timestr = time.strftime("%Y%m%d-%H%M%S")
    error_list=[]
    app_user = ""
    try:
        entity_collection = db_connection()
        distinct_platforms_db = entity_collection.ri_score.distinct("platform")#-------------------------------------------------------------------------------------------------------------------------------
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
        tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
        error_list.append({'Exception type and value':etype_value})
        error_list.append({'File name and line number':tb1})

    if 'regression-tool-username' in session:
        app_user = session['regression-tool-username']

    print("loggedin_user : ",app_user)
    return render_template('reports_new_11.html', home_menu = home_menu, test_area_menu = test_area_menu, reports_menu = reports_menu, 
                           error = error_list, ri_scores_menu = ri_scores_menu, our_team_menu = our_team_menu,  
                           search_dd_platform = distinct_platforms_db,
                           search_dd_version = [],
                           search_dd_sub_version = [],
                           timestr = timestr, loggedin_user = app_user)                        
#------------------------------------------------------------------------------------------------------------------------

@app.route('/getReportsAjax', methods=['POST'])
def getReportsAjax():
    error_list=[]
    latest_score_data = []
    platform_wise_score_breakup = {}
    previous_score_data = []
    search_dd_platform = []
    search_dd_version = []
    loggedin_user = ''
    cdets_info_slice = []
    component_wise = []
    severity_wise = []
    trend_xaxis_data = []
    trend_chart_main_title = 'Trend Chart : Platform Wise'
    trend_chart_legends = 1
    trend_chart_new_legends = 1 
    test_areas_for_breakup = {}
    trend_chart_width = 0
    trend_chart_categories = []
    trend_chart_score_data = []
    selected_platform = request.form['platform'].strip().lower()
    selected_version = request.form['version'].strip().lower()
    selected_sub_version = request.form['sub_version'].strip().lower()
    platform = request.form['platform'].strip().lower()
    version = request.form['version'].strip().lower()
    sub_version = request.form['sub_version'].strip().lower()
    cdets_info = []
    try:
        entity_collection = db_connection()
#-----------------------------------------------------------------------------------------------------------------------------------------------
# all + value + none or all + value + all
#-----------------------------------------------------------------------------------------------------------------------------------------------
        if platform=="all" and version!="" and version!="all" and sub_version=="":
            print("Trend chart : Block 1")
            trend_chart_main_title = "Regression Score Trend ( %s )"%(version.upper())
            #For new chart==================================================================================================  
            distinct_platforms_db = entity_collection.ri_score.distinct('platform',{'version':version})
            for platform_idx,item_platform in enumerate(distinct_platforms_db):
                subversions_label = []              
                trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':version.lower()}).sort([("riscore_date",1)])
                if trend_chart_db_result.count() > 0 :
                    for idx,item in enumerate(trend_chart_db_result):
                        subversions_label.append(item['sub_version'])
                        trend_chart_score_data.append(float(item['score']))                                                     

                trend_chart_categories.append({
                                            'name': item_platform.upper(), # Versions 
                                            'categories': subversions_label # Sub Versions
                                          })
#-----------------------------------------------------------------------------------------------------------------------------------------------
# all + value + value
#-----------------------------------------------------------------------------------------------------------------------------------------------
        elif platform=="all" and version!="" and version!="all" and sub_version!="":
            print("Trend chart : Block 2")      
            trend_chart_main_title = "Regression Score Trend ( %s, %s )"%(version.upper(),sub_version.lower())
            trend_chart_legends = 0
            #For new chart==================================================================================================  
            distinct_platforms_db = entity_collection.ri_score.distinct('platform',{'version':version,'sub_version':sub_version.lower()})
            for platform_idx,item_platform in enumerate(distinct_platforms_db):             
                subversions_label = []              
                trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':version.lower(),'sub_version':sub_version.lower()}).sort([("riscore_date",1)])
                if trend_chart_db_result.count() > 0 :
                    for idx,item in enumerate(trend_chart_db_result):
                        subversions_label.append(sub_version.lower())
                        trend_chart_score_data.append(float(item['score']))                                                     

                trend_chart_categories.append({
                                            'name': item_platform.upper()+' - '+version, # Versions 
                                            'categories': subversions_label # Sub Versions
                                          })
#-----------------------------------------------------------------------------------------------------------------------------------------------
# all + none + none
#-----------------------------------------------------------------------------------------------------------------------------------------------
        elif platform=="all" and version=="" and sub_version=="":
            print("Trend chart : Block 3")      
            trend_chart_main_title = "Regression Score Trend ( Platform Wise Latest Score )"
            trend_chart_legends = 0
            #For new chart==================================================================================================  
            distinct_platforms_db = entity_collection.ri_score.distinct('platform')
            trend_chart_new_legends = 1 
            for platform_idx,item_platform in enumerate(distinct_platforms_db):
                distinct_versions_db = entity_collection.ri_score.distinct('version',{'platform':item_platform.lower()})
                trend_chart_categories_temp = []                    
                for version_idx_idx,item_version in enumerate(distinct_versions_db):                
                    subversions_label = []              
                    trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':item_version.lower()}).sort([("riscore_date",1)])
                    if trend_chart_db_result.count() > 0 :
                        for idx,item in enumerate(trend_chart_db_result):
                            subversions_label.append(item['sub_version'])
                            trend_chart_score_data.append(float(item['score'])) 
                                                    
                    trend_chart_categories_temp.append({
                                                'name': item_version.upper(), # Versions 
                                                'categories': subversions_label # Sub Versions
                                              })
                trend_chart_categories.append({
                                                'name': item_platform.upper(), # Versions 
                                                'categories': trend_chart_categories_temp # Sub Versions
                                              })
#-----------------------------------------------------------------------------------------------------------------------------------------------
# value + none + none or value + none + all or value + all + none or value + all + all
#-----------------------------------------------------------------------------------------------------------------------------------------------
        elif platform!="all" and ( version=="" or version=="all" ) and ( sub_version=="" or sub_version=="all" ):
            print("Trend chart : Block 4")      
            trend_chart_main_title = "Regression Score Trend ( %s )"%(platform.upper())
            distinct_versions_db = entity_collection.ri_score.distinct("version",{'platform':platform.lower()})
            for version_idx,item_version in enumerate(distinct_versions_db):
                subversions_label = []              
                trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':item_version.lower()}).sort([("riscore_date",1)])
                if trend_chart_db_result.count() > 0 :
                    for idx,item in enumerate(trend_chart_db_result):
                        subversions_label.append(item['sub_version'])
                        trend_chart_score_data.append(float(item['score']))                                                     

                trend_chart_categories.append({
                                            'name': item_version.upper(), # Versions 
                                            'categories': subversions_label # Sub Versions
                                          })
#-----------------------------------------------------------------------------------------------------------------------------------------------
# value + all + value
#-----------------------------------------------------------------------------------------------------------------------------------------------
        elif platform!="all" and version=="all" and sub_version!="" and sub_version!="all":
            print("Trend chart : Block 5")
            categories_legends = 0          
            trend_chart_main_title = "Regression Score Trend ( %s, %s, %s )"%(platform.upper(),version.upper(),sub_version.lower())
            distinct_versions_db = entity_collection.ri_score.distinct("version",{'platform':platform.lower(),'sub_version':sub_version.lower()})
            for version_idx,item_version in enumerate(distinct_versions_db):
                subversions_label = []              
                trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':item_version.lower(),'sub_version':sub_version.lower()}).sort([("riscore_date",1)])
                if trend_chart_db_result.count() > 0 :
                    for idx,item in enumerate(trend_chart_db_result):
                        subversions_label.append(item['sub_version'])
                        trend_chart_score_data.append(float(item['score']))                                                     

                trend_chart_categories.append(item_version.upper())                                       
#-----------------------------------------------------------------------------------------------------------------------------------------------
# value + value + none or value + value + all
#-----------------------------------------------------------------------------------------------------------------------------------------------
        elif platform!="all" and version!="" and version!="all" and ( sub_version=="" or sub_version=="all"):
            print("Trend chart : Block 6")      
            if sub_version=="all":
                trend_chart_main_title = "Regression Score Trend ( %s, %s, All Sub Versions )"%(platform.upper(),version)
            else:
                trend_chart_main_title = "Regression Score Trend ( %s, %s )"%(platform.upper(),version)

            trend_chart_legends = 0
            trend_chart_categories = []
            trend_chart_score_data = []                             
            subversions_label = []              
            trend_chart_db_result = entity_collection.ri_score.find({'platform':platform.lower(),'version':version.lower()}).sort([("riscore_date",1)])
            if trend_chart_db_result.count() > 0 :
                for idx,item in enumerate(trend_chart_db_result):
                    subversions_label.append(item['sub_version'])
                    trend_chart_score_data.append(float(item['score']))
                    trend_chart_categories.append(item['sub_version'])        
        #------------------------------------------------------------------------------------------------------------------        
        # value + value + value
        #------------------------------------------------------------------------------------------------------------------         
        elif platform!="all" and version!="" and version!="all" and sub_version!="" and sub_version!="all":
            print("Trend chart : Block 7")      
            trend_chart_main_title = "Regression Score Trend ( %s, %s, %s )"%(selected_platform.upper(),selected_version.lower(),selected_sub_version.lower())
            trend_chart_legends = 0 
            trend_chart_new_legends = 0             
            trend_chart_categories = []
            trend_chart_score_data = []                             
            trend_chart_db_result = entity_collection.ri_score.find({'platform':selected_platform.lower(),'version':selected_version.lower(),'sub_version':selected_sub_version.lower()}).sort([("riscore_date",1)])
            if trend_chart_db_result.count() > 0 :
                for idx,item in enumerate(trend_chart_db_result):
                    trend_chart_score_data.append(float(item['score'])) 

#-----------------------------------------------------------------------------------------------------------------------------------------------
# all + none + none
#-----------------------------------------------------------------------------------------------------------------------------------------------
        elif platform=="all" and version=="all" and sub_version=="all":
            print("Trend chart : Block 8")   
            # Run aggregate query
            platformwise_latest_record = entity_collection.ri_score.aggregate([

                { "$sort": { "riscore_date": -1 } },

                { "$group": {
                    "_id": "$platform",
                    "results": {
                        "$push": {
                            "platform": "$platform",            
                            "version": "$version", 
                            "sub_version": "$sub_version",
                            "riscore_date": "$riscore_date",                
                            "score": "$score"
                        }
                    },
                    "latest": { 
                        "$first": {
                            "platform": "$platform",            
                            "version": "$version", 
                            "sub_version": "$sub_version",
                            "riscore_date": "$riscore_date",                
                            "score": "$score"
                        }
                    }
                }},
                {'$project': {
                    'platform': '$_id.platform',
                    '_id': 0,
                    'latest':1                  
                }}  
            
            ])
            for item_ in platformwise_latest_record:
                print(item_['latest'])          
            #===============================================================================================================            
            trend_chart_main_title = "Regression Score Trend ( Platform Wise Latest Score )"
            #For new chart==================================================================================================  
            distinct_platforms_db = entity_collection.ri_score.distinct('platform')
            trend_chart_new_legends = 1 
            for platform_idx,item_platform in enumerate(distinct_platforms_db):
                distinct_versions_db = entity_collection.ri_score.distinct('version',{'platform':item_platform.lower()})
                trend_chart_categories_temp = []                    
                for version_idx_idx,item_version in enumerate(distinct_versions_db):                
                    subversions_label = []              
                    trend_chart_db_result = entity_collection.ri_score.find({'platform':item_platform.lower(),'version':item_version.lower()}).sort([("riscore_date",-1)]).limit(1)
                    if trend_chart_db_result.count() > 0 :
                        for idx,item in enumerate(trend_chart_db_result):
                            subversions_label.append(item['sub_version'])
                            trend_chart_score_data.append(float(item['score'])) 
                                                    
                    trend_chart_categories_temp.append({
                                                'name': item_version.upper(), # Versions 
                                                'categories': subversions_label # Sub Versions
                                              })
                trend_chart_categories.append({
                                                'name': item_platform.upper(), # Versions 
                                                'categories': trend_chart_categories_temp # Sub Versions
                                              })                    
                    
        #End: Trend Chart ==================================================================================================
            
        query_str_array = []
        if selected_platform!="" and selected_platform!="all":
            query_str_array.append({'platform':selected_platform.lower()})
        if selected_version!="" and selected_version!="all":
            query_str_array.append({'version':selected_version.lower()})
        if selected_sub_version!="" and selected_sub_version!="all":
            query_str_array.append({'sub_version':selected_sub_version.lower()})
        query_str = formQueryString(query_str_array)
        
        all_bugids = []
        if selected_platform!="" and selected_platform!="all":
            latest_score_by_platforms = entity_collection.ri_score.find(query_str).sort([("riscore_date", -1)]).limit(1)
            for item in latest_score_by_platforms:
                latest_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})
                platform_wise_score_breakup.update({item['platform'].lower():[{'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score']),'test_area':item['test_area']}]})
                cdets_array =  get_cdets_count(item['test_area'])
                for item in cdets_array:
                    all_bugids.append(item)
                        
            previous_score_by_platforms = entity_collection.ri_score.find(query_str).sort([("riscore_date", -1)]).skip(1).limit(1)
            for item in previous_score_by_platforms:
                previous_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})
                
        elif selected_platform=="all":
            distinct_platforms_db = entity_collection.ri_score.distinct("platform")
            for platform_idx,item_platform in enumerate(distinct_platforms_db):
                query_str['platform']=item_platform
                latest_score_by_platforms = entity_collection.ri_score.find(query_str).sort([("riscore_date", -1)]).limit(1)
                for item in latest_score_by_platforms:
                    latest_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})
                    platform_wise_score_breakup.update({item['platform'].lower():[{'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score']),'test_area':item['test_area']}]})
                    cdets_array =  get_cdets_count(item['test_area'])
                    for item in cdets_array:
                        all_bugids.append(item)                 
            
                previous_score_by_platforms = entity_collection.ri_score.find(query_str).sort([("riscore_date", -1)]).skip(1).limit(1)
                for item in previous_score_by_platforms:
                    previous_score_data.append({'platform':item['platform'].upper(),'version':item['version'],'sub_version':item['sub_version'],'score':float(item['score'])})
        print("all_bugids : ",all_bugids)   
        cdets_info = entity_collection.bug_data.find({"Identifier":{"$in":list(set(all_bugids))}})
        distinct_components = []
        distinct_severity = []
        for item in cdets_info:
            cdets_info_slice.append(item)
            distinct_components.append(item['Component'].lower())
            distinct_severity.append(item['Severity'].lower())

        for item in list(set(distinct_components)):
            component_wise.append({ 'name': item, 'y':distinct_components.count(item)})

        for item in list(set(distinct_severity)):
            severity_wise.append({ 'name': item, 'y':distinct_severity.count(item)})
        #-------------------------------------------------------------------------------------------------------------------------------
        # Platform Wise table
        #-------------------------------------------------------------------------------------------------------------------------------
        for pwsb_key,pwsb_item in platform_wise_score_breakup.items():
            platform_wise_breakup = []
            ddts_info = []
            bug_ids_for_breakup = []
            test_area_array = pwsb_item[0]['test_area']
            score = pwsb_item[0]['score']
            version = pwsb_item[0]['version']
            sub_version = pwsb_item[0]['sub_version']
            for testarea in test_area_array:
                if "test_area" in testarea and testarea['test_area']!="":
                    test_area_name = testarea['test_area']
                elif "test_area" in testarea and testarea['test_area']=="":
                    test_area_name = testarea['test_area_id']                   
                else:
                    test_area_name = testarea['test_area_id']
                    
                platform_wise_breakup.append({'area_score':testarea['score'],'area_name':test_area_name,'ddts':testarea['cdets'],'impact':testarea['comments']})
                if testarea['cdets']:
                    bug_ids_for_breakup.append(testarea['cdets'])

            if len(bug_ids_for_breakup)>0:
                uniquebug_ids=get_splitted_cdets(bug_ids_for_breakup)
                ddts_info = entity_collection.bug_data.find({"Identifier":{"$in":uniquebug_ids}})
            
            test_areas_for_breakup.update({pwsb_key:{'break_up':platform_wise_breakup,'ddts':ddts_info}})  
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
        tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
        error_list.append({'Exception type and value':etype_value})
        error_list.append({'File name and line number':tb1})

    return render_template('getReportsAjaxRowOne.html', error = error_list,latest_score_data = latest_score_data, previous_score_data = previous_score_data,
                           cdets_info = cdets_info_slice,component_wise = component_wise,severity_wise = severity_wise,                          
                           trend_chart_main_title = trend_chart_main_title,platform_wise_score_breakup = platform_wise_score_breakup,
                           test_areas_for_breakup = test_areas_for_breakup,trend_chart_categories = trend_chart_categories, trend_chart_new_legends = trend_chart_new_legends,
                           trend_chart_score_data = trend_chart_score_data,trend_chart_width_new = len(trend_chart_score_data)*33
                           ,categories_rotation=0)
#------------------------------------------------------------------------------------------------------------------------
@app.route('/isValidCDETS', methods=['POST'])
def isValidCDETS():
    cdets = request.form['cdets']
    cdets_valid_invalid="VALID"
    splitted_cdets=cdets.split(';')
    if len(splitted_cdets)>1:
        for entry in cdets.split(';'):
            if entry != '':
                ddts_data = get_new_ddts_attributes(entry)
                if ddts_data and ddts_data!="api_error" and ddts_data!="api_bugid_error":
                    cdets_valid_invalid="VALID"
                else:
                    cdets_valid_invalid="INVALID"
    else:
        ddts_data = get_new_ddts_attributes(cdets)
        if ddts_data and ddts_data!="api_error" and ddts_data!="api_bugid_error":
            cdets_valid_invalid="VALID"
        else:
            cdets_valid_invalid="INVALID"

    return cdets_valid_invalid
#------------------------------------------------------------------------------------------------------------------------
@app.route('/getVersionsForDropDown', methods=['POST'])
def getVersionsForDropDown():
    platform = request.form['platform']
    dd_values = '<option value="">Select Version</option>'
    entity_collection = db_connection()
    distinct_versions_db = ''   
    if platform.lower() == "all":   
        distinct_versions_db = entity_collection.ri_score.distinct("version")
    else:
        distinct_versions_db = entity_collection.ri_score.distinct("version",{'platform':platform.lower()})
        
    for item in distinct_versions_db:
        dd_values += '<option value="%s">%s</option>'%(item,item.upper())

    if platform.lower() != "all":   
        dd_values += '<option value="all">All</option>'
    
    return dd_values    
#------------------------------------------------------------------------------------------------------------------------
@app.route('/getSubVersionsForDropDown', methods=['POST'])
def getSubVersionsForDropDown():
    platform = request.form['platform']
    version = request.form['version']
        
    dd_values = '<option value="">Select Sub Version</option>'
    entity_collection = db_connection()
    distinct_subversions_db = ''    
    if platform.lower() != "all" and version.lower() == "all":  
        distinct_subversions_db = entity_collection.ri_score.distinct("sub_version",{'platform':platform.lower()})
    elif platform.lower() == "all" and version.lower() == "all":    
        distinct_subversions_db = entity_collection.ri_score.distinct("sub_version")
    elif platform.lower() == "all" and version.lower() != "all":    
        distinct_subversions_db = entity_collection.ri_score.distinct("sub_version",{'version':version.lower()})        
    else:
        distinct_subversions_db = entity_collection.ri_score.distinct("sub_version",{'platform':platform.lower(),'version':version.lower()})    
    
    for item in distinct_subversions_db:
        dd_values += '<option value="%s">%s</option>'%(item,item.upper())
        
    if platform.lower() != "all":   
        dd_values += '<option value="all">All</option>'     
    
    return dd_values     

@app.route('/regression-backup')
def dbbackup_router():
    home_menu = ''
    test_area_menu = 'class=active'
    reports_menu = ''
    error_list=[]
    user_message = ''
    dirs = ''
    try:
        entity_collection = db_connection()
        fileRoot = app.config['BACKUP_FOLDER']
        dirs = os.listdir( fileRoot+"/db" )
        today_date=datetime.datetime.today().strftime('%Y-%m-%d')
        backup_date_list=[]
        for file_name in dirs:
            file_name_array=file_name.split("_")
            file_name_date=file_name_array[1]
            file_name_date_array=file_name_date.split(".")
            backup_date_list.append(file_name_date_array[0])

        backup_date_list=list(set(backup_date_list))
        if today_date not in backup_date_list:
            riscore_results_db_records = entity_collection.ri_score.find({})
            testarea_db_records = entity_collection.test_area.find({})

            riscore_results = []
            for result in riscore_results_db_records:
                riscore_results.append(result)

            json_testarea = []
            for result in testarea_db_records:
                json_testarea.append(result)

            results_data = json.dumps(riscore_results, default=json_util.default)
            with open(fileRoot+"/db/riscores_"+today_date+".json","w") as f:
                f.write(results_data)

            urls_data = json.dumps(json_testarea, default=json_util.default)
            with open(fileRoot+"/db/testareas_"+today_date+".json","w") as f:
                f.write(urls_data)

            dirs = os.listdir( fileRoot+"/db" )
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
        tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
        error_list.append({'Exception type and value':etype_value})
        error_list.append({'File name and line number':tb1})

    if 'regression-tool-username' in session:
        return render_template('regression-db-backup.html', file_list=dirs, loggedin_user = session['regression-tool-username'], error = error_list, home_menu = home_menu, test_area_menu = test_area_menu, reports_menu = reports_menu)
    else:
        return redirect(url_for('login'))

@app.route('/loan-int-management', methods=['post', 'get'])
def loan_int_management():
    home_menu = ''
    test_area_menu = ''
    loan_int_menu = 'class=active'  
    reports_menu = ''
    input_success = ''
    error_list=[]
    loan_int_list = []
    user_message = ''   
        
    if request.method == 'POST':
        try:
            test_area = request.form['test_area'].strip()
            user_id = request.form['user_id'].strip()           
            form_input_array = {'test_area': test_area,'user_id': user_id,'used_status':0}      
            entity_collection = db_connection()
            entity_collection.test_area.insert(form_input_array)
            session['test-area-user-message']='Test area added successfully'
            loan_int_list=entity_collection.test_area.find({'user_id':session['regression-tool-username']})         
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0] 
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
    else:
        try:
            entity_collection = db_connection()
            loan_int_list=entity_collection.loan_int_mgt.find({})
            loan_int_list_array = []
            p_os_total = 0
            int_month_total = 0            
            for item in loan_int_list:
                int_month = item['p_os'] * (item['roi']/100) * (1/12)           
                loan_int_list_array.append({'issuer':item['issuer'],
                                            'p_os':item['p_os'],
                                            'roi':item['roi'],
                                            'int_for_next_month':math.ceil(int_month)})
                p_os_total+=item['p_os']
                int_month_total+=int_month              
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0] 
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            
    if 'test-area-user-message' in session:
        user_message = session['test-area-user-message']
        session.pop('test-area-user-message', None)     
            

    return render_template('loan-int-management.html',user_message = user_message, 
    loan_int_list = loan_int_list_array, p_os_total = math.ceil(p_os_total), int_month_total = math.ceil(int_month_total), 
    input_success = input_success, 
    error = error_list, home_menu = home_menu, test_area_menu = test_area_menu, reports_menu = reports_menu, loan_int_menu = loan_int_menu) 

#####################################
#======Helper functions start=======#
#####################################

def py_mail_new(SUBJECT, BODY, TO, FROM):
    """With this function we send out our html email"""

    TOADDR = [TO]
    #CCADDR = ['jthanisl@cisco.com']
    # Create message container - the correct MIME type is multipart/alternative here!
    MESSAGE = MIMEMultipart('alternative')
    MESSAGE['subject'] = SUBJECT
    MESSAGE['To'] = TO
    #MESSAGE['Cc'] =  'jthanisl@cisco.com'
    MESSAGE['From'] = FROM
    MESSAGE.preamble = """
Your mail reader does not support the report format.
Please visit us <a href="http://www.mysite.com">online</a>!"""

    # Record the MIME type text/html.
    HTML_BODY = MIMEText(BODY, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
       # the HTML message, is best and preferred.
    MESSAGE.attach(HTML_BODY)

    # The actual sending of the e-mail
    server = smtplib.SMTP('email.cisco.com')

    # Print debugging output when testing
    if __name__ == "__main__":
        server.set_debuglevel(1)

    # Credentials (if needed) for sending the mail
    #password = "mypassword"

    #server.starttls()
    #server.login(FROM,password)
    server.sendmail(FROM, TOADDR, MESSAGE.as_string())
    server.quit()

def trigger_mail(user_id,token):

    headline = "REGRESSION TOKEN - To login in Regression Dashboard"
    TEXT = """<head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
              <title>html title</title>
              <style type="text/css" media="screen">
                table{
                    background-color: #AAD373;
                    empty-cells:hide;
                }
                td.cell{
                    background-color: white;
                    padding:8px;
                }
              </style>
            </head>
            <body>
              <p>Hello,<br/><br/>
               As requested, </p>
              <table style="border: blue 1px solid;">
                <tr><th class="cell">User ID</th><th class="cell">Regression Token</th></tr>
                <tr><td class="cell">"""+str(user_id)+"""</td><td class="cell">"""+str(token)+"""</td></tr>
              </table>
              <br/><br/><p> Please use the below link to login. <br/><br/>
                <a href="http://x19-dell-rasa:8833/login">http://x19-dell-rasa:8833/login</a>


              </p>Regards,<br/>IDT / Tools-Infra-Regression Dev Team
            </body>"""
        #------------------------------------------------------------------------------------------------------------
    TO = '%s@cisco.com'%user_id
    FROM = 'jthanisl@cisco.com'
    py_mail_new(headline, TEXT, TO, FROM)

def print_string_format(printable_array):
    printable_array = ','.join(printable_array)
    print(printable_array)

def print_json_format(printable_array):
    print(json.dumps(printable_array, indent=4, sort_keys=True))

def db_connection():
    client = MongoClient('localhost:27017') # Localhost
    conn_string = client.regression_score
    return conn_string
#####################################
#======Main app start===============#
#####################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8834, debug=True)