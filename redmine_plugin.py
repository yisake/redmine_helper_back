#encoding=utf-8
from flask import Flask,jsonify, request,Response
from redmine import Redmine
import json
import os
import traceback
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
redmine_url='http://redmine.fangdd.net/'
redmine=Redmine(redmine_url)
filepath=[]
#project_set=redmine.project.all(offset=1,limit=1000)

@app.route('/login' ,methods=['GET' ,'POST'])
def login():
    global redmine
    global redmine_url
    print request.form
    #print request.form['name']
    #print request.form.get('name')
    #print request.form.getlist('name')
    #print request.form.get('nickname', default='little apple')
    #print request.args
    username=request.form.get('username')
    password=request.form.get('password')
    if request.method=='POST':
        redmine = Redmine(redmine_url, username=username, password=password)
        try:
            redmine.auth()
            print 'Auth OK'
            return jsonify(result='y')
        except Exception:
            print 'Auth NOK'
            return jsonify(result='n')
    else:
        return jsonify(result='Redirect to Login in page')

@app.route('/getAllProjects' )
def get_all_projects():
    #project = redmine.project.get('vacation')
    global redmine_url
    print request.form    
    ps=redmine.project.all(offset=1,limit=1000)
    ps_list=[ ]
    print 'start to get '
    for pro in ps:
        ps_list.append(
                       {
                        'project_name':pro.name,
                        'project_id':str(pro.id),
                        }
                       )
    return Response(json.dumps(ps_list),mimetype='content-type/application/json' )

@app.route('/getProjectMembers' ,methods=['POST']) 
def get_project_members():
    global redmine
    print request.form
    project_id=request.form.get('projectid' )
    memberships = redmine.project_membership.filter(project_id=project_id)
    member_list=[ ]
    for id in range(0,memberships.__len__()):
        member_list.append({
                            "username" : memberships[id].user.name,
                            "userid": memberships[id].user.id
                            })
    return Response(json.dumps(member_list),mimetype='content-type/application/json' )

def allowed_file(filename):
    return '.' in filename and \
      filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload' , methods=['GET' , 'POST' ])
def upload():
    print request.form
    print request.files
    filenames = [ ]
    global filepath
    filepath=[ ]
    #uploaded_files = request.files.getlist("file[]" )
    uploaded_files = request.files.getlist("attachment" )
    print uploaded_files
    for upload_file in uploaded_files:
        upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'],upload_file.filename))
        uploadspath=os.path.join(app.config['UPLOAD_FOLDER'],upload_file.filename)
        filepath.append(os.path.join(os.getcwd(),uploadspath))
        filenames.append(upload_file.filename)
    print filepath
    return jsonify(result='y' )

'''
@summary: upload_file_demo:
@demo: one file
files={'image01':open('D:/Git/customer_side/testSuite.py','rb')}
s=requests.post('http://127.0.0.1:5000/uploadDemo',files=files)

@demo: multiple files
files={'image01':open('D:/Git/customer_side/testSuite.py','rb'),'image02':open('D:/Git/customer_
side/README.txt','rb')}
'''
@app.route('/uploadDemo' ,methods=['GET' , 'POST' ])
def uploadDemo():
    print request.form
    upload_file = request.files['image01']
    if upload_file:
        #filename = secure_filename(upload_file.filename)
        filename = upload_file.filename
        print filename
        upload_file.save('./' +filename)
        return 'hello, '+request.form.get('name', 'little apple')+'. success'
    else:
        return 'hello, '+request.form.get('name', 'little apple')+'. failed'


'''
@demo: create issue with local files
r=Redmine('http://redmine.fangdd.net/',username='huangfuchunfeng',password='fangdd1234')
issue = r.issue.create(project_id='443', 
subject='Vacation', 
tracker_id=1, 
description='test', 
status_id=1, 
priority_id=10, 
assigned_to_id=342,
custom_fields=[{
            "id": 1,
            "value": u"\u4e00\u822c"
        }, {
            "id": 3,
            "value": u"\u662f"
        }, {
            "id": 4,
            "value": u"\u4ee3\u7801\u9519\u8bef"
        }, {
            "id": 6,
            "value": u"\u6d4b\u8bd5\u73af\u5883"
        }],
uploads=[{'path': 'D:/Git/customer_side/testSuite.py','filename':'testSuite.py'}, {'path': 'D:/Git/customer_side/README.txt','filename':'README.txt'}])
'''
@app.route('/createIssue' ,methods=['POST' ] )
def create_issue():
    global redmine_url
    global filepath
    global redmine
    print filepath
    print request.form
    uploads=[]
    if filepath==[]:
        uploads=[]
    else:
        for item in filepath:
            uploads.append({
                            'path': item ,
                            'filename': item,
                            })
    print uploads
    username=request.form.get('login')
    password=request.form.get('password')
    redmine=Redmine(redmine_url, username=username, password=password)
    projectid=request.form.get('projectid')
    subject=request.form.get('subject')
    tracker_id=request.form.get('track')
    description=request.form.get('description')
    #status_id=request.form.get('status_id')
    priority_id=request.form.get('priority')
    assigned_to_id=request.form.get('assigneeid')
    severity=request.form.get('severity')
    bugtype=request.form.get('type')
    reappear=request.form.get('reappear')
    environment=request.form.get('environment')
    try:
        redmine.issue.create(project_id=projectid, 
subject=subject, 
tracker_id=int(tracker_id), 
description=description, 
status_id=int(1), 
priority_id=priority_id, 
assigned_to_id=int(assigned_to_id),
custom_fields=[{
            "id": 1,
            "value": severity #严重程度
        }, {
            "id": 3,
            "value": reappear#是否必现
        }, {
            "id": 4,
            "value": bugtype#bug类型
        }, {
            "id": 6,
            "value": environment #测试环境 预发布环境
        }],
uploads=uploads)
        print 'ok'
        return jsonify(result='success' )
    except Exception:
        traceback.print_exc()  
        print 'fail'
        return jsonify(result='failed' )

if __name__=='__main__':
        app.run(host='0.0.0.0',debug=True)
