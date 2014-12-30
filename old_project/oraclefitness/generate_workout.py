

def generateWorkout(currentUser, currentDateTime, dayOfWeek, thisWeekObject, baseExercises, exerciseMatrix):
  userInfo=UserInformation.objects.filter(user=currentUser)[0]
  phases=userInfo.goal.phase.all()
  existingWorkout=TodaysWorkout.objects.filter(user=currentUser, date=currentDateTime)
  if True:  # if not existing_workout
    myPhase=phases[userInfo.currentPhase]
    myFitnessLevel=userInfo.currentFitnessLevel
    currentWeek= ((userInfo.currentDay-1)/7)+1

    maxWeekInPhase=6
    currentWeekToUse=currentWeek
    if myPhase in userInfo.visitedPhases.all():
      currentWeekToUse=maxWeekInPhase

    exercisesPerMuscleGroup=ExercisesPerMuscleGroup.objects.filter(phase=myPhase, fitnessLevel=userInfo.currentFitnessLevel).select_related('muscleGroup')
    exercisesPerMuscleGroupDict={}
    for iterator in exercisesPerMuscleGroup:
      key=iterator.muscleGroup.name
      exercisesPerMuscleGroupDict[key]=iterator

    volumeTable=VolumeTable.objects.filter(fitnessLevel=myFitnessLevel, phase=myPhase, week=currentWeekToUse)[0]
    todaysWorkout=TodaysWorkout()

    todaysWorkout.date=currentDateTime
    todaysWorkout.user=currentUser
    todaysWorkout.thisWeek=thisWeekObject
    todaysWorkout.save()

    myWeek=todaysWorkout.thisWeek



    stabPhase=Phase.objects.filter(name='stabilization')[0]
    if len(myWeek.workoutComponents.all())==0 and not myWeek.cardio:
      todaysWorkout.offDay=True
      todaysWorkout.save()
      userInfo.todaysWorkout=todaysWorkout
      userInfo.save()
      return todaysWorkout
    volume1=0
    volume2=0
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

    # list to prevent the same exercises being used twice in a workout
    todaysExercises=[]

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

    if baseExercises is None:
      baseExercises=list(getBaseExercises(currentUser, None))

    baseExercises = [e for e in baseExercises if e.muscleGroup not in yesterdayMuscles]
    potentialExercises=filterByMuscleGroups(currentUser, potentialExercises, currentDateTime, None)

    potentialExercisesStart=Exercise.objects.filter(id__in=[i.id for i in potentialExercises])
    muscleDictionary = {m.name: 0 for m in MuscleGroup.objects.all()}
    muscleTraverseDict = {m.id: m for m in MuscleGroup.objects.all()}

    relevantVolumes=Volume.objects.filter(parentTable=volumeTable).select_related('workoutComponent')
    volumeDict = {v.workoutComponent.name: v for v in relevantVolumes}

    for workout_component in reversed(myWeek.workoutComponents.all()):
      key=workout_component.name
      currentVolume=volumeDict[key]
      exercise_creation_count=random.randint(currentVolume.minExercises, currentVolume.maxExercises)

      superset=False
      # superset var indicates that we are in the superset portion
      previousSeries=None

      if workout_component.name=='Flexibility': #######special case
          #have to pass this because flexibility is last
        pass
      else:
          ##########EXERCISE FILTERING###############################################

        nextMuscleGroup=None                        #tryme
        if nextMuscleGroup==None:
          potentialExercises=list(potentialExercisesStart.filter(Q(workoutComponent=workout_component) | Q(workoutComponent2=workout_component) | Q(workoutComponent3=workout_component)))
          #NOW EVEN OUT THE DISTRUBUTION SO THERE IS AN EQUAL NUMBER FROM EACH MUSCLE GROUP!!
          potentialExercises=evenlyDistribute(potentialExercises, None)
        else:
          potentialExercises=list(potentialExercisesStart.filter(Q(workoutComponent=iterator) | Q(workoutComponent2=iterator) | Q(workoutComponent3=iterator), muscleGroup=nextMuscleGroup))
          if len(potentialExercises)==0:
            potentialExercises=list(potentialExercisesStart.filter(Q(workoutComponent=iterator) | Q(workoutComponent2=iterator) | Q(workoutComponent3=iterator)))
            potentialExercises=evenlyDistribute(potentialExercises, None)

          ##########END EXERCISE FILTERING###########################################

        oldPotentials=list(potentialExercises)
        oldPotentialsForSuperset=list(potentialExercises)

        potentialExerciseIds = [i.id for i in potentialExercises]

        reset_for_related_muscle_groups=False
        previousMuscle=None
        muscleCount=1
        if workout_component.name=='Resistance' and (myPhase.name=='power' or myPhase.name=='muscleEndurance') and exercise_creation_count%2==1:
          exercise_creation_count=exercise_creation_count+1
        iterationCounter=0

        while iterationCounter<exercise_creation_count:
          if previousMuscle:
            relatedToPrevious=[]
            start=previousMuscle
            relatedToPrevious.append(start)
            next=muscleTraverseDict[start.relatedMuscleGroup.__str__()]
            while next!=start:
              relatedToPrevious.append(next)
              next=muscleTraverseDict[next.relatedMuscleGroup.__str__()]

          cannotUse=list(userInfo.avoidedExercise.all())
          for iterator in todaysExercises:
            cannotUse.extend(filterByMutex(exerciseMatrix, potentialExercises, iterator, None))

          potentialExercises = [e for e in potentialExercises if e not in todaysExercises and e not in cannotUse]

          if superset:
            oldPotentialsForSuperset = [e for e in oldPotentialsForSuperset if e not in todaysExercises and e not in cannotUse]

          if not superset and (myPhase.name=='power' or myPhase.name=='muscle endurance'):
            potentialExercises = list(oldPotentials)
            potentialExercises = evenlyDistribute(list(potentialExercises), None)

          elif superset and (myPhase.name=='power' or myPhase.name=='muscle endurance'):  #SUPERSET
            success, potentialExercises, possibles=supersetPossibles(oldPotentialsForSuperset, potentialExercises, myPhase, previousSeries, todaysExercises, None, exerciseMatrix)

          exhaustionPercent=Exhaustion.objects.filter(daysPerWeek=userInfo.daysPerWeek, phase=myPhase)[0].percent
          if previousMuscle and not superset and workout_component.name=='Resistance' and float(muscleCount)*100.0/float(exercise_creation_count)<=exhaustionPercent:
            potentialExercises2=Exercise.objects.filter(id__in=potentialExerciseIds, muscleGroup__in=relatedToPrevious)
            if potentialExercises2.count()>0:
              potentialExercises=evenlyDistribute(list(potentialExercises2), None)
              reset_for_related_muscle_groups=True

          elif (reset_for_related_muscle_groups and workout_component.name=='Resistance' and float(muscleCount)*100.0/float(exercise_creation_count)>exhaustionPercent and not superset):
            reset_for_related_muscle_groups=False
            previousMuscle=None
            potentialExercises=list(Exercise.objects.filter(id__in=potentialExerciseIds))
            potentialExercises=evenlyDistribute(potentialExercises, None)

          someExercise=Series()
          someExercise.reps=random.randint(currentVolume.minReps, currentVolume.maxReps)
          if (myPhase.name=='power' or myPhase.name=='muscle endurance') and workout_component.name=='Resistance':
            if not superset:
              someExercise.reps=random.randint(volume1.minReps, volume1.maxReps)
            else:
              someExercise.reps=random.randint(volume2.minReps, volume2.maxReps)
          if someExercise.reps % 2 == 1:
              someExercise.reps += 1
          if someExercise.reps == 14:
              someExercise.reps += 1
          someExercise.sets=random.randint(currentVolume.minSets, currentVolume.maxSets)

          someExercise.tempo=myPhase.tempo + " seconds" #tempo is the rate at which you do the actual exercise
          if superset and myPhase.name=='muscle endurance':
            someExercise.tempo=stabPhase.tempo
          someExercise.rest=myPhase.rest

          if len(potentialExercises)>=1:
            started=False
            anExercise=1
            counter=0
            todaysMuscles = {e.muscleGroup for e in todaysExercises}

            for currentMuscleGroup in todaysMuscles:
              firstMuscleGroup=currentMuscleGroup
              while True:
                todaysMuscles.add(currentMuscleGroup)
                currentMuscleGroup=muscleTraverseDict[currentMuscleGroup.relatedMuscleGroup.__str__()]
                if currentMuscleGroup == firstMuscleGroup:
                    break

            reset=False

            while ((anExercise in todaysExercises or not started or anExercise in cannotUse)) and counter<15:#I reduced from 15 to 5

              condition=""
              started=True
              if len(potentialExercises) > 1:
                anExercise=potentialExercises[random.randint(0, len(potentialExercises)-1)]
              else:  #This happen when the db runs out of exercises to use
                break #exit the loop to stop doing computations

              if anExercise.compound:
                break
              else: #there must be at least 1 compound muscle group already there
                if anExercise.muscleGroup in todaysMuscles:
                    break
              checkExercisesPerMuscleGroup=exercisesPerMuscleGroupDict[anExercise.muscleGroup.name]
              if muscleDictionary[anExercise.muscleGroup.name] >= checkExercisesPerMuscleGroup.maximum:#no more muscle groups from this trash
                continue
                condition="couldn't add because of exercises per muscle group"
              if workout_component.name=='Resistance' and (myPhase.name=='power' or myPhase.name=='muscle endurance') and not superset:
                condition="good so far"
                strengthType=ExerciseType.objects.filter(name='Strength')[0]
                if not strengthType in anExercise.exerciseType.all():
                  condition="couldn't add because no strength type exercises"
                  continue
                else:
                  blankSeries=Series(exercise=anExercise)
                  #I think I wasted a bunch of stuff here...
                  goodToUse, blank, possibles=supersetPossibles(oldPotentialsForSuperset, potentialExercises, myPhase, blankSeries, todaysExercises, request, exerciseMatrix)
                  if not goodToUse or possibles==1:
                    condition="couldn't use cause of superset possibles"
                    continue
              counter=counter+1

              if counter>=7 and not reset:
                reset=True
                potentialExercises=list(Exercise.objects.filter(id__in=potentialExerciseIds))
                potentialExercises=evenlyDistribute(potentialExercises, request)

            if counter==15 and workout_component.name=='Resistance' and (myPhase.name=='power' or myPhase.name=='muscle endurance'):
              iterationCounter=iterationCounter+1#increment because this will cause a floater
              superSet=False
              #this was never reached

            if counter<15 and anExercise!=1:
              someExercise.exercise=anExercise
              todaysExercises.append(anExercise)
              someExercise.save()
              previousMuscle=anExercise.muscleGroup
              muscleCount=muscleCount+1
              if not superset:
                todaysWorkout.exercises.add(someExercise)
                if (myPhase.name=='muscle endurance' or myPhase.name=='power') and workout_component.name=='Resistance' and strengthType in anExercise.exerciseType.all():
                  superset=True
                  previousSeries=someExercise
              else:
                previousSeries.superSet=someExercise.id
                previousSeries.save()
                superset=False
                previousSeries=None
              if workout_component.name=='Resistance' or workout_component.name=='Core':
                muscleDictionary[someExercise.exercise.muscleGroup.name]=muscleDictionary[someExercise.exercise.muscleGroup.name]+1
                checkExercisesPerMuscleGroup=ExercisesPerMuscleGroup.objects.filter(muscleGroup=someExercise.exercise.muscleGroup, phase=myPhase, fitnessLevel=userInfo.currentFitnessLevel)[0]

                if muscleDictionary[someExercise.exercise.muscleGroup.name] < checkExercisesPerMuscleGroup.minimum:
                  nextMuscleGroup=someExercise.exercise.muscleGroup

                else:
                  nextMuscleGroup=None
          iterationCounter=iterationCounter+1

