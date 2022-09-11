import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from attendance_api.models import attendance, client
from attendance_api.serializers import AttendanceRecordSerializer, ClientSerializer, PunchSerializer
from rest_framework.permissions import IsAuthenticated
from dashboard.models import Profile, Shift
from attendance_api.utils import measuring_radius

class PunchAPI(APIView):
    def post(self, request, *args, **kwargs):
        permission_classes = (IsAuthenticated,)
        try:
            tokken_user_id =request.user.id
            user_given_id = int(request.data['i_user'])
            
            if tokken_user_id==user_given_id:    
                client_data_boolen = False
                is_wfh = False
                client_obj_dict = dict()
                client_data = dict()
                punch_in_serializer = PunchSerializer(context={'user_id': request.user.id}, data=request.data)
                all_clients = list(client.objects.filter(is_active=True).values_list('id',flat=True))
                
                if 'client_id' in request.data:
                    if len(request.data['client_id'])==0:
                        client_data_boolen = False
                    else:
                        client_id = int(request.data['client_id'])
                        if client_id == -2:
                            wfh_obj = client.objects.filter(id=-2)    
                            if wfh_obj:
                                client_obj_dict['client_obj'] = wfh_obj[0]
                                is_wfh = True
                            else:
                                return Response({'error': 'No WFH is available in client list', 'error_code': 'H402', 'data':{}}, status=200)
                        else:
                            if client_id in all_clients:
                                client_obj = client.objects.filter(id= int(request.data['client_id']))[0]
                                client_obj_dict['client_obj'] = client_obj
                                client_data_boolen = True
                            else:
                                return Response({'error': 'No Valid Client id', 'error_code': 'H402', 'data':{}}, status=200)
                        
                if is_wfh == True:
                    client_obj = client_obj_dict['client_obj']
                    
                elif  client_data_boolen == False:
                    client_obj = client.objects.filter(id=-1)
                    if client_obj:
                        client_obj = client_obj[0]
                    else:
                        return Response({'error': 'No Default Company is available', 'error_code': 'H402', 'data':{}}, status=200)                        
                else:
                    client_obj = client_obj_dict['client_obj']
                    
                client_data['id'] = client_obj.id
                client_data['name'] = client_obj.name
                if client_obj.address:
                    client_data['address'] = client_obj.address
                else:
                    client_data['address'] = ''
                if client_obj.longitude:
                    client_data['longitude'] = client_obj.longitude
                else:
                    client_data['longitude'] = 0
                if client_obj.latitude:
                    client_data['latitude'] = client_obj.latitude
                else:
                    client_data['latitude'] = 0
                if client_obj.radius:
                    client_data['radius'] = client_obj.radius
                else:
                    client_data['radius'] = 0
                    
                client_obj_longitude = float(client_data['longitude'])
                client_obj_latitude = float(client_data['latitude'])

                user_longitude = float(request.data['longitude'])
                user_latitude = float(request.data['latitude'])
                    
                if is_wfh:
                    distance_in_meters = 0
                else:
                    distance_in_meters = measuring_radius(client_obj_longitude, client_obj_latitude, user_longitude, user_latitude)
                
                time_now = datetime.datetime.now()
                punch_obj = attendance.objects.filter(i_user_id = user_given_id).order_by('-id')
                shift_id = Profile.objects.get(i_user_id=user_given_id).shift_id
                shift_obj = Shift.objects.get(id=shift_id)
                current_time = datetime.timedelta(hours=time_now.time().hour, minutes=time_now.time().minute)
                x = shift_obj.start_time
                start_time = datetime.timedelta(hours=x.hour, minutes=x.minute)
                y = shift_obj.end_time
                end_time = datetime.timedelta(hours=y.hour, minutes=y.minute)

                    
                
                if distance_in_meters <= int(client_data['radius']):
                    if punch_in_serializer.is_valid():
                        punch_in_serializer.save()
                        validated_data = punch_in_serializer.data
                        
                        if validated_data['is_punch_in']:
                            data_dict = dict()
                            data_dict['punch_in_longitude'] =  validated_data['longitude']
                            data_dict['punch_in_latitude'] =  validated_data['latitude']
                            data_dict['punch_in_note'] = validated_data['note']
                            data_dict['punch_in_image_path'] = validated_data['image_path']
                            data_dict['punch_in_time'] = time_now
                            data_dict['i_user_id'] = user_given_id
                            data_dict['i_client_id'] = validated_data['client_id']
                            
                            
                            grace_time = start_time + datetime.timedelta(minutes=shift_obj.grace_min)
                            halfday_limit = start_time + datetime.timedelta(minutes=shift_obj.halfday_limit)
                            absent_time_limit = start_time + datetime.timedelta(minutes=shift_obj.absent_time_limit)
                            
                            
                            if punch_obj:
                                punch_obj = punch_obj[0]
                                punch_out_time = punch_obj.punch_out_time
                                if punch_out_time is None:
                                    return Response({'error': 'Already Punch in', 'error_code': 'H201', 'data':{}}, status=200)
                                
                                
                                if absent_time_limit > current_time:
                                    if halfday_limit > current_time:
                                        if grace_time > current_time:
                                            attendance.objects.create(**data_dict,user_punch_in_status='on time')
                                        else:
                                            attendance.objects.create(**data_dict,user_punch_in_status='late')
                                    else:
                                        attendance.objects.create(**data_dict,user_punch_in_status='half day')
                                else:
                                    attendance.objects.create(**data_dict,user_punch_in_status='absent')
                            else:
                                if absent_time_limit > current_time:
                                    if halfday_limit > current_time:
                                        if grace_time > current_time:
                                            attendance.objects.create(**data_dict,user_punch_in_status='on time')
                                        else:
                                            attendance.objects.create(**data_dict,user_punch_in_status='late')
                                    else:
                                        attendance.objects.create(**data_dict,user_punch_in_status='half day')
                                else:
                                    attendance.objects.create(**data_dict,user_punch_in_status='absent')
                                
                                
                            
                            data_dict['punch_in_time'] = time_now.strftime("%d-%m-%Y %I:%M %p")
                            data_dict['punch_out_longitude'] =  ''
                            data_dict['punch_out_latitude'] =  ''
                            data_dict['punch_out_note'] = ''
                            data_dict['punch_out_time'] = ''
                            data_dict['punch_out_image_path'] = ''
                            data_dict['i_client_id'] =  client_data
                            data_dict['status']='Punch In'
                            
                            return Response(
                                            {'error': '', 'error_code': '', 'data': data_dict}, status=200)

                        else:
                            data_dict = dict()  
                            
                            early_out_time = end_time + datetime.timedelta(minutes=shift_obj.early_out_time)
                            # current_time = datetime.timedelta(hours=time_now.time().hour, minutes=time_now.time().minute)
                            if punch_obj:
                                punch_obj = punch_obj[0]
                                punch_out_time = punch_obj.punch_out_time
                                if punch_out_time is not None:
                                    return Response({'error': 'Already Punch Out', 'error_code': 'H201', 'data':{}}, status=200)
                                
                                

                                punch_obj.punch_out_latitude =  validated_data['latitude']
                                punch_obj.punch_out_longitude = validated_data['longitude']
                                punch_obj.punch_out_note = validated_data['note']
                                punch_obj.punch_out_time = time_now
                                punch_obj.punch_out_image_path = validated_data['image_path']
                                if early_out_time > current_time:
                                    punch_obj.user_punch_out_status = 'early out'
                                else:
                                    punch_obj.user_punch_out_status = 'on time'
                                    
                                punch_obj.save()

                                data_dict['punch_in_longitude'] =  ''
                                data_dict['punch_in_latitude'] =  ''
                                data_dict['punch_in_note'] = ''
                                data_dict['punch_in_time'] = ''
                                data_dict['punch_in_image_path'] = ''
                                data_dict['punch_out_longitude'] =  validated_data['longitude']
                                data_dict['punch_out_latitude'] =  validated_data['latitude']
                                data_dict['punch_out_note'] = validated_data['note']
                                data_dict['punch_out_image_path'] = validated_data['image_path']
                                data_dict['punch_out_time'] = time_now.strftime("%d-%m-%Y %I:%M %p")
                                data_dict['i_user_id'] = user_given_id
                                data_dict['i_client_id'] =  client_data
                                data_dict['status']='Punch out'
                                
                        return Response(
                            {'error': '', 'error_code': '', 'data': data_dict}, status=200)

                    error_list = punch_in_serializer.errors
                    err_str = "" 
                    for i in error_list: 
                        err_str +=i+', '
                    else:
                        return Response({'error': err_str, 'error_code': 'HS002', 'data':{}}, status=200)
                else:
                    return Response(
                        {'error': 'you are out range, please get in range', 'error_code': 'H205', 'data': ''}, status=200)
            else:
                return Response({'error': "User is not matched", 'error_code': 'H201', 'matched': 'N', 'data': {}}, status=400)
        
        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': {}}, status=400)

