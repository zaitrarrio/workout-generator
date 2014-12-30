
def setupWeek(user, currentDateTime, request):
  t1=datetime.datetime.now()
  weeksToDelete=ThisWeek.objects.filter(user=user)
  allTodays=TodaysWorkout.objects.all().iterator()
  seriesIds=[]
#  for iterator in allTodays:
#    seriesIds.extend(list(iterator.exercises.all()))#ok, so keep all these
#  seriesIds = Series.objects.filter(todaysworkout__set__isnull=False).values_list('id', flat=True)
#  seriesInAllWorkouts=Series.objects.filter(id__in=TodaysWorkout.objects.all().values_list('id',flat=True))


####################
#  seriesIds= Series.objects.all().values_list('id', flat=True)
#  seriesToKeep=Series.objects.filter(id__in=seriesIds)
#  firstSupersets=seriesToKeep.exclude(superSet=None)
#  seriesToKeep=list(seriesToKeep)
#
#  for j in range(0, len(seriesToKeep)):
#    seriesToKeep[j]=seriesToKeep[j].id
#
#
#  for iterator in firstSupersets:
#    seriesToKeep.append(iterator.superSet)
#
#  Series.objects.all().exclude(id__in=seriesToKeep).delete()
##############################


  oldWorkouts=TodaysWorkout.objects.filter(user=user)
  for iterator in oldWorkouts:
    iterator.thisWeek=None
    iterator.save()

  weeksToDelete.delete()
  userInformation=UserInformation.objects.filter(user=user).select_related('currentFitnessLevel')[0]
  daysAvailable=userInformation.daysPerWeek
  currentWeek= ((userInformation.currentDay-1)/7)+1
  if userInformation.currentDay==0:
    currentWeek=1

  maxWeekInPhase=6
  currentWeekToUse=currentWeek
  try:
    myPhase=list(userInformation.goal.phase.all())[userInformation.currentPhase]
  except:#I RAN INTO THIS WHEN YOU CHANGE THE DATE AS THE WORKOUT IS LOADING...
    userInformation.currentPhase=0
    userInformation.save()
    myPhase=list(userInformation.goal.phase.all())[0]
  if myPhase in userInformation.visitedPhases.all():
    currentWeekToUse=maxWeekInPhase




  import random
  thisWeekDict={}
  userThisWeek=ThisWeek.objects.filter(user=user)
  for iterator in userThisWeek:
    key=iterator.dayNumber.__str__()
    thisWeekDict[key]=iterator

  componentDict={}
  allComponentFrequencies=Frequency.objects.filter(currentFitnessLevel=userInformation.currentFitnessLevel,
          week=currentWeekToUse).select_related('workoutComponent')
  for iterator in allComponentFrequencies:
    key=iterator.workoutComponent.name.__str__()
    componentDict[key]=iterator

  allWorkoutComponents=WorkoutComponent.objects.all()
  for componentObject in allWorkoutComponents:
    try:
#      componentFrequency=Frequency.objects.filter(currentFitnessLevel=userInformation.currentFitnessLevel,
#                                                  workoutComponent=componentObject,
#                                                  week=currentWeekToUse,
#      )[0]
      componentFrequency=componentDict[componentObject.name]
    except:

      writeTestData("Component Frequency hasn't been set up for this fitness level "+userInformation.currentFitnessLevel.name +" "+componentObject.name+" "+currentWeekToUse.__str__())
    timesPerWeek=random.randint(componentFrequency.minimum, componentFrequency.maximum)#times per week for this component
    if timesPerWeek>=daysAvailable:
      for j in range(1, daysAvailable+1):
        #thisWeek=ThisWeek.objects.filter(dayNumber=j, user=user)
        key=j.__str__()
        if key in thisWeekDict:
          thisWeek=thisWeekDict[key]
        else:
          thisWeek=ThisWeek(dayNumber=j, user=user, cardio=False)
          thisWeekDict[j.__str__()]=thisWeek
          thisWeek.save()

        thisWeek.workoutComponents.add(componentObject)
    else:
      decrementor=timesPerWeek
      dayCounter=random.randint(1, daysAvailable)
      alreadyExists=False
      while decrementor>0:
        alreadyExists=False
        if random.random()< float(timesPerWeek)/float(daysAvailable):
          #thisWeek=ThisWeek.objects.filter(dayNumber=dayCounter, user=user)
          key=dayCounter.__str__()
          if key in thisWeekDict:
            thisWeek=thisWeekDict[key]
          else:
            thisWeek=ThisWeek(dayNumber=dayCounter, user=user, cardio=False)
            thisWeek.save()
            thisWeekDict[dayCounter.__str__()]=thisWeek

            if componentObject in thisWeek.workoutComponents.all(): #NEED TO OPTIMIZE THIS
              alreadyExists=True
          #need to ensure that this day doesn't already have the current component object
          if not alreadyExists:
            decrementor=decrementor-1
            thisWeek.workoutComponents.add(componentObject)#NEED TO OPTIMIZE THESE 2 LINES
            #thisWeek.save()

        dayCounter=dayCounter+1
        if dayCounter>daysAvailable:
          dayCounter=1
    cardioAlreadyAdded=0
    for j in range(1, daysAvailable+1):#ensures that a day is created no matter what