######################END FOR LOOP####################################
    todaysWorkout=reduceToTime(todaysWorkout, myWeek.cardio, myPhase, myWeek.timed, myWeek.level, volumeTable, request)

    _group_exercises_by_musclegroup()
    _add_flexibility(todaysWorkout)
    todaysWorkout.save()

    userInfo.todaysWorkout=todaysWorkout
    userInfo.save()

  return todaysWorkout

def _add_flexibility(todays_workout):
    todaysMuscleGroups=[]
    for seriesObject in todaysWorkout.exercises.select_related().all():
      if not seriesObject.exercise.muscleGroup in todaysMuscleGroups:
        todaysMuscleGroups.append(seriesObject.exercise.muscleGroup)


    flexComponent=WorkoutComponent.objects.filter(name="Flexibility")[0]
    currentVolume=Volume.objects.filter(workoutComponent=flexComponent, parentTable=volumeTable)[0]
    for iterator in todaysMuscleGroups:
      flexibilityExercises=list(Exercise.objects.filter(workoutComponent=flexComponent, muscleGroup=iterator))
      someExercise=Series()
      someExercise.reps=random.randint(currentVolume.minReps, currentVolume.maxReps)
      someExercise.sets=1#random.randint(currentVolume.minSets, currentVolume.maxSets)
      someExercise.tempo=''
      someExercise.rest=0
      someExercise.exercise=flexibilityExercises[random.randint(0, len(flexibilityExercises)-1)]
      someExercise.save()
      todaysWorkout.exercises.add(someExercise)

