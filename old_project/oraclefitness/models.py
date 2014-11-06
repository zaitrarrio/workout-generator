from django.db import models


# YouTube Video References
class Video(models.Model):
    title=models.CharField(max_length=30)
    link=models.TextField(max_length=1024)
    rating=models.FloatField()
    dateAdded=models.DateTimeField()

# this can be deleted completely
class Description(models.Model):
    text=models.TextField()

# convert to enum
class WorkoutComponent(models.Model):
    name=models.CharField(max_length=40)
    #stabilization, power, strength


# convert to enum
class ExerciseType(models.Model):
    name=models.CharField(max_length=40)

# convert to enum
class Equipment(models.Model):
    name=models.CharField(max_length=30)


# convert to enum
class Phase(models.Model):
    name=models.CharField(max_length=30)
    tempo=models.CharField(max_length=9)
    rest=models.IntegerField()
    description=models.ForeignKey(Description, null=True)

# convert to enum
class Experience(models.Model):
    value=models.IntegerField()
    name=models.CharField(max_length=70)

# convert to enum
class FitnessLevel(models.Model):
    value=models.IntegerField()
    name=models.CharField(max_length=70)

# convert to enum
class CardioType(models.Model):
    name=models.CharField(max_length=30)
    minimum=models.IntegerField()
#endurance focused, bodybuilding, athletic focused, etc...

# convert to enum
class CardioMax(models.Model):
    fitnessLevel=models.ForeignKey(FitnessLevel)
    cardioType=models.ForeignKey(CardioType)
    loMaximum=models.IntegerField(default=7)
    medMaximum=models.IntegerField(default=7)
    hiMaximum=models.IntegerField(default=7)

# convert to enum
class CardioAction(models.Model):
  verb=models.CharField(max_length=30)
  equipment=models.ForeignKey(Equipment)

# convert to enum
class CardioZone(models.Model):
    level=models.IntegerField()
    zone=models.IntegerField()
    minInterval=models.FloatField()
    maxInterval=models.FloatField()
    minPrevious=models.IntegerField()
    maxPrevious=models.IntegerField()
    minHeartRate=models.IntegerField(null=True)
    heartRate=models.IntegerField()
    totalTime=models.IntegerField()
    fitnessLevel=models.ManyToManyField(FitnessLevel)
    cardioType=models.ManyToManyField(CardioType)
    maxOverall=models.IntegerField(null=True)

# convert to enum
class HardCodedRule(models.Model):
    cardioType=models.ForeignKey(CardioType)
    phase=models.ForeignKey(Phase)
    cardioZone=models.ForeignKey(CardioZone)

# not sure what this is, will need to dive into database directly
class Cardio(models.Model):
    name=models.CharField(max_length=100)
    equipment=models.ForeignKey(Equipment)
    sets=models.IntegerField(null=True)
    rest=models.IntegerField(null=True)
    distance=models.IntegerField(null=True)
    time=models.IntegerField(null=True)
    heartRate=models.IntegerField(null=True)
    timeOrDistance=models.BooleanField()
    description=models.TextField()
    minFitnessLevel=models.ForeignKey(FitnessLevel)
    totalTime=models.IntegerField(null=True)


# convert to enum
class Frequency(models.Model):
    minimum=models.IntegerField()
    maximum=models.IntegerField()
    phase=models.ForeignKey(Phase)
    currentFitnessLevel=models.ForeignKey(FitnessLevel)
    workoutComponent=models.ForeignKey(WorkoutComponent)
    week=models.IntegerField()


# convert to enum
class MuscleFrequency(models.Model):     #This generically applies to all muscle groups...i.e. don't work this muscle again
                                            #until later on this week because of the intensity you gave from last workout
    name=models.CharField(max_length=30)
    minimum=models.IntegerField()  #dependent variable, TIMES PER WEEK
    maximum=models.IntegerField()  #dependent variable, TIMES PER WEEK
    minSets=models.IntegerField()  #independent variable
    maxSets=models.IntegerField()  #independent variable
    minReps=models.IntegerField()  #independent variable
    maxReps=models.IntegerField()  #independent variable
    weekLength=models.IntegerField()
    exception=models.BooleanField(default=False)

# convert to enum
class MuscleGroup(models.Model):
    name=models.CharField(max_length=50)
    frequencyException=models.ManyToManyField(MuscleFrequency)
    relatedMuscleGroup=models.IntegerField(null=True)  #belongs to either the same larger muscle set, or super-settable
    complementaryMuscleGroup=models.IntegerField(null=True)

# convert to enum
class Exhaustion(models.Model):
    daysPerWeek=models.IntegerField()
    phase=models.ForeignKey(Phase)
    percent=models.IntegerField()