#      exists=ThisWeek.objects.filter(dayNumber=j, user=user)
      key=j.__str__()
      if not key in thisWeekDict:
#      if not exists:
        cardioAlreadyAdded=cardioAlreadyAdded+1
        #put cardio on a day automatically if there isn't anything
        thisWeek=ThisWeek(dayNumber=j, user=user, cardio=True, timed=True, level=1)
        thisWeek[j.__str__()]=thisWeek
        thisWeek.save()
  ###########now add cardio
  cardioDays=0




  maxWeekInPhase=6
  currentWeekToUse=currentWeek
  myPhase=list(userInformation.goal.phase.all())[userInformation.currentPhase]
  if myPhase in userInformation.visitedPhases.all():
    currentWeekToUse=maxWeekInPhase
  volumeTable=VolumeTable.objects.filter(fitnessLevel=userInformation.currentFitnessLevel, phase=myPhase, week=currentWeekToUse)[0]


  timedCardioDays=random.randint(volumeTable.minTimedCardio, volumeTable.maxTimedCardio)
  distanceCardioDays=random.randint(volumeTable.minDistanceCardio, volumeTable.maxDistanceCardio)



  timedCardioDays=timedCardioDays-cardioAlreadyAdded
  if timedCardioDays<0:
    timedCardioDays=0

  if timedCardioDays<userInformation.goal.cardioType.minimum:
    timedCardioDays=userInformation.goal.cardioType.minimum
  #now sort the days by those with the least workoutComponents
  sortedDays=[]
  myDays=list(ThisWeek.objects.filter(user=user))
  myDaysCount=[]
  for iterator in myDays:
    myDaysCount.append(iterator.workoutComponents.count())#myDays.index(iterator)

    # SBL WTF was I doing here
    # I believe this is just s
  for j in range(0,len(myDays)):
    smallest=myDaysCount[0]
    toRemove=myDays[0]
    for iterator in myDays:
      if myDaysCount[myDays.index(iterator)]<smallest:
        smallest=myDaysCount[myDays.index(iterator)]
        toRemove=iterator
    index=myDays.index(toRemove)
    del myDaysCount[index]
    myDays.remove(toRemove)
    sortedDays.append(toRemove)


  index=0
  for j in range(0, timedCardioDays):
    try:
      sortedDays[j].cardio=True
      sortedDays[j].timed=True
      sortedDays[j].level=random.randint(1,3)
      sortedDays[j].save()
    except:
      pass

    # SBL holy fuck.  Left off here
  allCardioDays=ThisWeek.objects.filter(user=user, cardio=True)
  myLevel=random.randint(1,3)
  for iterator in allCardioDays:
    iterator.level=myLevel
    iterator.save()
    if myLevel==1:
      myLevel=random.randint(2,3)
    elif myLevel==3:
      myLevel=random.randint(1,2)
    else:  #must equal 1 or 3
      myLevel=1
      if random.randint(0,1):
        myLevel=3

  cardioMax=CardioMax.objects.filter(fitnessLevel=userInformation.currentFitnessLevel, cardioType=userInformation.goal.cardioType)[0]
  allHighs=ThisWeek.objects.filter(user=user, level=3)
  totalHighs=allHighs.count()
  if totalHighs>cardioMax.hiMaximum:
    allHighs=list(allHighs)
    for j in range(0, totalHighs-cardioMax.hiMaximum):
      toChange=allHighs[random.randint(0, len(allHighs)-1)]
      toChange.level=2
      toChange.save()
      allHighs=list(ThisWeek.objects.filter(user=user, level=3))

  totalHighs=len(list(allHighs))
  additionalMeds=0
  if totalHighs<cardioMax.hiMaximum:
    additionalMeds=cardioMax.hiMaximum-totalHighs

  allMeds=ThisWeek.objects.filter(user=user, level=2)
  totalMeds=allMeds.count()
  if totalMeds>(cardioMax.medMaximum+additionalMeds):
    allMeds=list(allMeds)
    for j in range(0, totalMeds-(cardioMax.medMaximum+additionalMeds)):
      toChange=allMeds[random.randint(0, len(allMeds)-1)]
      toChange.level=1
      toChange.save()
      allMeds=list(ThisWeek.objects.filter(user=user, level=2))

  totalMeds=len(list(allMeds))
  additionalLos=0
  if totalMeds<cardioMax.loMaximum:
    additionalLos=cardioMax.medMaximum-totalMeds

  allLos=ThisWeek.objects.filter(user=user, level=1)
  totalLos=allLos.count()
  if totalLos>(cardioMax.loMaximum+additionalLos):
    allLos=list(allLos)
    for j in range(0, totalLos-(cardioMax.loMaximum+additionalLos)):
      toChange=allLos[random.randint(0, len(allLos)-1)]
      toChange.cardio=False
      toChange.timed=None
      toChange.level=None
      toChange.save()
      allLos=list(ThisWeek.objects.filter(user=user, level=1))
      #thisWeekObject


  currentOffDays=[]
  thisWeekDictionary={}
  thisWeekObjects=ThisWeek.objects.filter(user=user)
  for iterator in thisWeekObjects:
    key=iterator.dayNumber.__str__()
    thisWeekDictionary[key]=iterator
  # thisWeekDictionary = {this_week.day_number: this_week for this_week in thisWeekObjects}
  #now fit off days into the week
  for j in range(daysAvailable+1, 8):