def _group_exercises_by_musclegroup():
    #Exercises need to appear in this order
    #Balance
    #Reactive
    #resistance
    #core
    #cardio (as applicable)

    componentDict = {workout_component.name: workout_component for workout_component in WorkoutComponent.objects.all()}
    orderedComponents=[]
    orderedComponents.append(componentDict['Balance'])
    orderedComponents.append(componentDict['Reactive'])
    orderedComponents.append(componentDict['Resistance'])
    orderedComponents.append(componentDict['Core'])

    tempList=list(todaysWorkout.exercises.select_related('exercise__workoutComponent').all())
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
          currentMuscleGroup=muscleDict[currentMuscleGroup.relatedMuscleGroup.__str__()]
        for k in range(j+1, maxIndex):
          if allExercises[k].exercise.muscleGroup.id in muscleCluster:
            temp=allExercises[j+1]
            allExercises[j+1]=allExercises[k]
            allExercises[k]=temp

      allExercisesCopy=[]
      for j in range(0,maxIndex):
        allExercisesCopy.append(Series(exercise=allExercises[j].exercise, reps=allExercises[j].reps, sets=allExercises[j].sets, tempo=allExercises[j].tempo, rest=allExercises[j].rest, superSet=allExercises[j].superSet))

      for j in range(0, maxIndex):
        allExercisesCopy[j].save()
        todaysWorkout.exercises.add(allExercisesCopy[j])
    #DELETE THE OLD UNORDERED
    todaysWorkout.exercises.filter(id__in=initialIds).delete()


