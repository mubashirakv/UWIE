from flask import*
from database import*
resteam=Blueprint('resteam',__name__)

@resteam.route('/resteamhome')
def resteamhome():
    return render_template('resteamhome.html')
    
@resteam.route('/staffreg',methods=['post','get'])
def staffreg():

    if 'staffreg' in request.form:
        fname=request.form['fname']
        lname=request.form['lname']
        place=request.form['place']
        phone=request.form['phone']
        email=request.form['email']
        lscno=request.form['lscno']
        desig=request.form['desig']
        uname=request.form['uname']
        password=request.form['pass']
        
        qry="insert into login values(null,'%s','%s','staff')"%(uname,password)
        lid=insert(qry)

        qry1="insert into staff values(null,'%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(lid,session['res'],fname,lname,place,phone,email,lscno,desig)
        insert(qry1)
        return'''<script>alert('Registration Successfull');window.location="/resteamhome"</script>'''
    
    return render_template('staffreg.html')

@resteam.route('/sendcomplaints',methods=['post','get'])
def sendcomplaints():
    if 'submit' in request.form:
        title=request.form['title']
        compdesc=request.form['compdesc']
        reply=request.form['reply']
        date=request.form['date']
        qry2="insert into complaints values(null,'%s','%s','%s','%s','%s')"%(session['lid'],title,compdesc,reply,date)
        insert(qry2)
        return'''<script>alert('Complaint Registered');window.location="/resteamhome"</script>'''

    return render_template('rescomplaints.html')

@resteam.route('/viewreply')
def view():

    data={}
    qry3="select * from complaints where comp_id='%s'"%(session['lid'])
    res=select(qry3)
    data['view']=res
    return render_template('reply.html',data=data)

@resteam.route('/viewnotification')
def viewnotify():
    data={}
    qry4="select * from notifications"
    res=select(qry4)
    data['notify']=res
    return render_template('notifyview.html',data=data)