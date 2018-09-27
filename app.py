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

    if 'dues-user-message' in session:
        user_message = session['dues-user-message']
        session.pop('dues-user-message', None)

    if 'regression-tool-username' in session:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        current_dues_status=entity_collection.dues.aggregate([
                                                        { 
                                                            '$group': { 
                                                                '_id': "$payment_status", 
                                                                'bill_amount': { 
                                                                    '$sum': "$bill_amount" 
                                                                } 
                                                            } 
                                                        },
                                                        {'$project': {
                                                                    '_id':0,
                                                                    'payment': '$_id',
                                                                    'bill_amount': '$bill_amount'
                                                                    }
                                                        }
                                                    ])      
        return render_template('home.html', dues_summary = current_dues_status , dues_list = ri_score_list,
        input_success = input_success, error = error_list, timestr = timestr, user_message = user_message,
        home_menu = home_menu, test_area_menu = test_area_menu, reports_menu = reports_menu,loggedin_user = session['regression-tool-username'])
    else:
        return redirect(url_for('login'))
        
@app.route('/dues-edit', methods=['post', 'get'])
def dues_edit():
    home_menu = 'class=active'
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
            edit_db_result = entity_collection.dues.find({'_id': ObjectId(tid)})
            if edit_db_result.count() == 0 :
                user_message = 'Record is not in database'
            else:
                for item in edit_db_result:
                    editable_ri_score = item
                    bill_date = item['bill_date'].strftime("%m/%d/%Y")
                    due_date = item['due_date'].strftime("%m/%d/%Y")                      
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})

    if 'regression-tool-username' in session:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        return render_template('dues-edit.html', timestr = timestr, editable_ri_score = editable_ri_score, bill_date=bill_date, 
        due_date=due_date, user_message = user_message, loggedin_user = session['regression-tool-username'], error = error_list, 
        home_menu = home_menu,reports_menu = reports_menu)
    else:
        return redirect(url_for('login'))
        
@app.route('/dues-update', methods=['post', 'get'])
def ri_score_update():
    error_list=[]
    update_db_result = ''
    if request.method == 'POST' and 'regression-tool-username' in session:
        try:
            entity_collection = db_connection()     
            edit_id = request.form['edit_id']   
            biller = request.form['biller'].strip().lower()
            payment_status = request.form['payment_status'].strip().lower()
            bill_amount = float(request.form['bill_amount'].strip())            
            bill_date = datetime.datetime.strptime(request.form['bill_date'].strip(),"%m/%d/%Y")
            due_date = datetime.datetime.strptime(request.form['due_date'].strip(),"%m/%d/%Y")            
            update_data = {'payment_status':payment_status,'biller': biller.lower(),'bill_amount': bill_amount,'bill_date': bill_date,'due_date': due_date}
            update_db_result = entity_collection.dues.update({'_id': ObjectId(edit_id)},{'$set':update_data})
            if update_db_result['nModified'] == 1:
                session['dues-user-message'] = 'DUE modified successfully.'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            session['dues-user-message'] = error_list
    return redirect(url_for('home'))        


@app.route('/dues-remove', methods=['post', 'get'])
def dues_remove():
    error_list=[]
    if request.method == 'GET' and 'regression-tool-username' in session:
        try:
            tid = request.args['del_id']
            entity_collection = db_connection()
            db_result=entity_collection.dues.remove({'_id': ObjectId(tid)})
            session['ri-score-user-message'] = 'Due deleted successfully'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            session['ri-score-user-message'] = error_list
    return redirect(url_for('home'))
    
@app.route('/loan-int-management', methods=['post', 'get'])
def loan_int_management():
    home_menu = ''
    loan_int_menu = 'class=active'  
    reports_menu = ''
    input_success = ''
    error_list=[]
    loan_int_list = []
    user_message = ''   
        
    if request.method == 'POST':
        try:
            edit_id = request.form['edit_id']
            p_os = request.form['p_os'].strip()
            form_input_array = {'p_os': p_os}      
            entity_collection = db_connection()
            update_db_result = entity_collection.dues.update({'_id': ObjectId(edit_id)},{'$set':form_input_array})
            if update_db_result['nModified'] == 1:
                session['loan-details-user-message'] = 'Loan details modified successfully.'
            loan_int_list=entity_collection.loan_details.find({})         
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0] 
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
    else:
        try:
            entity_collection = db_connection()
            loan_int_list=entity_collection.loan_details.find({})
            loan_int_list_array = []
            p_os_total = 0
            int_month_total = 0            
            for item in loan_int_list:
                updated_on = ''
                if 'updated_on' in item: 
                    updated_on = item['updated_on']         
                int_month = item['p_os'] * (item['roi']/100) * (1/12)           
                loan_int_list_array.append({'_id':item['_id'],'issuer':item['issuer'],
                                            'p_os':item['p_os'],
                                            'roi':item['roi'],
                                            'int_for_next_month':math.ceil(int_month),
                                            'updated_on':updated_on})
                p_os_total+=item['p_os']
                int_month_total+=int_month              
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0] 
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            
    if 'loan-details-user-message' in session:
        user_message = session['loan-details-user-message']
        session.pop('loan-details-user-message', None)     
            

    return render_template('loan-int-management.html',user_message = user_message, 
    loan_int_list = loan_int_list_array, p_os_total = math.ceil(p_os_total), int_month_total = math.ceil(int_month_total), 
    input_success = input_success, 
    error = error_list, home_menu = home_menu, reports_menu = reports_menu, loan_int_menu = loan_int_menu) 

