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


@resteam.route('/view_images')
def view_images():
    data={}
    qry="select * from uw_image inner join res_team on uw_image.staff_id=res_team.res_team_id"
    res=select(qry)
    if res:
        data['view']=res
    return render_template("reteam_view_images.html",data=data)





######################################CORE ############################
import datetime
from flask import Flask, render_template, request,send_from_directory
import sys
import numpy as np
import cv2
import math
import os

app = Flask(__name__)

THRESHOLD_RATIO = 2000
MIN_AVG_RED = 60
MAX_HUE_SHIFT = 120
BLUE_MAGIC_VALUE = 1.2
SAMPLE_SECONDS = 2  # Extracts color correction from every N seconds

video_data = None  # Declare video_data outside the if block

def hue_shift_red(mat, h):
    U = math.cos(h * math.pi / 180)
    W = math.sin(h * math.pi / 180)

    r = (0.299 + 0.701 * U + 0.168 * W) * mat[..., 0]
    g = (0.587 - 0.587 * U + 0.330 * W) * mat[..., 1]
    b = (0.114 - 0.114 * U - 0.497 * W) * mat[..., 2]

    return np.dstack([r, g, b])

def normalizing_interval(array):
    high = 255
    low = 0
    max_dist = 0

    for i in range(1, len(array)):
        dist = array[i] - array[i-1]
        if(dist > max_dist):
            max_dist = dist
            high = array[i]
            low = array[i-1]

    return (low, high)

def apply_filter(mat, filt):
    r = mat[..., 0]
    g = mat[..., 1]
    b = mat[..., 2]

    r = r * filt[0] + g*filt[1] + b*filt[2] + filt[4]*255
    g = g * filt[6] + filt[9] * 255
    b = b * filt[12] + filt[14] * 255

    filtered_mat = np.dstack([r, g, b])
    filtered_mat = np.clip(filtered_mat, 0, 255).astype(np.uint8)

    return filtered_mat

def get_filter_matrix(mat):
    mat = cv2.resize(mat, (256, 256))

    avg_mat = np.array(cv2.mean(mat)[:3], dtype=np.uint8)

    new_avg_r = avg_mat[0]
    hue_shift = 0
    while(new_avg_r < MIN_AVG_RED):
        shifted = hue_shift_red(avg_mat, hue_shift)
        new_avg_r = np.sum(shifted)
        hue_shift += 1
        if hue_shift > MAX_HUE_SHIFT:
            new_avg_r = MIN_AVG_RED

    shifted_mat = hue_shift_red(mat, hue_shift)
    new_r_channel = np.sum(shifted_mat, axis=2)
    new_r_channel = np.clip(new_r_channel, 0, 255)
    mat[..., 0] = new_r_channel

    hist_r = hist = cv2.calcHist([mat], [0], None, [256], [0, 256])
    hist_g = hist = cv2.calcHist([mat], [1], None, [256], [0, 256])
    hist_b = hist = cv2.calcHist([mat], [2], None, [256], [0, 256])

    normalize_mat = np.zeros((256, 3))
    threshold_level = (mat.shape[0]*mat.shape[1])/THRESHOLD_RATIO
    for x in range(256):
        if hist_r[x] < threshold_level:
            normalize_mat[x][0] = x

        if hist_g[x] < threshold_level:
            normalize_mat[x][1] = x

        if hist_b[x] < threshold_level:
            normalize_mat[x][2] = x

    normalize_mat[255][0] = 255
    normalize_mat[255][1] = 255
    normalize_mat[255][2] = 255

    adjust_r_low, adjust_r_high = normalizing_interval(normalize_mat[..., 0])
    adjust_g_low, adjust_g_high = normalizing_interval(normalize_mat[..., 1])
    adjust_b_low, adjust_b_high = normalizing_interval(normalize_mat[..., 2])

    shifted = hue_shift_red(np.array([1, 1, 1]), hue_shift)
    shifted_r, shifted_g, shifted_b = shifted[0][0]

    red_gain = 256 / (adjust_r_high - adjust_r_low)
    green_gain = 256 / (adjust_g_high - adjust_g_low)
    blue_gain = 256 / (adjust_b_high - adjust_b_low)

    redOffset = (-adjust_r_low / 256) * red_gain
    greenOffset = (-adjust_g_low / 256) * green_gain
    blueOffset = (-adjust_b_low / 256) * blue_gain

    adjust_red = shifted_r * red_gain
    adjust_red_green = shifted_g * red_gain
    adjust_red_blue = shifted_b * red_gain * BLUE_MAGIC_VALUE

    return np.array([
        adjust_red, adjust_red_green, adjust_red_blue, 0, redOffset,
        0, green_gain, 0, 0, greenOffset,
        0, 0, blue_gain, 0, blueOffset,
        0, 0, 0, 1, 0,
    ])

def correct(mat):
    original_mat = mat.copy()
    filter_matrix = get_filter_matrix(mat)

    corrected_mat = apply_filter(original_mat, filter_matrix)
    corrected_mat = cv2.cvtColor(corrected_mat, cv2.COLOR_RGB2BGR)

    return corrected_mat