class UserStatus(APIView):

    def get(self, request):
        permission_classes = (IsAuthenticated,)
        try:
            total_duration_list = []
            data = dict()
            tokken_user_id =request.user.id
            user_given_id = int(request.query_params['id'])
            
            # import pdb
            # pdb.set_trace()
            
            if tokken_user_id==user_given_id:
                date_today = datetime.datetime.today()
                punch_obj = attendance.objects.filter(i_user_id = user_given_id).order_by('-id')
                if punch_obj:
                    punch_obj = punch_obj[0]
                    if punch_obj.punch_in_time and not punch_obj.punch_out_time:
                        punched_time = punch_obj.punch_in_time
                        total_duration =date_today - punched_time
                    else:
                        last_punched_day = punch_obj.punch_out_time.date()
                        punch_list = list(attendance.objects.filter(i_user_id = user_given_id,punch_out_time__date=last_punched_day))
                        if punch_list:
                            for i in punch_list:
                                punch_in = i.punch_in_time
                                punch_out = i.punch_out_time
                                punch_durations = punch_out-punch_in
                                total_duration_list.append(punch_durations)
                            
                            total_duration = sum(total_duration_list,datetime.timedelta())
                    total_duration = int(abs(total_duration.total_seconds()))
                    seconds = total_duration
                    hour = seconds // 3600
                    seconds %= 3600
                    minutes = seconds // 60
                    seconds %= 60
                    total_duration = (str(hour)).zfill(2)+":"+(str(minutes)).zfill(2)+":"+(str(seconds)).zfill(2)
                    # yeh code phatt jaye ga 99 hours ke bd
                        
                
                    if punch_obj.punch_in_latitude:
                        data['punch_in_latitude'] = punch_obj.punch_in_latitude
                    else:
                        data['punch_in_latitude'] = ''

                    if punch_obj.punch_in_longitude:
                        data['punch_in_longitude'] = punch_obj.punch_in_longitude
                    else:
                        data['punch_in_longitude'] = ''

                    if punch_obj.punch_out_latitude:
                        data['punch_out_latitude'] = punch_obj.punch_out_latitude
                    else:
                        data['punch_out_latitude'] = ''
                        
                    if punch_obj.punch_out_longitude:     
                        data['punch_out_longitude'] = punch_obj.punch_out_longitude
                    else:
                        data['punch_out_longitude'] = ''
                            
                    if punch_obj.punch_in_image_path:     
                        data['punch_in_image_path'] = punch_obj.punch_in_image_path
                    else:
                        data['punch_in_image_path'] = ''

                    if punch_obj.punch_out_image_path:     
                        data['punch_out_image_path'] = punch_obj.punch_out_image_path
                    else:
                        data['punch_out_image_path'] = ''

                    punch_in_time = punch_obj.punch_in_time
                    if punch_in_time:
                        punch_in_time = punch_in_time.strftime("%d-%m-%Y %I:%M %p")
                        data['punch_in_time']=punch_in_time
                    else:
                        data['punch_in_time']=''

                    punch_out_time = punch_obj.punch_out_time
                    if punch_out_time:
                        punch_out_time = punch_out_time.strftime("%d-%m-%Y %I:%M %p")
                        data['punch_out_time']=punch_out_time
                    else:
                        data['punch_out_time']=''

                    if punch_obj.punch_in_note:
                        data['punch_in_note']=punch_obj.punch_in_note
                    else:
                        data['punch_in_note']=''
                    
                    if punch_obj.punch_out_note:
                        data['punch_out_note']=punch_obj.punch_out_note
                    else:
                        data['punch_out_note']=''
                        
                    if total_duration:
                        data['total_duration']="0000-00-00 "+ str(total_duration)
                    else:
                        data['total_duration']='0000-00-00 00:00:00.0000'

                    data['i_user'] = user_given_id
                    data_dict = dict()
                    if punch_obj.i_client_id:
                        client_obj = client.objects.get(id = punch_obj.i_client_id)
                        data_dict['id'] = client_obj.id
                        data_dict['name'] = client_obj.name
                        data_dict['address'] = client_obj.address
                        data_dict['longitude'] = client_obj.longitude
                        data_dict['latitude'] = client_obj.latitude
                        data_dict['radius'] = client_obj.radius
                    else:
                        client_obj = client.objects.filter(id=-1)
                        if client_obj:
                            client_obj = client_obj[0]
                            data_dict['id'] = client_obj.id
                            data_dict['name'] = client_obj.name
                            data_dict['address'] = client_obj.address
                            data_dict['longitude'] = client_obj.longitude
                            data_dict['latitude'] = client_obj.latitude
                            data_dict['radius'] = client_obj.radius
                    data['i_client']= data_dict
                    if punch_in_time and punch_out_time is not None:
                        data['status']='Punch out'
                        return Response(
                                    {'error': '', 'error_code': '', 'data': data}, status=200)
                    else:
                        data['status']='Punch In'
                        return Response(
                                    {'error': '', 'error_code': '', 'data': data}, status=200)
                else:
                    data['punch_in_time']=''
                    data['punch_out_time']=''
                    data['punch_in_note']=''
                    data['punch_out_note']=''
                    data['punch_in_longitude'] = ''
                    data['punch_in_latitude'] = ''
                    data['punch_out_longitude'] = ''
                    data['punch_out_latitude'] = ''
                    data['punch_in_image_path'] = ''
                    data['punch_out_image_path'] = ''
                    data['status']='Punch out'
                    data['i_client']={
                        'id':0,
                        'name':'',
                        'address':'',
                        'longitude':'',
                        'latitude':'',
                        'radius':0
                    }
                    data['total_duration']='0000-00-00 00:00:00.0000'
                    return Response(
                                    {'error': '', 'error_code': '', 'data': data}, status=200)
            else:
                return Response({'error': "User is not matched", 'error_code': 'H201', 'matched': 'N', 'data': {}}, status=200)
       
        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': {}}, status=400)

