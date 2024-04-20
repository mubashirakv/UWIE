from flask import*
from database import*
staff=Blueprint('staff',__name__)

@staff.route('/staffhome')
def staffhome():
    return render_template('staffhome.html')

@staff.route('/viewprofile',methods=['post','get'])
def viewprofile():
    data={}
    qry="select * from staff where staff_id='%s'"%(session['staff'])
    res=select(qry)
    data['view']=res
    return render_template('profile.html',data=data)

import uuid

@staff.route('/uploadimage',methods=['post','get'])
def uploadimage():
    if 'submit' in request.form:
        print("jhgfdsdfghjkhgfdfg")
        title=request.form['title']
        image=request.files['img']
        path="static/"+str(uuid.uuid4())+image.filename
        image.save(path)
        description=request.form['desc']
        type=request.form['file_type']

     
        qry="insert into uw_image values(null,'%s','%s','%s','%s','pending','%s',curdate())"%(session['lid'],title,path,description,type)
        insert(qry)
        return'''<script>alert('Upload Successfull');window.location="/staffhome"</script>'''
    return render_template('uploadimage.html')


@staff.route('/viewenhancedimg',methods=['post','get'])
def viewenhacedimg():
    data={}
    qry="select * from uw_image"
    res=select(qry)
    data['view']=res
    return render_template('viewenhancedimg.html',data=data)
    



@staff.route('/staffsendcomplaints',methods=['post','get'])
def sendcomp():
    if 'submit' in request.form:
        title=request.form['title']
        compdesc=request.form['compdesc']
        reply=request.form['reply']
        date=request.form['date']
        qry1="insert into complaints values(null,'%s','%s','%s','%s','%s')"%(session['lid'],title,compdesc,reply,date)
        insert(qry1)
        return'''<script>alert('Complaint Registered');window.location="/staffhome"</script>'''
    return render_template('staffcomplaints.html')

@staff.route('/staffviewreply')
def view():

    data={}
    qry3="select * from complaints where comp_id='%s'"%(session['lid'])
    res=select(qry3)
    data['view']=res
    return render_template('staffreply.html',data=data)

@staff.route('/staffviewnotification')
def viewnotify():
    data={}
    qry4="select * from notifications"
    res=select(qry4)
    data['notify']=res
    return render_template('staffnotifyview.html',data=data)