#    thisWeek=ThisWeek.objects.filter(dayNumber=j, user=user)
    key=j.__str__()
    if key in thisWeekDictionary:
      thisWeek=thisWeekDictionary[key]
#    if not thisWeek:
    else:
      thisWeek=ThisWeek(dayNumber=j, user=user, cardio=False)
      thisWeek.save()
      thisWeekDictionary[key]=thisWeek
      currentOffDays.append(thisWeek)
#    else:
#      thisWeek=thisWeek[0]

#change currentOffDays to an array of integers, then filter by those days
  currentOffDaysDayNumber=[]
  for iterator in currentOffDays:
    currentOffDaysDayNumber.append(iterator.dayNumber)

  #now swap the off days with other days of the week so it fits into the user's default off days


  offDays=[]  #array of weekdays...corresponds to weekday(), so 0-6 rather than day number of 1-7
  for j in range(0, len(userInformation.defaultOffDays)):
    offDays.append(int(userInformation.defaultOffDays[j]))

  dayArray=[]
  for j in range(0,7):#this loop is needed because you're actually start the week on Wednesday or something
    dayArray.append((currentDateTime+timedelta(days=j)).weekday())
    #0 will be the first day of the week and so forth, dayNumber=index+1

  counter=0
#offDays is 0, 6
  numDaysOff=7-userInformation.daysPerWeek  #this is to combat a bug from mygoals not saving properly.  offdaystring will not update but num off days will
  for offDayInteger in offDays:
    if counter>=numDaysOff:#use greater than or equal to because of array indices
      break
    #offDayInteger is a weekday()
    willBeOffDay=ThisWeek.objects.filter(dayNumber=dayArray.index(offDayInteger)+1, user=user)[0]
    willBeOnDay=ThisWeek.objects.filter(dayNumber=currentOffDaysDayNumber[counter], user=user)[0]

    temp=willBeOffDay.dayNumber
    willBeOffDay.dayNumber=willBeOnDay.dayNumber
    willBeOnDay.dayNumber=temp


    willBeOffDay.save()
    willBeOnDay.save()
    counter=counter+1
  if userInformation.currentDay==0:
    userInformation.currentDay=1
    userInformation.save()