class ClientAPI(APIView):

    def post(self, request, *args, **kwargs):
        permission_classes = (IsAuthenticated,)
        try:
            client_serializer = ClientSerializer(data=request.data)
            
            if client_serializer.is_valid():
                client_serializer.save()
                
                return Response({'error': '', 'error_code': '', 'data':client_serializer.data}, status=200)
            else:
                return Response({'error': client_serializer.errors, 'error_code': 'HS002', 'data':{}}, status=200)

        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': {}}, status=400)

    def get(self, request):
            try:
                data_list = []
                clients = list(client.objects.filter(is_active = True).values_list('id','name','address','longitude','latitude','radius').order_by('-id'))
                for i in clients:
                    data_dict = dict()
    
                    data_dict['id'] = i[0]
                    data_dict['name'] = i[1]
                    if i[2]:
                        data_dict['address'] = i[2]
                    else:
                        data_dict['address'] = ''
                    if i[3]:
                        data_dict['longitude'] = i[3]
                    else:
                        data_dict['longitude']=''
                    if i[4]:
                        data_dict['latitude'] = i[4]
                    else:
                        data_dict['latitude']=''
                        
                    data_dict['radius'] = i[5]
                    data_list.append(data_dict)
                        
                return Response({'error': '', 'error_code': '', 'data':data_list}, status=200)
           
            except Exception as error:
                return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': {}}, status=400)
            
