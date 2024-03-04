from flask import*
from database import*
public=Blueprint('public',__name__)


@public.route('/')
def home():
    return render_template('home.html')

@public.route('/login',methods=['post','get'])
def login():
    if 'submit' in request.form:
        uname=request.form['uname']
        password=request.form['pass']
        qry="select * from login where uname='%s' and password='%s'"%(uname,password)
        a=select(qry)
        session['lid']=a[0]['login_id']

        if a[0]['utype']=='admin':
            return redirect (url_for('admin.home'))
        elif a[0]['utype']=='resteam':
            qry2="select * from res_team where login_id='%s'"%(session['lid'])
            b=select(qry2)
            session['res']=b[0]['res_team_id']
            return redirect (url_for('resteam.resteamhome'))
        elif a[0]['utype']=='staff':
            qry3="select * from staff where login_id='%s'"%(session['lid'])
            c=select(qry3)
            session['staff']=c[0]['staff_id']
            return redirect (url_for('staff.staffhome'))            
        
    return render_template('login.html')

@public.route('/register',methods=['post','get'])
def register():
    if 'submit' in request.form:
        rname=request.form['resname']
        place=request.form['place']
        phone=request.form['phone']
        email=request.form['email']
        lscno=request.form['lscno']
        est=request.form['estyear']
        founder=request.form['founder']
        vm=request.form['vm']
        uname=request.form['uname']
        password=request.form['pass']

        qry="insert into login values(null,'%s','%s','Pending')"%(uname,password)
        lid=insert(qry)
        qry2="insert into res_team values(null,'%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(lid,rname,place,phone,email,lscno,est,founder,vm)
        insert(qry2)
        return'''<script>alert('Registration Successfull');window.location="/"</script>'''

    return render_template('register.html')