#####################################################
#now move around resistance exercises to equally weight cardio with weightlifting
#####################################################

  myPhase=userInformation.goal.phase.all()[userInformation.currentPhase]
  myCardioZone=CardioZone.objects.filter(fitnessLevel=userInformation.currentFitnessLevel,
                                         cardioType=userInformation.goal.cardioType)

  existingHardCode=HardCodedRule.objects.filter(cardioType=userInformation.goal.cardioType, phase=myPhase)
  if existingHardCode:
    existingHardCode=existingHardCode[0]
    groupedCardioZone=existingHardCode.cardioZone
    toMatch=-1
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
    newCardioZone=CardioZone.objects.filter(id__in=possibleIds)
    #while this may be faulty, we take the max possible, so 0 for total time doesn't cause any errors here
    associatedFitnessLevels=newCardioZone[0].fitnessLevel.all()
    highestVal=-1
    for iterator in associatedFitnessLevels:
      if iterator.value>highestVal:
        highestVal=iterator.value
    if userInformation.currentFitnessLevel.value>=highestVal:
      myCardioZone=newCardioZone
  #END COPY AND PASTED CODE

  thisWeek=list(ThisWeek.objects.filter(user=user))
  thisWeek = [item for item in thisWeek if item.workoutComponents.count() > 0]
  #thisWeek is now an array of workable this week objects.  What day number it is we really don't care about
  cardioDays = [item for item in thisWeek if item.cardio]
  nonCardioDays = [item for item in thisWeek if not item.cardio]

  #If there is no resistance and no cardio, but there still exists other components, need to swap out one of the components
  resistanceComponent=WorkoutComponent.objects.filter(name='Resistance')[0]
  for iterator in nonCardioDays:
    if not iterator.cardio and not (resistanceComponent in iterator.workoutComponents.all()) and iterator.workoutComponents.count()>0:
        #we have some standalone things...swap it out with a resistance on a cardio day
      deleted=False
      for componentObject in iterator.workoutComponents.all():#remove this component and swap it into a cardio day that has resistance
        if not deleted:
          for thisWeekObject in cardioDays:
            if resistanceComponent in thisWeekObject.workoutComponents.all() and not (componentObject in thisWeekObject.workoutComponents.all()) and not deleted:
              iterator.workoutComponents.add(resistanceComponent)#TODO: this is where the swap occurs
              iterator.workoutComponents.remove(componentObject)
              thisWeekObject.workoutComponents.add(componentObject)
              thisWeekObject.save()
              iterator.save()
              deleted=True
          if not deleted:
            iterator.workoutComponents.remove(componentObject)
            iterator.save()
      if not deleted:
        iterator.workoutComponents.add(resistanceComponent)
        iterator.save()

  flexComponent=WorkoutComponent.objects.filter(name='Flexibility')[0]
  for iterator in thisWeek:
    if iterator.workoutComponents.count()==1 and iterator.workoutComponents.all()[0]==flexComponent:
      iterator.workoutComponents.remove(flexComponent)
      iterator.save()


  #############  START SWAPPING CARDIO DAYS
  for i in range(0,2):
    thisWeek=0
    if i==0:
      thisWeek=list(ThisWeek.objects.filter(user=user).order_by('dayNumber'))
    else:
      thisWeek=list(ThisWeek.objects.filter(user=user).order_by('-dayNumber'))

    orderedDays=[]
    for iterator in thisWeek:
      if iterator.workoutComponents.count()==0 and not iterator.cardio:
        orderedDays.append(-1)
      elif iterator.cardio:
        orderedDays.append(1)
      else:
        orderedDays.append(0)

    # orderedDays is a list of -1, 0, and 1 representing off day, pure
    # resistance, and cardio


    for j in range(0, 7):
      if orderedDays[j]==1:
        nextIndex=j+1
        if nextIndex<7 and orderedDays[nextIndex]==1:#we have adjacent cardio days
          secondList=orderedDays[nextIndex:7]
          try:
            nonCardioIndex=secondList.index(0)+nextIndex
            #now swap nextIndex and nonCardioIndex
            orderedDays[nextIndex]=0
            orderedDays[nonCardioIndex]=1
            if i==0:
              toSwap1=ThisWeek.objects.filter(user=user, dayNumber=nextIndex+1)[0]
              toSwap2=ThisWeek.objects.filter(user=user, dayNumber=nonCardioIndex+1)[0]
            else:
              toSwap1=ThisWeek.objects.filter(user=user, dayNumber=6-nextIndex+1)[0]
              toSwap2=ThisWeek.objects.filter(user=user, dayNumber=6-nonCardioIndex+1)[0]

            temp=toSwap1.dayNumber
            toSwap1.dayNumber=toSwap2.dayNumber
            toSwap2.dayNumber=temp
            toSwap1.save()
            toSwap2.save()
          except:
            pass
  #############  END SWAPPING CARDIO DAYS


  thisWeek=list(ThisWeek.objects.filter(user=user).order_by('dayNumber'))
  baseExercises=getBaseExercises(user, request)
  exerciseMatrix=getMutexMatrix(request)
  for iterator in thisWeek:
    generateWorkout(user, currentDateTime+timedelta(days=iterator.dayNumber-1), False, "", iterator.dayNumber, iterator, baseExercises, request, exerciseMatrix)
  deletePreviousWorkouts(userInformation, currentDateTime+timedelta(days=7))#this deletes anything beyond past 7 days

  t2=datetime.datetime.now()
  delta=t2-t1
