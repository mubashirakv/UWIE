from flask import*
from database import*
admin=Blueprint('admin',__name__)

@admin.route('/admin home')
def home():
    return render_template('admin_home_page.html')


@admin.route('/view')
def view():
    data={}
    qry1="select * from res_team inner join login using(login_id)"
    res=select(qry1)
    data['view']=res

    if 'action' in request.args:
        action=request.args['action']
        id=request.args['id']
    else:
        action=None
    if action=='verify':
        qry="update login set utype='resteam' where login_id='%s'"%(id)
        update(qry)
    if action=='reject':
        qry1="update login set utype='pending' where login_id='%s'"%(id)
        update(qry1)
    
    
    return render_template('view.html',data=data)

@admin.route('/staffview')
def staffview():
    data={}
    qry1="select * from staff inner join login using(login_id)"
    res=select(qry1)
    data['staffview']=res

    
    return render_template('staffview.html',data=data)

@admin.route('/viewcomplaints')
def complaints():
    data={}
    qry2="select * from complaints"
    res=select(qry2)
    data['compview']=res
    return render_template('viewcomplaints.html',data=data)

@admin.route('/updatereply',methods=['post','get'])
def updatereply():

    id=request.args['id']

    if 'reply' in request.form:
        reply=request.form['reply']
        qry3="update complaints set reply='%s' where comp_id='%s'"%(reply,id)
        update(qry3)

    return render_template('updatereply.html')

@admin.route('/notifications',methods=['post','get'])
def notifications():
    if 'submit' in request.form:
        title=request.form['title']
        desc=request.form['desc']
        date=request.form['date']

        qry4="insert into notifications values(null,'%s','%s','%s')"%(title,desc,date)
        insert(qry4)
    return render_template('notifications.html')


@admin.route('/viewimage')
def viewimage():
    data={}
    qry3="select * from uw_image"
    img=select(qry3)
    data['view']=img
    return render_template('imagedesc.html',data=data)