class AttendanceRecordAPI(APIView):
    def post(self, request, *args, **kwargs):
        permission_classes = (IsAuthenticated,)
        try:
            
          
            tokken_user_id =request.user.id
            user_given_id = int(request.data['i_user'])
            if tokken_user_id==user_given_id:
                data_list = []
                overall_duration_list =[]
                data_dict = dict()

                client_serializer = AttendanceRecordSerializer(data=request.data)
                if client_serializer.is_valid():
                    client_serializer.save()
                    start_date = client_serializer.data['start_date']
                    if start_date:
                        start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
                    end_date = client_serializer.data['end_date']
                    if end_date:
                        end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
                        
                    if start_date is None and end_date is None:
                        current_month = datetime.datetime.today().month
                        data_dict['punch_list'] = list(attendance.objects.filter(i_user_id = user_given_id,punch_out_time__month=current_month)
                                        .order_by('-id').values_list('id','i_user_id','punch_in_image_path','punch_out_image_path',
                                                                    'punch_in_note','punch_out_note','punch_in_time','punch_out_time','i_client'))
                    else:
                        if start_date is None:
                            end_date = datetime.datetime.strptime(client_serializer.data['end_date'],"%Y-%m-%d")
                            data_dict['punch_list'] = list(attendance.objects.filter(i_user_id = user_given_id,punch_out_time__date=end_date).order_by('-id').values_list('id','i_user_id','punch_in_image_path','punch_out_image_path',
                                                                    'punch_in_note','punch_out_note','punch_in_time','punch_out_time','i_client'))
                        
                        elif start_date and end_date:
                            if start_date == end_date:
                                data_dict['punch_list']= list(attendance.objects.filter(i_user_id = user_given_id,punch_out_time__date=end_date).order_by('-id').values_list('id','i_user_id','punch_in_image_path','punch_out_image_path',
                                                                    'punch_in_note','punch_out_note','punch_in_time','punch_out_time','i_client'))
                            else:
                                data_dict['punch_list'] = list(attendance.objects.filter(i_user_id = user_given_id,punch_out_time__date__range=(start_date, end_date)).order_by('-id').values_list('id','i_user_id','punch_in_image_path','punch_out_image_path',
                                                                        'punch_in_note','punch_out_note','punch_in_time','punch_out_time','i_client'))
                        else:
                            return Response({'error': 'Something went wrong', 'error_code': 'HD201', 'data':''}, status=400)
                        
                    if data_dict['punch_list']:
                        punch_list = data_dict['punch_list']
                        for data in punch_list:
                            data_dict = dict()
                            data_dict['id'] = data[0]
                            data_dict['i_user_id'] = data[1]
                            if data[2]:
                                data_dict['punch_in_image_path'] = data[2]
                            else:
                                data_dict['punch_in_image_path'] = ''
                            if data[3]:
                                data_dict['punch_out_image_path'] = data[3]
                            else:
                                data_dict['punch_out_image_path'] = ''
                                
                            if data[4]:
                                data_dict['punch_in_note'] = data[4]
                            else:
                                data_dict['punch_in_note'] = ''
                            if data[5]:
                                data_dict['punch_out_note'] = data[5]
                            else:
                                data_dict['punch_out_note'] = ''
                            data_dict['punch_in_time'] = data[6].strftime("%I:%M %p")
                            data_dict['punch_out_time'] = data[7].strftime("%I:%M %p")
                            data_dict['punch_in_date'] = data[6].strftime("%d %b %Y")
                            data_dict['punch_out_date'] = data[7].strftime("%d %b %Y")
                            data_dict['punch_in_day'] = data[6].strftime("%a")
                            data_dict['punch_out_day'] = data[7].strftime("%a")
                            if data[6] and data[7]:
                                total_duration = data[7] - data[6]
                                total_duration = int(abs(total_duration.total_seconds()))
                                overall_duration_list.append(total_duration)
                                seconds = total_duration
                                hour = seconds // 3600
                                seconds %= 3600
                                minutes = seconds // 60
                                seconds %= 60
                                total_duration = (str(hour)).zfill(2)+"h "+(str(minutes)).zfill(2)+"m"
                                data_dict['duration'] = str(total_duration)
                                data_dict['type'] = 'Full Day'
                            
                            client_dict = dict()
                            if data[8]:
                                client_id = data[8]
                            else:
                                client_id = -1
                            client_obj = client.objects.get(id=client_id)
                            client_dict['id']=client_obj.id
                            client_dict['name']=client_obj.name
                            client_dict['address']=client_obj.address
                            
                            data_dict['i_client'] = client_dict
                            data_list.append(data_dict)
                        overall_duration = sum(overall_duration_list)
                        seconds = overall_duration
                        hour = seconds // 3600
                        seconds %= 3600
                        minutes = seconds // 60
                        overall_duration = (str(hour)).zfill(2)+"h "+(str(minutes)).zfill(2)+"m"
                        # data_list.append(overall_duration)
                    else:
                        data_dict = dict()
                        data_dict['id'] = 0
                        data_dict['i_user_id'] = 0
                        data_dict['punch_in_image_path'] = ''
                        data_dict['punch_out_image_path'] = ''
                        data_dict['punch_in_note'] = ''
                        data_dict['punch_out_note'] = ''
                        data_dict['punch_in_time'] = ''
                        data_dict['punch_out_time'] = ''
                        data_dict['punch_in_date'] = ''
                        data_dict['punch_out_date'] = ''
                        data_dict['punch_in_day'] = ''
                        data_dict['punch_out_day'] = ''
                        data_dict['duration'] = '00h 00m'
                        data_dict['type'] = 'Full Day'
                        client_dict = dict()
                        client_dict['id']=0
                        client_dict['name']=''
                        client_dict['address']=''
                        data_dict['i_client'] = client_dict
                        overall_duration = '00h 00m'
                        # data_list.append(data_dict)

                    return Response({'error': '', 'error_code': '','overall_duration':overall_duration, 'data':data_list}, status=200)
                else:
                    return Response({'error': client_serializer.errors, 'error_code': 'HS002', 'data':{}}, status=200)
            else:
                return Response({'error': "User is not matched", 'error_code': 'H201', 'matched': 'N', 'data': {}}, status=200)
   
        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': {}}, status=400)
        
   