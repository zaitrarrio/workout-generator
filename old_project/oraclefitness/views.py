#TODO:  Fix eliminate repeat days
#TODO  Redo supersetting such that the exercise pooling is done before filter by muscle group

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db import connection
from django.conf.urls.defaults import *
from django.contrib.sessions.models import Session
from django import http

###for youtube videos
from django.template.defaultfilters import stringfilter
from django import template
import re

from myproject.oraclefitness.forms import *
from myproject.oraclefitness.models import *
from django.db.models import Q
#from strengthgoal.models import *

import random
import datetime
from datetime import timedelta
from datetime import date
from django.http import HttpResponseRedirect
#>>> date1=date.today()
#>>> date1
#datetime.date(2009, 11, 10)
#>>> date2=date(year=2009, month=12, day=31)
#>>> date2
#datetime.date(2009, 12, 31)
#>>> date2-date1
#datetime.timedelta(51)
#>>>
#timedelta.days gives 51

#time1=datetime.datetime.now()


from django.core import serializers
from django.utils import simplejson
timeDifference=-17
freeMembership=True
def sblDebug(inText):
    inText = inText.__str__()
    import datetime
    currentTime = datetime.datetime.now()
    f = open("/home/aesg/debug.txt", "a")
    f.write("%s: %s\n" % (currentTime, inText))
    f.close()

def view(request):

    try:
        import memcache
    except ImportError:
        raise http.Http404

    if not (request.user.is_authenticated() and
            request.user.is_staff):
        raise http.Http404

    # get first memcached URI
    m = re.match(
        "memcached://([.\w]+:\d+)", settings.CACHE_BACKEND
    )
    if not m:
        raise http.Http404

    host = memcache._Host(m.group(1))
    host.connect()
    host.send_cmd("stats")

    class Stats:
        pass

    stats = Stats()

    while 1:
        line = host.readline().split(None, 2)
        if line[0] == "END":
            break
        stat, key, value = line
        try:
            # convert to native type, if possible
            value = int(value)
            if key == "uptime":
                value = datetime.timedelta(seconds=value)
            elif key == "time":
                value = datetime.datetime.fromtimestamp(value)
        except ValueError:
            pass
        setattr(stats, key, value)

    host.close_socket()

    return render_to_response(
        'memcached_status.html', dict(
            stats=stats,
            hit_rate=100 * stats.get_hits / stats.cmd_get,
            time=datetime.datetime.now(),)) # server time



#AJAX
def lookup(request):
    results = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            if len(value) > 2:
                keys=value.split()
		if len(keys)==1:
                  model_results = Exercise.objects.filter(name__icontains=keys[0]).order_by('name')
		elif len(keys)==2:
                  model_results = Exercise.objects.filter(name__icontains=keys[0]).order_by('name') & Exercise.objects.filter(name__icontains=keys[1]).order_by('name')
		elif len(keys)>=3:
                  model_results = Exercise.objects.filter(name__icontains=keys[0]).order_by('name') & Exercise.objects.filter(name__icontains=keys[1]).order_by('name') & Exercise.objects.filter(name__icontains=keys[2]).order_by('name')
                results = [ x.name for x in model_results ]
#response_data['result']='failed'
#response_data['message']='you messed up'
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

#AJAX
def exercise_lookup(request):
    results = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            model_results = Exercise.objects.filter(name=value)
            if model_results:
              model_results=model_results[0]
    #        results = [ x.name for x in model_results ]
            results=model_results.url
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')







def writeTestData(string):
  entireFile=""
  try:
    myFile=open('./TESTTEST.txt', 'r')
    entireFile= myFile.read()
  except:
    pass
  myFile=open('./TESTTEST.txt', 'w')
  myFile.write(entireFile)
  myFile.write(string)
  myFile.write("\n")

def testOnly():
  allWorkouts=TodaysWorkout.objects.all()
  for workoutObject in allWorkouts:
    workoutObject.date=workoutObject.date+timedelta(days=-1)
    workoutObject.save()




def credentials(request):



#   currentCount=Count.objects.all()[0]
#   if currentCount.today.__str__()[0:10] != (datetime.datetime.today()+timedelta(hours=timeDifference)).date().__str__():
#     currentCount.traffic=1
#     currentCount.today=(datetime.datetime.today()+timedelta(hours=timeDifference)).date()
#
#   else:
#     currentCount.traffic=currentCount.traffic+1
#
#   currentCount.save()
#   request.session['totalCount']=currentCount.count
   request.session['totalCount']=45
   login=0
   superuser=0
   # SUPER HACKY but quick fix to make this work
   sblDebug(request.session.get('userID'))
   if request.session.get('userID', "").lower() in ("burkea101@gmail.com", "scott.lobdell@gmail.com"):
       superuser=1
   if 'temporaryID' in request.session:
     #this means that a page has been loaded again....
     try:
       userToDelete=User.objects.get(id=int(request.session['temporaryID']))
     except:
       return 1, 0
     if userToDelete.confirmed==False:
       try:
         userInformationToDelete=UserInformation.objects.filter(user=userToDelete)[0]
         userInformationToDelete.delete()
         userToDelete.delete()
         del request.session['temporaryID']
       except:
         pass


   if not 'userID' in request.session:
      login=1
   else:
      if request.session['role']=="superuser":
         superuser=1

      currentUser=User.objects.filter(username=request.session['userID'])[0]
      ip=request.META.get('REMOTE_ADDR', '<none>')
#real_ip = request.META['HTTP_X_FORWARDED_FOR']
#this is what happens if there is a load balancer proxy
      if ip.__str__() != currentUser.ip:
         #log the guy out as well
        if 'userID' in request.session:
          del request.session['userID']
        if 'role' in request.session:
          del request.session['role']
        login=2


   maxPhotos=33
   request.session['usePhoto']=False
   request.session['randomPhoto']=random.randint(1,maxPhotos)
   colors=[]
   for j in range(0,16):
     if j<10:
       colors.append(j.__str__())
     elif j==10:
       colors.append('A')
     elif j==11:
       colors.append('B')

     elif j==12:
       colors.append('C')
     elif j==13:
       colors.append('D')
     elif j==14:
       colors.append('E')
     elif j==15:
       colors.append('F')
   randomColor=""
   for j in range(0,6):
     index=random.randint(0, 15)
     randomColor=randomColor+colors[index]
   request.session['randomColor']=randomColor
   return login, superuser


def generatePassword(password):
   import md5
   password=md5.new(password.__str__()).digest()
   stringAsHex=""
   for character in password:
      stringAsHex=stringAsHex + character.__repr__()
   stringAsHex=stringAsHex.replace("\\x","")
   stringAsHex=stringAsHex.replace("'","")
   stringAsHex=stringAsHex.replace("\"","")
   password=stringAsHex
   return password

register = template.Library()

@register.filter
@stringfilter
def youtube(url):
    regex = re.compile(r"^(http://)?(www\.)?(youtube\.com/watch\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})")
    match = regex.match(url)
    if not match: return ""
    video_id = match.group('id')
    return """
    <div class="video">
    <object width="425" height="344">
    <param name="movie" value="http://www.youtube.com/watch/v/%s"></param>
    <param name="allowFullScreen" value="true"></param>
    <embed src="http://www.youtube.com/watch/v/%s" type="application/x-shockwave-flash" allowfullscreen="true" width="124" height="100" href="."  onMouseOver="expand(this);"  onmouseout="shrink(this);"></embed>
    </object>
    </div>
    """ % (video_id, video_id)
youtube.is_safe = True # Don't escape HTML

def cancelSubscription(request):
  login, superuser = credentials(request)
  if login:
    return signIn(request)
  currentUser=User.objects.filter(username=request.session['userID'])[0]

#  loginName="427VTgk7" #TESTING
#  transactionKey="89CFj64A3C2Mf7pd" #TESTING
  loginName="54LzBg3c" #ACTUAL
  transactionKey="59eQUcC5k4B23Z4j" #ACTUAL
  #URL="https://apitest.authorize.net/xml/v1/request.api"
  URL= "https://api.authorize.net/xml/v1/request.api"
  refId="refId"
  subscriptionId=currentUser.subscriptionId.__str__()

  content="<ARBCancelSubscriptionRequest \
xmlns=\"AnetApi/xml/v1/schema/AnetApiSchema.xsd\">\
  <merchantAuthentication>\
    <name>"+loginName+"</name>\
    <transactionKey>"+transactionKey+"</transactionKey>\
  </merchantAuthentication>\
  <refId>"+refId+"</refId>\
  <subscriptionId>"+subscriptionId+"</subscriptionId>\
</ARBCancelSubscriptionRequest>"


  def send_request(URL, content):
    import urllib2, urllib
    enc_params=urllib.quote(content)

    headers={'Content-Type': 'text/xml'}
    request=urllib2.Request(URL, content, headers)
    r = urllib2.urlopen(request).read()
    return r

  result = send_request(URL, content)

  from xml.dom.minidom import parseString
  doc=parseString(result)
  resultCode=doc.getElementsByTagName("resultCode")[0].firstChild.nodeValue
  if resultCode=="Ok":
    #delete that user
    toDelete=UserInformation.objects.filter(user=currentUser)[0]
    currentUser.delete()
    toDelete.delete()
    del request.session['userID']
    successMessage="Your account has been successfully deleted."
    return render_to_response('success.html', locals())

  else:
    pass
    #ERROR
  successMessage="An error has occurred."
  return render_to_response('success.html', locals())


def payupfool(postDict):
#  loginName="427VTgk7" #TESTING
#  transactionKey="89CFj64A3C2Mf7pd" #TESTING
  loginName="54LzBg3c" #ACTUAL
  transactionKey="59eQUcC5k4B23Z4j" #ACTUAL
  #URL="https://apitest.authorize.net/xml/v1/request.api"
  URL= "https://api.authorize.net/xml/v1/request.api"

  #start date, interval, and unit create duplicates

  amount="34.95"
  refId="refId"
  name="name"
  length="1"
  unit="months"
  currentDate=date.today().year.__str__()
  currentMonth=date.today().month.__str__()
  if len(currentMonth)==1:
    currentMonth='0'+currentMonth
  currentDate=currentDate+'-'+currentMonth
  currentDay=date.today().day.__str__()
  if len(currentDay)==1:
    currentDay='0'+currentDay
  currentDate=currentDate+'-'+currentDay


  startDate=currentDate #formatted like 2007-09-30
  totalOccurrences="1"#infinite is 9999
  trialOccurrences="0"
  trialAmount="0.00"
  cardNumber=postDict['cardNumber']
  expirationDate=postDict['year'].__str__()+'-'+postDict['month']
  firstName=postDict['firstName']
  lastName=postDict['lastName']



  content="<?xml version=\"1.0\" encoding=\"utf-8\"?>\
<ARBCreateSubscriptionRequest xmlns=\"AnetApi/xml/v1/schema/AnetApiSchema.xsd\">\
<merchantAuthentication>\
<name>" + loginName + "</name>\
<transactionKey>" + transactionKey + "</transactionKey>\
</merchantAuthentication>\
	<refId>" + refId + "</refId>\
<subscription>\
<name>" + name + "</name>\
<paymentSchedule>\
<interval>\
<length>"+length +"</length>\
<unit>" + unit +"</unit>\
</interval>\
<startDate>" + startDate + "</startDate>\
<totalOccurrences>" + totalOccurrences + "</totalOccurrences>\
<trialOccurrences>" + trialOccurrences + "</trialOccurrences>\
</paymentSchedule>\
<amount>" + amount + "</amount>\
<trialAmount>" + trialAmount + "</trialAmount>\
<payment>\
<creditCard>\
<cardNumber>" + cardNumber +"</cardNumber>\
<expirationDate>" + expirationDate + "</expirationDate>\
</creditCard>\
</payment>\
<billTo>\
<firstName>" + firstName + "</firstName>\
<lastName>"  + lastName + "</lastName>\
</billTo>\
</subscription>\
</ARBCreateSubscriptionRequest>"


#resultCode will give "Ok" or "Error"
#subscriptionId will give the subscription ID

#send request with host and content
  def send_request(URL, content):
    import urllib2, urllib
    enc_params=urllib.quote(content)

    headers={'Content-Type': 'text/xml'}
    request=urllib2.Request(URL, content, headers)
    r = urllib2.urlopen(request).read()
    return r

  result = send_request(URL, content)

  from xml.dom.minidom import parseString
  doc=parseString(result)
  resultCode=doc.getElementsByTagName("resultCode")[0].firstChild.nodeValue
  if resultCode=="Ok":
    subscriptionId = doc.getElementsByTagName("subscriptionId")[0].firstChild.nodeValue
    return subscriptionId
  else:
    return -1
    #ERROR

def aboutUs(request):
  login, superuser = credentials(request)
  return render_to_response('aboutus.html', locals())

def admincheckworkout(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  allUsers=UserInformation.objects.all()


  return render_to_response('admincheckworkout.html', locals())
def admincheckworkoutuser(request, userid=None):
  login, superuser = credentials(request)

  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())

  if not  userid is None:
    try:
#    if True:
      currentUser=User.objects.get(id=userid)
      currentUserInfo=UserInformation.objects.get(user=currentUser)

      weekDictionary={}
      for j in range(1, 8):
        tempWeek=ThisWeek.objects.filter(user=currentUser, dayNumber=j)[0]
        theExercises=TodaysWorkout.objects.filter(thisWeek=tempWeek)[0].exercises.all()
        weekDictionary[(j-1).__str__()]=theExercises
        weekDictionary["cardio"+(j-1).__str__()]=tempWeek.cardio
        myString="No"
        if tempWeek.level==1:
          myString="Light"
        if tempWeek.level==2:
          myString="Medium"
        if tempWeek.level==3:
          myString="Heavy"
        weekDictionary["cardioLevel"+(j-1).__str__()]=myString

#      for wObject in tempWeek.workoutComponents.all():
#        weekDictionary[tempWeekDay.__str__()].append({'exercise':{'name':wObject.name}})

        if (len(tempWeek.workoutComponents.all())==0 and not tempWeek.cardio) or TodaysWorkout.objects.filter(thisWeek=tempWeek)[0].offDay:
          weekDictionary[(j-1).__str__()]=[]
          weekDictionary[(j-1).__str__()].append({'exercise':{'name':'Rest Day'}})
    except:

      successMessage="error.  ???"
      return render_to_response('success.html', locals())
  return render_to_response('admincheckworkout2.html', locals())

def home(request):
#  referer= request.META.get('HTTP_REFERER', None)
  searchEngines=True
  if request.method=='GET':
    searchEngines=False

  if request.method=='POST' and not freeMembership:
    success=payupfool(request.POST)
    if success==-1:
      successMessage="There was an error in processing your response.  Please ensure you input the correct information or that you don't already have a subscription with us."
      login=1
      return render_to_response('success.html', locals())
    else:
      #IF SUCCESSFUL PAYMENT
      request.session['userID']=request.session['paymentEmail']
      checkForUser=User.objects.filter(username=request.session['paymentEmail'])[0]
      request.session['role']=checkForUser.role
      checkForUser.confirmed=True
      checkForUser.payment="authorize"
      checkForUser.ip=request.META.get('REMOTE_ADDR', '<none>')
      checkForUser.subscriptionId=success
      checkForUser.save()
      from django.core.mail import send_mail
      send_mail("Someone signed up", request.session['paymentEmail'].__str__(), 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)


      lastFour=request.POST['cardNumber'].__str__()
      lastFour=lastFour[len(lastFour)-4:len(lastFour)]
      message="Welcome to WorkoutGenerator.net!\n\
Your subscription number is "+checkForUser.subscriptionId.__str__()+"\n\
Your username is "+request.session['paymentEmail'].__str__()+"\n\
\Service Terms:\n\
$34.95 USD will be billed to ************"+lastFour+"\n\
Start Date: "+date.today().__str__()+"\n\n\
Thanks,\
WorkoutGenerator.net"
      send_mail("WorkoutGenerator.net Subscription Receipt", message, 'administrator@oraclefitness.com', [request.session['paymentEmail'].__str__(), 'scott.lobdell@gmail.com'], fail_silently=False)

  login, superuser = credentials(request)
  request.session['usePhoto']=False
  #hardcore the presence of myself in the database
  myUsername="LOBDELLBROTHERS"
#  request.session['usePhoto']=False


  existingUser = User.objects.filter(username=myUsername)
  if not existingUser:
    superUserToInsert=User(username=myUsername,
       password="9dG9882b4a3i02a31Wea^e3<c1",
       role="superuser"
    )
    superUserToInsert.save()
    newUserInfo=UserInformation()
    newUserInfo.user=superUserToInsert
    newUserInfo.save()
#  request.session['usePhoto']=False
  if False:
    currentUser=User.objects.filter(username=request.session['userID'])[0]
    userInfo=UserInformation.objects.filter(user=currentUser)[0]

    if request.method=='POST' and 'day' in request.POST:

      validDay=int(request.POST['day'])
      for j in range(0, 4):#kind of inefficient, but whatever...it will iterate all 4 times regardless
        try:
          userInfo.goalDate=date(year=int(request.POST['year']), month=int(request.POST['month']), day=validDay)
        except:
          validDay=validDay-1
      userInfo.goalText=request.POST['goalText']
      userInfo.save()

    if userInfo.goalDate:
      daysRemaining=(userInfo.goalDate-date.today()).days
      if daysRemaining<0:
        userInfo.goalDate=None
        userInfo.save()

    allDays=[]
    for j in range(1,32):
      allDays.append(j)
    allYears=[]
    for j in range(date.today().year,date.today().year+5):
      allYears.append(j)
    currentMonth=date.today().month
    currentDay=date.today().day
    relevantArticles=list(Article.objects.filter(gender=userInfo.gender, goal=userInfo.goal))
    relevantArticles.extend(Article.objects.filter(gender=None, goal=userInfo.goal))
    for j in range(0, len(relevantArticles)):
      relevantArticles[j]=relevantArticles[j].id

    relevantArticles=list(Article.objects.filter(id__in=relevantArticles).order_by('-date'))
    articlesToDisplay=3
    #split into top 3rd, middle 3rd, last 3rd, then choose a random one from each
    listSize=len(relevantArticles)/articlesToDisplay
    if listSize==0:
      listSize=1
    index=0
    myList=[]

    for j in range(0, articlesToDisplay):
      myArticle=relevantArticles[j*len(relevantArticles)/articlesToDisplay:(j+1)*len(relevantArticles)/articlesToDisplay]
      if len(myArticle)>0:
        myArticle=myArticle[random.randint(0, len(myArticle)-1)]
        myList.append(myArticle)
#    while index<len(relevantArticles):
#      myArticle=relevantArticles[index: index+listSize]
#      if len(myArticle)>0:
#        myArticle=myArticle[random.randint(0, len(myArticle)-1)]
#        myList.append(myArticle)
#      index=index+listSize
    relevantArticles=myList




    return render_to_response('userhomepage.html', locals())
  return render_to_response('home.html', locals())

def addGoal(request, exercise=None):
  login, superuser = credentials(request)
  allPhases=Phase.objects.all()
  allCardioTypes=CardioType.objects.all()
  if request.method=="POST":
    goalToAdd=Goal()
    goalToAdd.name=request.POST["name"]
    goalToAdd.cardioType=CardioType.objects.get(id=int(request.POST['cardioType']))
    goalToAdd.image=request.POST["image"]
    description=Description(text=request.POST['description'])
    description.save()
    goalToAdd.description=description
    goalToAdd.save()
    allPhases=Phase.objects.all()
    for iterator in allPhases:
      if (iterator.id).__str__() in request.POST:
        goalToAdd.phase.add(iterator)
        thisPhaseLength=PhaseLength(goal=goalToAdd, phase=iterator,
                                    minLength=int(request.POST['minLength'+iterator.id.__str__()]),
                                    maxLength=int(request.POST['maxLength'+iterator.id.__str__()]),
        )
        thisPhaseLength.save()



    goalToAdd.save()
    successMessage="New Goal added."
    return render_to_response('success.html', locals())



  return render_to_response('addgoal.html', locals())

def addCardio(request):
  login, superuser = credentials(request)
  allEquipment=Equipment.objects.all().order_by('name')
  allFitness=FitnessLevel.objects.all()
  if request.method=='POST':
    newCardio=Cardio(name=request.POST['name'], equipment=Equipment.objects.get(id=int(request.POST['equipment'])),
                      description=request.POST['description'], minFitnessLevel=FitnessLevel.objects.get(id=int(request.POST['fitness']))
    )
    newCardio.totalTime=int(request.POST['totalTime'])






    if request.POST['timeOrDistance']=='1':#time
      newCardio.timeOrDistance=True
      newCardio.time=int(request.POST['time'])
      newCardio.heartRate=int(request.POST['heartrate'])
    else:#distance
      newCardio.timeOrDistance=False
      newCardio.sets=int(request.POST['sets'])
      newCardio.rest=int(request.POST['rest'])
      newCardio.distance=int(request.POST['distance'])
    newCardio.save()
    successMessage="New Cardio successfully added"
    return render_to_response('success.html', locals())
  return render_to_response('addcardio.html', locals())


def addExercise(request):
  login, superuser = credentials(request)
  allEquipment=Equipment.objects.all().order_by('name')
  allEquipment=listToMatrix(allEquipment)
  allMuscleGroups=MuscleGroup.objects.all().order_by('name')
  allPhases=Phase.objects.all()
  allComponents=WorkoutComponent.objects.all()
  allFitnessLevels=FitnessLevel.objects.all()
  allExperiences=Experience.objects.all()
  allExerciseTypes=ExerciseType.objects.all()
  matrixMuscleGroup=listToMatrix(allMuscleGroups)


  similarExercises=Exercise.objects.all().order_by('name')
  currentMutex=None
  if request.method=="POST":

    #get the video info, make a new vid
    allNames=[]
    for iterator in Exercise.objects.all():
      allNames.append(iterator.name.upper())
    if request.POST['name'].upper() in allNames:
      successMessage="You already have that exercise in the database.  <a href='../addexercise/'>Go Back</a>"
      return render_to_response("success.html", locals())
    newExercise=Exercise(url=request.POST['video'],
         name=request.POST['name'],
         muscleGroup=MuscleGroup.objects.get(id=request.POST['muscleGroup']),
    )


    if 'timed' in request.POST:
      newExercise.timed=True
    if 'oneLimb' in request.POST:
      newExercise.oneLimb=True

    newExercise.minFitnessLevel=FitnessLevel.objects.get(id=request.POST['fitnessLevel'])
    newExercise.minExperience=Experience.objects.get(id=request.POST['experience'])
    if request.POST['compound']=='0':
      newExercise.compound=False
    else:
      newExercise.compound=True
    newExercise.workoutComponent=WorkoutComponent.objects.get(id=int(request.POST['workoutComponent']))
    newExercise.lastModified=datetime.datetime.now()+timedelta(hours=timeDifference)



    if request.POST['workoutComponent2']=='none':
      newExercise.workoutComponent2=None
    else:
      newExercise.workoutComponent2=WorkoutComponent.objects.get(id=int(request.POST['workoutComponent2']))

    if request.POST['workoutComponent3']=='none':
      newExercise.workoutComponent3=None
    else:
      newExercise.workoutComponent3=WorkoutComponent.objects.get(id=int(request.POST['workoutComponent3']))



    if request.POST['mutuallyExclusive']!='none':
      newExercise.mutuallyExclusive=int(request.POST['mutuallyExclusive'])
    else:
      newExercise.mutuallyExclusive=None



    theDay=int((datetime.datetime.today()+timedelta(hours=timeDifference)).weekday())
    if theDay==0:
      newExercise.dayOfWeek="Monday"
    elif theDay==1:
      newExercise.dayOfWeek='Tuesday'
    elif theDay==2:
      newExercise.dayOfWeek='Wednesday'
    elif theDay==3:
      newExercise.dayOfWeek='Thursday'
    elif theDay==4:
      newExercise.dayOfWeek='Friday'
    elif theDay==5:
      newExercise.dayOfWeek='Saturday'
    elif theDay==6:
      newExercise.dayOfWeek='Sunday'

    newExercise.save()


    for iterator in allExerciseTypes:
      if 'exerciseType'+iterator.id.__str__() in request.POST:
        newExercise.exerciseType.add(iterator)


    for iterator in allMuscleGroups:
      if "helper"+(iterator.id).__str__() in request.POST:
        newExercise.helpers.add(iterator)
    allEquipment=Equipment.objects.all()
    for iterator in allEquipment:
      if "equipment"+(iterator.id).__str__() in request.POST:
        newExercise.equipment.add(iterator)

    for iterator in allPhases:
      if (iterator.id).__str__() in request.POST:
        newExercise.phase.add(iterator)
    newExercise.save()



    successMessage="New Exercise successfully added. <a href='../addexercise/'>Add another</a>"
    return render_to_response('success.html', locals())
  return render_to_response('addexercise.html', locals())



def addVolume(request):
  login, superuser = credentials(request)
  allPhases=Phase.objects.all()
  currentFitness=FitnessLevel.objects.all()
  components=WorkoutComponent.objects.all()


  maxPhaseLength=7
  allVolumeTables=[]
  for j in range(1, maxPhaseLength):
    newVolumeTable=VolumeTable()
    newVolumeTable.week=j
    allVolumeTables.append(newVolumeTable)

  if request.method=="POST":
    allWorkoutComponents=WorkoutComponent.objects.all()
    dictionary={}
    for j in range (1, maxPhaseLength):
      newTable=VolumeTable()
      newTable.phase=Phase.objects.get(id=int(request.POST['phase']))
      newTable.fitnessLevel=FitnessLevel.objects.get(id=int(request.POST['fitness']))
      newTable.week=j
      newTable.save()




    for iterator in allWorkoutComponents:
      for j in range(1,maxPhaseLength):
        dictionary[iterator.name+j.__str__()]=Volume()
        dictionary[iterator.name+j.__str__()].workoutComponent=iterator

    for iterator in request.POST:
      if iterator.__str__()!="fitness" and iterator.__str__()!="phase":
        var=iterator.__str__()[0:4]
        oneOrTwo=iterator.__str__()[4:5]
        week=int(iterator.__str__()[5:6])
        key=iterator.__str__()[6:len(iterator.__str__())]
        key=key+week.__str__()

        filteredFitness=FitnessLevel.objects.get(id=int(request.POST['fitness']))
        filteredPhase=Phase.objects.get(id=int(request.POST['phase']))

        if week!=0:
          theParent=VolumeTable.objects.filter(fitnessLevel=filteredFitness,
                                               phase=filteredPhase,
                                               week=week,
          )[0]
          dictionary[key].parentTable=theParent
        if var=="reps":
          if oneOrTwo=="1":
            dictionary[key].minReps=int(request.POST[iterator])
          else:
            dictionary[key].maxReps=int(request.POST[iterator])
        elif var=="sets":
          if oneOrTwo=="1":
            dictionary[key].minSets=int(request.POST[iterator])
          else:
            dictionary[key].maxSets=int(request.POST[iterator])
        elif var=="exer":
          for j in range(1, maxPhaseLength):
            key=key[0:len(key)-1]+j.__str__()
            if oneOrTwo=="1":
              dictionary[key].minExercises=int(request.POST[iterator])
            else:
              dictionary[key].maxExercises=int(request.POST[iterator])
        elif var=="tCar":
          if oneOrTwo=="1":
            theParent.minTimedCardio=int(request.POST[iterator])
          else:
            theParent.maxTimedCardio=int(request.POST[iterator])
          theParent.save()
        elif var=="dCar":
          if oneOrTwo=="1":
            theParent.minDistanceCardio=int(request.POST[iterator])
          else:
            theParent.maxDistanceCardio=int(request.POST[iterator])
          theParent.save()

    for iterator in allWorkoutComponents:
      for j in range(1, maxPhaseLength):
        try:
          dictionary[iterator.name+j.__str__()].save()
        except:
          dictionary[iterator.name+j.__str__()].parentTable=VolumeTable.objects.filter(fitnessLevel=filteredFitness,
                                               phase=filteredPhase,
                                               week=j,
          )[0]
          dictionary[iterator.name+j.__str__()].minReps=0
          dictionary[iterator.name+j.__str__()].maxReps=0
          dictionary[iterator.name+j.__str__()].minSets=0
          dictionary[iterator.name+j.__str__()].maxSets=0
          dictionary[iterator.name+j.__str__()].save()
    successMessage="New volume successfully added"
    return render_to_response('success.html', locals())
  return render_to_response('addvolume.html', locals())

def contact(request):
  login, superuser = credentials(request)
  return render_to_response('contact.html', locals())


##############################################################################################################
##############################################################################################################
##############################################################################################################

def myGoalsNew(request):
  login, superuser = credentials(request)
  allFitnessLevel=FitnessLevel.objects.all()
  allGoals=Goal.objects.all()
  allEquipment=Equipment.objects.all()
  experience=Experience.objects.all()
  allEquipment=listToDimensionalMatrix(allEquipment, 3)



  return render_to_response('mygoalsnew.html', locals())


def createUser(request):
  login, superuser = credentials(request)
  if request.method=="POST":
    #currentUser=User.objects.filter(username=request.session['userID'])[0]
    #userInfoToModify=UserInformation.objects.filter(user=currentUser)[0]
    allEquipment=Equipment.objects.all()

    request.session['goalAge']=request.POST['age']
    request.session['goalGender']=request.POST['gender']
    request.session['goalMinutesPerDay']=request.POST['minutesPerDay']
    request.session['goalDaysPerWeek']=request.POST['daysPerWeek']
    request.session['goalCurrentFitnessLevel']=request.POST['fitnessLevel']
    request.session['goalExperience']=request.POST['experience']
    request.session['goalGoal']=request.POST['goal']

    dayString=""
    somethingChanged=False

    if 'mon' in request.POST:
      dayString=dayString+"0"
      somethingChanged=True
    if 'tues' in request.POST:
      dayString=dayString+"1"
      somethingChanged=True
    if 'wed' in request.POST:
      dayString=dayString+"2"
      somethingChanged=True
    if 'thurs' in request.POST:
      dayString=dayString+"3"
      somethingChanged=True
    if 'fri' in request.POST:
      dayString=dayString+"4"
      somethingChanged=True
    if 'sat' in request.POST:
      dayString=dayString+"5"
      somethingChanged=True
    if 'sun' in request.POST:
      dayString=dayString+"6"
      somethingChanged=True

    request.session['goalDayString']=dayString
#    userInfoToModify.defaultOffDays=dayString


    from django.core.mail import send_mail
#    send_mail("Why I Joined", request.POST['hearUs'].__str__(), 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
    equipmentString=""

    for iterator in allEquipment:
      currentEquipment=Equipment.objects.get(id=iterator.id)
      if (iterator.id).__str__() in request.POST:
        #add equipment to the database
        equipmentString=equipmentString+(iterator.id).__str__()+", "
#stuff will be POSTed from newgoals page
    request.session['goalEquipmentString']=equipmentString[0:len(equipmentString)-2]
  return render_to_response('createuser.html', locals())


###confirmed is a boolean field

def payment(request):
  login =1
  if request.method=='POST':
    fillUsername=request.POST['email']
    fillPassword=request.POST['password']
    request.session['paymentEmail']=fillUsername
    fillConfirmPassword=request.POST['confirmPassword']
    if fillPassword != fillConfirmPassword:
      successMessage="Password and confirm password did not match."
      return render_to_response('success.html', locals())
    fillPassword=generatePassword(fillPassword)
    userToInsert=User(username=fillUsername,
                  password=fillPassword
    )
    existingUser=User.objects.filter(username=fillUsername)
    error=0
    fillRole="user"
    if existingUser:
      existingUser=existingUser[0]
      if existingUser.confirmed:
        successMessage="User account creation failed.  That email address already exists in our database."
        return render_to_response("success.html", locals())
      else:
        existingUser=False
        userToDelete=existingUser
        try:
          userInformationToDelete=UserInformation.objects.filter(user=userToDelete)[0]
          userInformationToDelete.delete()
        except:
          pass
        try:
          userToDelete.delete()
        except:
          pass

    if not existingUser:
      userToInsert.username=request.POST['email'].upper()
      userToInsert.email=request.POST['email']
      userToInsert.confirmed=False
      userToInsert.save()
      request.session['temporaryID']=userToInsert.id
      newUserInfo=UserInformation()
      newUserInfo.user=userToInsert
      try:
        newUserInfo.age=int(request.session['goalAge'])
        newUserInfo.gender=request.session['goalGender']
        newUserInfo.minutesPerDay=int(request.session['goalMinutesPerDay'])
        newUserInfo.daysPerWeek=int(request.session['goalDaysPerWeek'])
        newUserInfo.currentFitnessLevel=FitnessLevel.objects.get(id=int(request.session['goalCurrentFitnessLevel']))
        newUserInfo.experience=Experience.objects.get(id=int(request.session['goalExperience']))
        newUserInfo.goal=Goal.objects.get(id=int(request.session['goalGoal']))
        newUserInfo.defaultOffDays=request.session['goalDayString']
        newUserInfo.previousPhase=None
      except:
        pass
      newUserInfo.save()
      try:
        equipmentList=request.session['goalEquipmentString'].split(',')
        for iterator in equipmentList:
          currentEquipment=Equipment.objects.get(id=int(iterator))
          newUserInfo.equipmentAvailable.add(currentEquipment)
          newUserInfo.save()
      except:
        pass #this means the user has no equipment


  if freeMembership:
    #IF SUCCESSFUL PAYMENT
    request.session['userID']=request.session['paymentEmail']
    checkForUser=User.objects.filter(username=request.session['paymentEmail'])[0]
    request.session['role']=checkForUser.role
    checkForUser.confirmed=True
    checkForUser.payment="authorize"
    checkForUser.ip=request.META.get('REMOTE_ADDR', '<none>')
    checkForUser.subscriptionId=9999
    checkForUser.save()
    from django.core.mail import send_mail
    send_mail("Someone signed up", request.session['paymentEmail'].__str__(), 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)

    message="Welcome to WorkoutGenerator.net!\n\
Your username is "+request.session['paymentEmail'].__str__()+"\n\
Start Date: "+date.today().__str__()+"\n\n\
Thanks,\
WorkoutGenerator.net"
#    send_mail("WorkoutGenerator.net Subscription Receipt", message, 'administrator@oraclefitness.com', [request.session['paymentEmail']], fail_silently=False)
# SBL I think this is where we are at...code sucks....
    return paypal(request)
  return render_to_response('payment.html', locals())

def paypal(request):
    return render_to_response("pay_what_you_want.html", locals())

def payment_flow(request):
    if request.method != "POST":
        return HttpResponseRedirect("/")
    payment_value = int(request.POST['payment_amount'])
    if payment_value == 0:
        return HttpResponseRedirect("/todaysworkout/")
    render_data = {}
    if payment_value == 5:
        render_data["hosted_val"] = "5FUBUL9SZ2Z3C"
        return render_to_response("pay5.html", render_data)
    else:
        render_data["hosted_val"] = "MK3RCKXKVFY3Q"
        return render_to_response("pay5.html", render_data)