def reduceToTime(todaysWorkout, cardio, phase, timed, level, volumeTable, request):  #2nd var is boolean
  allExercises=list(todaysWorkout.exercises.select_related('exercise').all())
#oneRepTime=float(int(somePhase.tempo[0:1])+int(somePhase.tempo[2:3])+int(somePhase.tempo[4:5]))
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

  todaysWorkout.save()
  time6=datetime.datetime.now()
  if cardio:
    todaysWorkout.cardio=cardioString
  time7=datetime.datetime.now()
  t2=datetime.datetime.now()
  delta=t2-t1
  if todaysWorkout.cardio:
    return fillMoreTime(userInfo, todaysWorkout, totalLength, volumeTable, phase)
  else:
    return todaysWorkout


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
        workout_component=WorkoutComponent.objects.filter(name=key)[0]
        applicableVolume=Volume.objects.filter(workoutComponent=workout_component, parentTable=volumeTable)[0]
        if timeToFill>0.0 and value<applicableVolume.maxExercises and workout_component!=flexComponent:
          #add another exercise from this workout component of appropriate difficulty with proper equipment, fuck...
          #can't be some anything we already used..todaysExercises=[]

          potentialExercisesStart=Exercise.objects.filter(workoutComponent__in=[workout_component], equipment__in=list(userInfo.equipmentAvailable.all()), phase__in=[phase], muscleGroup__in=allMuscleGroups)

          potentialExercisesBodyWeight=Exercise.objects.filter(workoutComponent__in=[workout_component], phase__in=[phase], muscleGroup__in=allMuscleGroups)
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