# keep as database thing, need to move to admin interface and grab from
# existing DB
class Exercise(models.Model):
    url=models.CharField(max_length=200)
    url2=models.CharField(max_length=200, null=True)
    name=models.CharField(max_length=100)

    multiJoint=models.NullBooleanField(null=True)

    phase=models.ManyToManyField(Phase, related_name='exercisePhases')

    minFitnessLevel=models.ForeignKey(FitnessLevel)
    minExperience=models.ForeignKey(Experience)
    muscleGroup=models.ForeignKey(MuscleGroup)
    secondaryMuscleGroup=models.ForeignKey(MuscleGroup, related_name='secondary', null=True)

    equipment=models.ManyToManyField(Equipment, related_name='equipments')
    workoutComponent=models.ForeignKey(WorkoutComponent, null=True)
    compound=models.BooleanField()
    progressor=models.IntegerField(null=True)#my cheap way of doing a foreign key to itself

    helpers=models.ManyToManyField(MuscleGroup, related_name='helpers')
    timed=models.NullBooleanField(null=True, default=False)
    oneLimb=models.NullBooleanField(null=True, default=False)
    lastModified=models.DateTimeField(null=True)
    dayOfWeek=models.CharField(max_length=20, null=True)
    exerciseType2=models.ForeignKey(ExerciseType, null=True)# now useless, need to do intense scripting to fix this
    mutuallyExclusive=models.IntegerField(null=True)
    exerciseType=models.ManyToManyField(ExerciseType, related_name='exercisetype')
    # used in 11 cases
    workoutComponent2=models.ForeignKey(WorkoutComponent, null=True, related_name='workoutcomponent2')
    # never used
    workoutComponent3=models.ForeignKey(WorkoutComponent, null=True, related_name='workoutcomponent3')

# convert to enum
class ExercisesPerMuscleGroup(models.Model):  #this will determine # of exercises per muscle group
    muscleGroup=models.ForeignKey(MuscleGroup)
    phase=models.ForeignKey(Phase)
    minimum=models.IntegerField(null=True)
    maximum=models.IntegerField(null=True)
    fitnessLevel=models.ForeignKey(FitnessLevel)

# convert to enum
class VolumeTable(models.Model):
    fitnessLevel=models.ForeignKey(FitnessLevel)
    phase=models.ForeignKey(Phase)
    week=models.IntegerField()
    minTimedCardio=models.IntegerField(null=True)
    maxTimedCardio=models.IntegerField(null=True)
    minDistanceCardio=models.IntegerField(null=True)
    maxDistanceCardio=models.IntegerField(null=True)


# convert to enum
class Volume(models.Model):
    minReps=models.IntegerField()
    maxReps=models.IntegerField()
    minSets=models.IntegerField()
    maxSets=models.IntegerField()
    minExercises=models.IntegerField()
    maxExercises=models.IntegerField()
    workoutComponent=models.ForeignKey(WorkoutComponent)
    parentTable=models.ForeignKey(VolumeTable)
    maxTotalReps=models.IntegerField(null=True)

# convert to enum...check out the data in the database and see how many of each
# we actually got to see popularity
class Goal(models.Model):
    name=models.CharField(max_length=70)
    phase=models.ManyToManyField(Phase)
    cardioType=models.ForeignKey(CardioType)
    description=models.ForeignKey(Description, null=True)
    startPhase=models.ForeignKey(Phase, null=True, related_name='startPhase')
    image=models.CharField(max_length=100, null=True)

# convert to enum
class PhaseLength(models.Model):
    goal=models.ForeignKey(Goal)
    phase=models.ForeignKey(Phase)
    minLength=models.IntegerField()
    maxLength=models.IntegerField()

# user specific DB table
class Series(models.Model):
    exercise=models.ForeignKey(Exercise)
    reps=models.IntegerField()
    sets=models.IntegerField()
    tempo=models.CharField(max_length=30)
    rest=models.IntegerField()
    superSet=models.IntegerField(null=True)#id of another series object


# user specific DB table
class ThisWeek(models.Model):
    dayNumber=models.IntegerField()
    user=models.ForeignKey(User)
    workoutComponents=models.ManyToManyField(WorkoutComponent)
    cardio=models.BooleanField()
    timed=models.NullBooleanField(null=True)
    level=models.IntegerField(null=True)



# user specific DB table
class TodaysWorkout(models.Model):
    date=models.DateField()
    exercises=models.ManyToManyField(Series)#, through="WorkoutSeries")
    user=models.ForeignKey(User)
    cardio=models.TextField(null=True)
    offDay=models.BooleanField(default=False)
    visited=models.BooleanField(default=False)
    thisWeek=models.ForeignKey(ThisWeek, null=True)

# user specific DB table
class WorkoutSeries(models.Model):
    todaysWorkout=models.ForeignKey(TodaysWorkout)
    series=models.ForeignKey(Series)
    class Meta:
        db_table = "oraclefitness_todaysworkout_exercises"