##############################################################################################################
##############################################################################################################
##############################################################################################################




def delete(request):
  login, superuser = credentials(request)
  if request.method=='POST':
    if request.POST['type']=='cardio':
      Cardio.objects.get(id=int(request.POST['id'])).delete()
    elif request.POST['type']=='exercise':
      Exercise.objects.get(id=int(request.POST['id'])).delete()
    elif request.POST['type']=='goal':
      Goal.objects.get(id=int(request.POST['id'])).delete()
    elif request.POST['type']=='volume':
      VolumeTable.objects.get(id=int(request.POST['id'])).delete()
    elif request.POST['type']=='frequencyException':
      MuscleFrequency.objects.get(id=int(request.POST['id'])).delete()
    elif request.POST['type']=='cardioAction':
      toDelete=CardioAction.objects.get(id=int(request.POST['id']))
      #now delete the associated intensities
      toDelete.delete()
    elif request.POST['type']=='hardCodedRule':
      HardCodedRule.objects.get(id=int(request.POST['id'])).delete()
    elif request.POST['type']=='comicalStatement':
      ComicalStatement.objects.get(id=int(request.POST['id'])).delete()
    elif request.POST['type']=='article':
      Article.objects.get(id=int(request.POST['id'])).delete()
    successMessage="Delete successful"
  return render_to_response('success.html', locals())

def generateRandomPassword():
  myString=""
  for j in range(0,10):
    var=random.randint(0,25)+65
    if random.randint(0,1):
      var=var+32
    if not random.randint(0,2):
      var=random.randint(2,9)+48
    if chr(var)=='l':
      var=var-1
    elif chr(var)=='O':
      var=var+1
    elif chr(var)=='I':
      var=var-1
    myString=myString+chr(var)
  return myString  #7 character password returned

