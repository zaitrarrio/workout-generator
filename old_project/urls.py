from django.conf.urls.defaults import *

from myproject.oraclefitness.views import *

urlpatterns = patterns('',
    (r'^$', home),
    (r'^[Aa]boutus/$', aboutUs),
    (r'^[Aa]ddcardio/$', addCardio),
    (r'^[Aa]ddexercise/$', addExercise),
    (r'^[Aa]ddgoal/$', addGoal),
    (r'^[Aa]ddvolume/$', addVolume),
    (r'^[Aa]dmincheckworkout/$', admincheckworkout),
    (r'^[Aa]dmincheckworkoutuser(?P<userid>\d+)/$',admincheckworkoutuser),

    (r'^[Ee]xerciselibrary(?P<pageNumber>\d+)/$',exerciseLibrary),
    (r'^[Vv]iew-exercise-(?P<exercise>\d+)/$',exerciseLibraryLookup),
    (r'^[Vv]iew-exercise-(?P<exercise>\w+)/$',exerciseLibraryLookup2),


    (r'^[Bb]log/$', blog),
    (r'^[Cc]ardio/$', cardio),
    (r'^[Cc]ancelsubscription/$', cancelSubscription),
    (r'^[Cc]ardiomax(?P<cardio>\d+)/$', cardioMax),
    (r'^[Cc]ontact/$', contact),
    (r'^[Cc]hangepassword/$', changePassword),
    (r'^[Cc]omponentdescriptions/$', componentDescriptions),
    (r'^[Cc]reateuser/$', createUser),

    (r'^[Dd]elete/$', delete),
    (r'^[Dd]escriptionlauncher(?P<description>\d+)/$',descriptionLauncher),
    (r'^[Ii]pn/$',ipn),
    (r'^[Ee]ditarticles/$',editArticles),
    (r'^[Ee]ditcardio(?P<cardio>\d+)/$',editCardio),

    (r'^[Ee]ditcardiomaxes/$',editCardioMaxes),
    (r'^[Ee]ditcardios/$',editCardios),
    (r'^[Ee]ditcomicalstatements/$', editComicalStatements),
    (r'^[Ee]ditdescriptions/$', editDescriptions),
    (r'^[Ee]ditexercise(?P<exercise>\d+)/$',editExercise),


    (r'^[Ee]ditexercises/$', editExercises),
    (r'^[Ee]ditexhaustion/$', editExhaustion),
    (r'^[Ee]ditfrequency(?P<fitnessLevel>\d+)/$',editFrequency),
    (r'^[Ee]ditfrequencies/$', editFrequencies),

    (r'^[Ee]ditfrequencyexceptions/$', editFrequencyExceptions),



    (r'^[Ee]ditgoal(?P<goal>\d+)/$',editGoal),
    (r'^[Ee]ditgoals/$', editGoals),
    (r'^[Ee]ditmusclefrequencies/$', editMuscleFrequencies),
    (r'^[Ee]ditphases/$', editPhases),
    (r'^[Ee]ditvolumes/$', editVolumes),
    (r'^[Ee]ditvolume(?P<volume>\d+)/$', editVolume),
    (r'^[Ff]aq/$', faq),
    (r'^[Ff]orgotpassword/$', forgotPassword),
    (r'^[Gg]yms/', gyms),
    (r'^[Ss]peed/$', speed),
    (r'^[Ss]tats/$', stats),

    (r'^[Ee]mailworkout/$', emailWorkout),
    (r'^[Hh]ome/$', home),
    (r'^[Ll]ocalgyms/$', localGyms),
    (r'^[Ll]ogout/$', logout),

    (r'^todaysWorkoutX/', todaysWorkoutX),
    (r'^getGoalsX/', getGoalsX),
    (r'^setGoalsX/', setGoalsX),
    (r'^getWeekX/', getWeekX),
    (r'^disabledX/', disabledX),
    (r'^setDisabledX/', setDisabledX),
    (r'^sendRating/', sendRating),
    (r'^[Rr]efer(?P<adnumber>\d+)/$', refer),
    (r'^[Mm]ygoals/', myGoals),
    (r'^[Mm]ygoalsiphone(?P<deviceid>[-\d\w]{36})/$', myGoalsiPhone),
    (r'^[Mm]ygoalsiphone(?P<deviceid>[-\d\w]{40})/$', myGoalsiPhone),

    (r'^[Mm]ygoalsiphonelite(?P<deviceid>[-\d\w]{36})/$', myGoalsiPhone),
    (r'^[Mm]ygoalsiphonelite(?P<deviceid>[-\d\w]{40})/$', myGoalsiPhone),
    (r'^[Mm]ygoalsnew/$', myGoalsNew),


    (r'^[Nn]ewadmin/$', newAdmin),
    (r'^[Nn]ewuser/$', newUser),
    (r'^[Nn]utrition/$', nutrition),
    (r'^[Nn]ewthread/$', newThread),
    (r'^[Pp]ayment/$', payment),

    (r'^[Pp]hasedescriptions/$', phaseDescriptions),
    (r'^[Pp]rivacypolicy/$', privacyPolicy),
    (r'^[Pp]rintfriendly/$', printFriendly),
    (r'^[Pp]rintentireweek/$', printEntireWeek),

    (r'^[Ee]nablemusclegroup(?P<muscleGroup>\d+)/$', enableMuscleGroup),
    (r'^[Dd]isablemusclegroup(?P<muscleGroup>\d+)/$', disableMuscleGroup),

    (r'^[Dd]isablemusclegroups/$', disableMuscleGroups),
    (r'^[Dd]isabledexercises/$', disabledExercises),
    (r'^[Dd]isabledexercisesiphone(?P<deviceid>[-\d\w]{36})/$', disableMuscleGroups),
    (r'^[Dd]isabledexercisesiphone(?P<deviceid>[-\d\w]{40})/$', disableMuscleGroups),
    (r'^[Ll]anding/$', landing),
    (r'^[Pp]aypal/$', paypal),
    (r'^pay_what_you_want/$', paypal),
    (r'^payment_flow/$', payment_flow),
    (r'^[Rr]eaddexercise(?P<exercise>\d+)/$',readdExercise),
    (r'^[Rr]emoveexercise(?P<exercise>\d+)/$',removeExercise),
    (r'^[Rr]esources/$',resources),
    (r'^[Ss]ampleprint/$', samplePrint),
    (r'^[Ss]ampleworkout/$', sampleWorkout),
    (r'^[Ss]hareworkout(?P<workoutId>\d+)/$', shareWorkout),
    (r'^[Ss]ignin/$', signIn),
    (r'^[Tt]ermsofservice/$', termsOfService),
    (r'^[Tt]hread(?P<id>\d+)/$', thread),
    (r'^[Tt]hreads/$', threads),
    (r'^test/$', test),
    (r'^[Tt]odaysworkout/$', todaysworkout),
    (r'^[Tt]odaysworkoutiphone(?P<deviceid>[-\d\w]{36})/$', todaysworkoutiPhone),
    (r'^[Tt]odaysworkoutiphone(?P<deviceid>[-\d\w]{40})/$', todaysworkoutiPhone),
    (r'^[Tt]odaysworkoutiphonelite(?P<deviceid>[-\d\w]{36})/$', todaysworkoutiPhone),
    (r'^[Tt]odaysworkoutiphonelite(?P<deviceid>[-\d\w]{40})/$', todaysworkoutiPhone),

    (r'^[Ww]eeklayoutiphone(?P<deviceid>[-\d\w]{36})/$', todaysworkoutiPhone2),
    (r'^[Ww]eeklayoutiphone(?P<deviceid>[-\d\w]{40})/$', todaysworkoutiPhone2),

    (r'^[Ww]eeklayoutiphonelite(?P<deviceid>[-\d\w]{36})/$', todaysworkoutiPhone2),
    (r'^[Ww]eeklayoutiphonelite(?P<deviceid>[-\d\w]{40})/$', todaysworkoutiPhone2),
    (r'^[Tt]our/$', tour),
    (r'^[Vv]iewmutex/$', viewMutex),
    (r'^[Vv]iewexercises/$', viewExercises),
    (r'^[Yy]outubelauncher(?P<exercise>\d+)/$',youtubeLauncher),
    (r'^[Ww]eightlifting/$', weightLifting),
    (r'^xd_receiver/$', xd_receiver),
#    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/slobdell/webapps/oraclefitness/myproject/public_html/site_media'}),



#def viewnation(request, nation=None):
#  dictionary=commonVariables(request)
#  if not dictionary['username']:
#    return home(request)
#  nationToView=NationState.objects.filter(id=nation)[0]
#s  rulername=User.objects.filter(nation=nationToView)[0]




    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # Uncomment this for admin:
#    (r'^admin/', include('django.contrib.admin.urls')),
)