@app.route('/loan-details-edit', methods=['post', 'get'])
def loan_details_edit():
    home_menu = ''
    loan_details_menu = 'class=active'
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
            edit_db_result = entity_collection.loan_details.find({'_id': ObjectId(tid)})
            if edit_db_result.count() == 0 :
                user_message = 'Record is not in database'
            else:
                for item in edit_db_result:
                    editable_ri_score = item
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})

    if 'regression-tool-username' in session:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        return render_template('loan-details-edit.html', timestr = timestr, editable_ri_score = editable_ri_score, user_message = user_message, loggedin_user = session['regression-tool-username'], error = error_list, 
        home_menu = home_menu,loan_details_menu = loan_details_menu, reports_menu = reports_menu)
    else:
        return redirect(url_for('login')) 

@app.route('/loan-details-update', methods=['post', 'get'])
def loan_details_update():
    error_list=[]
    update_db_result = ''
    if request.method == 'POST' and 'regression-tool-username' in session:
        try:
            entity_collection = db_connection()     
            edit_id = request.form['edit_id']
            p_os = float(request.form['p_os'].strip())           
            update_data = {'p_os':p_os,'updated_on':datetime.datetime.now()}
            update_db_result = entity_collection.loan_details.update({'_id': ObjectId(edit_id)},{'$set':update_data})
            if update_db_result['nModified'] == 1:
                session['loan-details-user-message'] = 'Loan Details modified successfully.'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
            tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
            error_list.append({'Exception type and value':etype_value})
            error_list.append({'File name and line number':tb1})
            session['loan-details-user-message'] = error_list
    return redirect(url_for('loan_int_management'))     
    
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
    if 'regression-tool-username' in session:
        app_user = session['regression-tool-username']
    return render_template('reports.html', home_menu = home_menu, test_area_menu = test_area_menu, reports_menu = reports_menu, 
                           error = error_list, ri_scores_menu = ri_scores_menu, our_team_menu = our_team_menu,timestr = timestr, loggedin_user = app_user)                        
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
    selected_biller = request.form['biller'].strip().lower()
    try:
        entity_collection = db_connection()
        current_dues_status=entity_collection.dues.aggregate([
                                                        { 
                                                            '$group': { 
                                                                '_id': "$payment_status", 
                                                                'bill_amount': { 
                                                                    '$sum': "$bill_amount" 
                                                                } 
                                                            } 
                                                        },
                                                        {'$project': {
                                                                    '_id':0,
                                                                    'payment': '$_id',
                                                                    'bill_amount': '$bill_amount'
                                                                    }
                                                        }
                                                    ])
        for item in current_dues_status:
            component_wise.append({ 'name': item['payment'], 'y':item['bill_amount']})
        print(component_wise)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
        tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
        error_list.append({'Exception type and value':etype_value})
        error_list.append({'File name and line number':tb1})

    return render_template('getReportsAjaxRowOne.html', error = error_list,component_wise = component_wise) 


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

@app.route('/jjapp-backup')
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
            riscore_results_db_records = entity_collection.dues.find({})
            testarea_db_records = entity_collection.loan_details.find({})

            riscore_results = []
            for result in riscore_results_db_records:
                riscore_results.append(result)

            json_testarea = []
            for result in testarea_db_records:
                json_testarea.append(result)

            results_data = json.dumps(riscore_results, default=json_util.default)
            with open(fileRoot+"/db/dues_"+today_date+".json","w") as f:
                f.write(results_data)

            urls_data = json.dumps(json_testarea, default=json_util.default)
            with open(fileRoot+"/db/loan_details_"+today_date+".json","w") as f:
                f.write(urls_data)

            dirs = os.listdir( fileRoot+"/db" )
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        etype_value = (traceback.format_exception_only(exc_type, exc_value))[0]
        tb1 ='<br>'.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2])))
        error_list.append({'Exception type and value':etype_value})
        error_list.append({'File name and line number':tb1})

    if 'regression-tool-username' in session:
        return render_template('db-backup.html', file_list=dirs, loggedin_user = session['regression-tool-username'], error = error_list, home_menu = home_menu, test_area_menu = test_area_menu, reports_menu = reports_menu)
    else:
        return redirect(url_for('login'))



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