def iPhone(request, deviceid):
    checkForUser=None
    exists=False
    current_url = request.build_absolute_uri().__str__()
    if 'lite' in current_url:
      deviceid='lite'+deviceid

    deviceid=deviceid.replace("litelite","lite")
    request.session['userID']=deviceid
    try:
      checkForUser=User.objects.filter(username=deviceid)[0]
      exists=True
    except:
      checkForUser=User(username=deviceid)
      checkForUser.password=generatePassword("iphone")
      checkForUser.role="user"
      checkForUser.email="iphone@apple.com"
      checkForUser.payment="appstore"
      exists=False
      checkForUser.ip=request.META['HTTP_X_FORWARDED_FOR']


    request.session['role']=checkForUser.role
    checkForUser.confirmed=True
    checkForUser.subscriptionId=9999
    checkForUser.save()
    if not exists:
      newUserInfo=UserInformation(startDate=date.today())
      newUserInfo.rated=False
      newUserInfo.user=checkForUser
      newUserInfo.save()

      from django.core.mail import send_mail
      send_mail("Someone signed up", request.session['userID'].__str__(), 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
    return 0, exists #this is the return value for login (user does NOT need to login)


def ipn(request):
  message=""
  try:
    if request.method=='POST' and request.POST['txn_type']=='subscr_signup':
      fillUsername=request.POST['payer_email']
      fillUsername=fillUsername.upper()
      fillPassword=generateRandomPassword()
      from django.core.mail import send_mail
      emailAddress=fillUsername
      alreadyExists=OldEmailAddress.objects.filter(email=emailAddress)
      if alreadyExists:
        message="Our records show that you have already signed up with us before and cancelled your account.  Due to the free trial associated with a subscription, please contact administrator@oraclefitness.com if you would still like to use our service."
        send_mail("Error with your sign up", message, 'administrator@oraclefitness.com', [emailAddress], fail_silently=False)
        return
        #need a more elegant solution than this
      message="Thank you for signing up with WorkoutGenerator!  \nYour temporary password is:\n\n"+fillPassword+"\n\nYou can sign in at http://www.WorkoutGenerator.net/signin/ and get started with telling us your goal"
      send_mail("Thank you for signing up with WorkoutGenerator.net", message, 'administrator@oraclefitness.com', [emailAddress], fail_silently=False)


      fillPassword=generatePassword(fillPassword)
      userToInsert=User(username=fillUsername,
                    password=fillPassword
      )
      existingUser=User.objects.filter(username=fillUsername)
      error=0
      if not existingUser:
        userToInsert.email=fillUsername
        userToInsert.confirmed=True
        userToInsert.save()
        newUserInfo=UserInformation()
        newUserInfo.user=userToInsert
        newUserInfo.save()
      OldEmailAddress(email=fillUsername).save()
    elif request.method=='POST' and request.POST['txn_type']=='subscr_cancel':
      pass#cancel the user's membership
      #delete thisweek, delete workouts, delete userinfo, delete user id, del
      try:
        currentUser=User.objects.filter(username=request.POST['payer_email'])[0]
        UserInformation.objects.filter(user=currentUser).delete()
        ThisWeek.objects.filter(user=currentUser).delete()
        TodaysWorkout.objects.filter(user=currentUser).delete()
        currentUser.delete()
  #      if request.POST['payer_email'] in request.session:
  #        del request.session[request.POST['userID']]
        #delete all sessions with this userID
        allSessions=Sessions.objects.all()
        toRemove=[]
        for iterator in allSessions:
          s=iterator.get_decoded()
          if 'userID' in s and s['userID']==request.POST['payer_email'].upper():
            toRemove.append(iterator)
        for iterator in toRemove:
          iterator.delete()
        message=request.POST['payer_email']


        send_mail("Account delete successful", message, 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
      except:
        send_mail("Account delete failed", message, 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
  except:
    pass
  return render_to_response('success.html', locals())


#all we're doing here is getting the IP address of the incoming dude and saving the adnumber as well
def refer(request, adnumber):
  myIp=request.META['HTTP_X_FORWARDED_FOR']
  toSave=IncomingReferral(ip=myIp, adNumber=adnumber)
  toSave.save()
  newURL="http://itunes.apple.com/us/app/workout-generator/id525773174?ls=1&mt=8"
  return HttpResponseRedirect(newURL)


def exerciseLibrary(request, pageNumber):

  login, superuser = credentials(request)

  numberPerPage=30
  import math
  allExercises=Exercise.objects.all().select_related('muscleGroup').order_by('name')
  for iterator in allExercises:
    iterator.name2=iterator.name.replace(' ','_')
    if ',' in iterator.name2 or '/' in iterator.name2 or '-' in iterator.name2 or '(' in iterator.name2 or ')' in iterator.name2:
      iterator.name2=iterator.id
  totalExercises=len(list(allExercises))
  numberPages=float(totalExercises)/float(numberPerPage)  #need to get the ceiling of this
  numberPages=int(math.ceil(numberPages))
  pageNumber=int(pageNumber)
  startNumber=(pageNumber-1)*numberPerPage+1 #NUMBER, not INDEX.  i.e. 1st is index 1
  endNumber=startNumber-1+numberPerPage
  counter=1
  toDisplay=[]
  for iterator in allExercises:
    if iterator.url=="" or iterator.url=="none":
      iterator.video=False
    else:
      iterator.video=True
    if counter >= startNumber and counter <=endNumber:
      #add to ToDisplay
      toDisplay.append(iterator)
    counter=counter+1
  indices=[]
  for j in range (1, numberPages+1):
    indices.append(j)
  next=pageNumber+1
  previous=pageNumber-1

  return render_to_response('exerciselibrary.html', locals())

#(r'^[Vv]iew-exercise-(?P<exercise>\d+)/$',exerciseLibraryLookup),

def exerciseLibraryLookup2(request, exercise):
  #exercise is a string
  newExercise=exercise.replace("_"," ")
  currentE=Exercise.objects.filter(name=newExercise)[0]
  return exerciseLibraryLookup(request, currentE.id)

def exerciseLibraryLookup(request, exercise):

  login, superuser = credentials(request)
  currentExercise=Exercise.objects.get(id=exercise)
  exName=currentExercise.name.__str__()
  lastChar=exName[len(exName)-1:len(exName)]
  currentExercise.pluralName=currentExercise.name.lower()
  sToLast=exName[len(exName)-2:len(exName)-1]
  if lastChar!='s' and lastChar!=')':
    currentExercise.pluralName=currentExercise.name + 's'
  elif sToLast=='s':
    currentExercise.pluralName=currentExercise.name+'es'
  currentExercise.pluralName=currentExercise.pluralName.lower()
  phases=""

  tempPhases=currentExercise.phase.all()
  for iterator in tempPhases:
    phases=phases+iterator.name+", "
  phases=phases[0:len(phases)-2].lower()

  currentExercise.muscleGroup.name=currentExercise.muscleGroup.name.lower()
  myChar=currentExercise.muscleGroup.name.__str__()[0:1]
  word="a"
  if myChar=='a' or myChar=='e' or myChar=='i' or myChar =='o' or myChar=='u':
    word="an"


  numberPerPage=30
  import math
  allExercises=Exercise.objects.all().select_related('muscleGroup').order_by('name')
  totalExercises=len(list(allExercises))
  numberPages=float(totalExercises)/float(numberPerPage)  #need to get the ceiling of this
  numberPages=int(math.ceil(numberPages))


  counter=0
  backNumber=0
  for iterator in allExercises:
    if currentExercise==iterator:
      backNumber=int(math.ceil(float(counter)*float(numberPages)/float(totalExercises)))
      if counter % numberPerPage==0:
        backNumber=backNumber+1
    counter=counter+1
  indices=[]
  for j in range (1, numberPages+1):
    indices.append(j)

  return render_to_response('exercise.html', locals())

def editArticles(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  if request.method=='POST':
    newArticle=Article()
    newArticle.title=request.POST['title']
    newArticle.author=request.POST['author']
    newArticle.url=request.POST['url']
    if request.POST['gender']!='none':
      newArticle.gender=request.POST['gender']
    newArticle.body=request.POST['body']
    newArticle.date=date.today()
    newArticle.save()
    for iterator in request.POST:
      if 'goal' in iterator:
        goalID=int(iterator[4:len(iterator.__str__())])
        newArticle.goal.add(Goal.objects.get(id=goalID))
    newArticle.save()

  allArticles=Article.objects.all()
#need to do allGoals and all genders
#has to be a matrix

#data structure will be a list of dictionaries containing a list
  allObjects=[]
  allGoals=Goal.objects.all()
  for iterator in allGoals:
    newDictionary={}
    newDictionary['goal']=iterator.name
    newDictionary['gender']='male'
    newDictionary['list']=list(Article.objects.filter(gender='male', goal=iterator))
    newDictionary['list'].extend(list(Article.objects.filter(gender=None, goal=iterator)))
    allObjects.append(newDictionary)


    newDictionary2={}
    newDictionary2['goal']=iterator.name
    newDictionary2['gender']='female'
    newDictionary2['list']=list(Article.objects.filter(gender='female', goal=iterator))
    newDictionary2['list'].extend(list(Article.objects.filter(gender=None, goal=iterator)))
    allObjects.append(newDictionary2)


  return render_to_response('editarticles.html', locals())

def editFrequencyExceptions(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  allFrequencies=MuscleFrequency.objects.filter(exception=False)
  if request.method=='POST':
    if 'delete' in request.POST:
      toDelete=MuscleFrequency.objects.get(id=int(request.POST['toDelete']))
      toDelete.delete()
      return render_to_response('editfrequencyexceptions.html', locals())
    newMuscleFrequency=MuscleFrequency(name=request.POST['name'], minimum=int(request.POST['minimum']),
                    maximum=int(request.POST['maximum']), minSets=int(request.POST['minSets']),
                    maxSets=int(request.POST['maxSets']), minReps=int(request.POST['minReps']),
                    maxReps=int(request.POST['maxReps']), exception=True,
    )
    newMuscleFrequency.save()




    for iterator in request.POST:
      if iterator.__str__().find('muscle') != -1:
        muscleGroupId=int(iterator.__str__()[6:len(iterator.__str__())])
        currentMuscleGroup=MuscleGroup.objects.get(id=muscleGroupId)
        currentExceptions=currentMuscleGroup.frequencyException.all()
        for iterator in currentExceptions:
          if iterator.name==newMuscleFrequency.name:
            successMessage="Failed.  You already have an intensity for one of those muscle groups listed."
            newMuscleFrequency.delete()
            return render_to_response('success.html', locals())
        currentMuscleGroup.frequencyException.add(newMuscleFrequency)
        currentMuscleGroup.save()
  currentExceptions=MuscleFrequency.objects.filter(exception=True)
  allMuscleGroups=MuscleGroup.objects.all()

  currentExceptionsCopy=[]
  for exceptionObject in currentExceptions:
    dictionary={}
    dictionary['name']=exceptionObject.name
    dictionary['id']=exceptionObject.id
    dictionary['muscles']=""
    for muscleGroupObject in allMuscleGroups:
      if exceptionObject in muscleGroupObject.frequencyException.all():
        dictionary['muscles']=dictionary['muscles']+muscleGroupObject.name+" "
    currentExceptionsCopy.append(dictionary)
  currentExceptions=currentExceptionsCopy


  return render_to_response('editfrequencyexceptions.html', locals())

def editDescriptions(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  if request.method=='POST':
    currentDescription=Description.objects.get(id=int(request.POST['id']))
    currentDescription.text=request.POST['finalText']
    currentDescription.save()
  allDescriptions=Description.objects.all()
  return render_to_response('editdescriptions.html', locals())



def editGoal(request, goal=None):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  currentGoal=Goal.objects.get(id=goal)
  allPhases=Phase.objects.all()
  allPossiblePhases=currentGoal.phase.all()
  checkedPhases=currentGoal.phase.all()
  allCardioTypes=CardioType.objects.all()
  currentCardio=currentGoal.cardioType
  phaseLengths=PhaseLength.objects.filter(goal=currentGoal)
  phaseDictionaries=[]
  for iterator in phaseLengths:
    dictionary={}
    dictionary['key']='minLength'+iterator.phase.id.__str__()
    dictionary['value']=iterator.minLength
    phaseDictionaries.append(dictionary)
    dictionary2={}
    dictionary2['key']='maxLength'+iterator.phase.id.__str__()
    dictionary2['value']=iterator.maxLength
    phaseDictionaries.append(dictionary2)

  if request.method=="POST":
    goalToModify=Goal.objects.get(id=int(request.POST['goalID']))
    goalToModify.cardioType=CardioType.objects.get(id=int(request.POST['cardioType']))
    goalToModify.name=request.POST['name']
    goalToModify.image=request.POST["image"]
    goalToModify.description.text=request.POST['description']
    goalToModify.description.save()
    goalToModify.startPhase=Phase.objects.get(id=int(request.POST['startPhase']))
    goalToModify.save()
    for iterator in allPhases:
      if (iterator.id).__str__() in request.POST:
        #add equipment to the database
        if not iterator in goalToModify.phase.all():
          goalToModify.phase.add(iterator)
        goalToModify.save()
        alreadyExists=PhaseLength.objects.filter(goal=goalToModify, phase=iterator)
        if alreadyExists:
          alreadyExists=alreadyExists[0]
          alreadyExists.minLength=int(request.POST['minLength'+iterator.id.__str__()])
          alreadyExists.maxLength=int(request.POST['maxLength'+iterator.id.__str__()])
          alreadyExists.save()
        else:
          thisPhaseLength=PhaseLength(goal=goalToModify, phase=iterator,
                                      minLength=int(request.POST['minLength'+iterator.id.__str__()]),
                                      maxLength=int(request.POST['maxLength'+iterator.id.__str__()]),
          )
          thisPhaseLength.save()

      else:
        #potentially delete it from the list of available equipment
        if iterator in goalToModify.phase.all():
          goalToModify.phase.remove(iterator)
          goalToModify.save()
          toDelete=PhaseLength.objects.filter(goal=goalToModify, phase=iterator)
          for iterator in toDelete:
            iterator.delete()



    successMessage="Goals updated"
    return render_to_response('success.html', locals())
  return render_to_response('editgoal.html', locals())

def editGoals(request):

  allGoals=Goal.objects.all()
  newList=[]
  for iterator in allGoals:
    temp={}
    temp['id']=iterator.id
    temp['name']=iterator.name
    temp['cardioType']=iterator.cardioType
    temp['phase']=iterator.phase.all()
    temp['description']=iterator.description
    newList.append(temp)
  allGoals=newList


  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  return render_to_response('editgoals.html', locals())


def editMuscleFrequencies(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())

  if request.method=='POST' and 'case1' in request.POST:
    for iterator in request.POST:
      if 'weekLength' in iterator:
        myId=int(iterator[len('weekLength'):len(iterator)])
        toModify=MuscleFrequency.objects.get(id=myId)
        toModify.weekLength=int(request.POST[iterator])
        toModify.save()
  elif request.method=='POST':
    for iterator in request.POST:
      stringToSplit=iterator.__str__()
      index=stringToSplit.find('_')
      muscleGroupId=int(stringToSplit[0:index])

      stringToSplit=stringToSplit[index+1:len(stringToSplit)]
      index=stringToSplit.find('_')
      phaseId=int(stringToSplit[0:index])

      stringToSplit=stringToSplit[index+1:len(stringToSplit)]
      index=stringToSplit.find('_')
      fitnessLevelId=int(stringToSplit[0:index])

      stringToSplit=stringToSplit[index+1:len(stringToSplit)]
      minOrMax=int(stringToSplit)

      phase=Phase.objects.get(id=phaseId)
      muscleGroup=MuscleGroup.objects.get(id=muscleGroupId)
      fitnessLevel=FitnessLevel.objects.get(id=fitnessLevelId)
      exercisesPerMuscleGroup=ExercisesPerMuscleGroup.objects.filter(phase=phase, muscleGroup=muscleGroup, fitnessLevel=fitnessLevel)
      currentRow=1
      if exercisesPerMuscleGroup:  #this row already exists
        currentRow=exercisesPerMuscleGroup[0]
      else:
        currentRow=ExercisesPerMuscleGroup(phase=phase, muscleGroup=muscleGroup, fitnessLevel=fitnessLevel)
      if minOrMax==1:
        currentRow.minimum=request.POST[iterator]
      else:
        currentRow.maximum=request.POST[iterator]
      currentRow.save()




  allMuscleFrequencies=MuscleFrequency.objects.filter(exception=False)
  allMuscleGroups=MuscleGroup.objects.all()
  allPhases=Phase.objects.all()
  allFitnessLevels=FitnessLevel.objects.all()
  count=ExercisesPerMuscleGroup.objects.count()
  alreadyExists=False
  existingList=[]
  if count > 0:
    alreadyExists=True
    allExercisesPerMuscleGroup=ExercisesPerMuscleGroup.objects.all()
    for iterator in allExercisesPerMuscleGroup:
      dictionary={}
      key=str(iterator.muscleGroup.id) + '_' + str(iterator.phase.id) + '_'+str(iterator.fitnessLevel.id)+'_1'
      value=iterator.minimum
      dictionary['key']=key
      dictionary['value']=value

      dictionary2={}
      key=str(iterator.muscleGroup.id) + '_' + str(iterator.phase.id) +"_" +str(iterator.fitnessLevel.id)+'_2'
      value=iterator.maximum
      dictionary2['key']=key
      dictionary2['value']=value

      existingList.append(dictionary)
      existingList.append(dictionary2)
  allExercisesPerMuscleGroup=ExercisesPerMuscleGroup.objects.all()
  existingList2=[]
  for iterator in allExercisesPerMuscleGroup:
    quickDictionary={}
    quickDictionary['key']=iterator.muscleGroup.id.__str__()+"_"+iterator.phase.id.__str__()+"_"+iterator.fitnessLevel.id.__str__()+"_1"
    quickDictionary['value']=iterator.minimum
    quickDictionary2={}
    quickDictionary2['key']=iterator.muscleGroup.id.__str__()+"_"+iterator.phase.id.__str__()+"_"+iterator.fitnessLevel.id.__str__()+"_2"
    quickDictionary2['value']=iterator.maximum
    existingList2.append(quickDictionary)
    existingList2.append(quickDictionary2)
#(muscleId)_phaseID_min/max






  return render_to_response('editmusclefrequencies.html', locals())


def editPhases(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  allPhases=Phase.objects.all()
  if request.method=='POST':
    for iterator in request.POST:
      phaseToEdit=Phase.objects.get(id=int(iterator[0]))
      if iterator[1:len(iterator)]=='tempo':
        phaseToEdit.tempo=(request.POST[iterator])
      elif iterator[1:len(iterator)]=='rest':
        phaseToEdit.rest=int(request.POST[iterator])
      else:
        phaseToEdit.description.text=request.POST[iterator]
        phaseToEdit.description.save()
      phaseToEdit.save()
    successMessage="Phases saved."
    return render_to_response('success.html', locals())
  return render_to_response('editphases.html', locals())

def editCardio(request, cardio=None):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  currentCardio=CardioIntensityPerFitnessLevel.objects.get(id=cardio)

  allCardio=list(CardioIntensityPerFitnessLevel.objects.all())

  currentIndex=allCardio.index(currentCardio)
  previousIndex=currentIndex-1
  if previousIndex==-1:
    previousIndex=len(allCardio)-1
  nextIndex=currentIndex+1
  if nextIndex==len(allCardio):
    nextIndex=0
  previousIndex=allCardio[previousIndex].id
  nextIndex=allCardio[nextIndex].id



  if request.method=='POST':
    currentCardio.time=int(request.POST['time'])
    currentCardio.rest=int(request.POST['rest'])
    currentCardio.heartRate=int(request.POST['heartRate'])
    currentCardio.distance=int(request.POST['distance'])
    currentCardio.sprintDistance=int(request.POST['sprintDistance'])
    currentCardio.save()
    successMessage="New Cardio successfully saved.  <a href='../editcardios/'>Edit Another</a><br><br><a href='../editcardio"+previousIndex.__str__()+"/'>Previous Cardio</a> <a href='../editcardio"+nextIndex.__str__()+"/'>Next Cardio</a>"

    return render_to_response('success.html', locals())

#  if request.method=='POST':
#    newCardio=Cardio.objects.get(id=int(request.POST['currentCardio']))
#    newCardio.name=request.POST['name']
#    newCardio.equipment=Equipment.objects.get(id=int(request.POST['equipment']))
#    newCardio.description=request.POST['description']
#    newCardio.minFitnessLevel=FitnessLevel.objects.get(id=int(request.POST['fitness']))
#    newCardio.totalTime=int(request.POST['totalTime'])
#    if request.POST['timeOrDistance']=='1':#time
#      newCardio.timeOrDistance=True
#      newCardio.time=int(request.POST['time'])
#      newCardio.heartRate=int(request.POST['heartrate'])
#    else:#distance
#      newCardio.timeOrDistance=False
#      newCardio.sets=int(request.POST['sets'])
#      newCardio.rest=int(request.POST['rest'])
#      newCardio.distance=int(request.POST['distance'])
#    newCardio.save()
#    successMessage="New Cardio successfully added"
#    return render_to_response('success.html', locals())

  return render_to_response('editcardio.html', locals())

def editCardioMaxes(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  allMaxes=CardioMax.objects.all()
  return render_to_response('editcardiomaxes.html', locals())



def editCardios(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  allEquipment=Equipment.objects.all().order_by('name')
  allCardioType=CardioType.objects.all()
  if request.method=='POST':
    if 'newTable' in request.POST:
      #first find if there's any zone table already existing with no crap
      exists=CardioZone.objects.filter(fitnessLevel=None, cardioType=None)
      if exists:
        successMessage="You already have a blank zone table.  Fill that out first.  <a href='../editcardios'>Go back</a>."
        return render_to_response('success.html', locals())
      for j in range(1,4):
        for k in range(1,4):
          newZone=CardioZone()
          newZone.level=j
          newZone.zone=k
          newZone.minInterval=0
          newZone.maxInterval=0
          newZone.minPrevious=0
          newZone.maxPrevious=0
          newZone.minHeartRate=0
          newZone.heartRate=0
          newZone.totalTime=0
          newZone.maxOverall=0
          newZone.save()
          if k==2:
            newZone=CardioZone()
            newZone.level=j
            newZone.zone=k
            newZone.minInterval=0
            newZone.maxInterval=0
            newZone.minPrevious=0
            newZone.maxPrevious=0
            newZone.heartRate=0
            newZone.totalTime=0
            newZone.maxOverall=0
            newZone.save()
    elif 'priority' in request.POST:
      pass
    elif 'hardCodedRule' in request.POST:
      newRule=HardCodedRule()
      newRule.phase=Phase.objects.get(id=int(request.POST['phase']))
      newRule.cardioType=CardioType.objects.get(id=int(request.POST['cardioType']))
      newRule.cardioZone=CardioZone.objects.get(id=int(request.POST['cardioZone']))
      newRule.save()
    elif 'cardiotypes' in request.POST:
      for iterator in request.POST:
        if 'cardiotype' in iterator and iterator!='cardiotypes':
          cardioTypeId=int(iterator[10:len(iterator)])
          toModify=CardioType.objects.get(id=cardioTypeId)
          toModify.minimum=int(request.POST[iterator])
          toModify.save()
    elif 'save' in request.POST:
      allIds=[]
      for iterator in request.POST:
        if 'minInterval' in iterator:
          myId=iterator[11:len(iterator.__str__())]
          myId=int(myId)
          allIds.append(myId)
          toModify=CardioZone.objects.get(id=myId)
          toModify.minInterval=request.POST[iterator]
          toModify.save()
        elif 'maxInterval' in iterator:
          myId=iterator[11:len(iterator.__str__())]
          myId=int(myId)
          allIds.append(myId)
          toModify=CardioZone.objects.get(id=myId)
          toModify.maxInterval=request.POST[iterator]
          toModify.save()
        elif 'minPrevious' in iterator:
          myId=iterator[11:len(iterator.__str__())]
          myId=int(myId)
          allIds.append(myId)
          toModify=CardioZone.objects.get(id=myId)
          toModify.minPrevious=request.POST[iterator]
          toModify.save()
        elif 'maxPrevious' in iterator:
          myId=iterator[11:len(iterator.__str__())]
          myId=int(myId)
          allIds.append(myId)
          toModify=CardioZone.objects.get(id=myId)
          toModify.maxPrevious=request.POST[iterator]
          toModify.save()
        elif 'minHeartRate' in iterator:
          myId=iterator[12:len(iterator.__str__())]
          myId=int(myId)
          allIds.append(myId)
          toModify=CardioZone.objects.get(id=myId)
          toModify.minHeartRate=request.POST[iterator]
          toModify.save()
        elif 'heartRate' in iterator:
          myId=iterator[9:len(iterator.__str__())]
          myId=int(myId)
          allIds.append(myId)
          toModify=CardioZone.objects.get(id=myId)
          toModify.heartRate=request.POST[iterator]
          toModify.save()
        elif 'totalTime' in iterator:
          myId=iterator[9:len(iterator.__str__())]
          myId=int(myId)
          allIds.append(myId)
          toModify=CardioZone.objects.get(id=myId)
          toModify.totalTime=request.POST[iterator]
          toModify.save()
        elif 'maxOverall' in iterator:
          myId=iterator[10:len(iterator.__str__())]
          myId=int(myId)
          allIds.append(myId)
          toModify=CardioZone.objects.get(id=myId)
          toModify.maxOverall=request.POST[iterator]
          toModify.save()
      for iterator in allIds:
        toModify=CardioZone.objects.get(id=iterator)
        for item in toModify.fitnessLevel.all():
          toModify.fitnessLevel.remove(item)
        for item in toModify.cardioType.all():
          toModify.cardioType.remove(item)
        toModify.save()
      for iterator in request.POST:
        if 'fitness' in iterator:
          fitnessId=iterator[7:len(iterator.__str__())]
          toAdd=FitnessLevel.objects.get(id=fitnessId)
          for cardioZoneObject in allIds:
            myZone=CardioZone.objects.get(id=cardioZoneObject)
            myZone.fitnessLevel.add(toAdd)
            myZone.save()
        elif 'cardio' in iterator:
          cardioId=iterator[6:len(iterator.__str__())]
          toAdd=CardioType.objects.get(id=cardioId)
          for cardioZoneObject in allIds:
            myZone=CardioZone.objects.get(id=cardioZoneObject)
            myZone.cardioType.add(toAdd)
            myZone.save()

    else:
      newAction=CardioAction()
      newAction.verb=request.POST['verb']
      newAction.equipment=Equipment.objects.get(id=int(request.POST['equipment']))
      newAction.save()

  #allPriorities=CardioPriority.objects.all()
  allFitnessLevels=FitnessLevel.objects.all()
  allCardioTypes=CardioType.objects.all()
  allPhases=Phase.objects.all()
  allCardioActions=CardioAction.objects.all()
  allCardioZones=list(CardioZone.objects.all())
  row1=[]
  row2=[]
  row3=[]
  allZones=[]
  for iterator in allCardioZones:
    modId=iterator.id % 12
    if modId==0:
      modId=12

    if modId<=4:
      row1.append(iterator)
    elif modId<=8:
      row2.append(iterator)
    else:
      row3.append(iterator)
    if len(row3)==4:
      dictionary={}
      matrix=[]
      matrix.append(row1)
      matrix.append(row2)
      matrix.append(row3)
      row1=[]
      row2=[]
      row3=[]
      dictionary['matrix']=matrix
      dictionary['lastZone']=iterator
      dictionary['fitnessLevels']=iterator.fitnessLevel.all()
      dictionary['cardioTypes']=iterator.cardioType.all()
      hardCodedRules=list(HardCodedRule.objects.all())

      dictionary['hardCodedRules']=[]
      toMatch=-1
      if dictionary['lastZone'].id % 12==0:
        toMatch=(dictionary['lastZone'].id/12)-1
      else:
        toMatch=dictionary['lastZone'].id/12
      for iterator in hardCodedRules:
        category=-1
        if iterator.cardioZone.id % 12 ==0:
          category=(iterator.cardioZone.id/12)-1
        else:
          category=iterator.cardioZone.id/12

        if toMatch==category:
          dictionary['hardCodedRules'].append(iterator)
      allZones.append(dictionary)


#  allZones=[]
#  for j in range(1,4):
#    someTable=[]
#    startZone=CardioZone.objects.filter(fitnessLevel=None, cardioType=None, level=j)
#    someTable.append(startZone)
#    allZones.append(someTable)



#  for outer in allFitnessLevels:
#    for inner in allCardioTypes:
#      someZone=CardioZone.objects.filter(fitnessLevel=outer, cardioType=inner)
#      allZones.append(someZone)
  return render_to_response('editcardios.html', locals())

def editComicalStatements(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  if request.method=='POST':
    if request.POST['gender'] != 'Either':
      ComicalStatement(statement=request.POST['statement'], gender=request.POST['gender']).save()
    else:
      ComicalStatement(statement=request.POST['statement']).save()
  allComicalStatements=ComicalStatement.objects.all()
  return render_to_response('editcomicalstatements.html', locals())

def editExhaustion(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())

  allPhase=Phase.objects.all()
  allFitness=FitnessLevel.objects.all()
  allExperience=Experience.objects.all()
  allMuscles=list(MuscleGroup.objects.all())


  muscleGroupMatrix=[]
  while allMuscles:
    row=[]
    start=allMuscles[0]
    next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
    row.append(start)
    allMuscles.remove(start)
    while next!=start:
      row.append(next)
      try:
        allMuscles.remove(next)
      except:
        pass
      next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)
    if row:
      muscleGroupMatrix.append(row)

  allStrings=[]
  someObject={}
  someObject['name']="Phase"
  someObject['list']=[]
  start=True
  validComponents=[]
  for iterator in list(WorkoutComponent.objects.all()):
    if iterator.name=='Resistance':
      validComponents.append(iterator)

  for phaseObject in allPhase:
    total=0
    myList=[]
    for muscleList in muscleGroupMatrix:
      count=Exercise.objects.filter(Q(workoutComponent__in=validComponents) | Q(workoutComponent2__in=validComponents) | Q(workoutComponent3__in=validComponents), phase__in=[phaseObject], muscleGroup__in=muscleList).count()
      myList.append(count)
      total=total+count
      if start:
        someObject['list'].append(muscleList[0].name)
    start=False
    for j in range (0, len(myList)):
      myList[j]=int(float(myList[j])*100.0/float(total))
    phaseObject.list=myList
  allPhase2=[someObject]
  allPhase2.extend(allPhase)
  allPhase=allPhase2

  if request.method=='POST':
    for iterator in request.POST:
      if 'exhaustion' in iterator:
        myId=int(iterator[len('exhaustion'):len(iterator)])
        toModify=Exhaustion.objects.get(id=myId)
        toModify.percent=int(request.POST[iterator])
        toModify.save()

  allPhase2=Phase.objects.all()
  for iterator in allPhase2:
    myList=[]
    for j in range(1, 8):
      exists=Exhaustion.objects.filter(phase=iterator, daysPerWeek=j)
      if not exists:
        exists=Exhaustion(phase=iterator, daysPerWeek=j, percent=0)
        exists.save()
      else:
        exists=exists[0]
      myList.append(exists)
    iterator.list=myList

  return render_to_response('editexhaustion.html', locals())


def editExercise(request, exercise=None):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  currentExercise=Exercise.objects.get(id=exercise)


  exerciseList=list(Exercise.objects.all())
  currentIndex=exerciseList.index(currentExercise)
  previousIndex=currentIndex-1
  if previousIndex==-1:
    previousIndex=len(exerciseList)-1
  nextIndex=currentIndex+1
  if nextIndex==len(exerciseList):
    nextIndex=0
  previousIndex=exerciseList[previousIndex].id
  nextIndex=exerciseList[nextIndex].id



  allEquipment=Equipment.objects.all().order_by('name')
  allEquipment=listToMatrix(allEquipment)
  allMuscleGroups=MuscleGroup.objects.all().order_by('name')
  allPhases=Phase.objects.all()
  allComponents=WorkoutComponent.objects.all()
  allExerciseTypes=ExerciseType.objects.all()
  checkedPhases=currentExercise.phase.all()
  checkedHelpers=currentExercise.helpers.all()
  checkedEquipment=currentExercise.equipment.all()
  allFitnessLevels=FitnessLevel.objects.all()
  allExperiences=Experience.objects.all()
  currentMuscleGroup=currentExercise.muscleGroup
  matrixMuscleGroup=listToMatrix(allMuscleGroups)
  currentMutex=None
  if currentExercise.mutuallyExclusive:
    currentMutex=currentExercise.mutuallyExclusive


  checkedExerciseTypes=currentExercise.exerciseType.all()

  similarExercises=Exercise.objects.filter(muscleGroup=currentExercise.muscleGroup).order_by('name')
  if request.method=="POST":
    #get the video info, make a new vid
    currentExercise=Exercise.objects.get(id=request.POST["currentID"])
    currentExercise.url=request.POST['video']
    currentExercise.name=request.POST['name']
    currentExercise.workoutComponent=WorkoutComponent.objects.get(id=int(request.POST['workoutComponent']))
    currentExercise.minFitnessLevel=FitnessLevel.objects.get(id=int(request.POST['fitnessLevel']))
    currentExercise.minExperience=Experience.objects.get(id=int(request.POST['experience']))
    currentExercise.muscleGroup=MuscleGroup.objects.get(id=int(request.POST['muscleGroup']))
    if request.POST['workoutComponent2']=='none':
      currentExercise.workoutComponent2=None
    else:
      currentExercise.workoutComponent2=WorkoutComponent.objects.get(id=int(request.POST['workoutComponent2']))

    if request.POST['workoutComponent3']=='none':
      currentExercise.workoutComponent3=None
    else:
      currentExercise.workoutComponent3=WorkoutComponent.objects.get(id=int(request.POST['workoutComponent3']))


    for iterator in allExerciseTypes:
      if 'exerciseType'+iterator.id.__str__() in request.POST:
        currentExercise.exerciseType.add(iterator)
      else:
        if iterator in currentExercise.exerciseType.all():
          currentExercise.exerciseType.remove(iterator)

    currentExercise.lastModified=datetime.datetime.now()+timedelta(hours=timeDifference)
    if request.POST['mutuallyExclusive']!='none':
      currentExercise.mutuallyExclusive=int(request.POST['mutuallyExclusive'])
    else:
      currentExercise.mutuallyExclusive=None
    theDay=int((datetime.datetime.today()+timedelta(hours=timeDifference)).weekday())
    if theDay==0:
      currentExercise.dayOfWeek="Monday"
    elif theDay==1:
      currentExercise.dayOfWeek='Tuesday'
    elif theDay==2:
      currentExercise.dayOfWeek='Wednesday'
    elif theDay==3:
      currentExercise.dayOfWeek='Thursday'
    elif theDay==4:
      currentExercise.dayOfWeek='Friday'
    elif theDay==5:
      currentExercise.dayOfWeek='Saturday'
    elif theDay==6:
      currentExercise.dayOfWeek='Sunday'


    for iterator in allPhases:
      if (iterator.id).__str__() in request.POST:
        currentExercise.phase.add(iterator)
      elif iterator in currentExercise.phase.all():
        currentExercise.phase.remove(iterator)
    for iterator in allMuscleGroups:
      if "helper"+(iterator.id).__str__() in request.POST:
        currentExercise.helpers.add(iterator)
      elif iterator in currentExercise.helpers.all():
        currentExercise.helpers.remove(iterator)
    allEquipment=Equipment.objects.all()
    for iterator in allEquipment:
      if "equipment"+(iterator.id).__str__() in request.POST:
        currentExercise.equipment.add(iterator)
      elif iterator in currentExercise.equipment.all():
        currentExercise.equipment.remove(iterator)

    if 'timed' in request.POST:
      currentExercise.timed=True
    else:
      currentExercise.timed=False

    if 'oneLimb' in request.POST:
      currentExercise.oneLimb=True
    else:
      currentExercise.oneLimb=False


    if request.POST['compound']=='0':
      currentExercise.compound=False
    else:
      currentExercise.compound=True
    currentExercise.save()
    someVar=5
    successMessage="Exercise successfully edited. <a href='../editexercises/'>Edit Another</a><br><br><a href='../editexercise"+previousIndex.__str__()+"/'>Previous Exercise</a> <a href='../editexercise"+nextIndex.__str__()+"/'>Next Exercise</a><br><br><br><a href='../viewmutex/'>Or view mutually exclusive exercises</a>"
    return render_to_response('success.html', locals())

  return render_to_response('editexercise.html', locals())

def editExercises(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  nonFlexComponents=[]
  allComponents=WorkoutComponent.objects.all()
  exercisesStart=Exercise.objects.all()
  for iterator in allComponents:
    if iterator.name!="Flexibility":
      nonFlexComponents.append(iterator)




  if request.method=='POST':
    if request.POST['filterPhase']!='none':
      exercisesStart=exercisesStart.filter(phase__in=[Phase.objects.get(id=int(request.POST['filterPhase']))])
    if request.POST['filterEquipment']!='none':
      exercisesStart=exercisesStart.filter(equipment__in=[Equipment.objects.get(id=int(request.POST['filterEquipment']))])
    if request.POST['filterMuscleGroup']!='none':
      exercisesStart=exercisesStart.filter(muscleGroup__in=[MuscleGroup.objects.get(id=int(request.POST['filterMuscleGroup']))])

    if request.POST['filterWorkoutComponent']!='none':
      exercisesStart=exercisesStart.filter(workoutComponent__in=[WorkoutComponent.objects.get(id=int(request.POST['filterWorkoutComponent']))])
    if request.POST['filterExerciseType']!='none':
      exercisesStart=exercisesStart.filter(exerciseType__in=[ExerciseType.objects.get(id=int(request.POST['filterExerciseType']))])
    if request.POST['filterUrl']!='none':
      if request.POST['filterUrl']=='absent':
        exercisesStart=exercisesStart.filter(Q(url='') | Q(url='none'))
      else:
        exercisesStart=exercisesStart.exclude(Q(url='') | Q(url='none'))
    if request.POST['filterCompound']!='none':
      if request.POST['filterCompound']=='compound':
        exercisesStart=exercisesStart.filter(compound=True)
      else:
        exercisesStart=exercisesStart.filter(compound=False)

    if request.POST['filterTimed']!='none':
      if request.POST['filterTimed']=='timed':
        exercisesStart=exercisesStart.filter(timed=True)
      else:
        exercisesStart=exercisesStart.filter(timed=False)

  allPhases=Phase.objects.all().order_by('name')
  allEquipment=Equipment.objects.all().order_by('name')
  allMuscleGroup=MuscleGroup.objects.all().order_by('name')
  allWorkoutComponent=WorkoutComponent.objects.all().order_by('name')
  allExerciseType=ExerciseType.objects.all()

  exerciseList=[]
  allMuscleGroups=list(MuscleGroup.objects.all())
  alreadyDone=[]
  exerciseMatrix=[]
  for iterator in allMuscleGroups:
    currentMuscleGroup=iterator
    firstMuscleGroup=currentMuscleGroup
    started=False
    muscleCluster=[]
    while firstMuscleGroup!=currentMuscleGroup or not started:
      started=True
      if not currentMuscleGroup.id in muscleCluster and not currentMuscleGroup.id in alreadyDone:
        muscleCluster.append(currentMuscleGroup.id)
      currentMuscleGroup=MuscleGroup.objects.get(id=currentMuscleGroup.relatedMuscleGroup)
    alreadyDone.extend(muscleCluster)
    if muscleCluster:
      exercises=list(exercisesStart.filter(workoutComponent__in=nonFlexComponents, muscleGroup__in=muscleCluster).order_by('muscleGroup','workoutComponent','compound'))
      exerciseMatrix.append(exercises)






  #exercises=list(Exercise.objects.filter(workoutComponent__in=nonFlexComponents).order_by('muscleGroup','workoutComponent','compound'))
#  exercises=exerciseList
  flexExercises=list(exercisesStart.filter(workoutComponent=WorkoutComponent.objects.filter(name="Flexibility")[0]).order_by('muscleGroup','workoutComponent','compound'))
  exerciseMatrix.append(flexExercises)
  newMatrix=[]

  for exercises in exerciseMatrix:
    newList=[]
    for iterator in exercises:
      temp={}
      temp['id']=iterator.id
      temp['name']=iterator.name
      temp['url']=iterator.url
      temp['muscleGroup']=iterator.muscleGroup
      temp['minFitnessLevel']=iterator.minFitnessLevel
      temp['minExperience']=iterator.minExperience
      temp['equipment']=list(iterator.equipment.all())
      temp['workoutComponent']=iterator.workoutComponent
      temp['workoutComponent2']=iterator.workoutComponent2
      temp['workoutComponent3']=iterator.workoutComponent3
      temp['compound']=iterator.compound
      temp['exerciseType']=iterator.exerciseType
      if iterator.lastModified:
        temp['lastModified']=iterator.lastModified
      if iterator.dayOfWeek:
        temp['dayOfWeek']=iterator.dayOfWeek
      myString=""
      tempPhases=iterator.phase.all()
      for iterator in tempPhases:
        myString=myString+iterator.name+", "
      myString=myString[0:len(myString)-2]
      temp['phase']=myString

      newList.append(temp)
    if newList:
      newMatrix.append(newList)
  return render_to_response('editexercises.html', locals())

def editFrequencies(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  allFitnessLevels=FitnessLevel.objects.all()
  return render_to_response('editfrequencies.html', locals())

def editFrequency(request, fitnessLevel):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  currentFitnessLevel=FitnessLevel.objects.get(id=fitnessLevel)
  allPhases=Phase.objects.all()
  allWorkoutComponents=WorkoutComponent.objects.all()
  maxWeeks=7
  allWeeks=[]
  for counter in range(1, maxWeeks):
    allWeeks.append(counter)
  frequencyDictionary={}
  existingFrequencies=Frequency.objects.filter(currentFitnessLevel=currentFitnessLevel)
  alreadyExists=False
  existingList=[]

  if existingFrequencies:
    alreadyExists=True
    for outer in allPhases:
      for inner in allWorkoutComponents:
        for counter in range(1,maxWeeks):
          key1=(outer.id).__str__()+(inner.id).__str__()+counter.__str__()+'1'
          key2=(outer.id).__str__()+(inner.id).__str__()+counter.__str__()+'2'
          currentFrequency=Frequency.objects.filter(phase=outer,
                                     workoutComponent=inner,
                                     currentFitnessLevel=currentFitnessLevel,
                                     week=counter,
          )[0]
          quickDictionary={}
          quickDictionary['key']=key1
          quickDictionary['value']=currentFrequency.minimum
          existingList.append(quickDictionary)

          quickDictionary2={}
          quickDictionary2['key']=key2
          quickDictionary2['value']=currentFrequency.maximum
          existingList.append(quickDictionary2)



  if request.method=='POST':
    currentFitnessLevel=request.POST['currentFitnessLevel']
    for iterator in request.POST:
      if len(iterator.__str__())==4:
        currentPhase=Phase.objects.get(id=iterator[0])
        currentWorkoutComponent=WorkoutComponent.objects.get(id=iterator[1])
        currentWeek=int(iterator[2])
        currentFrequency=Frequency.objects.filter(phase=currentPhase,
                                   workoutComponent=currentWorkoutComponent,
                                   currentFitnessLevel=FitnessLevel.objects.get(id=request.POST['currentFitnessLevel']),
                                   week=currentWeek,
        )
        key=iterator[0]+iterator[1]+iterator[2]
        if currentFrequency:
          currentFrequency=currentFrequency[0]
          if not key in frequencyDictionary:
            frequencyDictionary[key]=currentFrequency
        else:
          if not key in frequencyDictionary:
            frequencyDictionary[key]=Frequency(phase=currentPhase,
                                     workoutComponent=currentWorkoutComponent,
                                     currentFitnessLevel=FitnessLevel.objects.get(id=request.POST['currentFitnessLevel']),
                                     week=currentWeek,
            )
        if iterator[3]=='1':
          frequencyDictionary[key].minimum=int(request.POST[iterator])
        else:
          frequencyDictionary[key].maximum=int(request.POST[iterator])
    #iterate through dictionary, save every objects
    allWorkoutComponents=WorkoutComponent.objects.all()
    for outer in allPhases:
      for inner in allWorkoutComponents:
        for counter in range(1, maxWeeks):
          key=(outer.id).__str__()+(inner.id).__str__()+counter.__str__()
          frequencyDictionary[key].save()
    successMessage="Frequency Table saved"
    return render_to_response('success.html', locals())

#{% for key, value in dictionary.items %}{{value}}{% endfor %}
  return render_to_response('editfrequency.html', locals())



def editVolume(request, volume=None):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  currentVolumeTable=VolumeTable.objects.get(id=volume)


  possibleVolumeTables=VolumeTable.objects.filter(fitnessLevel=currentVolumeTable.fitnessLevel,phase=currentVolumeTable.phase, week=1)[0]

  volumeList=list(VolumeTable.objects.filter(week=1))
  currentIndex=volumeList.index(possibleVolumeTables)
  previousIndex=currentIndex-1
  if previousIndex==-1:
    previousIndex=len(volumeList)-1
  nextIndex=currentIndex+1
  if nextIndex==len(volumeList):
    nextIndex=0
  previousIndex=volumeList[previousIndex].id
  nextIndex=volumeList[nextIndex].id



  currentVolumes=Volume.objects.filter(parentTable=currentVolumeTable)
  allPhases=Phase.objects.all()
  currentFitness=FitnessLevel.objects.all()
  experience=Experience.objects.all()
  components=WorkoutComponent.objects.all()


  maxPhaseLength=7
  allVolumeTables=[]
  for j in range(1, maxPhaseLength):
    newVolumeTable=VolumeTable()
    newVolumeTable.week=j
    allVolumeTables.append(newVolumeTable)

  possibleVolumeTables=VolumeTable.objects.filter(fitnessLevel=currentVolumeTable.fitnessLevel,phase=currentVolumeTable.phase)
  existingList=[]
  for outer in possibleVolumeTables:#.week
    dictionary10={}
    dictionary20={}
    dictionary30={}
    dictionary40={}

    key="tCar1"+(outer.week).__str__()
    value=outer.minTimedCardio
    dictionary10={}
    dictionary10['key']=key
    dictionary10['value']=value
    existingList.append(dictionary10)

    key="tCar2"+(outer.week).__str__()
    value=outer.maxTimedCardio
    dictionary20={}
    dictionary20['key']=key
    dictionary20['value']=value
    existingList.append(dictionary20)

    key="dCar1"+(outer.week).__str__()
    value=outer.minDistanceCardio
    dictionary30={}
    dictionary30['key']=key
    dictionary30['value']=value
    existingList.append(dictionary30)

    key="dCar2"+(outer.week).__str__()
    value=outer.maxDistanceCardio
    dictionary40={}
    dictionary40['key']=key
    dictionary40['value']=value
    existingList.append(dictionary40)

    for inner in components:#.name
      dictionary1={}
      dictionary2={}
      dictionary3={}
      dictionary4={}
      dictionary5={}
      dictionary6={}
      dictionary7={}
      currentVolume=Volume.objects.filter(workoutComponent=inner, parentTable=outer)[0]




      key="reps1" + (outer.week).__str__() + (inner.name).__str__()
      value=currentVolume.minReps
      dictionary1['key']=key
      dictionary1['value']=value
      existingList.append(dictionary1)

      key="reps2" + (outer.week).__str__() + (inner.name).__str__()
      value=currentVolume.maxReps
      dictionary2['key']=key
      dictionary2['value']=value
      existingList.append(dictionary2)

      key="sets1" + (outer.week).__str__() + (inner.name).__str__()
      value=currentVolume.minSets
      dictionary3['key']=key
      dictionary3['value']=value
      existingList.append(dictionary3)

      key="sets2" + (outer.week).__str__() + (inner.name).__str__()
      value=currentVolume.maxSets
      dictionary4['key']=key
      dictionary4['value']=value
      existingList.append(dictionary4)


      key="exer10" + (inner.name).__str__()
      value=currentVolume.minExercises
      dictionary5['key']=key
      dictionary5['value']=value
      existingList.append(dictionary5)

      key="exer20" + (inner.name).__str__()
      value=currentVolume.maxExercises
      dictionary6['key']=key
      dictionary6['value']=value
      existingList.append(dictionary6)

      key="matr1" + (outer.week).__str__() + (inner.name).__str__()
      value=currentVolume.maxTotalReps
      dictionary7['key']=key
      dictionary7['value']=value
      existingList.append(dictionary7)


#  ONLY NEED REPS AND SETS

#class Volume(models.Model):  #Volume for stabilization...another one for muscle endurance, etc
#  minReps=models.IntegerField()
#  maxReps=models.IntegerField()
#  minSets=models.IntegerField()
#  maxSets=models.IntegerField()
#  minExercises=models.IntegerField()
#  maxExercises=models.IntegerField()
  #workoutComponent=models.ForeignKey(WorkoutComponent)
#  parentTable=models.ForeignKey(VolumeTable)



  if request.method=="POST":
    allWorkoutComponents=WorkoutComponent.objects.all()

    dictionary={}
    for iterator in allWorkoutComponents:
      for j in range(1,maxPhaseLength):
        dictionary[iterator.name+j.__str__()]=Volume()
        dictionary[iterator.name+j.__str__()].workoutComponent=iterator

    for iterator in request.POST:
      if iterator.__str__()!="fitness" and iterator.__str__()!="phase":

        var=iterator.__str__()[0:4]
        oneOrTwo=iterator.__str__()[4:5]

        week=int(iterator.__str__()[5:6])

        key=iterator.__str__()[6:len(iterator.__str__())]
        key=key+week.__str__()

        filteredFitness=FitnessLevel.objects.get(id=int(request.POST['fitness']))
        filteredPhase=Phase.objects.get(id=int(request.POST['phase']))

        if week!=0:
          theParent=VolumeTable.objects.filter(fitnessLevel=filteredFitness,
                                               phase=filteredPhase,
                                               week=week,
          )[0]
          if len(key)!=1:
            dictionary[key].parentTable=theParent

        if var=="reps":
          if oneOrTwo=="1":
            dictionary[key].minReps=int(request.POST[iterator])
          else:
            dictionary[key].maxReps=int(request.POST[iterator])
        elif var=="sets":
          if oneOrTwo=="1":
            dictionary[key].minSets=int(request.POST[iterator])
          else:
            dictionary[key].maxSets=int(request.POST[iterator])
        elif var=="exer":
          for j in range(1, maxPhaseLength):
            key=key[0:len(key)-1]+j.__str__()
            if oneOrTwo=="1":
              dictionary[key].minExercises=int(request.POST[iterator])
            else:
              dictionary[key].maxExercises=int(request.POST[iterator])
        elif var=='matr':
          dictionary[key].maxTotalReps=int(request.POST[iterator])
        elif var=="tCar":
          if oneOrTwo=="1":
            theParent.minTimedCardio=int(request.POST[iterator])
          else:
            theParent.maxTimedCardio=int(request.POST[iterator])
          theParent.save()
        elif var=="dCar":
          if oneOrTwo=="1":
            theParent.minDistanceCardio=int(request.POST[iterator])
          else:
            theParent.maxDistanceCardio=int(request.POST[iterator])
          theParent.save()
#    myString=""
    for key, volumeObject in dictionary.items():
#      myString=myString + volumeObject.maxReps.__str__() +" "
      toUpdate=Volume.objects.filter(workoutComponent=volumeObject.workoutComponent, parentTable=volumeObject.parentTable)[0]
      toUpdate.minReps=volumeObject.minReps
      toUpdate.maxReps=volumeObject.maxReps
      toUpdate.minSets=volumeObject.minSets
      toUpdate.maxSets=volumeObject.maxSets
      toUpdate.minExercises=volumeObject.minExercises
      toUpdate.maxExercises=volumeObject.maxExercises
      toUpdate.maxTotalReps=volumeObject.maxTotalReps
      toUpdate.save()
#    return HttpResponse(myString)
    successMessage="Volumes updated successfully.   <a href='../editvolumes/'>Edit Another</a><br><br><a href='../editvolume"+previousIndex.__str__()+"/'>Previous Volume</a> <a href='../editvolume"+nextIndex.__str__()+"/'>Next Volume</a>"
    return render_to_response('success.html', locals())


  return render_to_response('editvolume.html', locals())

def editVolumes(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  allVolumes=VolumeTable.objects.filter(week=1)
  return render_to_response('editvolumes.html', locals())

def emailWorkout(request):
  login, superuser = credentials(request)

  currentUser=User.objects.filter(username=request.session['userID'])[0]
#  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  currentDateTime=datetime.datetime(year=int(request.POST['year']), month=int(request.POST['month']), day=int(request.POST['day']))


  todaysWorkout=TodaysWorkout.objects.filter(user=currentUser, date=currentDateTime)[0]
  todaysExercises=todaysWorkout.exercises.all()


  flexComponent=WorkoutComponent.objects.filter(name='Flexibility')[0]
  existingWorkout=todaysWorkout
  if existingWorkout:
    todaysExercises=list(existingWorkout.exercises.all())

    for iterator in todaysExercises:
      if iterator.superSet:
        iterator.superSet=Series.objects.get(id=iterator.superSet)

    for iterator in todaysExercises:
      if iterator.exercise.timed:
        iterator.reps=''

      if iterator.exercise.workoutComponent==flexComponent:
        iterator.rest=''
      elif iterator.exercise.workoutComponent.name=='Resistance':
        iterator.rest=float(iterator.rest)/60.0
        if float(iterator.rest)==float(int(iterator.rest)):
          iterator.rest=int(iterator.rest)
          iterator.rest=iterator.rest.__str__()+ "m"
        else:
          if float(iterator.rest)<1.0:
            iterator.rest=int(iterator.rest*60.0).__str__()+"s"
          else:
            minutes=int(iterator.rest)
            seconds=int((iterator.rest-float(int(iterator.rest)))*60.0)
            iterator.rest=minutes.__str__()+"m, "+seconds.__str__()+"s"
      else:
        iterator.rest='45s'



  emailAddress=request.POST['email']
  message=""
  for seriesObject in todaysExercises:
    if seriesObject.exercise.workoutComponent!=flexComponent:
      message=message+seriesObject.sets.__str__()+" x "+seriesObject.reps.__str__()+" reps of "+seriesObject.exercise.name+" (http://www.youtube.com/watch?v="+seriesObject.exercise.url+") "
      if seriesObject.superSet:
        message=message+" superset with "+seriesObject.superSet.exercise.name+" (http://www.youtube.com/watch?v="+seriesObject.superSet.exercise.url+") "
      message=message+" at "+seriesObject.rest.__str__()+" rest with a tempo of "+seriesObject.tempo.__str__()+"\n\n"
    else:
      message=message+seriesObject.sets.__str__()+" x "+seriesObject.exercise.name+"\nhttp://www.youtube.com/watch?v="+seriesObject.exercise.url+"\n\n"


#text_content = 'This is an important message.'
#html_content = '<p>This is an <strong>important</strong> message.</p>'
#msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
#msg.attach_alternative(html_content, "text/html")
#msg.send()




  if todaysWorkout.cardio:
    cardioString=""
    canUse=True
    for iterator in todaysWorkout.cardio:
      if iterator=='<':
        canUse=False
      elif iterator=='>':
        canUse=True
      elif canUse:
        cardioString=cardioString+iterator
    message=message+cardioString


  from django.core.mail import send_mail
  try:
    send_mail("Today's Workout brought to you by WorkoutGenerator.net", message, 'administrator@oraclefitness.com', [emailAddress], fail_silently=False)
    successMessage="Email sent.  <a href='../todaysworkout/'>Go Back</a>"
  except:
    successMessage="Invalid email address.  <a href='../todaysworkout/'>Go Back</a>"

###

  userAgent=request.META['HTTP_USER_AGENT']
  if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
    return render_to_response("successiphone.html", locals())
###

  return render_to_response('success.html', locals())

def faq(request):
  login, superuser = credentials(request)
#  request.session['usePhoto']=False
  return render_to_response('faq.html', locals())

def forgotPassword(request):
  login, superuser = credentials(request)

  if request.method=='POST':
    existingUser=User.objects.filter(username=request.POST['email'])
    if not existingUser:
      successMessage="Sorry, that email address doesn't exist in our records.  <a href='../forgotpassword'>Go back</a>."
      return render_to_response('success.html',locals())
    existingUser=existingUser[0]
    alternatePassword=generateRandomPassword()
    from django.core.mail import send_mail
    message="A request was just made for a new password to your user account at WorkoutGenerator.net.  If this request was made in error, your existing password will still work.  However, your temporary, alternate password is:\n\n"+alternatePassword+"\n\nSign in at http://www.WorkoutGenerator.net/signin/"

    send_mail("Your new password for WorkoutGenerator.net", message, 'administrator@oraclefitness.com', [request.POST['email']], fail_silently=False)
    alternatePassword=generatePassword(alternatePassword)
    existingUser.altPassword=alternatePassword
    existingUser.save()
    successMessage="Email sent."
    return render_to_response('forgotpassword.html', locals())

    #find the user
    #reset the user's alt password to a new password
    #email the new password
    #change login so that alt password becomes new password
  return render_to_response('forgotpassword.html', locals())


def fitnessArticles(request):
  login, superuser = credentials(request)
  return render_to_response('fitnessarticles.html', locals())

def funArticles(request):
  login, superuser = credentials(request)
  return render_to_response('funarticles.html', locals())

def guestAuthors(request):
  login, superuser = credentials(request)
  return render_to_response('guestauthors.html', locals())

def localGyms(request):

#import sys, urllib
#showlines = 6
#try:
#    servername, filename = sys.argv[1:]              # cmdline args?
#except:
#    servername, filename = 'starship.python.net', '/index.html'
#
  login, superuser = credentials(request)
  if request.method=='POST':
    try:
      city=request.POST['city']
      state=request.POST['state']
      streetAddress=request.POST['street']
      zipCode=int(request.POST['zipCode'])

      streetAddress=streetAddress.replace(' ','%20')
      city=city.replace(' ','%20')
      import urllib
      remoteaddr = 'http://%s' % 'www.gymticket.com/gyms/'+state+'/'+city+'/?zip='+zipCode.__str__()+'&address='+streetAddress
      remotefile = urllib.urlopen(remoteaddr)              # returns input file object
      remotedata = remotefile.readlines( )                      # read data directly here
      remotefile.close( )
      wholeString=""
      for iterator in remotedata:
        wholeString=wholeString+iterator
      index=wholeString.index("result altColor")+17
      index2=wholeString.index('<div id="majorcityheader">')
      wholeString=wholeString[index:index2]
    except:
      successMessage="No results found."
      return render_to_response('success.html', locals())


#  googleMapsKey="ABQIAAAAdlvXcuDGj1fseuY70wjUyBRQq-fVLVLh7gv5Yay4VuQqbXcAWRTkUc1irQkXuMI6iGZWfYGwa7xAew"
#  googleMapsKey="ABQIAAAAnfs7bKE82qgb3Zc2YyS-oBT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSySz_REpPq-4WZA27OwgbtyR3VcA" #localhost

  return render_to_response('localgyms.html', locals())


#how to use POST
#import httplib, urllib
#>>> params = urllib.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0})
#>>> headers = {"Content-type": "application/x-www-form-urlencoded",
#...            "Accept": "text/plain"}
#>>> conn = httplib.HTTPConnection("musi-cal.mojam.com:80")
#>>> conn.request("POST", "/cgi-bin/query", params, headers)
#>>> response = conn.getresponse()
#>>> print response.status, response.reason
#200 OK
#>>> data = response.read()
#>>> conn.close()

#import urllib
#import urllib2

#url = 'http://www.gymticket.com'
#values = {'zip' : '76548'}

#data = urllib.urlencode(values)
#req = urllib2.Request(url, data)
#response = urllib2.urlopen(req)
#the_page = response.read()




def logout(request):
  if 'userID' in request.session:
    del request.session['userID']

#  request.session['usePhoto']=False
  login, superuser = credentials(request)
  return render_to_response('home.html', locals())

def mostPopular(request):
  login, superuser = credentials(request)
  return render_to_response('mostpopular.html', locals())


def changePassword(request):
  login, superuser = credentials(request)
  if login:
    return signIn(request)

  currentUser=User.objects.filter(username=request.session['userID'])[0]
#  userInformation=UserInformation.objects.filter(user=currentUser)[0]
  if request.method=='POST':
    if request.POST['confirmPassword']!=request.POST['newPassword']:
      successMessage="Your new password and confirmation password did not match.  <a href='../changepassword/'>Go Back</a>."
      return render_to_response('success.html', locals())

    oldPassword=generatePassword(request.POST['oldPassword'])
    if oldPassword!=currentUser.password:
      successMessage="Your old password does not match your existing password.  <a href='../changepassword/'>Go Back</a>."
      return render_to_response('success.html', locals())
    else:
      newPassword=generatePassword(request.POST['newPassword'])
      currentUser.password=newPassword
      currentUser.save()
      successMessage="Password updated."
      return render_to_response('success.html', locals())
  return render_to_response('changepassword.html', locals())



def checkForChanges(dictionary):

  #check for equipment changes
  if not "oldGoal" in dictionary:
    return  #initial setup, no changes
  oldGoal=dictionary["oldGoal"]
  oldExperience=dictionary["oldExperience"]
  oldDaysPerWeek=dictionary["oldDaysPerWeek"]
  oldMinutesPerDay=dictionary["oldMinutesPerDay"]
  oldFitnessLevel=dictionary["oldFitnessLevel"]



  userInfo=dictionary["userInfoToModify"]



  checkedEquipment=dictionary["checkedEquipment"]
  equipmentChanged=False
  newCheckedEquipment=list(userInfo.equipmentAvailable.all())
  if len(newCheckedEquipment)!=len(checkedEquipment):
    equipmentChanged=True
  else:
    for j in range(0,len(checkedEquipment)):
      if newCheckedEquipment[j].id!=checkedEquipment[j].id:
        equipmentChanged=True
  if equipmentChanged:
    existingWorkout=TodaysWorkout.objects.filter(user=dictionary["currentUser"])
    if existingWorkout:
      for iterator in existingWorkout.all():

        for seriesObject in iterator.exercises.all():
          if not seriesObject.exercise.equipment in newCheckedEquipment:
            possibleExercises=Exercise.objects.filter(minFitnessLevel=seriesObject.exercise.minFitnessLevel,
                  minExperience=seriesObject.exercise.minExperience,
                  muscleGroup=seriesObject.exercise.muscleGroup,
                  workoutComponent=seriesObject.exercise.workoutComponent,
            )
            possibleExercises=list(possibleExercises.filter(equipment__in=newCheckedEquipment))

            toRemove=[]
            userEquipment=userInfo.equipmentAvailable.all()
            for exerciseObject in possibleExercises:
              canUse=True
              for equipmentObject in exerciseObject.equipment.all():
                if not equipmentObject in userEquipment:
                  canUse=False
              if not canUse:
                toRemove.append(exerciseObject)
            for iterator in toRemove:
              possibleExercises.remove(iterator)




            if possibleExercises:
              possibleExercises=possibleExercises[random.randint(0, len(possibleExercises)-1)]
              seriesObject.exercise=possibleExercises
              seriesObject.save()
            else:
              try:
                iterator.exercises.remove(seriesObject)
                seriesObject.delete()
              except:
 		pass  #got an error...sloppy, but you gotta do it...
            #just replace it with a different exercise with proper equipment



  else:
    pass

  #check for goal changes
  if oldGoal!=int(dictionary["userInfoToModify"].goal.id):
    if not userInfo.currentPhase is None:  #if NOT nothing's been generated yet, so no harm done or anything
      newGoal=dictionary["userInfoToModify"].goal
      if newGoal.startPhase is None:
        oldPhase=Phase.objects.get(id=int(dictionary["oldPhase"]))
        if oldPhase in newGoal.phase.all():
          userInfo.currentPhase=list(newGoal.phase.all()).index(oldPhase)
          userInfo.previousPhase=None
          userInfo.save()
        else:
          oldDay=int(userInfo.currentDay)
          userInfo.currentPhase=None
          userInfo.previousPhase=None
          existingWeek=ThisWeek.objects.filter(user=dictionary["currentUser"])
          existingWeek.delete()

#        setupWeek(dictionary["currentUser"], dictionary['currentDateTime'])
          userInfo.currentDay=oldDay
          existingWorkout=TodaysWorkout.objects.filter(user=dictionary["currentUser"])
          if existingWorkout:
            existingWorkout.delete()
          userInfo.save()
      else:

        startPhase=newGoal.startPhase
        userInfo.currentPhase=list(newGoal.phase.all()).index(startPhase)
        userInfo.previousPhase=None
        userInfo.currentDay=0
        userInfo.save()
        existingWeek=ThisWeek.objects.filter(user=dictionary["currentUser"])
        try:
          existingWeek.delete()
        except:
          pass#I don't even know if this is necessary, but I'm in the zone right now, there's no time!!!

#    somePhaseLength=PhaseLength.objects.filter(goal=userInfo.goal, phase=myPhase)[0]
#    userInfo.phaseLength=random.randint(somePhaseLength.minLength,somePhaseLength.maxLength)
#    userInfo.currentDay=userInfo.currentDay-1
#    userInfo.save()




  else:
    pass #goal unchanged

  #check for experience changes
  if oldExperience!=int(dictionary["userInfoToModify"].experience.id):
    if dictionary["userInfoToModify"].experience.value<Experience.objects.get(id=oldExperience).value:
      existingWorkout=TodaysWorkout.objects.filter(user=dictionary["currentUser"])
      for iterator in existingWorkout.all():
        for seriesObject in iterator.exercises.all():
          if seriesObject.exercise.minExperience.id==oldExperience:
            possibleExercises=Exercise.objects.filter(minFitnessLevel=seriesObject.exercise.minFitnessLevel,
                  minExperience=dictionary["userInfoToModify"].experience,
                  muscleGroup=seriesObject.exercise.muscleGroup,
                  workoutComponent=seriesObject.exercise.workoutComponent,
            )
            possibleExercises=list(possibleExercises.filter(equipment__in=newCheckedEquipment))

            toRemove=[]
            userEquipment=userInfo.equipmentAvailable.all()
            for exerciseObject in possibleExercises:
              canUse=True
              for equipmentObject in exerciseObject.equipment.all():
                if not equipmentObject in userEquipment:
                  canUse=False
              if not canUse:
                toRemove.append(exerciseObject)
            for iterator in toRemove:
              possibleExercises.remove(iterator)




            if possibleExercises:
              possibleExercises=possibleExercises[random.randint(0, len(possibleExercises)-1)]
              seriesObject.exercise=possibleExercises
              seriesObject.save()
            else:
              iterator.exercises.remove(seriesObject)
              iterator.save()
              seriesObject.delete()

        #find exercises that are now too easy and replace with a harder exercise of same muscle group


  else:
    pass #experience unchanged

  #check for day changes
#this caused some bugs...leave it for next week


#  if oldDaysPerWeek!=int(dictionary["userInfoToModify"].daysPerWeek):
#    setupWeek(dictionary["currentUser"])
#    if dictionary["userInfoToModify"].currentDay>dictionary["userInfoToModify"].daysPerWeek:
#      dictionary["userInfoToModify"].currentDay=0
#      dictionary["userInfoToModify"].save()
#  else:
#    pass #day unchanged

  #check for minutes per day changed
  if oldMinutesPerDay!=int(dictionary["userInfoToModify"].minutesPerDay):
    if dictionary["userInfoToModify"].minutesPerDay < oldMinutesPerDay:
      existingWorkout=TodaysWorkout.objects.filter(user=dictionary["currentUser"])
      for iterator in existingWorkout:
        existingCardio=False
        if iterator.cardio:
          existingCardio=True
        todaysWorkout=reduceToTime(iterator, existingCardio, list(dictionary["userInfoToModify"].goal.phase.all())[dictionary["userInfoToModify"].currentPhase], True, 1, None)
        todaysWorkout.save()
  else:
    pass
 #minutes per day unchanged

  #check for fitness changes
  if oldFitnessLevel!=int(dictionary["userInfoToModify"].currentFitnessLevel.id):
    if dictionary["userInfoToModify"].currentFitnessLevel.value<Experience.objects.get(id=oldFitnessLevel).value:
      existingWorkout=TodaysWorkout.objects.filter(user=dictionary["currentUser"])
      for iterator in existingWorkout.all():
        for seriesObject in iterator.exercises.all():
          if seriesObject.exercise.minFitnessLevel.id==oldFitnessLevel:
            possibleExercises=Exercise.objects.filter(minFitnessLevel=dictionary["userInfoToModify"].currentFitnessLevel,
                  minExperience=seriesObject.exercise.minExperience,
                  muscleGroup=seriesObject.exercise.muscleGroup,
                  workoutComponent=seriesObject.exercise.workoutComponent,
            )
            possibleExercises=list(possibleExercises.filter(equipment__in=newCheckedEquipment))


            toRemove=[]
            userEquipment=userInfo.equipmentAvailable.all()
            for exerciseObject in possibleExercises:
              canUse=True
              for equipmentObject in exerciseObject.equipment.all():
                if not equipmentObject in userEquipment:
                  canUse=False
              if not canUse:
                toRemove.append(exerciseObject)
            for iterator in toRemove:
              possibleExercises.remove(iterator)



            if possibleExercises:
              possibleExercises=possibleExercises[random.randint(0, len(possibleExercises)-1)]
              seriesObject.exercise=possibleExercises
              seriesObject.save()
            else:
              iterator.exercises.remove(seriesObject)
              seriesObject.delete()




    pass #fitness level changed
  else:
    pass #fitness level unchanged

def listToMatrix(someList):
  from math import sqrt
  base=sqrt(len(someList))
  #check and see if base is already an int
  if float(int(base))==base:
    pass#it's a solid number already
  else:
    base=int(base+1.0)  # round up

  base=int(base) #this will get rid of the warnings in apache...for loop truncates the value of base anyway
  counter=0
  matrix=[]
  for j in range(0, base):
    tempList=[]
    for k in range(0, base):
      if counter< len(someList):
        tempList.append(someList[counter])
      counter=counter+1
    matrix.append(tempList)
  return matrix

def listToDimensionalMatrix(someList, cols):

  rows=float(len(someList))/float(cols)
  #check and see if base is already an int
  if float(int(rows))==rows:
    pass#it's a solid number already
  else:
    rows=int(rows+1.0)  # round up

  rows=int(rows) #this will get rid of the warnings in apache...for loop truncates the value of base anyway
  counter=0
  matrix=[]
  for j in range(0, rows):
    tempList=[]
    for k in range(0, cols):
      if counter< len(someList):
        tempList.append(someList[counter])
      counter=counter+1
    matrix.append(tempList)
  return matrix


def setGoalsX(request):
  if request.method=="POST":
###ERROR IS SOMEWHERE RIGHT HERE
    deviceid=request.POST['deviceid']
    login, exists=iPhone(request, deviceid)
    currentUser=User.objects.filter(username=request.session['userID'])[0]
    userInfo=UserInformation.objects.filter(user=currentUser).select_related('currentFitnessLevel','experience','goal')[0]#OPTIMIZE #3
    equipmentDict={}
    experience=Experience.objects.all()
#######

    checkedEquipment=list(userInfo.equipmentAvailable.all())
    if not userInfo.goal is None:
      oldGoal=userInfo.goal.id
      oldExperience=userInfo.experience.id
      oldDaysPerWeek=userInfo.daysPerWeek
      oldMinutesPerDay=userInfo.minutesPerDay
      oldFitnessLevel=userInfo.currentFitnessLevel.id
###good so far
    if userInfo.currentPhase!=None:
      oldPhase=int(list(userInfo.goal.phase.all())[userInfo.currentPhase].id)
    allEquipment2=list(Equipment.objects.all())
    for iterator in allEquipment2:
      key=iterator.id.__str__()
      equipmentDict[key]=iterator
      #allEquipment=Equipment.objects.all()
      allEquipment=[]
      for iterator in allEquipment2:
        allEquipment.append(iterator)
#    userInfoToModify=UserInformation.objects.filter(user=currentUser)[0]

    userInfoToModify=userInfo
    userInfoToModify.age=int(request.POST['age'])
    userInfoToModify.gender=request.POST['gender']
    userInfoToModify.minutesPerDay=int(request.POST['minutesPerDay'])
    userInfoToModify.daysPerWeek=int(request.POST['daysPerWeek'])
    userInfoToModify.currentFitnessLevel=FitnessLevel.objects.get(id=int(request.POST['fitnessLevel']))
    userInfoToModify.experience=Experience.objects.get(id=int(request.POST['experience']))
    userInfoToModify.goal=Goal.objects.get(id=int(request.POST['goal']))
    userInfoToModify.previousPhase=None
    somethingChanged=False
    dayString=""
#I made a dumb mistake here...the days here are actually ON days rather than OFF
    if 'mon' in request.POST:
      dayString=dayString+"0"
      somethingChanged=True
    if 'tues' in request.POST:
      dayString=dayString+"1"
      somethingChanged=True
    if 'wed' in request.POST:
      dayString=dayString+"2"
      somethingChanged=True
    if 'thurs' in request.POST:
      dayString=dayString+"3"
      somethingChanged=True
    if 'fri' in request.POST:
      dayString=dayString+"4"
      somethingChanged=True
    if 'sat' in request.POST:
      dayString=dayString+"5"
      somethingChanged=True
    if 'sun' in request.POST:
      dayString=dayString+"6"
      somethingChanged=True
    actualOffDays="0123456"
    for character in dayString:
      actualOffDays=actualOffDays.replace(character,'')
    userInfoToModify.defaultOffDays=actualOffDays
    if dayString=="" and userInfoToModify.daysPerWeek==7:
      somethingChanged=True
####START RIGHT HERE
   # if somethingChanged or userInfoToModify.defaultOffDays==None or userInfoToModify.defaultOffDays=="":
   #   userInfoToModify.defaultOffDays=dayString

###START

    for iterator in allEquipment:
      #currentEquipment=Equipment.objects.get(id=iterator.id)
      currentEquipment=equipmentDict[iterator.id.__str__()]
      if (iterator.id).__str__() in request.POST:
        #add equipment to the database
        userInfoToModify.equipmentAvailable.add(currentEquipment)
      else:
        #potentially delete it from the list of available equipment
        if currentEquipment in checkedEquipment:
          userInfoToModify.equipmentAvailable.remove(currentEquipment)
######END
    userInfoToModify.save()
    currentDateTime=datetime.datetime(year=int(request.POST['year']), month=int(request.POST['month']), day=int(request.POST['day']))
    checkForChanges(locals())
    return HttpResponse("saved")
  else:
    return HttpResponse("Not a POST method")
  return HttpResponse("error")


def getWeekX(request):
  deviceid=""
  if request.method == "POST":
    deviceid = request.POST['deviceid']
  login, exists = iPhone(request, deviceid)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser).select_related('currentFitnessLevel','experience','goal')[0]#OPTIMIZE #3
  weekDictionary=todaysworkout(request, deviceid)
  myString=""
  newDict={}
  try:
    for key, value in weekDictionary.iteritems():
      pass
  except:
    return weekDictionary
  for key, value in weekDictionary.iteritems():
    if isinstance(value, list) and len(value)>0 and isinstance(value[0], Series):
      #unpack this thing
      toAdd=[]
      for seriesObject in value:
        toAppend={}
        if seriesObject.superSet:
          anotherSeries=Series.objects.get(id=seriesObject.superSet)
          toAppend={'exercise':{'id':anotherSeries.exercise.name, 'name':anotherSeries.exercise.name, 'url':anotherSeries.exercise.url}}
          toAdd.append(toAppend)
        toAppend={'exercise':{'id':seriesObject.exercise.id, 'name':seriesObject.exercise.name, 'url' : seriesObject.exercise.url}}
        toAdd.append(toAppend)
      weekDictionary[key]=toAdd
 # for key, value in weekDictionary.iteritems():
 #   myString=myString+key.__str__()+"...."+toAdd.__str__()+"\n"


  finalDict=simplejson.dumps(weekDictionary)

  return HttpResponse(finalDict)

def test(request):
  allE=Exercise.objects.all()
  myString=""
  for iterator in allE:
    myString=myString+iterator.url+"<br/>"
  return HttpResponse(myString)


def todaysWorkoutX(request):
  deviceid=""
  if request.method == "POST":
    deviceid = request.POST['deviceid']
  login, exists = iPhone(request, deviceid)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser).select_related('currentFitnessLevel','experience','goal')[0]#OPTIMIZE #3
  #what I plan to do is return a todaysWorkout object if something already exists...otherwise I'm going to just call todaysWorkout
  someJunk=todaysworkout(request, deviceid)
  userInfo=UserInformation.objects.filter(user=currentUser).select_related('currentFitnessLevel','experience','goal')[0]#OPTIMIZE #3
  # we have to re-populate the user data
  currentDateTime=datetime.datetime(year=int(request.POST['year']), month=int(request.POST['month']), day=int(request.POST['day']))
  if userInfo.startDate:
    startDate=userInfo.startDate
  else:
    startDate=date.today()
  flexComponent=WorkoutComponent.objects.filter(name='Flexibility')[0]
  existingWorkout=TodaysWorkout.objects.filter(user=currentUser, date=currentDateTime)
    #try again
  if existingWorkout:
    existingWorkout=existingWorkout[0]
    if existingWorkout.offDay:
      allComicals=list(ComicalStatement.objects.filter(Q(gender=userInfo.gender)|Q(gender=None)))
#  allComicals.extend(list(ComicalStatement.objects.filter(gender=None)))
      comicalStatement=allComicals[random.randint(0, len(allComicals)-1)]
      basicDict={}
      basicDict['offDay']=1
      basicDict['comicalStatement']=comicalStatement.statement
      basicDict['phaseLength']=userInfo.phaseLength
      basicDict['myPhase']=myPhase=list(userInfo.goal.phase.all())[userInfo.currentPhase].name
      basicDict['startDate']=startDate.__str__()
      json = simplejson.dumps(basicDict)
      return HttpResponse(json, mimetype='application/json')
    todaysWorkoutX.todaysExercises=list(existingWorkout.exercises.all())

    for iterator in todaysWorkoutX.todaysExercises:
      if iterator.superSet:
        iterator.superSet=Series.objects.get(id=iterator.superSet)


####
    actualRest=0
    try:
      actualRest=float(list(todaysWorkoutX.todaysExercises)[0].rest)/60.0
      if float(actualRest)==float(int(actualRest)):
        actualRest=int(actualRest)
        if actualRest==1:
          actualRest=actualRest.__str__()+" minute"
        else:
          actualRest=actualRest.__str__()+" minutes"
      else:
        if float(actualRest)<1.0:
          actualRest=int(actualRest*60.0).__str__()+ " seconds"
        else:
          minutes=int(actualRest)
          seconds=int((actualRest-float(int(actualRest)))*60.0)
          actualRest=minutes.__str__()+" minutes and "+seconds.__str__()+" seconds"
    except:
      pass
    for iterator in todaysWorkoutX.todaysExercises:
      if iterator.exercise.workoutComponent.name=='Resistance':
        iterator.actualRest=actualRest
      elif iterator.exercise.workoutComponent.name=='Flexibility':
        iterator.actualRest=None
      else:
        iterator.actualRest='45 seconds'


###



    previousComponent='this string could be anything...'
    for iterator in todaysWorkoutX.todaysExercises:
      if iterator.exercise.workoutComponent.name!=previousComponent:
        iterator.change=1
        previousComponent=iterator.exercise.workoutComponent.name
      else:
        iterator.change=0
    for iterator in todaysWorkoutX.todaysExercises:
      if iterator.superSet:
        try:
          iterator.superSet=Series.objects.get(id=iterator.superSet)
        except:
          pass

  #equipmentAvailable=simplejson.dumps(equipmentAvailable)
  #responseDictionary['equipmentAvailable']=equipmentAvailable
  #responseDictionary['minutesPerDay']=userInfo.minutesPerDay
  #responseDictionary['gender']=userInfo.gender
  finalList=[]

  for iterator in todaysWorkoutX.todaysExercises:
    abstractDictionary={}
    abstractDictionary['exercise']=iterator.exercise.name
    abstractDictionary['tempo']=iterator.tempo
    abstractDictionary['rest']=iterator.actualRest
    abstractDictionary['reps']=iterator.reps
    abstractDictionary['sets']=iterator.sets
    abstractDictionary['tempo']=iterator.tempo
    abstractDictionary['change']=iterator.change
    abstractDictionary['component']=iterator.exercise.workoutComponent.name
    abstractDictionary['url']=iterator.exercise.url
    abstractDictionary['id']=iterator.exercise.id
    if iterator.exercise.timed:
      abstractDictionary['timed']="1"
    else:
      abstractDictionary['timed']="0"
    if iterator.superSet:
      nestedDictionary={}
      nestedDictionary['id']=iterator.superSet.exercise.id
      nestedDictionary['exercise']=iterator.superSet.exercise.name
      nestedDictionary['reps']=iterator.superSet.reps
      nestedDictionary['tempo']=iterator.superSet.tempo
      nestedDictionary['rest']=iterator.superSet.rest
      nestedDictionary['tempo']=iterator.superSet.tempo
      nestedDictionary['url']=iterator.superSet.exercise.url
      abstractDictionary['superSet']=simplejson.dumps(nestedDictionary)
    else:
      abstractDictionary['superSet']=-1
    toAdd=simplejson.dumps(abstractDictionary)
    finalList.append(abstractDictionary)
#rponseDictionary['days']=userInfo.defaultOffDays
  finalDictionary={}
  finalDictionary['exercises']=simplejson.dumps(finalList)
  try:
    finalDictionary['cardio']=existingWorkout.cardio
  except:
    finalDictionary['cardio']=""
  finalDictionary['phaseLength']=userInfo.phaseLength
  if userInfo.rated:
    finalDictionary['rated']="1"
  else:
    finalDictionary['rated']="0"

  try:
    finalDictionary['startDate']=startDate.__str__()
  except:
   return HttpResponse("here is the error")
  phaseList=list(userInfo.goal.phase.all())
  #TRY, EXCEPT, DELETE USER!!
  finalDictionary['myPhase']=phaseList[userInfo.currentPhase].name
   # startIndex=phaseList.index(userInfo.goal.startPhase)
     # userInfo.currentPhase


#{% ifequal iterator.name myPhase.name %}
#({{userInfo.phaseLength}} weeks)
#{% endifequal %}
  json = simplejson.dumps(finalDictionary)
  return HttpResponse(json, mimetype='application/json')
  #except Exception, e:
    #return HttpResponse(e.__str__())

def sendRating(request):
  deviceid=""
  if request.method == "GET":
    if request.GET.has_key(u'deviceid'):
      deviceid = request.GET[u'deviceid']
  login, exists=iPhone(request, deviceid)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]#OPTIMIZE #3
  userInfo.rated=True
  userInfo.save()
  return HttpResponse("saved")
def getGoalsX(request):
  deviceid=""
  if request.method == "GET":
    if request.GET.has_key(u'query'):
      deviceid = request.GET[u'query']
  login, exists=iPhone(request, deviceid)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser).select_related('currentFitnessLevel','experience','goal')[0]#OPTIMIZE #3
  if userInfo.goal is None:
    return HttpResponse("nogoal")
  checkedEquipment=list(userInfo.equipmentAvailable.all())
  currentFitness=userInfo.currentFitnessLevel
  currentExperience=userInfo.experience
  isMale=True
  if userInfo.gender and userInfo.gender=='Female':
    isMale=False
  #login will always equal 0...
#response_data['result']='failed'
#response_data['message']='you messed up'
  responseDictionary={}
  responseDictionary['age']=userInfo.age
  responseDictionary['fitnessLevel']=userInfo.currentFitnessLevel.value
  responseDictionary['experience']=userInfo.experience.value
  equipmentAvailable = [ x.id for x in userInfo.equipmentAvailable.all() ]
  equipmentAvailable=simplejson.dumps(equipmentAvailable)
  responseDictionary['equipmentAvailable']=equipmentAvailable
  responseDictionary['minutesPerDay']=userInfo.minutesPerDay
  responseDictionary['gender']=userInfo.gender
  responseDictionary['goal']=userInfo.goal.id
  responseDictionary['days']=userInfo.defaultOffDays
  json = simplejson.dumps(responseDictionary)
  return HttpResponse(json, mimetype='application/json')


def myGoalsiPhone(request, deviceid):
  userAgent=request.META['HTTP_USER_AGENT']
  if not ('iPhone' in userAgent or 'iPod' in userAgent or  'iTouch' in userAgent):
    return myGoals(request)

  login, exists = iPhone(request, deviceid)
  if login:
    return signIn(request)
  allAges=[]
  for j in range(13,99):
    allAges.append(j)
  allMinutes=[]
  for j in range(20, 120):
    allMinutes.append(j)
  allFitnessLevel=FitnessLevel.objects.all()
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser).select_related('currentFitnessLevel','experience','goal')[0]#OPTIMIZE #3


  checkedEquipment=list(userInfo.equipmentAvailable.all())
  currentFitness=userInfo.currentFitnessLevel
  currentExperience=userInfo.experience

  allGoals=Goal.objects.all().select_related('description') #5
  allEquipment=Equipment.objects.all()

  allEquipment=listToDimensionalMatrix(allEquipment, 2)

  isMale=True
  experience=Experience.objects.all()

  if not userInfo.goal is None:
    oldGoal=userInfo.goal.id
    oldExperience=userInfo.experience.id
    oldDaysPerWeek=userInfo.daysPerWeek
    oldMinutesPerDay=userInfo.minutesPerDay
    oldFitnessLevel=userInfo.currentFitnessLevel.id
  if userInfo.currentPhase!=None:
    oldPhase=int(list(userInfo.goal.phase.all())[userInfo.currentPhase].id)

  if userInfo.gender and userInfo.gender=='Female':
    isMale=False



  equipmentDict={}
  allEquipment2=list(Equipment.objects.all())
  for iterator in allEquipment2:
    key=iterator.id.__str__()
    equipmentDict[key]=iterator
  if request.method=="POST":
    #allEquipment=Equipment.objects.all()
    allEquipment=[]
    for iterator in allEquipment2:
      allEquipment.append(iterator)
#    userInfoToModify=UserInformation.objects.filter(user=currentUser)[0]

    userInfoToModify=userInfo
    userInfoToModify.age=int(request.POST['age'])
    userInfoToModify.gender=request.POST['gender']
    userInfoToModify.minutesPerDay=int(request.POST['minutesPerDay'])
    userInfoToModify.daysPerWeek=int(request.POST['daysPerWeek'])
    userInfoToModify.currentFitnessLevel=FitnessLevel.objects.get(id=int(request.POST['fitnessLevel']))
    userInfoToModify.experience=Experience.objects.get(id=int(request.POST['experience']))
    userInfoToModify.goal=Goal.objects.get(id=int(request.POST['goal']))
    userInfoToModify.previousPhase=None
    somethingChanged=False
    dayString=""


    if 'mon' in request.POST:
      dayString=dayString+"0"
      somethingChanged=True
    if 'tues' in request.POST:
      dayString=dayString+"1"
      somethingChanged=True
    if 'wed' in request.POST:
      dayString=dayString+"2"
      somethingChanged=True
    if 'thurs' in request.POST:
      dayString=dayString+"3"
      somethingChanged=True
    if 'fri' in request.POST:
      dayString=dayString+"4"
      somethingChanged=True
    if 'sat' in request.POST:
      dayString=dayString+"5"
      somethingChanged=True
    if 'sun' in request.POST:
      dayString=dayString+"6"
      somethingChanged=True
    if dayString=="" and userInfoToModify.daysPerWeek==7:
      somethingChanged=True

    if len(dayString)<7-userInfoToModify.daysPerWeek and not '6' in dayString:
      dayString=dayString+'6'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '5' in dayString:
      dayString=dayString+'5'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '4' in dayString:
      dayString=dayString+'4'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '3' in dayString:
      dayString=dayString+'3'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '2' in dayString:
      dayString=dayString+'2'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '1' in dayString:
      dayString=dayString+'1'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '0' in dayString:
      dayString=dayString+'0'
    if somethingChanged or userInfoToModify.defaultOffDays==None or userInfoToModify.defaultOffDays=="":
      userInfoToModify.defaultOffDays=dayString
    for iterator in allEquipment:
      #currentEquipment=Equipment.objects.get(id=iterator.id)
      currentEquipment=equipmentDict[iterator.id.__str__()]
      if (iterator.id).__str__() in request.POST:
        #add equipment to the database
        userInfoToModify.equipmentAvailable.add(currentEquipment)
      else:
        #potentially delete it from the list of available equipment
        if currentEquipment in checkedEquipment:
          userInfoToModify.equipmentAvailable.remove(currentEquipment)

    userInfoToModify.save()
    currentDateTime=datetime.datetime(year=int(request.POST['year']), month=int(request.POST['month']), day=int(request.POST['day']))

    checkForChanges(locals())


    successMessage="Goals updated.  Check out today's workout!  Some changes won't take effect until next week."
    return render_to_response('successiphone.html', locals())

  current_url = request.build_absolute_uri().__str__()
  if 'lite' in current_url:
    return render_to_response('mygoalsiphonelite.html', locals())


  return render_to_response('mygoalsiphone.html', locals())

def myGoals(request):
  #todo: scrap today's workout upon update
  login, superuser = credentials(request)
  if login:
    return signIn(request)

  allFitnessLevel=FitnessLevel.objects.all()  #1
  currentUser=User.objects.filter(username=request.session['userID'])[0] #2
  userInfo=UserInformation.objects.filter(user=currentUser).select_related('currentFitnessLevel','experience','goal')[0]#OPTIMIZE #3
  checkedEquipment=list(userInfo.equipmentAvailable.all()) #4
  currentFitness=userInfo.currentFitnessLevel
  currentExperience=userInfo.experience



  allGoals=Goal.objects.all().select_related('description') #5
  allEquipment=Equipment.objects.all() #6

  allEquipment=listToDimensionalMatrix(allEquipment, 3)

  isMale=True
  experience=Experience.objects.all() #7

  if not userInfo.goal is None:
    oldGoal=userInfo.goal.id
    oldExperience=userInfo.experience.id
    oldDaysPerWeek=userInfo.daysPerWeek
    oldMinutesPerDay=userInfo.minutesPerDay
    oldFitnessLevel=userInfo.currentFitnessLevel.id
  if userInfo.currentPhase!=None:
    oldPhase=int(list(userInfo.goal.phase.all())[userInfo.currentPhase].id)#8

  if userInfo.gender and userInfo.gender=='Female':
    isMale=False

  equipmentDict={}
  allEquipment2=list(Equipment.objects.all())
  for iterator in allEquipment2:
    key=iterator.id.__str__()
    equipmentDict[key]=iterator
  if request.method=="POST":
    #allEquipment=Equipment.objects.all()
    allEquipment=[]
    for iterator in allEquipment2:
      allEquipment.append(iterator)
#    userInfoToModify=UserInformation.objects.filter(user=currentUser)[0]
    userInfoToModify=userInfo
    userInfoToModify.age=int(request.POST['age'])
    userInfoToModify.gender=request.POST['gender']
    userInfoToModify.minutesPerDay=int(request.POST['minutesPerDay'])
    userInfoToModify.daysPerWeek=int(request.POST['daysPerWeek'])
    userInfoToModify.currentFitnessLevel=FitnessLevel.objects.get(id=int(request.POST['fitnessLevel']))
    userInfoToModify.experience=Experience.objects.get(id=int(request.POST['experience']))
    userInfoToModify.goal=Goal.objects.get(id=int(request.POST['goal']))
    userInfoToModify.previousPhase=None
    somethingChanged=False
    dayString=""


    if 'mon' in request.POST:
      dayString=dayString+"0"
      somethingChanged=True
    if 'tues' in request.POST:
      dayString=dayString+"1"
      somethingChanged=True
    if 'wed' in request.POST:
      dayString=dayString+"2"
      somethingChanged=True
    if 'thurs' in request.POST:
      dayString=dayString+"3"
      somethingChanged=True
    if 'fri' in request.POST:
      dayString=dayString+"4"
      somethingChanged=True
    if 'sat' in request.POST:
      dayString=dayString+"5"
      somethingChanged=True
    if 'sun' in request.POST:
      dayString=dayString+"6"
      somethingChanged=True
    if dayString=="" and userInfoToModify.daysPerWeek==7:
      somethingChanged=True

    if len(dayString)<7-userInfoToModify.daysPerWeek and not '6' in dayString:
      dayString=dayString+'6'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '5' in dayString:
      dayString=dayString+'5'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '4' in dayString:
      dayString=dayString+'4'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '3' in dayString:
      dayString=dayString+'3'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '2' in dayString:
      dayString=dayString+'2'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '1' in dayString:
      dayString=dayString+'1'
    if len(dayString)<7-userInfoToModify.daysPerWeek and not '0' in dayString:
      dayString=dayString+'0'
    if somethingChanged or userInfoToModify.defaultOffDays==None or userInfoToModify.defaultOffDays=="":
      userInfoToModify.defaultOffDays=dayString
    for iterator in allEquipment:
#      currentEquipment=Equipment.objects.get(id=iterator.id)
      currentEquipment=equipmentDict[iterator.id.__str__()]
      if (iterator.id).__str__() in request.POST:
        #add equipment to the database
        userInfoToModify.equipmentAvailable.add(currentEquipment)
      else:
        #potentially delete it from the list of available equipment
        if currentEquipment in checkedEquipment:
          userInfoToModify.equipmentAvailable.remove(currentEquipment)

    userInfoToModify.save()
    currentDateTime=datetime.datetime(year=int(request.POST['year']), month=int(request.POST['month']), day=int(request.POST['day']))

    checkForChanges(locals())


    successMessage="Goals updated.  Check out <a href='../todaysworkout'> today's workout!</a>  Some changes won't take effect until next week."
    return render_to_response('success.html', locals())
  return render_to_response('mygoals.html', locals())



def newThread(request):
  login, superuser = credentials(request)
  if request.method=='POST':
    newThread=Thread(name=request.POST['name'])
    newThread.save()
    successMessage="Thread added.  <a href='../newthread'>Add another</a>"
    return render_to_response('success.html', locals())
  return render_to_response('newthread.html', locals())

def newAdmin(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())
  if request.method=='POST':
    fillUsername=request.POST['username'].upper()
    fillPassword=request.POST['password']
    fillConfirmPassword=request.POST['confirmPassword']
    if fillPassword != fillConfirmPassword:
      passwordError =1
      return render_to_response('newadmin.html', locals())
    fillPassword=generatePassword(fillPassword)
    userToInsert=User(username=fillUsername,
                  password=fillPassword,
    )
    if request.POST['isAdmin']=='1':
      userToInsert.role="superuser"
    existingUser=User.objects.filter(username=fillUsername)
    error=0
    fillRole="superuser"
    if not existingUser:
      userToInsert.save()
#      request.session['userID']=fillUsername
#      request.session['role']=fillRole
      newUserInfo=UserInformation()
      newUserInfo.user=userToInsert
      newUserInfo.save()
      successMessage="New Admin successfully added."
      login, superuser = credentials(request)
      return render_to_response("success.html", locals())
    else:
      error=1

  return render_to_response('newadmin.html', locals())





def newUser(request):
  login, superuser = credentials(request)
  if request.method=='POST':
    fillUsername=request.POST['username']
    fillPassword=request.POST['password']
    fillConfirmPassword=request.POST['confirmPassword']
    if fillPassword != fillConfirmPassword:
      passwordError =1
      return render_to_response('newuser.html', locals())
    fillPassword=generatePassword(fillPassword)
    userToInsert=User(username=fillUsername,
                  password=fillPassword
    )
    existingUser=User.objects.filter(username=fillUsername)
    error=0
    fillRole="user"
    if not existingUser:
#      import httplib, urllib
#      params = urllib.urlencode({'cmd': '_s-xclick', 'hosted_button_id': '45247'})
#      headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
#      conn = httplib.HTTPSConnection("www.sandbox.paypal.com:443")
#      conn.request("POST", "/cgi-bin/webscr", params, headers)
#      response = conn.getresponse()
#      conn.close()
#      return HttpResponse(response)
#      print response.status, response.reason
#      data=response.read()
#      conn.close()




#how to use POST
#import httplib, urllib
#>>> params = urllib.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0})
#>>> headers = {"Content-type": "application/x-www-form-urlencoded",
#...            "Accept": "text/plain"}
#>>> conn = httplib.HTTPConnection("musi-cal.mojam.com:80")
#>>> conn.request("POST", "/cgi-bin/query", params, headers)
#>>> response = conn.getresponse()
#>>> print response.status, response.reason
#200 OK
#>>> data = response.read()
#>>> conn.close()

#<form action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post">
#<input type="hidden" name="cmd" value="_s-xclick">
#<input type="hidden" name="hosted_button_id" value="45247">
#<input type="image"
#src="https://www.sandbox.paypal.com/en_US/i/btn/btn_subscribeCC_LG.gif"
#border="0" name="submit" alt="PayPal - The safer, easier way to pay
#online!">
#<img alt="" border="0"
#src="https://www.sandbox.paypal.com/en_US/i/scr/pixel.gif" width="1"
#height="1">
#</form>








      userToInsert.email=request.POST['email']
      userToInsert.confirmed=False
      userToInsert.save()
      request.session['userID']=fillUsername
      request.session['role']=fillRole
      newUserInfo=UserInformation()
      newUserInfo.user=userToInsert
      newUserInfo.save()
      successMessage="New User successfully added.  <a href='../mygoals'>Tell us your goal</a> so that we can start generating your workouts!"
      login, superuser = credentials(request)
      return render_to_response("success.html", locals())
    else:
      error=1

  return render_to_response('newuser.html', locals())

def blog(request):
  login, superuser = credentials(request)
  return render_to_response('blog.html', locals())



def weightLifting(request):
  login, superuser = credentials(request)
  return render_to_response('weightlifting.html', locals())

def cardio(request):
  login, superuser = credentials(request)
  return render_to_response('cardio.html', locals())

def cardioMax(request, cardio=None):
  login, superuser = credentials(request)
  currentMax=CardioMax.objects.get(id=cardio)


  allMaxes=list(CardioMax.objects.all())
  currentIndex=allMaxes.index(currentMax)
  previousIndex=currentIndex-1
  if previousIndex==-1:
    previousIndex=len(allMaxes)-1
  nextIndex=currentIndex+1
  if nextIndex==len(allMaxes):
    nextIndex=0
  previousIndex=allMaxes[previousIndex].id
  nextIndex=allMaxes[nextIndex].id

  if request.method=='POST':
    currentMax.loMaximum=int(request.POST['low'])
    currentMax.medMaximum=int(request.POST['medium'])
    currentMax.hiMaximum=int(request.POST['high'])
    currentMax.save()
    successMessage="Max successfully saved. <a href='../editcardiomaxes/'>Edit Another</a><br><br><a href='../cardiomax"+previousIndex.__str__()+"/'>Previous Max</a> <a href='../cardiomax"+nextIndex.__str__()+"/'>Next Max</a>"
    return render_to_response('success.html', locals())
  return render_to_response('cardiomax.html', locals())


def nutrition(request):
  login, superuser = credentials(request)
  return render_to_response('nutrition.html', locals())


def tour(request):
  login, superuser = credentials(request)
  allGoals=Goal.objects.all()
  return render_to_response('tour.html', locals())


def gyms(reqyest):
  return render_to_response('gyms.html', locals())

def printFriendly(request):
  login, superuser = credentials(request)
  currentUser=User.objects.filter(username=request.session['userID'])[0]

  currentDateTime=False
  if request.method=='POST' and 'year' in request.POST:
    currentDateTime=datetime.datetime(year=int(request.POST['year']), month=int(request.POST['month']), day=int(request.POST['day']))
  if not currentDateTime:
    needTime=True
    return render_to_response("printfriendly.html", locals())

  flexComponent=WorkoutComponent.objects.filter(name='Flexibility')[0]
  existingWorkout=TodaysWorkout.objects.filter(user=currentUser, date=currentDateTime)
  if existingWorkout:
    existingWorkout=existingWorkout[0]
    todaysExercises=list(existingWorkout.exercises.all())


    for iterator in todaysExercises:
      if iterator.superSet:
        iterator.superSet=Series.objects.get(id=iterator.superSet)



    for iterator in todaysExercises:
      iterator.setsList=[]
      for j in range (1, iterator.sets+1):
        iterator.setsList.append(j)
      if iterator.exercise.timed:
        iterator.reps=''

      if iterator.exercise.workoutComponent==flexComponent:
        iterator.rest=''
      elif iterator.exercise.workoutComponent.name=='Resistance':
        iterator.rest=float(iterator.rest)/60.0
        if float(iterator.rest)==float(int(iterator.rest)):
          iterator.rest=int(iterator.rest)
          iterator.rest=iterator.rest.__str__()+ "m"
        else:
          if float(iterator.rest)<1.0:
            iterator.rest=int(iterator.rest*60.0).__str__()+"s"
          else:
            minutes=int(iterator.rest)
            seconds=int((iterator.rest-float(int(iterator.rest)))*60.0)
            iterator.rest=minutes.__str__()+"m, "+seconds.__str__()+"s"
      else:
        iterator.rest='45s'



    previousComponent='this string could be anything...'
    for iterator in todaysExercises:
      if iterator.exercise.workoutComponent.name!=previousComponent:
        iterator.change=1
        previousComponent=iterator.exercise.workoutComponent.name
      else:
        iterator.change=0
    for iterator in todaysExercises:
      if iterator.superSet:
        try:
          iterator.superSet=Series.objects.get(id=iterator.superSet)
        except:
          pass


  return render_to_response('printfriendly.html', locals())



def printEntireWeek(request):
  login, superuser = credentials(request)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
#get thisWeek for particular user id, sort thisWeek by DayNumber, then get the corresponding todaysw rokout


  flexComponent=WorkoutComponent.objects.filter(name='Flexibility')[0]
  existingWorkouts=TodaysWorkout.objects.filter(user=currentUser).order_by('date')
  if not existingWorkouts:
    pass
  outer=[]
  for outerIterator in existingWorkouts:
    dictionary={}
    existingWorkout=outerIterator
    existingWorkout.visited=True
    existingWorkout.save()
    todaysExercises=list(existingWorkout.exercises.all())


    for iterator in todaysExercises:
      if iterator.superSet:
        iterator.superSet=Series.objects.get(id=iterator.superSet)



    for iterator in todaysExercises:
      iterator.setsList=[]
      for j in range (1, iterator.sets+1):
        iterator.setsList.append(j)
      if iterator.exercise.timed:
        iterator.reps=''

      if iterator.exercise.workoutComponent==flexComponent:
        iterator.rest=''
      elif iterator.exercise.workoutComponent.name=='Resistance':
        iterator.rest=float(iterator.rest)/60.0
        if float(iterator.rest)==float(int(iterator.rest)):
          iterator.rest=int(iterator.rest)
          iterator.rest=iterator.rest.__str__()+ "m"
        else:
          if float(iterator.rest)<1.0:
            iterator.rest=int(iterator.rest*60.0).__str__()+"s"
          else:
            minutes=int(iterator.rest)
            seconds=int((iterator.rest-float(int(iterator.rest)))*60.0)
            iterator.rest=minutes.__str__()+"m, "+seconds.__str__()+"s"
      else:
        iterator.rest='45s'



    previousComponent='this string could be anything...'
    for iterator in todaysExercises:
      if iterator.exercise.workoutComponent.name!=previousComponent:
        iterator.change=1
        previousComponent=iterator.exercise.workoutComponent.name
      else:
        iterator.change=0
    for iterator in todaysExercises:
      if iterator.superSet:
        try:
          iterator.superSet=Series.objects.get(id=iterator.superSet)
        except:
          pass
    dictionary['todaysExercises']=todaysExercises
    intDay=existingWorkout.date.isoweekday()
    if intDay==1:
      intDay="Monday"
    elif intDay==2:
      intDay="Tuesday"
    elif intDay==3:
      intDay="Wednesday"
    elif intDay==4:
      intDay="Thursday"
    elif intDay==5:
      intDay="Friday"
    elif intDay==6:
      intDay="Saturday"
    elif intDay==7:
      intDay="Sunday"

    dictionary['date']=intDay
    dictionary['date2']=existingWorkout.date
    if existingWorkout.cardio:
      dictionary['cardio']=existingWorkout.cardio
    outer.append(dictionary)
  return render_to_response('printentireweek.html', locals())

def componentDescriptions(request):
  login, superuser = credentials(request)
  return render_to_response('componentdescription.html', locals())

def phaseDescriptions(request):
  login, superuser = credentials(request)
  return render_to_response('phasedescription.html', locals())


def privacyPolicy(request):
  login, superuser = credentials(request)
#  request.session['usePhoto']=False
  return render_to_response('privacypolicy.html', locals())

def termsOfService(request):
  login, superuser = credentials(request)
#  request.session['usePhoto']=False
  return render_to_response('termsofservice.html', locals())


def avoidedExercises(request):
  login, superuser = credentials(request)
  if login:
    return signIn(request)

  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]



def enableMuscleGroup(request, muscleGroup=None):
  login, superuser = credentials(request)
  if login:
    return signIn(request)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  try:
    userInfo.avoidedMuscleGroup.remove(MuscleGroup.objects.get(id=muscleGroup))
    userInfo.save()
  except:
    pass
  return disableMuscleGroups(request)

def disableMuscleGroup(request, muscleGroup=None):
  login, superuser = credentials(request)
  if login:
    return signIn(request)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  userInfo.avoidedMuscleGroup.add(MuscleGroup.objects.get(id=muscleGroup))

  userInfo.save()
  return disableMuscleGroups(request)



def disableMuscleGroups(request, deviceid=None):
  login, superuser = credentials(request)
  if login:
    return signIn(request)
  userAgent=request.META['HTTP_USER_AGENT']
  if deviceid != None and ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
    junk, exists = iPhone(request, deviceid)
    if not exists:
      successMessage="You haven't set any goals yet.  Please see \"My Goals\""
      return render_to_response("successiphone.html", locals())


  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  allMuscleGroups=MuscleGroup.objects.all().order_by('name')
  allAvoids=userInfo.avoidedMuscleGroup.all()
  for iterator in allMuscleGroups:
    if iterator in allAvoids:
      iterator.enabled=False
    else:
      iterator.enabled=True
  userAgent=request.META['HTTP_USER_AGENT']
  if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
    disabledExercises=userInfo.avoidedExercise.all()
    return render_to_response('disabledexercisesiphone.html', locals())

  return render_to_response('disablemusclegroups.html', locals())

def setDisabledX(request):
  deviceid=""
  if request.method == "GET":
    deviceid = request.GET[u'deviceid']
  login, exists = iPhone(request, deviceid)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  #get either an exercise or a muscleGroup
  eOrM=request.GET[u'eOrM']
  #get the id of that thing
  id=request.GET[u'id']
  #set to enabled, true or false
  enabled=request.GET[u'enabled']
  #enablING
  if eOrM=="muscleGroup":
    muscleGroupToUse=MuscleGroup.objects.get(id=id)
    if enabled=="0" and not muscleGroupToUse in userInfo.avoidedMuscleGroup.all():
      userInfo.avoidedMuscleGroup.add(muscleGroupToUse)
      userInfo.save()
      #return HttpResponse("adding "+muscleGroupToUse.name+" to avoided muscle groups")
    elif enabled=="1":# and muscleGroupToUse in userInfo.avoidedMuscleGroup.all():
      while muscleGroupToUse in userInfo.avoidedMuscleGroup.all():
        userInfo.avoidedMuscleGroup.remove(muscleGroupToUse)
      userInfo.save()
      #return HttpResponse("removing "+muscleGroupToUse.name+" from avoided muscle groups")
  elif eOrM=="exercise":
    exerciseToUse=Exercise.objects.get(id=id)
    if enabled=="0" and not exerciseToUse in userInfo.avoidedExercise.all():
      userInfo.avoidedExercise.add(exerciseToUse)
    elif enabled=="1":
      while exerciseToUse in userInfo.avoidedExercise.all():
        userInfo.avoidedExercise.remove(exerciseToUse)
    userInfo.save()
  return HttpResponse("saved")

def disabledX(request):
  deviceid=""
  if request.method == "GET":
    deviceid = request.GET[u'deviceid']
  login, exists = iPhone(request, deviceid)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  disabledExercises=userInfo.avoidedExercise.all()
  allMuscleGroups=MuscleGroup.objects.all().order_by('name')
  allAvoids=userInfo.avoidedMuscleGroup.all()

  myList=[]

  for iterator in allMuscleGroups:
    myDict={}
    myDict['name']=iterator.name
    myDict['id']=iterator.id
    if iterator in allAvoids:
      iterator.enabled=False
      myDict['enabled']=0
    else:
      iterator.enabled=True
      myDict['enabled']=1
    myList.append(myDict)
  muscleGroups=simplejson.dumps(myList)
  myList=[]
  for iterator in disabledExercises:
    dict={}
    dict['name']=iterator.name
    dict['id']=iterator.id
    myList.append(dict)
  avoidedExercises = simplejson.dumps(myList)
  finalDict={}
  finalDict['avoidedExercises']=avoidedExercises
  finalDict['muscleGroups']=muscleGroups
  json=simplejson.dumps(finalDict)
  return HttpResponse(json, mimetype='application/json')

def disabledExercises(request):
  login, superuser = credentials(request)
  if login:
    return signIn(request)

  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  disabledExercises=userInfo.avoidedExercise.all()
  return render_to_response('disabledexercises.html', locals())


def readdExercise(request, exercise=None):
  login, superuser = credentials(request)
  if login:
    return signIn(request)

  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  try:
    userInfo.avoidedExercise.remove(Exercise.objects.get(id=exercise))
  except:
    pass
  userInfo.save()
  successMessage="This exercise has been re-enabled for you.  <a href='../disabledexercises/'>Go back</a>"

  userAgent=request.META['HTTP_USER_AGENT']
  if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
    successMessage="This exercise has been re-enabled for you.  <a href='../disablemusclegroups/'>Go back</a>"
    return render_to_response("successiphone.html", locals())

  return render_to_response('success.html', locals())
def landing(request):

  return render_to_response('landing.html', locals())

def removeExercise(request, exercise=None):
  login, superuser = credentials(request)
  if login:
    return signIn(request)

  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  userInfo.avoidedExercise.add(Exercise.objects.get(id=exercise))
  userInfo.save()
  successMessage="This exercise will not be given to you again."

  userAgent=request.META['HTTP_USER_AGENT']
  if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
    return render_to_response("successiphone.html", locals())

  return render_to_response('success.html', locals())



def sampleWorkout(request):
  login, superuser = credentials(request)
  return render_to_response('sampleworkout.html', locals())

def samplePrint(request):
  login, superuser = credentials(request)
  return render_to_response('sampleprint.html', locals())




def signIn(request):
  login, superuser = credentials(request)
  if login==2:
    pass

  if request.method=='POST' and 'password' in request.POST and 'username' in request.POST:
    getPassword=generatePassword(request.POST['password'])
    getUsername=request.POST['username']
    getUsername=getUsername.upper()
    checkForUser=User.objects.filter(username=getUsername,password=getPassword)
    if checkForUser:
      checkForUser=checkForUser[0]
      getRole=checkForUser.role
      request.session['userID']=getUsername
      request.session['role']=getRole
      if not checkForUser.confirmed:
        error=1
        return render_to_response('signin.html', locals())
      checkForUser.ip=request.META.get('REMOTE_ADDR', '<none>')
      checkForUser.save()

      request.method=None
      return home(request)

    else:
      checkForUser=User.objects.filter(username=getUsername,altPassword=getPassword)
      if checkForUser:
        checkForUser=checkForUser[0]
        getRole=checkForUser.role
        request.session['userID']=getUsername
        request.session['role']=getRole
        checkForUser.password=checkForUser.altPassword
        checkForUser.ip=request.META.get('REMOTE_ADDR', '<none>')
        checkForUser.save()

      else:
        error=1


  return render_to_response('signin.html', locals())

def speed2(request):
  login, superuser = credentials(request)

  return render_to_response('success.html', locals())


def stats(request):
  login, superuser = credentials(request)
  totalUsers=User.objects.filter(payment="appstore").count()
  percentMale=0
  percentFemale=0
  allAccounts=User.objects.filter(payment="appstore")

  allUsers=UserInformation.objects.filter(user__in=allAccounts)
  for iterator in allUsers:
    if iterator.gender=='Male':
      percentMale=percentMale+1
    elif iterator.gender=='Female':
      percentFemale=percentFemale+1

  usersWithGoals=list(UserInformation.objects.filter(goal__isnull=False).select_related('goal'))
  allGoals=Goal.objects.all()
  dictionary={}
  for goalObject in allGoals:
    dictionary[goalObject.name]=0
  for userInfoObject in usersWithGoals:
    dictionary[userInfoObject.goal.name]=dictionary[userInfoObject.goal.name]+1
  highestVal=0
  highestGoal=""

  for goalObject in allGoals:
    if dictionary[goalObject.name]>highestVal:
      highestVal=dictionary[goalObject.name]
      highestGoal=goalObject.name
  percentMale=int(float(percentMale)*100.0/float(len(allUsers)))
  percentFemale=int(float(percentFemale)*100.0/float(len(allUsers)))
  currentCount=Count.objects.all()[0]

#  weeksToDelete=ThisWeek.objects.filter(user=user)
#this is an alright place to delete any hanging series objects..., WRONG!!
  #now
#  if weeksToDelete.count()==7:#we create a week at a time
#  for iterator in weeksToDelete:
#    try:
#      toSave=TodaysWorkout.objects.filter(thisWeek=iterator)[0]
#      toSave.thisWeek=None
#      toSave.save()
#    except:
#      pass
#    iterator.delete()
#################################3
  return render_to_response('stats.html', locals())





def filterByMuscleGroups(currentUser, potentialExercises, date, request):
#goal is to elminate the exercises involving muscle groups that have already been worked too much
#(filter out muscle groups)
  t1=datetime.datetime.now()
  today=date
  yesterday=timedelta(days=-1)
  dictionary={}
  allMuscleGroups=MuscleGroup.objects.all()
  for iterator in allMuscleGroups:
    dictionary[iterator.name]=[]




  componentsThatMatter=[]#ALSO ADD BALANCE AND REACTIVE TO THIS
  for iterator in WorkoutComponent.objects.all():
    if iterator.name!="Flexibility" and iterator.name!='Balance' and iterator.name!='Reactive':
      componentsThatMatter.append(iterator)

  workoutDict={}
  userWorkouts=list(TodaysWorkout.objects.filter(user=currentUser))
  for iterator in userWorkouts:
    key=iterator.date.__str__()[0:10]
    workoutDict[key]=iterator

  dictOfSeriesLists={}#key will be workout ID
  relevantWorkoutSeries=WorkoutSeries.objects.select_related().filter(todaysWorkout__in=userWorkouts)
  #if the workout has no series in it, this won't work
  for iterator in relevantWorkoutSeries:
    key=iterator.todaysWorkout.id.__str__()
    if not key in dictOfSeriesLists:
      dictOfSeriesLists[key]=[]
    dictOfSeriesLists[key].append(iterator.series)
  for iterator in userWorkouts:
    key=iterator.id.__str__()
    if not key in dictOfSeriesLists:
      dictOfSeriesLists[key]=[]
  for j in range(0,7):#1 week's worth of exercising
    today= today+yesterday
    key=today.__str__()
    if key in workoutDict:
      exists=workoutDict[key]
    #exists=TodaysWorkout.objects.filter(date=today, user=currentUser)
    #if exists and not exists[0].offDay:
    if key in workoutDict and not exists.offDay:
#      workout=exists[0]
      workout=exists
#      allSeries=workout.exercises.select_related().all()
      allSeries=dictOfSeriesLists[exists.id.__str__()]
#.select_related('workoutComponent','workoutComponent2','workoutComponent3','muscleGroup')#OPTIMIZE
      for iterator in allSeries:

        if iterator.exercise.workoutComponent in componentsThatMatter or iterator.exercise.workoutComponent2 in componentsThatMatter or iterator.exercise.workoutComponent3 in componentsThatMatter:    #COMPLETE LATER
          key=iterator.exercise.muscleGroup.name
          setsOfReps=[]
#          embeddedDict={}
#          embeddedDict['day']=j
#          embeddedDict['list']=setsOfReps
          for k in range(0, iterator.sets):
            setsOfReps.append(iterator.reps)
          setsOfReps.append(j)#SIGNIFIES THE DAY OF THE WEEK
          dictionary[key].append(setsOfReps)#dictionary[key] represents all the days of that muscle group being worked


  #OPTIMIZE
  #I don't know why this doesn't work...if I take this and put outside the loop it ends up giving me errors
  possibleFrequenciesOriginal=list(MuscleFrequency.objects.filter(exception=False))
  toReplaceDict={}
  for iterator in possibleFrequenciesOriginal:
    toReplaceDict[iterator.name.__str__()]=iterator
  for muscleGroupObject in allMuscleGroups:
  #len dictionary[key] should be the times per week already worked
  #len of each list in dictionary[key] will be a representation of sets and reps
    timesPerWeek=len(dictionary[muscleGroupObject.name])
    if timesPerWeek>0:
      averageSets=0
      averageReps=0
      for m in range(0, timesPerWeek):
        setsOfReps=dictionary[muscleGroupObject.name][m]
        totalSets=len(setsOfReps)#WE IGNORE THE LAST ONE, THAT REPRESENTS THE DAY OF THE WEEK
        repRange=sum(setsOfReps)/totalSets
        averageSets=averageSets+totalSets
        averageReps=averageReps+repRange
      averageSets=averageSets/timesPerWeek
      averageReps=averageReps/timesPerWeek

      # SBL this is untested code, I just turned into a list comprehension so I
      # could read the shit
      possibleFrequencies = [f for f in possibleFrequenciesOriginal if f.minReps > averageReps or f.maxReps < averageReps or f.maxSets < averageSets]

      cornerCutter=False
      try:
        # FUCK YOU PAST SCOTT
        possibleFrequencies=possibleFrequencies[0]
        if possibleFrequencies.weekLength<7:#Go back and redo the process
          timesPerWeek=0
          for listObject in dictionary[muscleGroupObject.name]:
            if listObject[len(listObject)-1]<=possibleFrequencies.weekLength:#last element
              timesPerWeek=timesPerWeek+1


      except:#this means you've got super high reps and sets
        cornerCutter=True

      if cornerCutter or timesPerWeek>=possibleFrequencies.maximum:
        #remove iterator (a muscle group) from potentialExercises
        toRemove=[]
        for someExercises in potentialExercises:
          if someExercises.muscleGroup==muscleGroupObject:
            toRemove.append(someExercises)

        for remove in toRemove:
          potentialExercises.remove(remove)

  return potentialExercises


def filterByMutex(exerciseMatrix, potentialExercises, anExercise, request):
  t1=datetime.datetime.now()
  cannotUse=[]
  for exerciseList in exerciseMatrix:
    if anExercise in exerciseList:
      cannotUse.extend(exerciseList)

  t2=datetime.datetime.now()
  delta=t2-t1
  return cannotUse

def eliminateRepeatDays(currentUser, potentialExercises, currentDateTime):
  return potentialExercises
  QuerySetObject=TodaysWorkout.objects.filter(user=currentUser).order_by('date')
  lastWeek=[]
  try:
    currentDateTime=currentDateTime.date()
  except:
    pass

  chestIds=[]
  backIds=[]
  bicepIds=[]
  tricepIds=[]
  legIds=[]
  shoulderIds=[]


  start=MuscleGroup.objects.filter(name='Upper Chest')[0]
  chestIds.append(start)
  next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
  while next!=start:
    chestIds.append(next)
    next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)

  start=MuscleGroup.objects.filter(name='Biceps')[0]
  bicepIds.append(start)
  start=MuscleGroup.objects.filter(name='Triceps')[0]
  tricepIds.append(start)

  start=MuscleGroup.objects.filter(name='Quads')[0]
  legIds.append(start)
  next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
  while next!=start:
    if next.name!='Triple Extension':
      legIds.append(next)
    next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)

  start=MuscleGroup.objects.filter(name='Front Deltoids')[0]
  shoulderIds.append(start)
  next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
  while next!=start:
    shoulderIds.append(next)
    next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)

  start=MuscleGroup.objects.filter(name='Upper Back')[0]
  backIds.append(start)
  next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
  while next!=start:
    backIds.append(next)
    next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)






  lastWeek=list(QuerySetObject)
#  for iterator in QuerySetObject:
 #   writeTestData(iterator.date.__str__()+"        "+currentDateTime.__str__())
#    try:
#      if iterator.date<currentDateTime.date():#HAS NO ATTRIBUTE "DATE"
#        lastWeek.append(iterator)
#    except:#THIS IS SLOPPY, FUCK!!!  #TODO
#      if iterator.date<currentDateTime:
#        lastWeek.append(iterator)
#  writeTestData("LENGTH OF LAST WEEK IS "+len(lastWeek).__str__())

  dictionary={}#dictionary of the last time we worked everything
  oneWeekAgo=(currentDateTime)+timedelta(days=-7)
  dictionary['chest']=oneWeekAgo
  dictionary['biceps']=oneWeekAgo
  dictionary['triceps']=oneWeekAgo
  dictionary['legs']=oneWeekAgo#don't include triple extension here
  dictionary['back']=oneWeekAgo
  dictionary['shoulders']=oneWeekAgo

#  writeTestData("\n------------------------------\n")
  for todaysWorkoutObject in lastWeek:
#    writeTestData(todaysWorkoutObject.date.__str__()+"   <-----------")
    for seriesObject in todaysWorkoutObject.exercises.all():
      if seriesObject.exercise.workoutComponent.name=='Resistance' or (seriesObject.exercise.workoutComponent2 and seriesObject.exercise.workoutComponent2.name=='Resistance') or (seriesObject.exercise.workoutComponent3 and seriesObject.exercise.workoutComponent3.name=='Resistance'):
        if seriesObject.exercise.muscleGroup in chestIds:
          dictionary['chest']=todaysWorkoutObject.date
        elif seriesObject.exercise.muscleGroup in bicepIds:
          dictionary['biceps']=todaysWorkoutObject.date
        elif seriesObject.exercise.muscleGroup in tricepIds:
          dictionary['triceps']=todaysWorkoutObject.date
        elif seriesObject.exercise.muscleGroup in legIds:
          dictionary['legs']=todaysWorkoutObject.date
        elif seriesObject.exercise.muscleGroup in backIds:
          dictionary['back']=todaysWorkoutObject.date
        elif seriesObject.exercise.muscleGroup in shoulderIds:
          dictionary['shoulders']=todaysWorkoutObject.date


  forceInclude=[]
  if (currentDateTime-dictionary['chest']).days>=7:
    forceInclude.extend(chestIds)
  if (currentDateTime-dictionary['biceps']).days>=7:
    forceInclude.extend(bicepIds)
  if (currentDateTime-dictionary['triceps']).days>=7:
    forceInclude.extend(tricepIds)
  if (currentDateTime-dictionary['legs']).days>=7:
    forceInclude.extend(legIds)
  if (currentDateTime-dictionary['back']).days>=7:
    forceInclude.extend(backIds)
  if (currentDateTime-dictionary['shoulders']).days>=7:
    forceInclude.extend(shoulderIds)
  if forceInclude:
    nonResistance=list(WorkoutComponent.objects.all().exclude(name='Resistance'))
    forceInclude.append(MuscleGroup.objects.filter(name='Total Body')[0])
    for j in range(0, len(potentialExercises)):
      potentialExercises[j]=potentialExercises[j].id
    potentialExercises=Exercise.objects.filter(id__in=potentialExercises)
    potentialExercises=list(potentialExercises.filter(Q(muscleGroup__in=forceInclude) | Q(workoutComponent__in=nonResistance)))
  if False:
    writeTestData("The last time chest was worked was "+(currentDateTime-dictionary['chest']).days.__str__()+" days ago")
    writeTestData("The last time biceps was worked was "+(currentDateTime-dictionary['biceps']).days.__str__()+" days ago")
    writeTestData("The last time triceps was worked was "+(currentDateTime-dictionary['triceps']).days.__str__()+" days ago")
    writeTestData("The last time back was worked was "+(currentDateTime-dictionary['back']).days.__str__()+" days ago")
    writeTestData("The last time shoulders was worked was "+(currentDateTime-dictionary['shoulders']).days.__str__()+" days ago")

  #you could just take the top 3 and delete or something...eeeeeer

  return potentialExercises

def getCardioZone(cardioType, phase, fitnessLevel, level):
  currentZone=random.randint(1,3)
  myCardioZone=list(CardioZone.objects.filter(level=level,zone=currentZone, fitnessLevel=fitnessLevel, cardioType=cardioType))

  existingHardCode=HardCodedRule.objects.filter(cardioType=cardioType, phase=phase)
  if existingHardCode:
    existingHardCode=existingHardCode[0]
    groupedCardioZone=existingHardCode.cardioZone
    if groupedCardioZone.id%12==0:
      toMatch=(groupedCardioZone.id/12)-1
    else:
      toMatch=groupedCardioZone.id/12
    allCardioZones=list(CardioZone.objects.all())
    toRemove=[]
    for iterator in list(allCardioZones):
      if iterator.id % 12 ==0:
        if (iterator.id/12)-1!=toMatch:
          toRemove.append(iterator)
      elif iterator.id/12!=toMatch:
        toRemove.append(iterator)
    for iterator in toRemove:
      allCardioZones.remove(iterator)
    possibleIds=[]
    for iterator in allCardioZones:
      possibleIds.append(iterator.id)
    newCardioZone=CardioZone.objects.filter(id__in=possibleIds,level=level,zone=currentZone)
    while newCardioZone[0].totalTime==0:
      currentZone=currentZone-1
      newCardioZone=CardioZone.objects.filter(id__in=possibleIds,level=level,zone=currentZone)
    associatedFitnessLevels=newCardioZone[0].fitnessLevel.all()
    highestVal=-1
    for iterator in associatedFitnessLevels:
      if iterator.value>highestVal:
        highestVal=iterator.value
    if fitnessLevel.value>=highestVal:
      myCardioZone=newCardioZone
  myCardioZone=myCardioZone[random.randint(0,len(myCardioZone)-1)]

  while myCardioZone.totalTime==0:
#    currentZone=currentZone-1
#    myCardioZone=list(CardioZone.objects.filter(level=level,zone=currentZone, fitnessLevel=fitnessLevel, cardioType=cardioType))
#    myCardioZone=myCardioZone[random.randint(0,len(myCardioZone)-1)]
    myCardioZone=CardioZone.objects.get(id=int(myCardioZone.id)-1)

  return myCardioZone





def fillMoreTime(userInfo, todaysWorkout, cardioLength, volumeTable, phase):  #fuck, no way to do this without knowing the length of the cardio...
  if volumeTable==None:
    return todaysWorkout

  def computeTotalTime():
    allExercises=todaysWorkout.exercises.select_related('exercise','exercise__workoutComponent').all()
    totalTime=0.0


    for seriesObject in allExercises:
      val1=int(phase.tempo[0:1])
      val2=int(phase.tempo[2:3])
      val3=int(phase.tempo[4:5])
      if val1==0:
        val1=1
      if val2==0:
        val2=1
      if val3==0:
        val3=1
      oneRepTime=float(val1+val2+val3)#SECONDS

      setTime=((float(seriesObject.sets*seriesObject.reps)*oneRepTime)/60.0)#MINUTES
      if seriesObject.exercise.oneLimb:
        setTime=setTime*2.0
      restTime=0
      if seriesObject.exercise.workoutComponent.name=='Resistance':
        restTime=(setTime*float(phase.rest))/60.0
      else:
        restTime=0.75
      totalTime=totalTime+setTime+restTime
    totalTime=totalTime*1.08 #8% fudge factor
    return totalTime
  timeToFill=float(userInfo.minutesPerDay-(computeTotalTime()+cardioLength))


  val1=int(phase.tempo[0:1])
  val2=int(phase.tempo[2:3])
  val3=int(phase.tempo[4:5])
  oneRepTime=float(val1+val2+val3)#SECONDS

  if float(timeToFill)/float(userInfo.minutesPerDay)>0.20:#if 20% short, go ahead and add
    allWorkoutComponents=WorkoutComponent.objects.all()
    componentDictionary={}
    for workoutComponentObject in allWorkoutComponents:
      componentDictionary[workoutComponentObject.name]=0
    todaysExercises=[]
    allMuscleGroups=[]


    allMuscleGroups2=MuscleGroup.objects.all()
    muscleTraverseDict={}
    #check to see if there's any muscle group worked only once for this workout and drop if so
    for muscleGroupObject in allMuscleGroups2:
      key=muscleGroupObject.id.__str__()
      muscleTraverseDict[key]=muscleGroupObject

    for seriesObject in todaysWorkout.exercises.all():
      componentDictionary[seriesObject.exercise.workoutComponent.name]=componentDictionary[seriesObject.exercise.workoutComponent.name]+1
      applicableVolume=Volume.objects.filter(workoutComponent=seriesObject.exercise.workoutComponent, parentTable=volumeTable)[0]
      todaysExercises.append(seriesObject.exercise)
      if not seriesObject.exercise.muscleGroup in allMuscleGroups:
        start=seriesObject.exercise.muscleGroup
        allMuscleGroups.append(start)
#        next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
        next=muscleTraverseDict[start.relatedMuscleGroup.__str__()]
        while next!=start:
          allMuscleGroups.append(next)
#          next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)
          next=muscleTraverseDict[next.relatedMuscleGroup.__str__()]

      if timeToFill>0.0 and applicableVolume.maxSets>seriesObject.sets:
        seriesObject.sets=seriesObject.sets+1
        timeToFill=timeToFill-((oneRepTime*float(seriesObject.reps)+float(phase.rest))/60.0)
        seriesObject.save()

    muscleDictionary={}
    for iterator in allMuscleGroups:
      muscleDictionary[iterator.name]=0
    for seriesObject in todaysWorkout.exercises.all():
      muscleDictionary[seriesObject.exercise.muscleGroup.name]=muscleDictionary[seriesObject.exercise.muscleGroup.name]+1
    toRemove=[]
    for muscleGroupObject in allMuscleGroups:
      myMax=ExercisesPerMuscleGroup.objects.filter(muscleGroup=muscleGroupObject, phase=phase, fitnessLevel=userInfo.currentFitnessLevel)[0]
#      except:
#        writeTestData("No Exercises/Musclegroup for "+muscleGroupObject.name+", "+phase.name+", "+userInfo.currentFitnessLevel.name)
      myCount=muscleDictionary[muscleGroupObject.name]
      if myMax>=myCount:
        toRemove.append(muscleGroupObject)
    for iterator in toRemove:
      allMuscleGroups.remove(iterator)
    #we now have all the muscle groups that have been worked today
    equipmentList=userInfo.equipmentAvailable.all()
    addedSomething=False
    flexComponent=WorkoutComponent.objects.filter(name='Flexibility')[0]
    for key, value in componentDictionary.items():#key is the workout component name, value is the count of those components
      if value>0:
        currentComponent=WorkoutComponent.objects.filter(name=key)[0]
        applicableVolume=Volume.objects.filter(workoutComponent=currentComponent, parentTable=volumeTable)[0]
        if timeToFill>0.0 and value<applicableVolume.maxExercises and currentComponent!=flexComponent:
          #add another exercise from this workout component of appropriate difficulty with proper equipment, fuck...
          #can't be some anything we already used..todaysExercises=[]

          potentialExercisesStart=Exercise.objects.filter(workoutComponent__in=[currentComponent], equipment__in=list(userInfo.equipmentAvailable.all()), phase__in=[phase], muscleGroup__in=allMuscleGroups)

          potentialExercisesBodyWeight=Exercise.objects.filter(workoutComponent__in=[currentComponent], phase__in=[phase], muscleGroup__in=allMuscleGroups)
          potentialExercisesBodyWeight=list(potentialExercisesBodyWeight.exclude(equipment__in=list(Equipment.objects.all())))

          potentialExercises=list(potentialExercisesStart)
          toRemove=[]
          userEquipment=userInfo.equipmentAvailable.all()
          for exerciseObject in potentialExercises:
            canUse=True
            for equipmentObject in exerciseObject.equipment.all():
              if not equipmentObject in userEquipment:
                canUse=False
            if not canUse:
              toRemove.append(exerciseObject)
          for iterator in toRemove:
            potentialExercises.remove(iterator)
          potentialExercises.extend(potentialExercisesBodyWeight)

          toRemove=[]
          for exerciseObject in potentialExercises:
            if exerciseObject.minFitnessLevel.value > userInfo.currentFitnessLevel.value:#filter difficulty
              toRemove.append(exerciseObject)
            elif exerciseObject.minExperience.value > userInfo.experience.value:
             toRemove.append(exerciseObject)
          for exerciseObject in toRemove:
            try:
              potentialExercises.remove(exerciseObject)
            except:
              pass#may have already been removed




      #added sets, now add exercises


#MAKE SURE AND SAVE EVERYTHING AT THE END

  #check workout components and expand sets
  return todaysWorkout


def shareWorkout(request, workoutId):
  login, superuser = credentials(request)
  todaysWorkout=None
  try:
    todaysWorkout=TodaysWorkout.objects.get(id=workoutId)
  except:
    successMessage="This workout no longer exists.  We don't store workouts in our database that long, sorry."
    return render_to_response("success.html", locals())
  todaysExercises=todaysWorkout.exercises.select_related('exercise__workoutComponent').all()
  previousComponent='this string could be anything...'
  for iterator in todaysExercises:
    if iterator.exercise.workoutComponent.name!=previousComponent:
      iterator.change=1
      previousComponent=iterator.exercise.workoutComponent.name
    else:
      iterator.change=0
  for iterator in todaysExercises:
    if iterator.superSet:
      iterator.superSet=Series.objects.get(id=iterator.superSet)

  actualRest=0
  try:
    actualTempo=list(todaysExercises)[0].tempo
    actualRest=float(list(todaysExercises)[0].rest)/60.0
    if float(actualRest)==float(int(actualRest)):
      actualRest=int(actualRest)
      if actualRest==1:
        actualRest=actualRest.__str__()+" minute"
      else:
        actualRest=actualRest.__str__()+" minutes"
    else:
      if float(actualRest)<1.0:
        actualRest=int(actualRest*60.0).__str__()+ " seconds"
      else:
        minutes=int(actualRest)
        seconds=int((actualRest-float(int(actualRest)))*60.0)
        actualRest=minutes.__str__()+" minutes and "+seconds.__str__()+" seconds"
  except:
    pass
  for iterator in todaysExercises:
    if iterator.exercise.workoutComponent.name=='Resistance':
      iterator.actualRest=actualRest
    elif iterator.exercise.workoutComponent.name=='Flexibility':
      iterator.actualRest=None
    else:
      iterator.actualRest='45 seconds'

  return render_to_response('shareworkout.html', locals())


def reduceToTime(todaysWorkout, cardio, phase, timed, level, volumeTable, request):  #2nd var is boolean
  t1=datetime.datetime.now()
  allExercises=list(todaysWorkout.exercises.select_related('exercise').all())
#oneRepTime=float(int(somePhase.tempo[0:1])+int(somePhase.tempo[2:3])+int(somePhase.tempo[4:5]))
  time1=datetime.datetime.now()
  def computeTotalTime():
    totalTime=0.0


    for seriesObject in allExercises:
      val1=int(phase.tempo[0:1])
      val2=int(phase.tempo[2:3])
      val3=int(phase.tempo[4:5])
      if val1==0:
        val1=1
      if val2==0:
        val2=1
      if val3==0:
        val3=1
      oneRepTime=float(val1+val2+val3)#SECONDS
      if seriesObject.exercise.oneLimb:  #COMPLETE LATER
        oneRepTime=oneRepTime*2
      setTime=((float(seriesObject.sets*seriesObject.reps)*oneRepTime)/60.0)
      if seriesObject.exercise.oneLimb:
        setTime=setTime*2.0
      restTime=0
      if seriesObject.exercise.workoutComponent.name=='Resistance':
        restTime=(setTime*float(phase.rest))/60.0
      else:
        restTime=0.45
      totalTime=totalTime+setTime+restTime
    totalTime=totalTime*1.08 #8% fudge factor
    return totalTime


  userInfo=UserInformation.objects.filter(user=todaysWorkout.user)[0]
  timeAvailable=userInfo.minutesPerDay
  time2=datetime.datetime.now()




  totalLength=0#used to address the amount of time for cardio
  if cardio:
    cardioString=""
    currentUser=todaysWorkout.user
    userInformation=userInfo

    phases=userInformation.goal.phase.all()
    try:
      myPhase=phases[userInfo.currentPhase]
    except:
      userInfo.currentPhase=0
      userInfo.save()
      myPhase=phases[0]
    myCardioZone=getCardioZone(userInformation.goal.cardioType, myPhase, userInformation.currentFitnessLevel, level)

    if not myCardioZone:
      pass#this is an error, might wanna set up an automated email
    else:
      totalTime1=0
      totalTime2=0
      totalTime3=0


      timeOverLimit=computeTotalTime()+myCardioZone.maxOverall-timeAvailable
      if timeOverLimit<0:
        timeOverLimit=0
#      writeTestData("Time over limit is "+timeOverLimit.__str__()+" and compute total is "+computeTotalTime().__str__()+" and cardio is "+myCardioZone.maxOverall.__str__())
      timeToReduceCardio=0
      if timeOverLimit>0:
         timeToReduceCardio=timeOverLimit/2#half of time over the limit cause the other half should reduce resistance exercises
      else:
         pass#special scenario?
      myCardioZone.maxOverall=myCardioZone.maxOverall-timeToReduceCardio
      if myCardioZone.maxOverall<20:
        myCardioZone.maxOverall=20
      myCardioZone.maxOverall=int(myCardioZone.maxOverall)
      if myCardioZone.maxOverall>timeAvailable:
        myCardioZone.maxOverall=timeAvailable


      currentZone=myCardioZone.zone
      targetZone=currentZone
      targetTime=myCardioZone.totalTime #once total time in this zone is achieved, then go back to zone 2 and zone 1
      timeInZone=0.0
      try:
        possibleCardioActions=list(CardioAction.objects.filter(equipment__in=userInformation.equipmentAvailable.all()))
        myAction=possibleCardioActions[random.randint(0, len(possibleCardioActions)-1)]
        myAction=myAction.verb
      except:
        myAction="do some type of cardio"

      verb=myAction+" for "
      positiveDerivative=True
      first=True
      lastZone=0
      cardioString=cardioString+verb
########################################   TARGET ZONE 1   #####################################################################################
      maxHeartRate=220-userInformation.age
      if targetZone==1:
        totalLength=random.randint(myCardioZone.minInterval, myCardioZone.maxInterval)
        if totalLength>myCardioZone.maxOverall:
          totalLength=myCardioZone.maxOverall

        cardioString=verb + totalLength.__str__() + " minutes at a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher18', 'launcher', 'height=350','width=425').focus()\">heart rate between "+(myCardioZone.minHeartRate*maxHeartRate/100).__str__()+" and "+(myCardioZone.heartRate*maxHeartRate/100).__str__()+" bpm (Zone 1)</a>"
################################################################################################################################################
      elif targetZone==2:
        ratio=float(myCardioZone.totalTime)/float(myCardioZone.maxInterval)
        zone2Interval=random.randint(myCardioZone.minInterval, myCardioZone.maxInterval)
        targetTime=zone2Interval * ratio
        zone1Interval=random.randint(myCardioZone.minPrevious, myCardioZone.maxPrevious)
        numRepeats=float(targetTime)/float(zone2Interval)
        if numRepeats!=float(int(numRepeats)):# did not divide evenly, round up
          numRepeats=int(numRepeats)+1

        periodTime=zone1Interval+zone2Interval
        numRepeats2=float(myCardioZone.maxOverall)/float(periodTime)
        if numRepeats2!=float(int(numRepeats2)):# did not divide evenly, round up
          numRepeats2=int(numRepeats2)+1


        if numRepeats2<numRepeats:
          numRepeats=numRepeats2
        zone2MinHeartRate=myCardioZone.minHeartRate
        zone2HeartRate=myCardioZone.heartRate
        secondZone=CardioZone.objects.get(id=myCardioZone.id-1)
        if secondZone.zone==2:
          secondZone=CardioZone.objects.get(id=secondZone.id-1)#real sloppy, but this works
        zone1MinHeartRate=secondZone.minHeartRate
        zone1HeartRate=secondZone.heartRate

        if int(numRepeats)>1:
          cardioString=verb + " "+zone1Interval.__str__() + " minutes at a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher18', 'launcher', 'height=350','width=425').focus()\">heart rate between " + (zone1MinHeartRate*maxHeartRate/100).__str__() +" and "+(zone1HeartRate*maxHeartRate/100).__str__()+" bpm (Zone 1)</a> followed by " +zone2Interval.__str__() + " minutes at a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher19', 'launcher', 'height=350','width=425').focus()\">heart rate between " + (zone2MinHeartRate*maxHeartRate/100).__str__() + " and "+(zone2HeartRate*maxHeartRate/100).__str__()+" bpm (Zone 2)</a> then repeat " + int(numRepeats).__str__() +" times."
        else:
          cardioString=verb + " "+zone1Interval.__str__() + " minutes at a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher18', 'launcher', 'height=350','width=425').focus()\">heart rate between " + (zone1MinHeartRate*maxHeartRate/100).__str__() +" and "+(zone1HeartRate*maxHeartRate/100).__str__()+" bpm (Zone 1)</a> followed by " +zone2Interval.__str__() + " minutes at a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher19', 'launcher', 'height=350','width=425').focus()\">heart rate between " + (zone2MinHeartRate*maxHeartRate/100).__str__() + " and "+(zone2HeartRate*maxHeartRate/100).__str__()+" bpm (Zone 2)</a> and finally  " + zone1Interval.__str__() + " minutes at a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher18', 'launcher', 'height=350','width=425').focus()\">heart rate between " + (zone1MinHeartRate*maxHeartRate/100).__str__() +" and "+(zone1HeartRate*maxHeartRate/100).__str__()+" bpm (Zone 1)</a>"
        totalLength=(zone1Interval+zone2Interval)*numRepeats
      elif targetZone==3:
        ratio=float(myCardioZone.totalTime)/float(myCardioZone.maxInterval)
        zone3Interval= myCardioZone.maxInterval
        zone3Initial=zone3Interval
        zone3Interval=int(zone3Interval * 60.0).__str__() + " seconds"
        targetTime=float(zone3Initial) * ratio
        zone2Interval=random.randint(myCardioZone.minPrevious, myCardioZone.maxPrevious)
        numRepeats=targetTime/zone3Initial
        periodTime=zone3Initial+float(zone2Interval)+2.0
        numRepeats2=float(myCardioZone.maxOverall)/periodTime
        if numRepeats2<float(numRepeats):
          numRepeats=numRepeats2
        zone3MinHeartRate=myCardioZone.minHeartRate
        zone3HeartRate=myCardioZone.heartRate
        zone2MinHeartRate=CardioZone.objects.get(id=myCardioZone.id-2).minHeartRate
        zone2HeartRate=CardioZone.objects.get(id=myCardioZone.id-2).heartRate
        zone1MinHeartRate=CardioZone.objects.get(id=myCardioZone.id-3).minHeartRate
        zone1HeartRate=CardioZone.objects.get(id=myCardioZone.id-3).heartRate

        zone1Interval=2
        cardioString=verb + " "+zone1Interval.__str__() + " minutes at a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher18', 'launcher', 'height=350','width=425').focus()\">heart rate between " + (zone1MinHeartRate*maxHeartRate/100).__str__() +" and "+(zone1HeartRate*maxHeartRate/100).__str__()+" bpm (Zone 1)</a> followed by " +zone2Interval.__str__() + " minutes at a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher19', 'launcher', 'height=350','width=425').focus()\">heart rate between " + (zone2MinHeartRate*maxHeartRate/100).__str__() + " and "+(zone2HeartRate*maxHeartRate/100).__str__()+" bpm (Zone 2)</a> followed by "+zone3Interval.__str__() + " at a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher20', 'launcher', 'height=350','width=425').focus()\">heart rate between " +(zone3MinHeartRate*maxHeartRate/100).__str__()+" and "+(zone3HeartRate*maxHeartRate/100).__str__()+" bpm (Zone 3)</a>.  Step back down to a <a href=\"javascript:void(0)\" onclick=\"window.open('../descriptionlauncher19', 'launcher', 'height=350','width=425').focus()\">heart rate between "+(zone2MinHeartRate*maxHeartRate/100).__str__() + " bpm and "+(zone2HeartRate*maxHeartRate/100).__str__()+" bpm (Zone 2)</a> for "+zone2Interval.__str__()+" minutes then repeat the whole process "+int(numRepeats).__str__()+ " times."

        totalLength=int((float(zone1Interval)+float(zone2Interval)+float(zone3Initial))*float(numRepeats))


  time3=datetime.datetime.now()

  timeAvailable=userInfo.minutesPerDay
  counter=0
  isolationCounter=0
  allW=WorkoutComponent.objects.all()
  componentDictionary={}
  for workoutComponentObject in allW:
    if workoutComponentObject.name=='Resistance':
      componentDictionary[workoutComponentObject.name]=99999#infinity
    elif workoutComponentObject.name=='Balance':
      componentDictionary[workoutComponentObject.name]=1#infinity
    elif workoutComponentObject.name=='Core':
      componentDictionary[workoutComponentObject.name]=2#infinity
    elif workoutComponentObject.name=='Reactive':
      componentDictionary[workoutComponentObject.name]=1#infinity
    elif workoutComponentObject.name=='Flexibility':
      componentDictionary[workoutComponentObject.name]=99999#infinity
  keepGoing=True
  time4=datetime.datetime.now()
  allExercises=list(todaysWorkout.exercises.select_related('exercise__workoutComponent','exercise__muscleGroup').all())
  while computeTotalTime()+totalLength>timeAvailable and len(allExercises)>0 and keepGoing:
    componentDictionary2={}
    for seriesObject in allExercises:
      try:
        componentDictionary2[seriesObject.exercise.workoutComponent.name]=componentDictionary2[seriesObject.exercise.workoutComponent.name]+1
      except:
        componentDictionary2[seriesObject.exercise.workoutComponent.name]=1
    keepGoing=False
    for key, value in componentDictionary2.items():
      if componentDictionary2[key]>componentDictionary[key] and computeTotalTime()+totalLength>timeAvailable and len(allExercises)>0:#remove something from this component...
        found=False
        keepGoing=True
        toRemove=[]
        for seriesObject in allExercises:
          if not found and seriesObject.exercise.workoutComponent.name==key:
            found=True
            todaysWorkout.exercises.remove(seriesObject)
            toRemove.append(seriesObject)
        for seriesObject in toRemove:
          allExercises.remove(seriesObject)
  todaysWorkout.save()

###################################



  time5=datetime.datetime.now()
# need to count out all the components...
  while computeTotalTime()+totalLength>timeAvailable and len(allExercises)>0:
    #algorithm:  drop a lonely muscle group, drop isolation exercises, reduce sets

    deletedSomething=False
    maxSetsToRemove=6


    #now reduce sets
    setsReduced=0
    if computeTotalTime()>timeAvailable:
      for seriesObject in allExercises:
        if seriesObject.sets>3 and computeTotalTime()>timeAvailable and setsReduced<maxSetsToRemove:
          seriesObject.sets=seriesObject.sets-1
          seriesObject.save()
          setsReduced=setsReduced+1




    allMuscleGroups=MuscleGroup.objects.all()
    muscleDictionary={}
    muscleTraverseDict={}
    #check to see if there's any muscle group worked only once for this workout and drop if so
    for muscleGroupObject in allMuscleGroups:
      muscleDictionary[muscleGroupObject.name]=0
      key=muscleGroupObject.id.__str__()
      muscleTraverseDict[key]=muscleGroupObject

    for seriesObject in allExercises:
      startMuscle=seriesObject.exercise.muscleGroup
      muscleDictionary[startMuscle.name]=muscleDictionary[startMuscle.name]+1
#      next=MuscleGroup.objects.get(id=startMuscle.relatedMuscleGroup)
      next=muscleTraverseDict[startMuscle.relatedMuscleGroup.__str__()]
      while next.id!=startMuscle.id:
        muscleDictionary[next.name]=muscleDictionary[next.name]+1
        #next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)
        next=muscleTraverseDict[next.relatedMuscleGroup.__str__()]


    found=False
    for key, value in muscleDictionary.items():
      if value==1:
        found=True  #if found, then we know we can drop 1 muscle group
    removeArray=[]
    removeIds=[]
    if found and not deletedSomething:
      for seriesObject in allExercises:
        if muscleDictionary[seriesObject.exercise.muscleGroup.name]==1 and found:
          toRemove=seriesObject
          maxSetsToRemove=toRemove.sets#this ensures consistency with removing an exercise and reducing sets...whoo-pa!
          found=False#prevent additional exercises being deleted
          todaysWorkout.exercises.remove(toRemove)
          removeArray.append(toRemove)
          #toRemove.delete()
          #todaysWorkout.save()
          deletedSomething=True
      for seriesObject in removeArray:
        try:
          allExercises.remove(seriesObject)
        except:
          allExercises=list(allExercises)
          allExercises.remove(seriesObject)
        removeIds.append(seriesObject.id)
#LEFT OFF HERE!
    #muscleTraverseDict={}
    if not deletedSomething: #there are no lonely exercises.  Trim from the exercises w/too many from a particular muscle group
      greatestVal=0
      greatestKey=""
      for key, value in muscleDictionary.items():
        if value>greatestVal:
          greatestVal=value
          greatestKey=key
      removeArray=[]
      for seriesObject in allExercises:#first check for an isolated
        startMuscle=seriesObject.exercise.muscleGroup
#        next=MuscleGroup.objects.get(id=startMuscle.relatedMuscleGroup)
        next=muscleTraverseDict[startMuscle.relatedMuscleGroup.__str__()]
        while next.id!=startMuscle.id:
          if (startMuscle.name==greatestKey or next.name==greatestKey) and not deletedSomething and seriesObject.exercise.compound==False:
            toRemove=seriesObject
            maxSetsToRemove=toRemove.sets
            todaysWorkout.exercises.remove(toRemove)
            removeArray.append(toRemove)
#            toRemove.delete()
#            todaysWorkout.save()
            deletedSomething=True
          #next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)
          next=muscleTraverseDict[next.relatedMuscleGroup.__str__()]
      for seriesObject in removeArray:
        allExercises.remove(seriesObject)
        removeIds.append(seriesObject.id)

      removeArray=[]
      for seriesObject in allExercises:#now check for a compound
        startMuscle=seriesObject.exercise.muscleGroup
        #next=MuscleGroup.objects.get(id=startMuscle.relatedMuscleGroup)
        next=muscleTraverseDict[startMuscle.relatedMuscleGroup.__str__()]
        while next.id!=startMuscle.id:
          if (startMuscle.name==greatestKey or next.name==greatestKey) and not deletedSomething:
            toRemove=seriesObject
            maxSetsToRemove=toRemove.sets
            todaysWorkout.exercises.remove(toRemove)
            removeArray.append(toRemove)
            #toRemove.delete()
            #todaysWorkout.save()
            deletedSomething=True

          #next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)
          next=muscleTraverseDict[next.relatedMuscleGroup.__str__()]

      for seriesObject in removeArray:
        allExercises.remove(seriesObject)
        removeIds.append(seriesObject.id)



    Series.objects.filter(id__in=removeIds).delete()



     #now drop an isolation exercise
    if computeTotalTime()>timeAvailable and isolationCounter%3==2:#drop an isolation exercise every 3...can modify this...
      toRemove=0
      deleted=False
      for seriesObject in allExercises:
        if seriesObject.exercise.compound==False and not deleted:
          deleted=True
          toRemove=seriesObject
      if deleted:
        todaysWorkout.exercises.remove(toRemove)
        try:
          toRemove.delete()
        except:
          pass
        todaysWorkout.save()

        #toRemove.delete()
    isolationCounter=isolationCounter+1



    counter=counter+1
    if counter>10:#we're caught in an infinite loop
      allExercises=todaysWorkout.exercises.all()
      #next remove based on workout component
      componentDictionary={}
      for seriesObject in allExercises:
        componentDictionary[seriesObject.exercise.workoutComponent.name]=0
      for seriesObject in allExercises:
        componentDictionary[seriesObject.exercise.workoutComponent.name]=componentDictionary[seriesObject.exercise.workoutComponent.name]+1
    #find the greatest # of exercises for all the components
      greatest=-1
      componentKey=""
      for key, value in componentDictionary.items():
        if value>greatest:

          greatest=value
          componentKey=key
      found=False
      for seriesObject in allExercises:
        if seriesObject.exercise.workoutComponent.name==componentKey and not found:
          toRemove=seriesObject
          found=True

          todaysWorkout.exercises.remove(toRemove)
          toRemove.delete()
      todaysWorkout.save()

#    if deletedSomething:
#      writeTestData("dropped something")
    #now remove an exercise with a workout component that matches a key

  todaysWorkout.save()
  time6=datetime.datetime.now()
  if cardio:
    todaysWorkout.cardio=cardioString
  time7=datetime.datetime.now()
  t2=datetime.datetime.now()
  delta=t2-t1
######################################################
  if todaysWorkout.cardio:
    return fillMoreTime(userInfo, todaysWorkout, totalLength, volumeTable, phase)
  else:
    return todaysWorkout
############################################END REDUCE TO TIME################################



#def deletePreviousWorkouts(userInfo, currentDateTime):
#  daysToTrack=7
#  saveThese=[]
#  for j in range(1,daysToTrack+1):
#    currentDay=currentDateTime
#    existingWorkout=TodaysWorkout.objects.filter(user=userInfo.user, date=currentDay+timedelta(days=-j))
#    if existingWorkout:
#      saveThese.append(existingWorkout[0])
#  workoutsToDelete=TodaysWorkout.objects.filter(user=userInfo.user)
#
#  for workoutObject in workoutsToDelete:
#    if not workoutObject in saveThese:
#      for seriesObject in workoutObject.exercises.all():
#        seriesObject.delete()
#      workoutObject.delete()


def deletePreviousWorkouts(userInfo, currentDateTime):
  daysToTrack=7
  saveThese=[]
  previousWorkouts=TodaysWorkout.objects.filter(user=userInfo.user)
  workoutDict={}
  for iterator in previousWorkouts:
    key=iterator.date.__str__()
    workoutDict[key]=iterator
  for j in range(1,daysToTrack+1):
    currentDay=currentDateTime
    #existingWorkout=TodaysWorkout.objects.filter(user=userInfo.user, date=currentDay+timedelta(days=-j))
    key=currentDay+timedelta(days=-j)
    key=key.__str__()[0:10]
    if key in workoutDict:
      existingWorkout=workoutDict[key]
      saveThese.append(existingWorkout.id)
#    if existingWorkout:
  workoutsToDelete=TodaysWorkout.objects.filter(user=userInfo.user).exclude(id__in=saveThese)
#now we also need to delete the supersets associated with this
  relevantWorkoutSeries=WorkoutSeries.objects.select_related().filter(todaysWorkout__in=workoutsToDelete)
  seriesList=[]
  superSetIds=[]
  for iterator in relevantWorkoutSeries:
    if not iterator.series.superSet is None:
      superSetIds.append(iterator.series.superSet)

  Series.objects.filter(id__in=superSetIds).delete()


  workoutsToDelete.delete()

#  count=0
#  for workoutObject in workoutsToDelete:
#    if not workoutObject in saveThese:
#      for seriesObject in workoutObject.exercises.all():
#        seriesObject.delete()
#      workoutObject.delete()
#      count=count+1
#  from django.core.mail import send_mail
#  send_mail("Deleting", count.__str__(), 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)




#myWeek=ThisWeek.objects.filter(user=currentUser, dayNumber=dayOfWeek)[0]
#
#  dayOfWeek=userInfo.currentDay % 7
#  if dayOfWeek==0:
#    dayOfWeek=7


#options:  check difference between date, and current time...not very feasibly in actuality
#tie a workout to a given day of week
def descriptionLauncher(request, description=None):
  myDescription=Description.objects.get(id=description)
  if not myDescription is None:
    description=myDescription.text
  userAgent=request.META['HTTP_USER_AGENT']
  referer= request.META['HTTP_REFERER']
  if ('iPhone' in userAgent or 'iPod' in userAgent or  'iTouch' in userAgent):
    return render_to_response('descriptionlauncheriphone.html', locals())

  return render_to_response('descriptionlauncher.html', locals())


def makeOffDay(user, date):
  existingWorkout=TodaysWorkout.objects.filter(user=user, date=date)
  if existingWorkout:
    existingWorkout=existingWorkout[0]
    existingWorkout.visited=True
    existingWorkout.save()
    if existingWorkout.offDay:
      return
    toRemove=[]
#    for iterator in existingWorkout.exercises.all():
#      toRemove.append(iterator)
#    for iterator in toRemove:
#      existingWorkout.exercises.remove(iterator)
#    existingWorkout.cardio=None
#    existingWorkout.offDay=True
#  else:
#    existingWorkout=TodaysWorkout(user=user, date=date, offDay=True)
#  existingWorkout.save()


  userInfo=UserInformation.objects.filter(user=user)[0]
  userInfo.offDays=userInfo.offDays-1
  userInfo.save()
  toModify=[]

  dayOfWeek=userInfo.currentDay % 7
  if dayOfWeek==0:
    dayOfWeek=7


  for j in range(dayOfWeek, 8):
    toModify.append(ThisWeek.objects.filter(user=user, dayNumber=j)[0])
  justStarted=True
  stopPushingDays=False

  for thisWeekObject in toModify:
    if thisWeekObject.workoutComponents.count()==0 and thisWeekObject.cardio==False and not justStarted and not stopPushingDays:
      #this day is an off day, we need to turn it into an on day
      stopPushingDays=True
#      toMove=TodaysWorkout.objects.filter(thisWeek=thisWeekObject)[0]
      thisWeekObject.delete()#THIS MIGHT CAUSE A BUG, don't know
      userInfo.offDays=userInfo.offDays+1
      userInfo.save()

    if not stopPushingDays:
      thisWeekObject.dayNumber=thisWeekObject.dayNumber+1
      correspondingWorkout=TodaysWorkout.objects.filter(thisWeek=thisWeekObject)[0]
      correspondingWorkout.date=correspondingWorkout.date+timedelta(days=1)
      correspondingWorkout.save()
      thisWeekObject.save()
    if thisWeekObject.dayNumber>=8:
      correspondingWorkout=TodaysWorkout.objects.filter(thisWeek=thisWeekObject)[0]
      correspondingWorkout.delete()
      thisWeekObject.delete()

    justStarted=False
  thisWeekVar=ThisWeek(dayNumber=dayOfWeek, user=user, cardio=False)
  thisWeekVar.save()
  emptyWorkout=TodaysWorkout(user=user, thisWeek=thisWeekVar, date=date, offDay=True, visited=True)
  emptyWorkout.save()




def missedYesterday(user, currentDateTime):
  userInfo=UserInformation.objects.filter(user=user)[0]
  dayOfWeek=userInfo.currentDay % 7
  if dayOfWeek==0:
    dayOfWeek=7
  yesterdaysWorkout=TodaysWorkout.objects.filter(user=user, date=currentDateTime+timedelta(days=-1))
  if yesterdaysWorkout and yesterdaysWorkout[0].offDay:
    return False

#make yesterday an off day, grab yesterday's workout, and push all else forward

  makeOffDay(user, currentDateTime)

  todayThisWeek=ThisWeek.objects.filter(user=user, dayNumber=dayOfWeek)[0]
  yesterdayThisWeek=ThisWeek.objects.filter(user=user, dayNumber=dayOfWeek-1)[0]
  temp=todayThisWeek.dayNumber
  todayThisWeek.dayNumber=yesterdayThisWeek.dayNumber
  yesterdayThisWeek.dayNumber=temp

#  allComponents=list(todayThisWeek.workoutComponents.all())
#  for iterator in allComponents:
#    todayThisWeek.workoutComponents.remove(iterator)
#  todayThisWeek.cardio=False

  yesterdayWorkout=TodaysWorkout.objects.filter(thisWeek=yesterdayThisWeek)[0]
  todayWorkout=TodaysWorkout.objects.filter(thisWeek=todayThisWeek)[0]

  temp=todayWorkout.date
  todayWorkout.date=yesterdayWorkout.date
  yesterdayWorkout.date=temp
  todayWorkout.offDay=True
  todayWorkout.save()
  yesterdayWorkout.save()



  yesterdayThisWeek.save()
  todayThisWeek.save()

  return True

def gcd(a, b):
  while b!=0:
    t=b
    b=a%b
    a=t
  return a

def lcm(a, b):
  return a*b/gcd(a,b)


def evenlyDistribute(potentialExercises, request):
  t1=datetime.datetime.now()
  allMuscleGroups=MuscleGroup.objects.all()
  muscleDictionary={}
  ids=[]
  for iterator in potentialExercises:
    ids.append(iterator.id)

  potentialExercises=list(Exercise.objects.filter(id__in=ids).select_related('muscleGroup'))

  for iterator in allMuscleGroups:
    muscleDictionary[iterator.name]=0
  for iterator in potentialExercises:
    muscleDictionary[iterator.muscleGroup.name]=muscleDictionary[iterator.muscleGroup.name]+1

  first=True
  previous=0
  myList=[]
  for key, value in muscleDictionary.items():
    myList.append(value)


  keepGoing=True
  while keepGoing:
    try:
      myList.remove(0)
    except:
      keepGoing=False
  if len(myList)==0:
    return potentialExercises


  while len(myList)>1:
    small1=myList[0]
    for j in range(0, len(myList)):
      if myList[j]<small1:
        small1=myList[j]
    myList.remove(small1)


    small2=myList[0]
    for j in range(0, len(myList)):
      if myList[j]<small2:
        small2=myList[j]
    myList.remove(small2)
    myList.append(lcm(small1,small2))

  myLCM=myList[0]
  if myLCM>30:
    myLCM=30
  #now section off potential Exercises by muscle group...

#muscleDictionary[muscleName] is the number of exercises for this muscle group
  potentialExercisesCopy=[]
  for iterator in potentialExercises:
    potentialExercisesCopy.append(iterator)
  potentialExercises=[]
  for outer in allMuscleGroups:
    if muscleDictionary[outer.name]>0:
      incrementor=muscleDictionary[outer.name]
      #ratio=float(myLCM)/float(incrementor)
      counter=0
      exercisesOfSaidMuscleGroup=[]
      for inner in potentialExercisesCopy:
        if inner.muscleGroup==outer:
          exercisesOfSaidMuscleGroup.append(inner)
      index=0
      while counter<myLCM:
        potentialExercises.append(exercisesOfSaidMuscleGroup[index])
        counter=counter+1
        index=index+1
        if index>=len(exercisesOfSaidMuscleGroup):
          index=0


  muscleDictionary={}
  for iterator in allMuscleGroups:
    muscleDictionary[iterator.name]=0
  for iterator in potentialExercises:
    muscleDictionary[iterator.muscleGroup.name]=muscleDictionary[iterator.muscleGroup.name]+1

#  for iterator in potentialExercises:
#    writeTestData(iterator.name)
#  writeTestData("==========================")

  t2=datetime.datetime.now()
  delta=t2-t1
  return potentialExercises


def supersetPossibles(oldPotentials, potentialExercises, myPhase, previousSeries, todaysExercises, request, exerciseMatrix):

  cannotUse=filterByMutex(exerciseMatrix, None, previousSeries.exercise, None)
  goodToSuperset=True
  t1=datetime.datetime.now()
  #I changed oldPotentials to an array of exercises
#  potentialExercises=Exercise.objects.filter(id__in=oldPotentials)
  potentialExercises=oldPotentials
  todaysIds=[]
  for item in todaysExercises:
    #todaysIds.append(item.id)
    while item in potentialExercises:
      potentialExercises.remove(item)

  while previousSeries.exercise in potentialExercises:
    potentialExercises.remove(previousSeries.exercise)
    #THIS DEFINITELY WORKS!!
  for iterator in cannotUse:
    while iterator in potentialExercises:
      potentialExercises.remove(iterator)

#potential exercises are also excluding the previous workout
  allMuscles=MuscleGroup.objects.all()
  allMusclesDict={}
  allMusclesDictByName={}
  for iterator in allMuscles:
    key=iterator.id.__str__()
    allMusclesDict[key]=iterator
    key=iterator.name
    allMusclesDictByName[key]=iterator

  legIds=[]
#  start=MuscleGroup.objects.filter(name='Quads')[0]
  start=allMusclesDictByName['Quads']
  legIds.append(start)
  next=allMusclesDict[start.relatedMuscleGroup.__str__()]
#  next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
  while next!=start:
    if next.name!='Triple Extension' and next.name!='Calves':
      legIds.append(next)
#    next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)
    next=allMusclesDict[next.relatedMuscleGroup.__str__()]

  muscleList=[]
  muscleList.append(previousSeries.exercise.muscleGroup)
#legs can be paired with triple E
#but triple E can't be paired with legs

  if previousSeries.exercise.muscleGroup in legIds:
#    muscleList.append(MuscleGroup.objects.filter(name='Triple Extension')[0])
    muscleList.append(allMusclesDictByName['Triple Extension'])

  elif previousSeries.exercise.muscleGroup.name=='Lower Chest':
#    muscleList.append(MuscleGroup.objects.filter(name='Upper Chest')[0])
    muscleList.append(allMusclesDictByName['Upper Chest'])

  elif previousSeries.exercise.muscleGroup.name=='Upper Chest':
#    muscleList.append(MuscleGroup.objects.filter(name='Lower Chest')[0])
    muscleList.append(allMusclesDictByName['Lower Chest'])

#strip down potentialExercises such that only those within muscle list are present
  toUse=[]
  for iterator in potentialExercises:
    if iterator.muscleGroup in muscleList:
      toUse.append(iterator)
#  potentialExercises=list(potentialExercises.filter(muscleGroup__in=muscleList))
  potentialExercises=toUse



  toRemove=[]
  powerType=ExerciseType.objects.filter(name='power')[0]
  stabType=ExerciseType.objects.filter(name='stabilization')[0]


  ids=[]
  for iterator in potentialExercises:
    ids.append(iterator.id)

  if myPhase.name=='power':
    potentialExercises=list(Exercise.objects.filter(id__in=ids, exerciseType__in=[powerType]))
  elif myPhase.name=='muscle endurance':
    potentialExercises=list(Exercise.objects.filter(id__in=ids, exerciseType__in=[stabType]))


  possibles=len(potentialExercises)
  if len(potentialExercises)==0:
    goodToSuperset=False
    superset=False
    previousSeries=None
#    potentialExercises=Exercise.objects.filter(id__in=oldPotentials)
    potentialExercises=oldPotentials
    potentialExercises=evenlyDistribute(list(potentialExercises), request)
  t2=datetime.datetime.now()
  delta=t2-t1
  myString=""
  return goodToSuperset, potentialExercises, possibles



def getBaseExercises(currentUser, request):
  t1=datetime.datetime.now()
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  phases=userInfo.goal.phase.all()
  myPhase=phases[userInfo.currentPhase]
  rawUserId=currentUser.id
  componentList=list(WorkoutComponent.objects.all())
  flexComponent=WorkoutComponent.objects.filter(name="flexibility")[0]
  try:
    componentList.remove(flexComponent)
  except:
    pass
  baseExercises=list(Exercise.objects.raw("select id from (select t1.id, t2.exercise_id, t2.equipment_id, t3.name from oraclefitness_exercise as t1 join oraclefitness_exercise_equipment as t2 on t1.id=t2.exercise_id join oraclefitness_equipment as t3 on t2.equipment_id=t3.id) as o1 join (select t6.name from oraclefitness_userinformation as t4 join oraclefitness_userinformation_equipmentAvailable as t5 on t4.id=t5.userinformation_id join oraclefitness_equipment as t6 on t5.equipment_id = t6.id where t4.user_id=%s) as o2 on o1.name=o2.name;",[rawUserId]))#FILTERS BY EQUIPMENT
  mustRemove=list(Exercise.objects.raw("select id from (select t1.id, t2.exercise_id, t2.equipment_id, t3.name from oraclefitness_exercise as t1 join oraclefitness_exercise_equipment as t2 on t1.id=t2.exercise_id join oraclefitness_equipment as t3 on t2.equipment_id=t3.id) as o1 left outer join (select t6.name from oraclefitness_userinformation as t4 join oraclefitness_userinformation_equipmentAvailable as t5 on t4.id=t5.userinformation_id join oraclefitness_equipment as t6 on t5.equipment_id = t6.id where t4.user_id=%s) as o2 on o1.name=o2.name where o2.name is null;",[rawUserId]))
  muscleGroupRemoves=(Exercise.objects.raw("select id from (select t1.id, t1.name, t2.name as name3 from oraclefitness_exercise as t1 join oraclefitness_musclegroup as t2 on t1.muscleGroup_id=t2.id) as o1 join (select t6.name as name2 from oraclefitness_userinformation as t4 join oraclefitness_userinformation_avoidedMuscleGroup as t5 on t4.id=t5.userinformation_id join oraclefitness_musclegroup as t6 on t5.musclegroup_id = t6.id where t4.user_id=%s) as o2 on o1.name3=o2.name2;",[rawUserId]))

  exerciseIdList=[]
  for iterator in baseExercises:
    exerciseIdList.append(iterator.id)
  for iterator in mustRemove:
    if iterator.id in exerciseIdList:
      exerciseIdList.remove(iterator.id)

  musclesToRemoveQuery=ExercisesPerMuscleGroup.objects.filter(minimum=0, phase=myPhase, fitnessLevel=userInfo.currentFitnessLevel)

  allFitnessLevels=FitnessLevel.objects.all()
  allExperience=Experience.objects.all()
  fitnessIds=[]
  experienceIds=[]
  fitnessVal=userInfo.currentFitnessLevel.value
  experienceVal=userInfo.experience.value
  for iterator in allFitnessLevels:
    if iterator.value <= fitnessVal:
      fitnessIds.append(iterator.id)
  for iterator in allExperience:
    if iterator.value <= experienceVal:
      experienceIds.append(iterator.id)



  baseExercises=Exercise.objects.filter(Q(workoutComponent__in=componentList) | Q(workoutComponent2__in=componentList) | Q(workoutComponent3__in=componentList), phase__in=[myPhase], minFitnessLevel__in=fitnessIds, minExperience__in=experienceIds, id__in=exerciseIdList)

  baseExercises=baseExercises.exclude(muscleGroup__in=userInfo.avoidedMuscleGroup.all()).exclude(muscleGroup__in=musclesToRemoveQuery)

  #convert muscle group list to a bunch of ids
  muscleGroupRemovesList=[]
  for iterator in muscleGroupRemoves:
    muscleGroupRemovesList.append(iterator.id)

  baseExercises=baseExercises.exclude(id__in=muscleGroupRemovesList)

  basePotentials=Exercise.objects.raw("select t1.id from oraclefitness_exercise as t1 left outer join oraclefitness_exercise_equipment as t2 on t1.id=t2.exercise_id where t2.id is null;")
  baseIds=[]
  for iterator in basePotentials:
    baseIds.append(iterator.id)
  potentialExercisesBodyWeight=Exercise.objects.filter(Q(workoutComponent__in=componentList) | Q(workoutComponent2__in=componentList) | Q(workoutComponent3__in=componentList), phase__in=[myPhase], minFitnessLevel__in=fitnessIds, minExperience__in=experienceIds, id__in=baseIds)
  potentialExercisesBodyWeight=potentialExercisesBodyWeight.exclude(id__in=muscleGroupRemovesList)

  potentialExercisesBodyWeight=list(potentialExercisesBodyWeight.select_related('minFitnesslevel','minExperience','muscleGroup','secondaryMuscleGroup','workoutComponent','exerciseType2','workoutComponent2','workoutComponent3'))
  baseExercises=list(baseExercises.select_related('minFitnesslevel','minExperience','muscleGroup','secondaryMuscleGroup','workoutComponent','exerciseType2','workoutComponent2','workoutComponent3'))

  baseExercises.extend(potentialExercisesBodyWeight)

  return baseExercises

def generateWorkout(currentUser, currentDateTime, debug, debugMessage, dayOfWeek, thisWeekObject, baseExercises, request, exerciseMatrix):  #request is only passed in for debugging
  p=datetime.datetime.now()
  time3=p
  time4=p
  time5=p
  time6=p
  time7=p
  time8=p
  time9=p
  time10=p
  time11=p
  time12=p

  time1=datetime.datetime.now()
  t1=datetime.datetime.now()
  potentialErrorString=""
  debug=False
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  phases=userInfo.goal.phase.all()
  existingWorkout=TodaysWorkout.objects.filter(user=currentUser, date=currentDateTime)
  time2=datetime.datetime.now()
  if (not existingWorkout):# or forceWorkout:
    myPhase=phases[userInfo.currentPhase]
    myFitnessLevel=userInfo.currentFitnessLevel
    currentWeek= ((userInfo.currentDay-1)/7)+1

    strengthType=ExerciseType.objects.filter(name='Strength')[0]

    maxWeekInPhase=6
    currentWeekToUse=currentWeek
    if myPhase in userInfo.visitedPhases.all():
      currentWeekToUse=maxWeekInPhase

    time3=datetime.datetime.now()
    exercisesPerMuscleGroup=ExercisesPerMuscleGroup.objects.filter(phase=myPhase, fitnessLevel=userInfo.currentFitnessLevel).select_related('muscleGroup')
    exercisesPerMuscleGroupDict={}
    for iterator in exercisesPerMuscleGroup:
      key=iterator.muscleGroup.name
      exercisesPerMuscleGroupDict[key]=iterator
    exhaustionPercent=Exhaustion.objects.filter(daysPerWeek=userInfo.daysPerWeek, phase=myPhase)[0].percent
    time4=datetime.datetime.now()

    volumeTable=VolumeTable.objects.filter(fitnessLevel=myFitnessLevel, phase=myPhase, week=currentWeekToUse)[0]
    todaysWorkout=TodaysWorkout()

    todaysWorkout.date=currentDateTime#+testingDelta
    todaysWorkout.user=currentUser
    todaysWorkout.thisWeek=thisWeekObject
    todaysWorkout.save()
    time5=datetime.datetime.now()

    myWeek=todaysWorkout.thisWeek



    stabPhase=Phase.objects.filter(name='stabilization')[0]
    if len(myWeek.workoutComponents.all())==0 and not myWeek.cardio:
      todaysWorkout.offDay=True
      todaysWorkout.save()
      userInfo.todaysWorkout=todaysWorkout
      userInfo.save()
      return todaysWorkout, debugMessage

#      return render_to_response('todaysworkout.html', locals())
    time6=datetime.datetime.now()
    volume1=0
    wlume2=0
    resistanceComponent=WorkoutComponent.objects.filter(name='Resistance')[0]
    if myPhase.name=='muscle endurance':
      #hypertrophy and stabilization
      hypPhase=Phase.objects.filter(name='hypertrophy')[0]
      stabPhase=Phase.objects.filter(name='stabilization')[0]
      volumeTable2=VolumeTable.objects.filter(fitnessLevel=myFitnessLevel, phase=hypPhase, week=currentWeekToUse)[0]
      volume1=Volume.objects.filter(workoutComponent=resistanceComponent, parentTable=volumeTable2)[0]
      volumeTable2=VolumeTable.objects.filter(fitnessLevel=myFitnessLevel, phase=stabPhase, week=currentWeekToUse)[0]
      volume2=Volume.objects.filter(workoutComponent=resistanceComponent, parentTable=volumeTable2)[0]


    elif myPhase.name=='power':
      #max strength and power
      maxPhase=Phase.objects.filter(name='maximal strength')[0]
      powPhase=Phase.objects.filter(name='power')[0]

      volumeTable2=VolumeTable.objects.filter(fitnessLevel=myFitnessLevel, phase=maxPhase, week=currentWeekToUse)[0]
      volume1=Volume.objects.filter(workoutComponent=resistanceComponent, parentTable=volumeTable2)[0]

      volumeTable2=VolumeTable.objects.filter(fitnessLevel=myFitnessLevel, phase=powPhase, week=currentWeekToUse)[0]
      volume2=Volume.objects.filter(workoutComponent=resistanceComponent, parentTable=volumeTable2)[0]
    time7=datetime.datetime.now()




    todaysExercises=[]#list to prevent the same exercises being used twice in a workout


    equipmentList=userInfo.equipmentAvailable.all()
    allEquipmentList=Equipment.objects.all()

    yesterdayMuscles=[]
    yesterday=currentDateTime+timedelta(days=-1)
    yesterdayWorkout=TodaysWorkout.objects.filter(date=yesterday, user=currentUser)
    if yesterdayWorkout:
      yesterdaySeries=yesterdayWorkout[0].exercises.select_related('exercise__muscleGroup').all()
      for seriesObject in yesterdaySeries:
        yesterdayMuscles.append(seriesObject.exercise.muscleGroup)
        yesterdayMuscles.extend(list(seriesObject.exercise.helpers.all()))


    time8=datetime.datetime.now()




    time9=datetime.datetime.now()
    if baseExercises is None:
      baseExercises=getBaseExercises(currentUser, request)
    potentialExercises=[]
    for iterator in baseExercises:
      potentialExercises.append(iterator)


    potentialErrorString=potentialErrorString+"cp1: "+len(potentialExercises).__str__()+"\n"
    toRemove=[]
    userEquipment=userInfo.equipmentAvailable.all()
    time12=datetime.datetime.now()
    #toRemoveString=""
#    value1=len(potentialExercises)
#    for exerciseObject in potentialExercises:
#      canUse=True
#      for equipmentObject in exerciseObject.equipment.all():
#        if not equipmentObject in userEquipment:
#          canUse=False
#      if not canUse:
#        toRemove.append(exerciseObject)
#     #   toRemoveString=toRemoveString+exerciseObject.name
#    for iterator in toRemove:
#      potentialExercises.remove(iterator)
#    value2=len(potentialExercises)



#yesterday muscles n  workinc, and neither is the equipment list
    toRemove=[]
    for iterator in potentialExercises:
      if iterator.muscleGroup in yesterdayMuscles:
        toRemove.append(iterator)
    for iterator in toRemove:
      potentialExercises.remove(iterator)

    potentialErrorString=potentialErrorString+"cp2: "+len(potentialExercises).__str__()+"\n"


#    toRemove=[]
#    for exerciseObject in potentialExercises:
#      if exerciseObject.minFitnessLevel.value > fitnessVal:
#        toRemove.append(exerciseObject)
#      elif exerciseObject.minExperience.value > experienceVal:
#       toRemove.append(exerciseObject)
#    for exerciseObject in toRemove:
#      try:
#        potentialExercises.remove(exerciseObject)
#      except:
#        pass#may have already been removed
#    time5TotalRemoved=len(toRemove).__str__()
    potentialErrorString=potentialErrorString+"cp3: "+len(potentialExercises).__str__()+"\n"


    if debug:
      debugMessage=debugMessage+len(potentialExercises).__str__()+" potential exercises before muscle filtering on "+currentDateTime.__str__()+".<br>\n"



    potentialExercises=filterByMuscleGroups(currentUser, potentialExercises, currentDateTime, request)

#   this isn't even used
#    potentialExercises=eliminateRepeatDays(currentUser, potentialExercises, currentDateTime)

    if debug:
      newWeek=ThisWeek.objects.filter(user=currentUser)
      counter=0
      for iterator in newWeek:
        if iterator.cardio:
          counter=counter+1
      debugMessage=debugMessage+"There are "+counter.__str__()+" cardio days this week.<br>\n"
      debugMessage=debugMessage+len(potentialExercises).__str__()+" potential exercises before volume integration<br>\n"


    for j in range(0, len(potentialExercises)):
      potentialExercises[j]=potentialExercises[j].id
    #potential Exercises has redundancies...
      #convert back to queryset object
    potentialExercisesStart=Exercise.objects.filter(id__in=potentialExercises)
######################START FOR LOOP####################################
    workoutComponentsReverseOrder=[]#wrong type of exercises are being trimmed first, this mitigates that
    initial=list(myWeek.workoutComponents.all())
    #I dunno how to do a reverse for loop in python and I have no internets =/
    counter=len(initial)-1
    while counter>=0:
      workoutComponentsReverseOrder.append(initial[counter])
      counter=counter-1

    muscleDictionary={}                         #tryme
    for iterator in MuscleGroup.objects.all():  #tryme
      muscleDictionary[iterator.name]=0         #tryme
    nextMuscleGroup=None                        #tryme

###########################################################

#    send_mail("cp1", "got here", 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
    muscleTraverseDict={}
    muscleTraverseDictName={}
    allMuscleGroups=MuscleGroup.objects.all()
    #check to see if there's any muscle group worked only once for this workout and drop if so
    for muscleGroupObject in allMuscleGroups:
      key=muscleGroupObject.id.__str__()
      key2=muscleGroupObject.name
      muscleTraverseDict[key]=muscleGroupObject
      muscleTraverseDictName[key2]=muscleGroupObject
#################################3
    chestIds=[]
    legIds=[]
#    start=MuscleGroup.objects.filter(name='Upper Chest')[0]
    start=muscleTraverseDictName['Upper Chest']
    chestIds.append(start)
#    next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
    next=muscleTraverseDict[start.relatedMuscleGroup.__str__()]
    while next!=start:
      chestIds.append(next)
#      next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)
      next=muscleTraverseDict[next.relatedMuscleGroup.__str__()]

#    start=MuscleGroup.objects.filter(name='Quads')[0]
    start=muscleTraverseDictName['Quads']
    legIds.append(start)
    #next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
    next=muscleTraverseDict[start.relatedMuscleGroup.__str__()]
    while next!=start:
      if next.name!='Triple Extension':
        legIds.append(next)
      #next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)
      next=muscleTraverseDict[next.relatedMuscleGroup.__str__()]

    relevantVolumes=Volume.objects.filter(parentTable=volumeTable).select_related('workoutComponent')
    volumeDict={}
    cannotUse=list(userInfo.avoidedExercise.all())
    for iterator in relevantVolumes:
      key=iterator.workoutComponent.name
      volumeDict[key]=iterator
    for iterator in workoutComponentsReverseOrder:
      currentComponent=iterator
#      currentVolume=Volume.objects.filter(workoutComponent=iterator, parentTable=volumeTable)[0]
      key=iterator.name
      currentVolume=volumeDict[key]
      maxRange=random.randint(currentVolume.minExercises, currentVolume.maxExercises)
      if debug:
        debugMessage=debugMessage+maxRange.__str__()+" exercises should be generated from "+currentVolume.workoutComponent.name+" <br>\n"


      superset=False
      previousSeries=None

      if iterator.name=='Flexibility': #######special case
        pass
          #have to pass this because flexibility is last
      else:
          ##########EXERCISE FILTERING###############################################

        if nextMuscleGroup==None:
          potentialExercises=list(potentialExercisesStart.filter(Q(workoutComponent=iterator) | Q(workoutComponent2=iterator) | Q(workoutComponent3=iterator)))
          #NOW EVEN OUT THE DISTRUBUTION SO THERE IS AN EQUAL NUMBER FROM EACH MUSCLE GROUP!!
          potentialExercises=evenlyDistribute(potentialExercises, request)
        else:
          potentialExercises=list(potentialExercisesStart.filter(Q(workoutComponent=iterator) | Q(workoutComponent2=iterator) | Q(workoutComponent3=iterator), muscleGroup=nextMuscleGroup))  #tryme
          if len(potentialExercises)==0:
            potentialExercises=list(potentialExercisesStart.filter(Q(workoutComponent=iterator) | Q(workoutComponent2=iterator) | Q(workoutComponent3=iterator)))
            potentialExercises=evenlyDistribute(potentialExercises, request)


        potentialErrorString=potentialErrorString+"cp4: "+len(potentialExercises).__str__()+"\n"

          ##########END EXERCISE FILTERING###########################################
        if debug:
          debugMessage=debugMessage+len(potentialExercises).__str__()+" possible exercises from "+currentVolume.workoutComponent.name+" <br>\n"
          if len(potentialExercises)<=15:
            for item in potentialExercises:
              debugMessage=debugMessage+"    -"+item.name+" <br>\n"

        oldPotentials=[]
        oldPotentialsForSuperset=[]
        for iterator in potentialExercises:
          oldPotentials.append(iterator)
          oldPotentialsForSuperset.append(iterator)



        potentialExerciseIds=[]
        for iterator in potentialExercises:
          potentialExerciseIds.append(iterator.id)
        changed=False
        previousMuscle=None
        muscleCount=1
        if currentComponent.name=='Resistance' and (myPhase.name=='power' or myPhase.name=='muscleEndurance') and maxRange%2==1:
          maxRange=maxRange+1
        iterationCounter=0
        totalReps=0
#################




    #muscleTraverseDict={}
    #muscleTraverseDictName={}
########



##begin select exercises and all that###########3
        while iterationCounter<maxRange:
#        for count in range(0, maxRange):
          if previousMuscle:
            relatedToPrevious=[]
            start=previousMuscle
            relatedToPrevious.append(start)
#            next=MuscleGroup.objects.get(id=start.relatedMuscleGroup)
            next=muscleTraverseDict[start.relatedMuscleGroup.__str__()]
            while next!=start:
              relatedToPrevious.append(next)
              #next=MuscleGroup.objects.get(id=next.relatedMuscleGroup)
              next=muscleTraverseDict[next.relatedMuscleGroup.__str__()]




          for iterator in todaysExercises:
            cannotUse.extend(filterByMutex(exerciseMatrix, potentialExercises, iterator, request))


          toRemove=[]
          for exerciseObject in potentialExercises:
            if exerciseObject in todaysExercises or exerciseObject in cannotUse:
              toRemove.append(exerciseObject)
          for exerciseObject in toRemove:
            while exerciseObject in potentialExercises:
              potentialExercises.remove(exerciseObject)

          if superset:  #don't know if I'm duplicating unnecessary work here, I might be
            toRemove=[]
            for exerciseObject in oldPotentialsForSuperset:
              if exerciseObject in todaysExercises or exerciseObject in cannotUse:
                toRemove.append(exerciseObject)
#            from django.core.mail import send_mail
#            removeString=""
#            for iterator in toRemove:
#              removeString=removeString+iterator.name+", "
#            send_mail("Exercises to remove", removeString, 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
            for exerciseObject in toRemove:
              while exerciseObject in oldPotentialsForSuperset:
                oldPotentialsForSuperset.remove(exerciseObject)
                #DON'T KNOW IF THIS EVEN DOES ANYTHING...NEED TO TEST!!


          if not superset and (myPhase.name=='power' or myPhase.name=='muscle endurance'):
            potentialExercises=[]
            for iterator in oldPotentials:
              potentialExercises.append(iterator)
            potentialExercises=evenlyDistribute(list(potentialExercises), request)
          elif superset and (myPhase.name=='power' or myPhase.name=='muscle endurance'):  #SUPERSET
            success, potentialExercises, possibles=supersetPossibles(oldPotentialsForSuperset, potentialExercises, myPhase, previousSeries, todaysExercises, request, exerciseMatrix)
            #T/F,    exercise list,    , len(exercise list)
          if previousMuscle and not superset and currentComponent.name=='Resistance' and float(muscleCount)*100.0/float(maxRange)<=exhaustionPercent:
            potentialExercises2=Exercise.objects.filter(id__in=potentialExerciseIds, muscleGroup__in=relatedToPrevious)
            if potentialExercises2.count()>0:
              potentialExercises=evenlyDistribute(list(potentialExercises2), request)
              changed=True

          elif (changed and currentComponent.name=='Resistance' and float(muscleCount)*100.0/float(maxRange)>exhaustionPercent and not superset):
            changed=False
            previousMuscle=None
            potentialExercises=list(Exercise.objects.filter(id__in=potentialExerciseIds))
            potentialExercises=evenlyDistribute(potentialExercises, request)
          potentialErrorString=potentialErrorString+"cp5: "+len(potentialExercises).__str__()+"\n"
          someExercise=Series()
          someExercise.reps=random.randint(currentVolume.minReps, currentVolume.maxReps)
          if (myPhase.name=='power' or myPhase.name=='muscle endurance') and currentComponent.name=='Resistance':
            if not superset:
              someExercise.reps=random.randint(volume1.minReps, volume1.maxReps)
            else:
              someExercise.reps=random.randint(volume2.minReps, volume2.maxReps)
          if someExercise.reps==7:
            someExercise.reps=8
          elif someExercise.reps==9:
            someExercise.reps=10
          elif someExercise.reps==11:
            someExercise.reps=12
          elif someExercise.reps==13:
            someExercise.reps=12
          elif someExercise.reps==14:
            someExercise.reps=15
          totalReps=totalReps+someExercise.reps
          if totalReps>=currentVolume.maxTotalReps:
            iterationCounter=maxRange#max it out
          someExercise.sets=random.randint(currentVolume.minSets, currentVolume.maxSets)

          someExercise.tempo=myPhase.tempo + " seconds" #tempo is the rate at which you do the actual exercise
          if superset and myPhase.name=='muscle endurance':
            someExercise.tempo=stabPhase.tempo
#            someExercise.tempo=Phase.objects.filter(name='stabilization')[0].tempo

          someExercise.rest=myPhase.rest

          potentialErrorString=potentialErrorString+"cp6: "+len(potentialExercises).__str__()+"\n"
          potentialErrorString=potentialErrorString+"And the length of todaysExercises is "+len(todaysExercises).__str__()+"\n"
          newMuscleDict={}
          muscleGroups=MuscleGroup.objects.all()
          for iterator in muscleGroups:
            key=iterator.id.__str__()
            newMuscleDict[key]=iterator
          if len(potentialExercises)>=1:
            started=False
            anExercise=1
            counter=0
            todaysMuscles=[]
            for iterator in todaysExercises:
              if not iterator.muscleGroup in todaysMuscles:
                todaysMuscles.append(iterator.muscleGroup)
            for iterator in todaysMuscles:
              currentMuscleGroup=iterator
              firstMuscleGroup=currentMuscleGroup
              started=False
              while firstMuscleGroup!=currentMuscleGroup or not started:
                started=True
                if not currentMuscleGroup in todaysMuscles:
                  todaysMuscles.append(currentMuscleGroup)
#                currentMuscleGroup=MuscleGroup.objects.get(id=currentMuscleGroup.relatedMuscleGroup)
                currentMuscleGroup=newMuscleDict[currentMuscleGroup.relatedMuscleGroup.__str__()]
#            exerciseMatrix=getMutexMatrix(request)
#            if superset:
#              for someItem in potentialExercises:
#                writeTestData("  ----->"+someItem.name)

            keepGoing=True  #for isolated exercises
            reset=False

    #POST-PRODUCTION...NO TESTIONG HERE, I'm shooting from the hip


            potentialErrorString=potentialErrorString+"cp7: "+len(potentialExercises).__str__()+"\n"
            #writeTestData("test")
            while ((anExercise in todaysExercises or not started or keepGoing or anExercise in cannotUse)) and counter<15:#I reduced from 15 to 5

              condition=""
              started=True
              if len(potentialExercises)-1>0:
                anExercise=potentialExercises[random.randint(0, len(potentialExercises)-1)]
              else:  #This happen when the db runs out of exercises to use
#                from django.core.mail import send_mail
#                send_mail("Error with potential exercise length", potentialErrorString, 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
                keepGoing=False
                break #exit the loop to stop doing computations
              if keepGoing and  anExercise.compound:
                keepGoing=False
              else: #there must be at least 1 compound muscle group already there
                if anExercise.muscleGroup in todaysMuscles:
                  keepGoing=False
              checkExercisesPerMuscleGroup=exercisesPerMuscleGroupDict[anExercise.muscleGroup.name]
#              checkExercisesPerMuscleGroup=ExercisesPerMuscleGroup.objects.filter(muscleGroup=anExercise.muscleGroup, phase=myPhase, fitnessLevel=userInfo.currentFitnessLevel)[0]
              if muscleDictionary[anExercise.muscleGroup.name] >= checkExercisesPerMuscleGroup.maximum:#no more muscle groups from this trash
                keepGoing=True
                condition="couldn't add because of exercises per muscle group"
              if currentComponent.name=='Resistance' and (myPhase.name=='power' or myPhase.name=='muscle endurance') and not superset:
                condition="good so far"
                if not strengthType in anExercise.exerciseType.all():
                  keepGoing=True
                  condition="couldn't add because no strength type exercises"
                else:
                  blankSeries=Series(exercise=anExercise)
                  #I think I wasted a bunch of stuff here...
                  goodToUse, blank, possibles=supersetPossibles(oldPotentialsForSuperset, potentialExercises, myPhase, blankSeries, todaysExercises, request, exerciseMatrix)
                  if not goodToUse or possibles==1:
                    keepGoing=True
                    condition="couldn't use cause of superset possibles"
              counter=counter+1

              if counter>=7 and not reset:
                reset=True
                potentialExercises=list(Exercise.objects.filter(id__in=potentialExerciseIds))
                potentialExercises=evenlyDistribute(potentialExercises, request)
#              if counter==15:
#                writeTestData("COULDN'T ADD "+anExercise.name+" "+condition)
#                writeTestData("stuck on "+anExercise.name)
#                forceReset=True
#            if counter==55:
#              writeTestData("couldn't add "+anExercise.name)
#              if superset:
#                writeTestData("superset is on")
#              else:
#                writeTestData("superset is off")
#           i   iterationCounter=iterationCounter-1


            if counter==15 and currentComponent.name=='Resistance' and (myPhase.name=='power' or myPhase.name=='muscle endurance'):
              iterationCounter=iterationCounter+1#increment because this will cause a floater
              superSet=False
              #this was never reached

#              from django.core.mail import send_mail
#              send_mail("Error with superset", "Got here", 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
            if counter<15 and anExercise!=1:
              someExercise.exercise=anExercise
              todaysExercises.append(anExercise)
              someExercise.save()
              previousMuscle=anExercise.muscleGroup
              muscleCount=muscleCount+1
              if not superset:
                todaysWorkout.exercises.add(someExercise)
                if (myPhase.name=='muscle endurance' or myPhase.name=='power') and currentComponent.name=='Resistance' and strengthType in anExercise.exerciseType.all():
                  superset=True
                  previousSeries=someExercise
              else:
                previousSeries.superSet=someExercise.id
                previousSeries.save()
                superset=False
                previousSeries=None
              if currentComponent.name=='Resistance' or currentComponent.name=='Core':
                muscleDictionary[someExercise.exercise.muscleGroup.name]=muscleDictionary[someExercise.exercise.muscleGroup.name]+1
                checkExercisesPerMuscleGroup=ExercisesPerMuscleGroup.objects.filter(muscleGroup=someExercise.exercise.muscleGroup, phase=myPhase, fitnessLevel=userInfo.currentFitnessLevel)[0]

                if muscleDictionary[someExercise.exercise.muscleGroup.name] < checkExercisesPerMuscleGroup.minimum:
                  nextMuscleGroup=someExercise.exercise.muscleGroup

                else:
                  nextMuscleGroup=None
          iterationCounter=iterationCounter+1

######################END FOR LOOP####################################






    #potentialErrorString=potentialErrorString+(todaysWorkout.exercises.all().count()).__str__()+" Exercises before trimmed to time\n"
    if debug:
      debugMessage=debugMessage+len(list(todaysWorkout.exercises.all())).__str__()+" Exercises before trimmed to time<br>\n"

    todaysWorkout=reduceToTime(todaysWorkout, myWeek.cardio, myPhase, myWeek.timed, myWeek.level, volumeTable, request)
    if debug:
      debugMessage=debugMessage+len(list(todaysWorkout.exercises.all())).__str__()+" Exercises after trimmed to time<br>\n"
      writeTestData(debugMessage+"\n\n")
    #potentialErrorString=potentialErrorString+(todaysWorkout.exercises.all().count()).__str__()+" Exercises after trimmed to time\n"
    #from django.core.mail import send_mail
    #send_mail("NO Error with potential exercise length", potentialErrorString, 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)

#Exercises need to appear in this order
#Balance
#Reactive
#resistance
#core
#cardio (as applicable)

    someComponents=WorkoutComponent.objects.all()
    componentDict={}
    for iterator in someComponents:
      key=iterator.name
      componentDict[key]=iterator

    orderedComponents=[]
    orderedComponents.append(componentDict['Balance'])
    orderedComponents.append(componentDict['Reactive'])
    orderedComponents.append(componentDict['Resistance'])
    orderedComponents.append(componentDict['Core'])
#    orderedComponents.append(WorkoutComponent.objects.filter(name='Balance')[0])
#    orderedComponents.append(WorkoutComponent.objects.filter(name='Reactive')[0])
#    orderedComponents.append(WorkoutComponent.objects.filter(name='Resistance')[0])
#    orderedComponents.append(WorkoutComponent.objects.filter(name='Core')[0])
##################group muscle groups together########################s

    tempList=list(todaysWorkout.exercises.select_related('exercise__workoutComponent').all())
#.select_related('workoutComponent', 'muscleGroup'))#filter(workoutComponent=workoutComponentObject)
    initialIds=[]
    for iterator in tempList:
      initialIds.append(iterator.id)
    muscleDict={}
    allMuscles=MuscleGroup.objects.all()
    for iterator in allMuscles:
      key=iterator.id.__str__()
      muscleDict[key]=iterator
    for workoutComponentObject in orderedComponents:
      allExercises=[]
      for iterator in tempList:
        if iterator.exercise.workoutComponent==workoutComponentObject: #COMPLETE LATER
          allExercises.append(iterator)
      maxIndex=len(allExercises)
      for j in range(0,maxIndex-1):
        currentMuscleGroup=allExercises[j].exercise.muscleGroup
        firstMuscleGroup=currentMuscleGroup
        started=False
        muscleCluster=[]
        while firstMuscleGroup!=currentMuscleGroup or not started:
          started=True
          muscleCluster.append(currentMuscleGroup.id)
#          currentMuscleGroup=MuscleGroup.objects.get(id=currentMuscleGroup.relatedMuscleGroup)
          currentMuscleGroup=muscleDict[currentMuscleGroup.relatedMuscleGroup.__str__()]
        for k in range(j+1, maxIndex):
          if allExercises[k].exercise.muscleGroup.id in muscleCluster:
            temp=allExercises[j+1]
            allExercises[j+1]=allExercises[k]
            allExercises[k]=temp

      allExercisesCopy=[]
      for j in range(0,maxIndex):
        allExercisesCopy.append(Series(exercise=allExercises[j].exercise, reps=allExercises[j].reps, sets=allExercises[j].sets, tempo=allExercises[j].tempo, rest=allExercises[j].rest, superSet=allExercises[j].superSet))
       # allExercises[j].delete()

      for j in range(0, maxIndex):
        allExercisesCopy[j].save()
        todaysWorkout.exercises.add(allExercisesCopy[j])
    #DELETE THE OLD UNORDERED
    todaysWorkout.exercises.filter(id__in=initialIds).delete()
########################end grouping################################3

############now do flexibility#####################
    todaysMuscleGroups=[]
    for seriesObject in todaysWorkout.exercises.select_related().all():
      if not seriesObject.exercise.muscleGroup in todaysMuscleGroups:
        todaysMuscleGroups.append(seriesObject.exercise.muscleGroup)


    flexComponent=WorkoutComponent.objects.filter(name="Flexibility")[0]
    currentVolume=Volume.objects.filter(workoutComponent=flexComponent, parentTable=volumeTable)[0]
    maxRange=random.randint(currentVolume.minExercises, currentVolume.maxExercises)
#      for count in range(0, maxRange):############I GOT RID OF THIS, MIGHT BE NOTEWORTHY, but might not be either
    for iterator in todaysMuscleGroups:
      flexibilityExercises=list(Exercise.objects.filter(workoutComponent=flexComponent, muscleGroup=iterator))
      someExercise=Series()
      someExercise.reps=random.randint(currentVolume.minReps, currentVolume.maxReps)
      someExercise.sets=1#random.randint(currentVolume.minSets, currentVolume.maxSets)
      someExercise.tempo=''
      someExercise.rest=0
      try:
        someExercise.exercise=flexibilityExercises[random.randint(0, len(flexibilityExercises)-1)]
        someExercise.save()
        todaysWorkout.exercises.add(someExercise)
      except:
        pass




##############################################################################

    todaysWorkout.save()
    if debug:
      debugMessage=debugMessage+len(list(todaysWorkout.exercises.all())).__str__()+" Exercises after save<br>"

#    totalCount=Count.objects.all()[0]
#    totalCount.count=totalCount.count+1
#    totalCount.save()
    userInfo.todaysWorkout=todaysWorkout
    userInfo.save()


  else:#workout for today has already been generated
    todaysWorkout=TodaysWorkout.objects.filter(user=currentUser, date=currentDateTime)[0]
    currentWeek= ((userInfo.currentDay-1)/7)+1
    userInfo.todaysWorkout=todaysWorkout
    userInfo.save()
    try:
      myPhase=phases[userInfo.currentPhase]
    except:
      userInfo.currentPhase=0
      userInfo.save()
      myPhase=phases[0]
    if debug:
      debugMessage=debugMessage+"Workout ID: "+todaysWorkout.id.__str__()+"<br>"

  if len(todaysWorkout.exercises.all())==0 and not todaysWorkout.cardio and todaysWorkout.thisWeek:#need to make it an off day
    toModify=todaysWorkout.thisWeek
    for iterator in toModify.workoutComponents.all():
      toModify.workoutComponents.remove(iterator)
    toModify.save()
    todaysWorkout.offDay=True
    todaysWorkout.save()
  t2=datetime.datetime.now()
  delta=t2-t1
#  from django.core.mail import send_mail
#  messageString=delta.seconds+.000001*delta.microseconds

#  send_mail("Time for one workout generation", messageString.__str__(), 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
#  writeTestData("ID #"+todaysWorkout.id.__str__()+"\n"+debugMessage)
  delta1=time2-time1
  delta1=delta1.seconds+.000001*delta1.microseconds
  delta2=time3-time2
  delta2=delta2.seconds+.000001*delta2.microseconds
  delta3=time4-time3
  delta3=delta3.seconds+.000001*delta3.microseconds
  delta4=time5-time4
  delta4=delta4.seconds+.000001*delta4.microseconds
  delta5=time6-time5
  delta5=delta5.seconds+.000001*delta5.microseconds
  delta6=time7-time6
  delta6=delta6.seconds+.000001*delta6.microseconds
  delta7=time8-time7
  delta7=delta7.seconds+.000001*delta7.microseconds
  delta8=time9-time8
  delta8=delta8.seconds+.000001*delta8.microseconds
  delta9=time10-time9
  delta9=delta9.seconds+.000001*delta9.microseconds
  delta10=time11-time10
  delta10=delta10.seconds+.000001*delta10.microseconds
  delta11=time12-time11
  delta11=delta11.seconds+.000001*delta11.microseconds
  messageString="delta1: "+delta1.__str__()+"\n"
  messageString=messageString+"delta2: "+delta2.__str__()+"\n"
  messageString=messageString+"delta3: "+delta3.__str__()+"\n"
  messageString=messageString+"delta4: "+delta4.__str__()+"\n"
  messageString=messageString+"delta5: "+delta5.__str__()+"\n"
  messageString=messageString+"delta6: "+delta6.__str__()+"\n"
  messageString=messageString+"delta7: "+delta7.__str__()+"\n"
  messageString=messageString+"delta8: "+delta8.__str__()+"\n"
  messageString=messageString+"delta9: "+delta9.__str__()+"\n"
  messageString=messageString+"delta10: "+delta10.__str__()+"\n"
  messageString=messageString+"delta11: "+delta11.__str__()+"\n"
#  from django.core.mail import send_mail
#  send_mail("Innter Loop Times", messageString.__str__(), 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)
  return todaysWorkout, debugMessage
#need to account for debug message, dayOfWeek, userInfo





def putToNextPhase(userInfo):
  currentWeek=1
  userInfo.currentDay=1
  dayOfWeek=1
  userInfo.save()
  phases=userInfo.goal.phase.all()
  myPhase=phases[userInfo.currentPhase]
  if len(phases)==2:#special case
    userInfo.previousPhase=userInfo.currentPhase
    if not myPhase in userInfo.visitedPhases.all():
      userInfo.visitedPhases.add(myPhase)
    userInfo.currentPhase=userInfo.currentPhase-1
    if userInfo.currentPhase==-1:
      userInfo.currentPhase=len(phases)-1
    myPhase=phases[userInfo.currentPhase]
    somePhaseLength=PhaseLength.objects.filter(goal=userInfo.goal, phase=myPhase)[0]
    userInfo.phaseLength=random.randint(somePhaseLength.minLength,somePhaseLength.maxLength)
  else:#choose a random phase other than the previous 2
    newList=[]
    for iterator in phases:
      newList.append(iterator)
    newList.remove(phases[userInfo.currentPhase])
    if not userInfo.previousPhase is None:
      newList.remove(phases[userInfo.previousPhase])
    try:
      randIndex=random.randint(0, len(newList)-1)
    except:

      randIndex=0#this will only happen if there is only one phase in the goal
    if not myPhase in userInfo.visitedPhases.all():
      userInfo.visitedPhases.add(myPhase)
    userInfo.previousPhase=userInfo.currentPhase
    userInfo.currentPhase=list(phases).index(newList[randIndex])
    myPhase=phases[userInfo.currentPhase]
    somePhaseLength=PhaseLength.objects.filter(goal=userInfo.goal, phase=myPhase)[0]
    userInfo.phaseLength=random.randint(somePhaseLength.minLength,somePhaseLength.maxLength)
  userInfo.save()
  return userInfo





def todaysworkout(request, altid=None):
  t1=datetime.datetime.now()
  login, superuser = credentials(request)
  if altid!=None:
    login=0
    request.session['userID']=altid
    request.session['role']="user"
  if login:
    return signIn(request)
  currentUser=User.objects.filter(username=request.session['userID'])[0]
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  goal=userInfo.goal
  if goal==None:
    successMessage="You have not yet chosen a <a href='../mygoals'>goal</a>"
    userAgent=request.META['HTTP_USER_AGENT']
    if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
      successMessage="You have not yet chosen a goal"
      return render_to_response("successiphone.html", locals())
    return render_to_response('success.html', locals())
  elif len(userInfo.equipmentAvailable.all())==0:
    successMessage="You need to input your <a href='../mygoals'>equipment</a> available to you"
    userAgent=request.META['HTTP_USER_AGENT']
    if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
      successMessage="You need to input your equipment available to you under \"My Goals\""
      return render_to_response('successiphone.html',locals())
    return render_to_response('success.html', locals())
  currentDateTime=False
  if request.method=='POST' and 'year' in request.POST:
    currentDateTime=datetime.datetime(year=int(request.POST['year']), month=int(request.POST['month']), day=int(request.POST['day']))

  if not currentDateTime:
    needTime=True
    userAgent=request.META['HTTP_USER_AGENT']

    if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
      return render_to_response('todaysworkoutiphone.html', locals())


    return render_to_response("todaysworkout.html", locals())
  forceWorkout=False

  debugMessage=""
  debug=False



  allComicals=list(ComicalStatement.objects.filter(Q(gender=userInfo.gender)|Q(gender=None)))
#  allComicals.extend(list(ComicalStatement.objects.filter(gender=None)))
  comicalStatement=allComicals[random.randint(0, len(allComicals)-1)]
  existingWorkout=TodaysWorkout.objects.filter(user=currentUser, date=currentDateTime).select_related('thisWeek')

  weekday=currentDateTime.weekday()
  debugMessage=debugMessage+"weekday gives a result of "+weekday.__str__()+"<br>"



  justStarted=False
  if userInfo.currentDay is None:
     userInfo.currentDay=1
     userInfo.save()
     justStarted=True
  if not justStarted and (not existingWorkout or not existingWorkout[0].visited):
     userInfo.currentDay=userInfo.currentDay+1
  elif existingWorkout and existingWorkout[0].visited:#check to see if you went back in time
#this can cause a bug when a user tries to make 2 simultaneous requests.
    try:
    #if True: #production
      userInfo.currentDay=(userInfo.currentDay/7)*7+existingWorkout[0].thisWeek.dayNumber
    except:
    #else:
      TodaysWorkout.objects.filter(user=currentUser).delete()
      ThisWeek.objects.filter(user=currentUser).delete()
#lastminfix
      successMessage="Woops!  There was an error processing your request.  Please go back to 'My Goals' and try again.  Sorry for the inconvenience."
      return render_to_response('successiphone.html', locals())
    #just make the workouts after this one not visited, rest of program will take care of it.
    dayList=[]
    for j in range(1, 7):#only need to look at next 6 days at most...
      nextDate=existingWorkout[0].date+timedelta(days=j)
      dayList.append(nextDate)
    toModify=TodaysWorkout.objects.filter(user=currentUser, date__in=dayList)
    for todaysWorkoutObject in toModify:
      oldVal=todaysWorkoutObject.visited
      todaysWorkoutObject.visited=False
      if oldVal!=todaysWorkoutObject.visited:
        todaysWorkoutObject.save()
  missedYesterdayButton=True
  try:
    dayOfWeek=userInfo.currentDay % 7
    if dayOfWeek==0:
      dayOfWeek=7
  except:
    missedYesterdayButton=False


  if missedYesterdayButton:
    yesterdaysWorkout=TodaysWorkout.objects.filter(user=currentUser, date=currentDateTime+timedelta(days=-1))
    if yesterdaysWorkout and yesterdaysWorkout[0].offDay:
      missedYesterdayButton=False


    yesterdayThisWeek=ThisWeek.objects.filter(user=currentUser, dayNumber=dayOfWeek-1)
    if yesterdayThisWeek and yesterdayThisWeek[0].workoutComponents.count()==0:
      missedYesterdayButton=False


    if not yesterdayThisWeek:
      missedYesterdayButton=False


  if request.method=='POST':
    if 'missed' in request.POST:
      alreadyOffDay=False
      missedYesterdayButton=False
      if existingWorkout and existingWorkout[0].offDay:
        alreadyOffDay=True
      pulledYesterdaysWorkout=missedYesterday(currentUser, currentDateTime)
      if not pulledYesterdaysWorkout:
        successMessage="Yesterday was an off day (or you already pulled yesterday's workout).  Go back to <a href='../todaysworkout'>today's workout</a>"
        userAgent=request.META['HTTP_USER_AGENT']
        if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
          return render_to_response('successiphone.html', locals())
        return render_to_response('success.html', locals())
      if pulledYesterdaysWorkout and alreadyOffDay:
        userInfo.offDays=userInfo.offDays+1
    elif 'offDay' in request.POST:
      makeOffDay(currentUser, currentDateTime)




  if forceWorkout:
    debugMessage=debugMessage+"Force workout is turned on<br>"
    testOnly()


  phases=list(goal.phase.all())
  todaysExercises=[]


#don't wanna display if it's a previous day number but a later part of the week
  if (userInfo.currentPhase is None):#base case
    if userInfo.goal.startPhase is None:
      randomPhase=random.randint(0,len(phases)-1)#inclusive
      userInfo.currentPhase=randomPhase
      myPhase=phases[userInfo.currentPhase]
    else:
      startPhase=userInfo.goal.startPhase
      userInfo.currentPhase=phases.index(startPhase)
      myPhase=startPhase
    somePhaseLength=PhaseLength.objects.filter(goal=userInfo.goal, phase=myPhase)[0]
    userInfo.phaseLength=random.randint(somePhaseLength.minLength,somePhaseLength.maxLength)
    userInfo.currentDay=userInfo.currentDay-1
    userInfo.save()
    return todaysworkout(request)





  currentWeek= ((userInfo.currentDay-1)/7)+1

  if currentWeek>userInfo.phaseLength:
    userInfo=putToNextPhase(userInfo)




  dayOfWeek=userInfo.currentDay % 7
  if dayOfWeek==0:
    dayOfWeek=7

  if  dayOfWeek==1 and not existingWorkout:
    try:
    #if True: #production
      setupWeek(currentUser, currentDateTime, request)
      #error we get is "matching ThisWeek query does not exist"
      #iphone fix
    except:  #product
    #else:
      TodaysWorkout.objects.filter(user=currentUser).delete()
#      ThisWeek.objects.filter(user=currentUser).delete()
      successMessage="There was an error processing your request.  This is likely due requesting 'Week Layout' and 'Today's Workout' before we finished generating your workouts.  Please try again."
      return render_to_response("successiphone.html", locals())
    userInfo.offDays=7-userInfo.daysPerWeek
    userInfo.save()
###############################UNDER CONSTRUCTION#######################################

  found=False
  lastWorkout=1

  if (not existingWorkout or not existingWorkout[0].visited) and dayOfWeek!=1:#ignore if it's the first day of the week
    foundAnything=False

    ###OPTIMIZE
    checkDayArray=TodaysWorkout.objects.filter(user=currentUser)
    todaysWorkoutDictionary={}
    for todaysWorkoutObject in checkDayArray:
      todaysWorkoutDictionary[todaysWorkoutObject.date.__str__()[0:10]]=todaysWorkoutObject
    #####

    for j in range(1, 8):#check past week for missed visits
      #checkDay=TodaysWorkout.objects.filter(user=currentUser, date=currentDateTime+timedelta(days=-j))
      checkDay=False

      key=(currentDateTime+timedelta(days=-j)).__str__()[0:10]
      if key in todaysWorkoutDictionary:
        checkDay=todaysWorkoutDictionary[key]
      if checkDay and checkDay.visited:
        foundAnything=True
        if not found:
          timeDeltaObject=currentDateTime.date()-checkDay.date
          lastWorkout=timeDeltaObject.days
        found=True
    if not foundAnything:
      userInfo.currentDay=(((userInfo.currentDay-1)/7)+1)*7#Put them into the next week
      currentWeek= ((userInfo.currentDay-1)/7)+1
      if userInfo.currentDay>=userInfo.phaseLength*7: #putting into the following week puts you at day 7
        userInfo=putToNextPhase(userInfo)
        userInfo.currentDay=0
      try:
      #if True:   #product
        setupWeek(currentUser, currentDateTime, request)
      #except:#you get this error from people trying to make multiple requests
      except:
      #else:
        TodaysWorkout.objects.filter(user=currentUser).delete()
        ThisWeek.objects.filter(user=currentUser).delete()
        successMessage="There was an error processing your request.  This is likely due to requesting 'Week Layout' and 'Today's Workout' before we finished generating your workouts.  Please go back to 'My Goals' then try again.  The bottom line is thank you and have a tremendous day."
        return render_to_response("successiphone.html", locals())

      userInfo.offDays=7-userInfo.daysPerWeek
      userInfo.save()

      return todaysworkout(request)
    actualMissed=0
    dayToModify=-1
    if abs(lastWorkout)>1:  #we missed some days
      missedDays=abs(lastWorkout)-1
#      if missedDays>dayOfWeek:
      if missedDays+dayOfWeek>7:
        #need to just call setupweek and stuff
        userInfo.currentDay=(((userInfo.currentDay-1)/7)+1)*7#Put them into the next week
        currentWeek= ((userInfo.currentDay-1)/7)+1
        if userInfo.currentDay>=userInfo.phaseLength*7:  #putting into the following week puts you at day 7
          userInfo=putToNextPhase(userInfo)
          userInfo.currentDay=0
        setupWeek(currentUser, currentDateTime, request)
        userInfo.offDays=7-userInfo.daysPerWeek
        userInfo.save()
        return todaysworkout(request)
      userInfo.currentDay=userInfo.currentDay+missedDays
      dayOfWeek=userInfo.currentDay % 7
      if dayOfWeek==0:
        dayOfWeek=7
      userInfo.offDays=userInfo.offDays-missedDays
      userInfo.save()

      for j in range(1, missedDays+1):
        try:
          toModify=ThisWeek.objects.filter(user=currentUser, dayNumber=dayOfWeek-j)[0]
        except:

          userInfo.currentDay=(((userInfo.currentDay-1)/7)+1)*7#Put them into the next week
          currentWeek= ((userInfo.currentDay-1)/7)+1

          if currentWeek>userInfo.phaseLength:
            userInfo=putToNextPhase(userInfo)
          setupWeek(currentUser, currentDateTime, request)

          userInfo.offDays=7-userInfo.daysPerWeek
          userInfo.save()
          return todaysworkout(request)


        doNothing=False
        if toModify.workoutComponents.count()==0 and toModify.cardio==False:
          doNothing=True
          makeVisited=TodaysWorkout.objects.filter(thisWeek=toModify)[0]
          makeVisited.visited=True
          makeVisited.save()
        if not doNothing:
          actualMissed=actualMissed+1
          found=False
          for j in range(dayOfWeek, 8): #now make some of the rest days on days
            oldOffDay=ThisWeek.objects.filter(user=currentUser, dayNumber=j)[0]#THIS IS THE FIRST INSTANCE OF AN OFF DAY

            if oldOffDay.workoutComponents.count()==0 and not oldOffDay.cardio:
              found=True
              if dayToModify==-1:
                dayToModify=j#first instance of an off day, need to rebuild from here
              temp=oldOffDay.dayNumber
              oldOffDay.dayNumber=toModify.dayNumber
              toModify.dayNumber=temp
              workoutToModify=TodaysWorkout.objects.filter(thisWeek=toModify)[0]
              workoutOldOffDay=TodaysWorkout.objects.filter(thisWeek=oldOffDay)[0]
              temp=workoutToModify.date
              workoutToModify.date=workoutOldOffDay.date
              workoutOldOffDay.date=temp
              workoutOldOffDay.visited=True#THIS ISN'T DOING ANYTHING
              workoutToModify.save()
              workoutOldOffDay.save()
              oldOffDay.save()
              toModify.save()


          if not found:
            for iterator in list(toModify.workoutComponents.all()):
              toModify.workoutComponents.remove(iterator)
            workoutToModify=TodaysWorkout.objects.filter(thisWeek=toModify)[0]
            workoutToModify.offDay=True
            workoutToModify.visited=True
            workoutToModify.save()
            toModify.cardio=False
            toModify.save()

    if actualMissed>0 and dayToModify!=-1:
      #rebuild from dayNumber j
      start=ThisWeek.objects.filter(user=currentUser, dayNumber=dayToModify)[0]
      startDate=(TodaysWorkout.objects.filter(thisWeek=start)[0]).date
      dayList=[]
      for j in range(dayToModify, 8):
        dayList.append(j)
      toModifyList=list(ThisWeek.objects.filter(user=currentUser, dayNumber__in=dayList).order_by('dayNumber'))
      workoutsToDelete=TodaysWorkout.objects.filter(thisWeek__in=toModifyList)
      workoutsToDelete.delete()
      baseExercises=getBaseExercises(currentUser, request)
      exerciseMatrix=getMutexMatrix(request)
      for thisWeekObject in toModifyList:
        generateWorkout(currentUser, startDate+timedelta(days=thisWeekObject.dayNumber-dayToModify), False, "", thisWeekObject.dayNumber, thisWeekObject,baseExercises, request, exerciseMatrix)



#so what I did was...it looks for the next off day, swaps them out if found, otherwise just forces an off day...

#            if oldOffDay.workoutComponents.count()==0 and not oldOffDay.cardio:
#              found=True
#              temp=oldOffDay.dayNumber
#              oldOffDay.dayNumber=toModify.dayNumber
#              toModify.dayNumber=temp
#              workoutToModify=TodaysWorkout.objects.filter(thisWeek=toModify)[0]
#              workoutOldOffDay=TodaysWorkout.objects.filter(thisWeek=oldOffDay)[0]
#              temp=workoutToModify.date
#              workoutToModify.date=workoutOldOffDay.date
#              workoutOldOffDay.date=temp
#              workoutToModify.save()
#              workoutOldOffDay.save()
#              oldOffDay.save()
#              toModify.save()

#          if not found:
#            for iterator in list(toModify.workoutComponents.all()):
#              toModify.workoutComponents.remove(iterator)
#            workoutToModify=TodaysWorkout.objects.filter(thisWeek=toModify)[0]
#            workoutToModify.offDay=True
#            workoutToModify.save()
#            toModify.cardio=False
#            toModify.save()

###############################END UNDER CONSTRUCTION#######################################




####THIS IS THE NORMAL CASE FOR HITTING TODAY'S WORKOUT!!!

  weekDictionary={}
  tempDayOfWeek=dayOfWeek
  tempWeekDay=weekday

#  successMessage="hello Scott"
#  return render_to_response("success.html",locals())
####################################################################################
#2 different for loops...one for before the current day and another for after
  try:  #product
  #if True:
    thisWeekDict={}  #thisWeek dictionary, key is dayNumber
    allWeekObjects=ThisWeek.objects.select_related().filter(user=currentUser)

    associatedWorkouts=list(TodaysWorkout.objects.filter(thisWeek__in=allWeekObjects).select_related('thisWeek'))
    for iterator in allWeekObjects:
      key=iterator.dayNumber.__str__()
      thisWeekDict[key]=iterator



    workoutDict={}   #dictionary of todaysworkouts, key is thisweek id
    workoutIdString=""  #used for the query
    seriesDict={}    #dictionary of lists of exercises, key is todaysworkout id
    for iterator in associatedWorkouts:
      key=iterator.thisWeek.id.__str__()
      workoutDict[key]=iterator
      workoutIdString=workoutIdString+"'"+iterator.id.__str__()+"', "
      seriesDict[iterator.id.__str__()]=[]

    workoutIdString=workoutIdString[0:len(workoutIdString)-2]
    query = "select t2.id, t1.todaysworkout_id, t4.id as component, t3.name as exercisename, t4.name as componentname from oraclefitness_todaysworkout_exercises as t1 join oraclefitness_series as t2 on t1.series_id=t2.id join oraclefitness_exercise as t3 on t2.exercise_id = t3.id join oraclefitness_workoutcomponent as t4 on t3.workoutcomponent_id = t4.id where todaysworkout_id IN (%s)" %workoutIdString


    seriesAndWorkouts=list(Series.objects.raw(query)) #list of todaysworkout id's and series id's

###########  I run this query so that I can reference Series objects instead of id's
    seriesList=[]
    for iterator in seriesAndWorkouts:
      seriesList.append(iterator.id)
    seriesList=list(Series.objects.filter(id__in=seriesList).select_related('exercise'))
    seriesDict2={}
    for iterator in seriesList:
      key=iterator.id.__str__()
      seriesDict2[key]=iterator
############3
    seriesComponentDict={} #Dictionary of workout components based on series id...key is series id
    seriesComponentDictName={} #dictionary of workoutComponent names, key is exercise name
    for iterator in seriesAndWorkouts:
      key=iterator.todaysworkout_id.__str__()
      seriesDict[key].append(seriesDict2[iterator.id.__str__()])#id of a series object
      workoutComponentId=iterator.component # gotta do something with this
      seriesComponentDict[iterator.id.__str__()]=workoutComponentId
      seriesComponentDictName[iterator.exercisename]=iterator.componentname
#REMEMBER THIS QUERY, IT IS SUPER SPECIAL!!


    thisWeekString=""
    for key, value in thisWeekDict.iteritems():
      thisWeekString=thisWeekString+"'"+value.id.__str__()+"', "
    thisWeekString=thisWeekString[0:len(thisWeekString)-2]
    query="select id, thisweek_id, COUNT(workoutcomponent_id) as mycount from oraclefitness_thisweek_workoutComponents WHERE thisweek_id IN (%s) GROUP BY thisweek_id" % thisWeekString
    thisWeekCounts=list(ThisWeek.objects.raw(query))
    countDictionary={}
    for iterator in thisWeekCounts:
      key=iterator.thisweek_id.__str__()
      countDictionary[key]=iterator.mycount
#now make a dictionary of counts where the is the key
    flexComponent=WorkoutComponent.objects.filter(name='Flexibility')[0]
    for j in range(dayOfWeek, 8):
      key=j.__str__()
      tempWeek=thisWeekDict[key]  #THIS COULD RAISE AN EXCEPTION, but I left it in there this time to regenerate workouts..will work as long as existing try/catch is there
#      theExercises=TodaysWorkout.objects.filter(thisWeek=tempWeek)[0].exercises.all()
      todaysWorkoutObject=workoutDict[tempWeek.id.__str__()]
      theExercises=seriesDict[todaysWorkoutObject.id.__str__()]
#      theExercises=workoutDict[tempWeek.id.__str__()].exercises.all()
#      theExercises=list(theExercises)
      toRemove=[]
      for seriesObject in theExercises:
        if seriesComponentDict[seriesObject.id.__str__()]==flexComponent.id:
        #if seriesObject.exercise.workoutComponent==flexComponent:
          toRemove.append(seriesObject)
      for seriesObject in toRemove:
        theExercises.remove(seriesObject)



      weekDictionary[tempWeekDay.__str__()]=theExercises

      #FOR TESTING ONLY, REMOVE ME
      for j in range(0,len(weekDictionary[tempWeekDay.__str__()])):
        weekDictionary[tempWeekDay.__str__()][j].exercise.name=weekDictionary[tempWeekDay.__str__()][j].exercise.name+" ("+seriesComponentDictName[weekDictionary[tempWeekDay.__str__()][j].exercise.name]+")"

#5566, 71
      weekDictionary["cardio"+tempWeekDay.__str__()]=tempWeek.cardio
      myString="No"
      if tempWeek.level==1:
        myString="Light"
      if tempWeek.level==2:
        myString="Medium"
      if tempWeek.level==3:
        myString="Heavy"
      weekDictionary["cardioLevel"+tempWeekDay.__str__()]=myString

#      for wObject in tempWeek.workoutComponents.all():
#        weekDictionary[tempWeekDay.__str__()].append({'exercise':{'name':wObject.name}})

      if (not tempWeek.id.__str__() in countDictionary and not tempWeek.cardio) or workoutDict[tempWeek.id.__str__()].offDay:
      #if (tempWeek.workoutComponents.count()==0 and not tempWeek.cardio) or workoutDict[tempWeek.id.__str__()].offDay:
        weekDictionary[tempWeekDay.__str__()]=[]
        weekDictionary[tempWeekDay.__str__()].append({'exercise':{'name':'Rest Day'}})

      tempWeekDay=tempWeekDay+1      #0-6


    tempDayOfWeek=dayOfWeek
    tempWeekDay=weekday
    for j in range(0, weekday):
      tempDayOfWeek=tempDayOfWeek-1
      tempWeekDay=tempWeekDay-1
      if tempDayOfWeek>0:
#        tempWeek=ThisWeek.objects.filter(user=currentUser, dayNumber=tempDayOfWeek)[0]
        tempWeek=thisWeekDict[tempDayOfWeek.__str__()]#key is the day number
        #ERROR: sometimes thisweek will be present but todaysworkout wont
    #    for wObject in tempWeek.workoutComponents.all():
    #      weekDictionary[tempWeekDay.__str__()].append({'exercise':{'name':wObject.name}})

        todaysWorkoutObject=workoutDict[tempWeek.id.__str__()]
        theExercises=seriesDict[todaysWorkoutObject.id.__str__()]

#        theExercises=TodaysWorkout.objects.filter(thisWeek=tempWeek)[0].exercises.all()
#        theExercises=list(theExercises)
#        flexComponent=WorkoutComponent.objects.filter(name='Flexibility')[0]
        toRemove=[]
        for seriesObject in theExercises:
          if seriesComponentDict[seriesObject.id.__str__()]==flexComponent.id:
#          if seriesObject.exercise.workoutComponent==flexComponent:
            toRemove.append(seriesObject)
        for seriesObject in toRemove:
          theExercises.remove(seriesObject)




        weekDictionary[tempWeekDay.__str__()]=theExercises
        #FOR TESTING ONLY, REMOVE ME
        for j in range(0,len(weekDictionary[tempWeekDay.__str__()])):
          weekDictionary[tempWeekDay.__str__()][j].exercise.name=weekDictionary[tempWeekDay.__str__()][j].exercise.name+" ("+seriesComponentDictName[weekDictionary[tempWeekDay.__str__()][j].exercise.name]+")"

        weekDictionary["cardio"+tempWeekDay.__str__()]=tempWeek.cardio
        myString="No"
        if tempWeek.level==1:
          myString="Light"
        if tempWeek.level==2:
          myString="Medium"
        if tempWeek.level==3:
          myString="Heavy"
        weekDictionary["cardioLevel"+tempWeekDay.__str__()]=myString
        if (len(tempWeek.workoutComponents.all())==0 and not tempWeek.cardio) or TodaysWorkout.objects.filter(thisWeek=tempWeek)[0].offDay:
          weekDictionary[tempWeekDay.__str__()]=[]
          weekDictionary[tempWeekDay.__str__()].append({'exercise':{'name':'Rest Day'}})
    #weekday variable is the yellow day
    for j in range(0, 7):#fill out any blank days with something else
      message=""
      if j<weekday:
        message="Previous Workout Unavailable"
      else:
        message="Not yet generated"
      if not j.__str__() in weekDictionary:
        weekDictionary[j.__str__()]=[]
        weekDictionary[j.__str__()].append({'exercise':{'name':message}})
  except:   #production
  #else:
    TodaysWorkout.objects.filter(user=currentUser).delete()
    successMessage="Woops!  There was an error processing your request.  Please go back to 'My Goals' and try again.  Sorry for the inconvenience."
    return render_to_response('successiphone.html', locals())

## THIS IS THE END OF THE DEFAULT CASE STUFF, WORKOUT GENERATION AND ALL THAT.  After this we're getting into the layout of the rest of the page and all that
##############################################################################################
  if 'needWeekDict' in request.POST:
    return weekDictionary
  userInfo.save()

  todaysWorkout, debugMessage=generateWorkout(currentUser, currentDateTime, debug, debugMessage, dayOfWeek, ThisWeek.objects.filter(dayNumber=dayOfWeek)[0], None,request, None)

  #todaysExercises=list(todaysWorkout.exercises.all().select_related('exercise'))#select_related('workoutComponent'))
#  todaysExercises=list(todaysWorkout.exercises.select_related().all())#select_related('workoutComponent'))
#  todaysExercises=list(Exercise.objects.select_related().filter(id__in=todaysWorkout.exercises.all()))
  todaysExercises=todaysWorkout.exercises.select_related('exercise__workoutComponent').all()
  #associatedExercises=list(Exercise.objects.filter(series__set__in=todaysExercises))
  #associatedExercises=todaysExercises[0].series_set.all()
#  WorkoutSeries.objects.select_related().filter(todaysWorkout__in=to
  previousComponent='this string could be anything...'
  for iterator in todaysExercises:
#    if iterator.exercise.workoutComponent.name!=previousComponent:
    if iterator.exercise.workoutComponent.name!=previousComponent:
      iterator.change=1
#      previousComponent=iterator.exercise.workoutComponent.name
      previousComponent=iterator.exercise.workoutComponent.name
    else:
      iterator.change=0
  for iterator in todaysExercises:
    if iterator.superSet:
      iterator.superSet=Series.objects.get(id=iterator.superSet)
  if not todaysWorkout.visited:
    todaysWorkout.visited=True
    todaysWorkout.save()
  try:
    myPhase=phases[userInfo.currentPhase]
  except:
    userInfo.currentPhase=0
    userInfo.save()
    myPhase=phases[0]
  firstTimeDescription=""
  firstTime=False
  if not myPhase in userInfo.visitedPhases.all() and userInfo.currentDay==1:
    #set up a first time description
    firstTime=True
    if myPhase.name=='stabilization':
      firstTimeDescription=Description.objects.get(id=21).text
    elif myPhase.name=='muscle endurance':
      firstTimeDescription=Description.objects.get(id=22).text
    elif myPhase.name=='power':
      firstTimeDescription=Description.objects.get(id=25).text
    elif myPhase.name=='maximal strength':
      firstTimeDescription=Description.objects.get(id=24).text
    elif myPhase.name=='hypertrophy':
      firstTimeDescription=Description.objects.get(id=23).text


#todaysExercises
  actualRest=0
  try:
    actualTempo=list(todaysExercises)[0].tempo
    actualRest=float(list(todaysExercises)[0].rest)/60.0
    if float(actualRest)==float(int(actualRest)):
      actualRest=int(actualRest)
      if actualRest==1:
        actualRest=actualRest.__str__()+" minute"
      else:
        actualRest=actualRest.__str__()+" minutes"
    else:
      if float(actualRest)<1.0:
        actualRest=int(actualRest*60.0).__str__()+ " seconds"
      else:
        minutes=int(actualRest)
        seconds=int((actualRest-float(int(actualRest)))*60.0)
        actualRest=minutes.__str__()+" minutes and "+seconds.__str__()+" seconds"
  except:
    pass
  for iterator in todaysExercises:
    if iterator.exercise.workoutComponent.name=='Resistance':
      iterator.actualRest=actualRest
    elif iterator.exercise.workoutComponent.name=='Flexibility':
      iterator.actualRest=None
    else:
      iterator.actualRest='45 seconds'
  try:
    requestedurl= request.META['HTTP_REFERER']
  except:
    requestedurl="some junk"
  userAgent=request.META['HTTP_USER_AGENT']

  t2=datetime.datetime.now()
  delta=t2-t1
#  from django.core.mail import send_mail
  messageString=""

#  send_mail("OracleFitness Stat Data", messageString.__str__(), 'administrator@oraclefitness.com', ['scott.lobdell@gmail.com'], fail_silently=False)

  if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
    if 'eeklayoutiphone' in requestedurl:
      return render_to_response('weeklayoutiphone.html', locals())
    return render_to_response('todaysworkoutiphone.html', locals())
  return render_to_response('todaysworkout.html', locals())

def todaysworkoutiPhone(request, deviceid):#this is to display today's workout
  userAgent=request.META['HTTP_USER_AGENT']
  if not ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
    return myGoals(request)

  #current_url = request.build_absolute_uri().__str__()
  #successMessage=deviceid.__str__()
  #if 'lite' in current_url:
  #  return render_to_response('success.html', locals())

  login, exists = iPhone(request, deviceid)
  if login:
    return signIn(request)

  if not exists:
    successMessage="You haven't set any goals yet.  Please edit \"My Goals\""
    return render_to_response('successiphone.html', locals())

  return todaysworkout(request)

def todaysworkoutiPhone2(request, deviceid):#this is to display this week's layout
  userAgent=request.META['HTTP_USER_AGENT']
  if not ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
    return myGoals(request)

  login, exists = iPhone(request, deviceid)
  if login:
    return signIn(request)
  if not exists:
    successMessage="You haven't set any goals yet.  Please edit \"My Goals\""
    return render_to_response('successiphone.html', locals())
  return todaysworkout(request)


def resources(request):
  login, superuser = credentials(request)
  return render_to_response('resources.html', locals())

def speed(request):
  login, superuser = credentials(request)

  allPosts=Post.objects.all()

  return render_to_response('forum.html', locals())

def thread(request):
  login, superuser = credentials(request)

  allPosts=Post.objects.all()

  return render_to_response('forum.html', locals())



def getMutexMatrix(request):
  t1=datetime.datetime.now()
#  allOutersOriginal=list(Exercise.objects.exclude(mutuallyExclusive=None).values_list('mutuallyExclusive',flat=True))
  allOutersOriginal=list(Exercise.objects.exclude(mutuallyExclusive=None))
  allOuters=[]
  exerciseListDictionary={}


  for iterator in allOutersOriginal:
    allOuters.append(iterator.mutuallyExclusive)
    key = iterator.mutuallyExclusive.__str__()
    if key in exerciseListDictionary:
      exerciseListDictionary[key].append(iterator)
    else:
      exerciseListDictionary[key]=[]
      exerciseListDictionary[key].append(iterator)

  #seriesIds= Series.objects.all().values_list('id', flat=True)
  #find the mutually exclusive outer limits,

  allRoots=[]#array of Exercise objects
  allRoots=list(Exercise.objects.filter(id__in=allOuters))
#  for j in range(0, len(allOuters)):
#    try:
#      nextItem=Exercise.objects.get(id=allOuters[j].mutuallyExclusive)
#      if not nextItem in allOuters:  #don't care about these ones
#        allRoots.append(nextItem)
#    except:
#      pass



  exerciseMatrix=[]
  graph=[]


  while allRoots:
    graph.append(allRoots[0])
    #children=list(Exercise.objects.filter(mutuallyExclusive=int(allRoots[0].id)))
    key=allRoots[0].id.__str__()
    children=exerciseListDictionary[key]

    while children:
      graph.extend(children)
      newChildren=[]
      for iterator in children:
        key=iterator.id.__str__()
        if key in exerciseListDictionary:
          newChildren.extend(exerciseListDictionary[key])
#        newChildren.extend(list(Exercise.objects.filter(mutuallyExclusive=int(iterator.id))))
      children=newChildren
    allRoots.remove(allRoots[0])
    exerciseMatrix.append(graph)
    graph=[]


  t2=datetime.datetime.now()
  delta=t2-t1
  return exerciseMatrix


def viewExercises(request):
  login, superuser = credentials(request)
  allExercises=Exercise.objects.all().order_by('name')
  totalCount=allExercises.count()
  for iterator in allExercises:
    if iterator.url=="" or iterator.url=="none":
      iterator.video=False
    else:
      iterator.video=True
  return render_to_response('viewexercises.html', locals())

def viewMutex(request):
  login, superuser = credentials(request)
  if not superuser:
    successMessage="You do not have sufficient rights to access this page."
    return render_to_response('success.html', locals())



  exerciseMatrix=getMutexMatrix(request)
  return render_to_response('viewmutex.html', locals())




def youtubeLauncher(request, exercise=None):
  myExercise=Exercise.objects.get(id=exercise)
  video=True
  if myExercise.url=="" or myExercise.url=="none":
    video=False
  if not exercise is None:
    url=myExercise.url
  userAgent=request.META['HTTP_USER_AGENT']
  referer= request.META['HTTP_REFERER']
  if ('iPhone' in userAgent or 'iPod' in userAgent or 'iTouch' in userAgent):
    return render_to_response('youtubelauncheriphone.html', locals())

  return render_to_response('youtubelauncher.html', locals())





def threads(request):
  login, superuser = credentials(request)
  allThreads=Thread.objects.all()
  return render_to_response('threads.html', locals())

def videoLibrary(request):
  login, superuser = credentials(request)
  videos=[]

  videos.append(youtube("http://www.youtube.com/watch?v=rghpvUUy7bA"))
  videos.append(youtube("http://www.youtube.com/watch?v=otV-0r3-Qd8"))
  videos.append(youtube("http://www.youtube.com/watch?v=flYDTlVxH-s"))
  videos.append(youtube("http://www.youtube.com/watch?v=WobDtKrQaPo"))
  videos.append(youtube("http://www.youtube.com/watch?v=rLewqVuOSRM"))
  videos.append(youtube("http://www.youtube.com/watch?v=7qoimP3fmhE"))
  videos.append(youtube("http://www.youtube.com/watch?v=AKpkFcAGCX8"))
  videos.append(youtube("http://www.youtube.com/watch?v=I3e8DhfRx_M"))
  videos.append(youtube("http://www.youtube.com/watch?v=d8oXDcnJ11w"))
  videos.append(youtube("http://www.youtube.com/watch?v=RnU8o-fqo1w"))
  videos.append(youtube("http://www.youtube.com/watch?v=8ZMEGWF6_8I"))
  videos.append(youtube("http://www.youtube.com/watch?v=_CZc_ZI_kdY"))
  videos.append(youtube("http://www.youtube.com/watch?v=XK57Nr9xtEY"))
  videos.append(youtube("http://www.youtube.com/watch?v=WHmLAhYPbhQ"))
  videos.append(youtube("http://www.youtube.com/watch?v=SCz0mZzX_-k"))
  videos.append(youtube("http://www.youtube.com/watch?v=O9ARHXiYLiE"))
  videos.append(youtube("http://www.youtube.com/watch?v=vWebEIt0JZU"))
  videos.append(youtube("http://www.youtube.com/watch?v=nljYWmj5irw"))
  videos.append(youtube("http://www.youtube.com/watch?v=zfhNlEg0toc"))
  videos.append(youtube("http://www.youtube.com/watch?v=JASjfQubPWU"))
  return render_to_response('videolibrary.html', locals())

#import facebook.djangofb as facebook

def xd_receiver(request):
#  name=request.facebook.users.getInfo([request.facebook.uid], ['first_name'])[0]['first_name']
  return render_to_response('xd_receiver.html', locals())


def sblDebug(inText):  # yank 7 lines
    inText = inText.__str__()
    import datetime
    currentTime = datetime.datetime.now()
    f = open('/home/aesg/debug.txt', 'a')
    f.write("%s: %s\n" % (currentTime, inText))
    f.close()