def correct_image(input_path, output_path):
    mat = cv2.imread(input_path)
    rgb_mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)

    corrected_mat = correct(rgb_mat)

    cv2.imwrite(output_path, corrected_mat)

    preview = mat.copy()
    width = preview.shape[1] // 2
    preview[::, width:] = corrected_mat[::, width:]

    preview = cv2.resize(preview, (960, 540))

    return cv2.imencode('.png', preview)[1].tobytes()

def analyze_video(input_video_path, output_video_path=None):
    cap = cv2.VideoCapture(input_video_path)
    fps = math.ceil(cap.get(cv2.CAP_PROP_FPS))
    frame_count = math.ceil(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    filter_matrix_indexes = []
    filter_matrices = []
    count = 0

    print("Analyzing...")
    while cap.isOpened():
        count += 1
        print(f"{count} frames", end="\r")
        ret, frame = cap.read()

        if not ret:
            print("End of video reached.")
            break

        if count >= frame_count:
            print("Processed all frames.")
            break

        if count % (fps * SAMPLE_SECONDS) == 0:
            mat = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            filter_matrix_indexes.append(count)
            filter_matrices.append(get_filter_matrix(mat))

    cap.release()


    filter_matrices = np.array(filter_matrices)

    result_dict = {
        "input_video_path": input_video_path,
        "output_video_path": output_video_path,
        "fps": fps,
        "frame_count": count,
        "filters": filter_matrices,
        "filter_indices": filter_matrix_indexes
    }

    return result_dict

def process_video(video_data, yield_preview=False):
    input_video_path = video_data["input_video_path"]
    output_path = video_data.get("output_video_path", "output_video.mp4")
  

    cap = cv2.VideoCapture(input_video_path)
    fps = video_data["fps"]
    frame_count = video_data["frame_count"]

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    new_video = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    filter_matrices = video_data["filters"]
    filter_indices = video_data["filter_indices"]

    filter_matrix_size = len(filter_matrices[0])

    def get_interpolated_filter_matrix(frame_number):
        return [np.interp(frame_number, filter_indices, filter_matrices[..., x]) for x in range(filter_matrix_size)]

    print("Processing...")

    count = 0
    while cap.isOpened():
        count += 1
        percent = 100 * count / frame_count
        print("{:.2f}".format(percent), end=" % \r")
        ret, frame = cap.read()

        if not ret:
            break

        rgb_mat = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        interpolated_filter_matrix = get_interpolated_filter_matrix(count)
        corrected_mat = apply_filter(rgb_mat, interpolated_filter_matrix)
        corrected_mat = cv2.cvtColor(corrected_mat, cv2.COLOR_RGB2BGR)

        new_video.write(corrected_mat)

        if yield_preview:
            preview = frame.copy()
            width = preview.shape[1] // 2
            height = preview.shape[0] // 2
            preview[::, width:] = corrected_mat[::, width:]

            preview = cv2.resize(preview, (width, height))

            yield percent, cv2.imencode('.png', preview)[1].tobytes()
        else:
            yield None

    cap.release()
    new_video.release()





app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Set upload directory



@resteam.route('/process', methods=['get','post'])
def process():
    file_type = request.args['type']
    input_file = request.args['file']
    id=request.args['id']

    if not file_type or not input_file:
        return "Please select a file type and upload a file."

    file_extension = os.path.splitext(input_file)[1].lower()
    if file_extension not in ('.jpg', '.jpeg', '.png', '.mp4'):
        return "Invalid file format. Only images (.jpg, .jpeg, .png) and videos (.mp4) are allowed."

    # Securely save the uploaded file
    # try:
        # input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}")
        # input_file.save(input_path)
    # except Exception as e:
    #     return f"Error saving file: {str(e)}"

    if file_type == 'image':
    
        output_path = os.path.join(app.config['UPLOAD_FOLDER']+"/"+str(id)+ 'corrected_image.jpg')  # Consistent naming
        try:
            corrected_image = correct_image(input_file, output_path)
            if corrected_image:  # Handle potential correction failure
                # return send_from_directory(app.config['UPLOAD_FOLDER'], 'corrected_image.jpg', as_attachment=True)
                qry2="update uw_image set enhanced_img='%s' where uw_image_id='%s'"%(output_path,id)
                update(qry2)
                return'''<script>alert('Enhanced');window.location="/view_images"</script>'''
            else:
                return "Image correction failed."
        except Exception as e:
            return f"Error processing image: {str(e)}"
    elif file_type == 'video':
        output_path = os.path.join(app.config['UPLOAD_FOLDER']+"/"+str(id)+ 'corrected_video.mp4')  # Consistent naming
        try:
            video_data = analyze_video(input_file, output_path)
            process_video(video_data)
            print(output_path,"pppppppppppppppppp")
            print(input_file,"ooooooooooooooo")
            print(video_data,"iiiiiiiiiiiiiiiiiiiiiiii")
            # qry2="update uw_image set enhanced_img='%s' where uw_image_id='%s'"%(output_path,id)
            # update(qry2)
            # return'''<script>alert('Enhanced');window.location="/view_images"</script>'''
            return send_from_directory(app.config['UPLOAD_FOLDER'], 'corrected_video.mp4', as_attachment=True)
        except Exception as e:
            return f"Error processing video: {str(e)}"
    else:
        return "Invalid file type"

# if __name__ == '__main__':
#     app.run(debug=True)





