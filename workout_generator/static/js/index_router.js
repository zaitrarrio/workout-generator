function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
function removeHash () {
    history.pushState("", document.title, window.location.pathname
        + window.location.search);
}

function redirectIfLoggedOut(){
    if (Parse.User.current() === null){
        Backbone.history.navigate('!login', {trigger: true});
    }
}

function facebookGetMe(){
    FB.api('/v2.1/me?fields=id,email', function(response) {
        var facebook_id = response.id;
        var facebookEmail = response.email || '';
        var parseUser = Parse.User.current();
        parseUser.set("facebook_id", facebook_id);
        parseUser.set("facebook_email", facebookEmail);
    });
    updateProfilePicture();
}

function updateProfilePicture() {
    FB.api('/v2.1/me/picture?redirect=false', function(response){
        var profilePictureUrl = response.data.url;
        $('.profile-circular').css({'background-image':'url(' + profilePictureUrl +')'});
        $('.profile-circular').show();
    });
}

function listToColumnMatrix(list, columns){
    var matrix = [];
    var buffer = [];
    for(var i=0; i < list.length; i++){
        buffer.push(list[i]);
        if (buffer.length === columns){
            matrix.push(buffer);
            buffer = [];
        }
    }
    matrix.push(buffer);
    return matrix;
}

AbstractView = Backbone.View.extend({
    transitionIn: function (callback) {
        var view = this;
        var animateIn = function () {
        view.$el.addClass('is-visible');
            view.$el.one('transitionend', function () {
                view.$el.css("position", "relative");
                if (_.isFunction(callback)) {
                    callback();
                }
            });
        };
        _.delay(animateIn, 20);
    },

    transitionOut: function (callback) {
        var view = this;
        view.$el.addClass('pushed-away');

        view.$el.one('transitionend', function () {
            view.$el.hide();
            if (_.isFunction(callback)) {
                callback();
            }
            else {
                view.remove();
            }
        });

    },

    postRender: function (options) {
        options = options || {};
        if (options.page === true) {
            this.$el.addClass('page');
        }
        return this;
    },
});

TemplateView = AbstractView.extend({
    initialize: function(templateSelector, extraRenderData){
        this.template = _.template($(templateSelector).html());
        this.renderData = extraRenderData || {};
    },
    render: function(options){
        this.$el.html(this.template(this.renderData));
        return this.postRender(options);
    }
});

SignUpView = AbstractView.extend({
    events: {
        "click .sign-up-continue": "clickSubmit",
        "click .facebook-button": "facebookLogin"
    },
    initialize: function(model, callback){
        this.model = model;
        this.template = _.template($("#sign-up-view").html());
        this.callback = callback;
    },
    facebookLogin: function(){
        var self = this;
        Parse.FacebookUtils.logIn("email", {
            success: function(user) {
                if (!user.existed()) {
                    // user signed up and logged in  through facebook
                } else {
                    // user logged in with facebook
                }
                facebookGetMe()
                self.callback();
            },
            error: function(user, error) {
                // User cancelled the Facebook login or didn't fully authorize
            }
        });
    },
    clickSubmit: function(){
        var email = this.$(".email-input").val();
        var password = this.$(".password-input").val();
        var isValidEmail = validateEmail(email);
        if(!isValidEmail){
            this.$(".error-area").html("Input a valid E-Mail address");
        }
        else if (password.length < 7){
            this.$(".error-area").html("Password needs to be at least 7 characters");
        }
        else {
            this.$(".loading-icon").show();
            this.$(".sign-up-continue").hide();
            var self = this;
            this.signUp(email, password, function(){
                self.$(".loading-icon").hide();
                self.$(".sign-up-continue").show();
                self.callback();
            });

        }
    },
    signUp: function(email, password, callback){
        var user = new Parse.User();
        user.set("username", email);
        user.set("password", password);
        user.set("email", email);
        user.signUp(null, {
            success: function(user) {
                $.ajax({
                    url: '/api/signup/',
                    data: {
                        email: email,
                        username: email
                    },
                    cache: false,
                    dataType: 'json',
                    traditional: true,
                    type: 'POST',
                    contentType: 'application/x-www-form-urlencoded;charset=utf-8',
                    success: function(response){
                        if (_.isFunction(callback)) {
                            callback();
                        }
                        Backbone.history.navigate('!confirmation/' + email, {trigger: true});
                    },
                    error: function(data){
                        self.$(".loading-icon").hide();
                        self.$(".sign-up-continue").show();
                        alert("error");
                    }
                });
            },
            error: function(user, error) {
                // Show the error message somewhere and let the user try again.
                alert("Error: " + error.code + " " + error.message);
                if (_.isFunction(callback)) {
                    callback();
                }
            }
        });
    },
    render: function(options){
        this.$el.html(this.template());
        return this.postRender(options);
    }
});

LandingView = AbstractView.extend({
    events: {
        "click .sign-up": "goSignUp"
    },
    initialize: function(model){
        this.model = model;
        this.template = _.template($("#landing-view").html());
    },
    goSignUp: function(){
        Backbone.history.navigate('!signup', {trigger: true});
    },
    render: function(options){
        this.$el.html(this.template());
        return this.postRender(options);
    }
});


DashboardView = AbstractView.extend({
    initialize: function(model){
        this.model = model;
        this.template = _.template($("#dashboard-view").html());
    },
    render: function(options){
        this.$el.html(this.template());
        return this.postRender(options);
    }
});

FitnessLevelView = AbstractView.extend({
    events: {
        "click .save": "save"
    },
    initialize: function(model, returnHome){
        this.returnHome = returnHome;
        this.model = model;
        this.template = _.template($("#fitness-level-view").html());

        var self = this;
        this.listenTo(this.model, "sync", function(){
            self.render();
        });
    },
    save: function(){
        var fitness_level = this.$(".slider-fitness").val();
        fitness_level = parseInt(parseInt(fitness_level, 10) / 20, 10);

        var experience = this.$(".slider-experience").val();
        experience = parseInt(parseInt(experience, 10) / 20, 10);

        var age = this.$(".age-select").val();
        var gender = this.$("input[name='gender']:checked").val();

        this.model.set("experience", experience);
        this.model.set("fitness_level", fitness_level);
        this.model.set("gender", gender);
        this.model.set("age", age);

        this.$(".save").hide();
        this.$(".loading-icon").show();
        var self = this;
        this.model.once('sync', function(){
            self.$(".loading-icon").hide();
            if(self.returnHome){
                Backbone.history.navigate('', {trigger: true});
            } else {
                Backbone.history.navigate('!equipment', {trigger: true});
            }
        });
        this.model.save();
    },
    render: function(options){
        this.$el.html(this.template());
        this.postRender(options);
        var self = this;

        setTimeout(function() {
            new Powerange(self.$(".slider-fitness")[0], {
                step: 1 ,
                min: 1,
                start: self.model.get('fitness_level') * 20,
                hideRange: true,
                max: 100
            });
            new Powerange(self.$(".slider-experience")[0], {
                step: 1 ,
                min: 1,
                start: self.model.get('experience') * 20,
                hideRange: true,
                max: 100
            });
        }, 0);
        if(this.model.get("age")){
            this.$(".age-select").val(this.model.get("age"));

            var selector = "#" + this.model.get("gender");
            this.$(selector).click();
        }
    }
});


ScheduleView = AbstractView.extend({
    events: {
        "click .save": "save"
    },
    initialize: function(model, returnHome){
        this.returnHome = returnHome;
        this.model = model;
        this.template = _.template($("#schedule-view").html());
        var self = this;
        this.listenTo(this.model, "sync", function(){
            self.render();
        });
    },
    _getCheckedWeekdays: function(){
        var selectedDays = [];
        for(var isoweekday=0; isoweekday<7; isoweekday++){
            var selector = "#isoweekday_" + isoweekday;
            if(this.$(selector).is(":checked")){
                selectedDays.push(isoweekday);
            }
        }
        return selectedDays;
    },
    save: function(){
        this.$(".save").hide();
        this.$(".loading-icon").show();

        this.model.set("enabled_days", this._getCheckedWeekdays());

        var minutesPerDay = parseInt(this.$(".minutes-per-day-select").val(), 10);
        this.model.set("minutes_per_day", minutesPerDay);
        var self = this;
        this.model.once('sync', function(){
            self.$(".loading-icon").hide();
            if(self.returnHome){
                Backbone.history.navigate('', {trigger: true});
            } else {
                Backbone.history.navigate('!fitnesslevel', {trigger: true});
            }
        });
        this.model.save();
    },
    _turnDayOn: function(isoweekday){
        var selector = "#isoweekday_" + isoweekday;
        if(!this.$(selector).is(":checked")){
            this.$(selector).click();
        }
    },
    _turnDayOff: function(isoweekday){
        var selector = "#isoweekday_" + isoweekday;
        if(this.$(selector).is(":checked")){
            this.$(selector).click();
        }
    },
    updateCheckedDaysWithModel: function(){
        for(var isoweekday=0; isoweekday<7; isoweekday++){
            if(this.model.hasDayEnabled(isoweekday)){
                this._turnDayOn(isoweekday);
            } else {
                this._turnDayOff(isoweekday);
            }
        }
    },
    render: function(options){
        this.$el.html(this.template());
        this.$("[name='toggle-switch']").bootstrapSwitch();

        var self = this;
        setTimeout(function(){
            self.updateCheckedDaysWithModel();
        }, 0);
        this.$(".minutes-per-day-select").val(this.model.get("minutes_per_day") || 60);
        return this.postRender(options);
    }
});

EquipmentView = AbstractView.extend({
    events: {
        "click .save": "save"
    },
    initialize: function(model, returnHome){
        this.returnHome = returnHome;
        this.model = model;
        this.template = _.template($("#equipment-view").html());
        this.availableEquipmentJSON = [];
        this.getEquipmentData();
        var self = this;
        this.listenTo(this.model, "sync", function(){
            self.render();
        });
    },
    _getEquipmentInputEl: function(equipmentId){
        var selector = "#equipment_" + equipmentId;
        var el = this.$(selector).find("input");
        return el;
    },
    _turnEquipmentIdOn: function(equipmentId){
        var el = this._getEquipmentInputEl(equipmentId);
        if(!el.is(":checked")){
            el.click();
        }
    },
    _turnEquipmentIdOff: function(equipmentId){
        var el = this._getEquipmentInputEl(equipmentId);
        if(el.is(":checked")){
            el.click();
        }
    },
    _getCheckedEquipmentIds: function(){
        var checkedEquipment = [];
        for(var i=0; i<this.availableEquipmentJSON.length; i++){
            var equipmentObject = this.availableEquipmentJSON[i];
            var el = this._getEquipmentInputEl(equipmentObject.id);
            if(el.is(":checked")){
                checkedEquipment.push(equipmentObject.id);
            }
        }
        return checkedEquipment;
    },
    save: function(){
        this.$(".save").hide();
        this.$(".loading-icon").show();
        this.model.set("equipment_ids", this._getCheckedEquipmentIds());

        var self = this;
        this.model.once('sync', function(){
            self.$(".loading-icon").show();
            if(self.returnHome){
                Backbone.history.navigate('', {trigger: true});
            } else {
                Backbone.history.navigate('!payment', {trigger: true});
            }
        });
        this.model.save();
    },
    getEquipmentData: function(){
        var self = this;
        $.ajax({
            url: '/api/equipment/',
            cache: false,
            dataType: 'json',
            traditional: true,
            type: 'GET',
            success: function(response){
                self.availableEquipmentJSON = response;
                self.render();
            },
            error: function(data){
            }
        });
    },
    updateTogglesWithModel: function(){
        for(var i=0; i<this.availableEquipmentJSON.length; i++){
            var equipmentObject = this.availableEquipmentJSON[i];
            if(this.model.hasEquipmentId(equipmentObject.id)){
                this._turnEquipmentIdOn(equipmentObject.id);
            } else {
                this._turnEquipmentIdOff(equipmentObject.id);
            }
        }
    },
    render: function(options){
        this.$el.html(this.template({
            equipmentMatrix: listToColumnMatrix(this.availableEquipmentJSON, 3)
        }));
        this.$("[name='toggle-switch']").bootstrapSwitch();
        this.updateTogglesWithModel();
        return this.postRender(options);
    }
});

PaymentView = AbstractView.extend({
    initialize: function(model){
        this.model = model;
        this.template = _.template($("#payment-view").html());
    },
    openStripeModal: function(){
        // READ
        // https://www.petekeen.net/using-stripe-checkout-for-subscriptions
        var self = this;
        var handler = StripeCheckout.configure({
            key: $("#stripe-publish-key").val(),
            image: $("#square-icon").val(),
            token: function(token) {
                $.ajax({
                    url: '/api/payment/',
                    data: {
                        username: Parse.User.current().get("username"),
                        tokenId: token.id,
                        tokenEmail: token.email
                    },
                    cache: false,
                    dataType: 'json',
                    traditional: true,
                    type: 'POST',
                    contentType: 'application/x-www-form-urlencoded;charset=utf-8',
                    success: function(response){
                        Backbone.history.navigate('', {trigger: true});
                    },
                    error: function(data){
                        alert("stripe fail");
                    }
                });
            }
        });

        var options = {
            name: 'WorkoutGenerator.net',
            description: 'Monthly Subscription'
        };
        options["panel-label"] = "Subscribe";
        handler.open(options);
    },
    render: function(options){
        this.$el.html(this.template());
        this.postRender(options);
        this.openStripeModal();
        return this.el;
    }
});

LoginView = AbstractView.extend({
    events: {
        "click .facebook-button": "facebookLogin",
        "click .log-in-continue": "login"
    },
    initialize: function(model, callback){
        this.model = model;
        this.callback = callback;
        this.template = _.template($("#login-view").html());
    },
    login: function(){
        var email = this.$(".email-input").val();
        var password = this.$(".password-input").val();
        this.$(".loading-icon").show();
        this.$(".log-in-continue").hide();

        var self = this;
        Parse.User.logIn(email, password, {
            success: function(){
                facebookGetMe()
                self.callback();
                self.$(".loading-icon").hide();
                self.$(".log-in-continue").show();
                Backbone.history.navigate('', {trigger: true});
            },
            error: function(){
                self.$(".loading-icon").hide();
                self.$(".log-in-continue").show();
                self.$(".error-area").html("That username and password combination does not exist.");
            }
        });
    },
    facebookLogin: function(){
        var self = this;
        Parse.FacebookUtils.logIn("email", {
            success: function(user) {
                if (!user.existed()) {
                    // user signed up and logged in  through facebook
                } else {
                    // user logged in with facebook
                }
                Backbone.history.navigate('', {trigger: true});
                self.callback();
            },
            error: function(user, error) {
                // User cancelled the Facebook login or didn't fully authorize
            }
        });
    },
    render: function(options){
        this.$el.html(this.template(this.renderData));
        return this.postRender(options);
    }
});

WorkoutView = AbstractView.extend({
    initialize: function(userModel){
        this.userModel = userModel;
        this.workoutCollection = new WorkoutCollection();
        this.template = _.template($("#workout-view").html());
        var self = this;
        this.listenTo(this.workoutCollection, 'sync', function(){
            self.render();
        });
        this.listenTo(this.userModel, 'sync', function(){
            self.render();
        });
        this.workoutCollection.fetch();
    },
    _initDatePickerView: function(){
        this.datePickerView = new DatePickerView(this.workoutCollection);
        this.listenTo(this.datePickerView, this.datePickerView.EVENTS.DATE_CHANGED, this.renderNewWorkout);
    },
    renderNewWorkout: function(isoweekday){
        var workoutModel = this.workoutCollection.getWorkoutForDay(isoweekday);
        this.renderLifting(workoutModel);
        this.renderCardio(workoutModel);
    },
    renderLifting: function(workoutModel){
        if(workoutModel === null){
            this.$("#workout-placeholder").html("<h1 style='margin-top: 20px;'>Off Day</h1>");
        } else {
            this.liftingView = new LiftingView(workoutModel);
            this.$("#workout-placeholder").html(this.liftingView.render().el);
        }
    },
    renderCardio: function(workoutModel){
        var cardioEl = this.$("#cardio-placeholder");
        if(!workoutModel || !workoutModel.get("cardio")){
            cardioEl.empty();
            return;
        }
        this.cardioView = new CardioView(this.userModel, workoutModel.get("cardio"), workoutModel.get("cardio_level"));
        cardioEl.html(this.cardioView.render().el);
    },
    renderMeta: function(){
        if(!this.userModel.get("phase")){
            return;
        }
        this.workoutMetaView = new WorkoutMetaView(this.userModel);
        this.$("#meta-placeholder").html(this.workoutMetaView.render().el);
    },

    render: function(options){
        this._initDatePickerView();
        this.$el.html(this.template());

        this.$("#datepicker-placeholder").html(this.datePickerView.render().el);
        this.datePickerView.selectToday();
        this.renderMeta();

        this.postRender(options);
        return this.$el;
    }
});


DatePickerView = Backbone.View.extend({
    events: {
        "changeDate": "dateChanged"
    },
    EVENTS: {
        DATE_CHANGED: "datepicker-date-changed"
    },
    initialize: function(workoutCollection){
        this.template = _.template($("#datepicker-view").html());
        this.workoutCollection = workoutCollection;
        this.startDateTime = new Date(this.workoutCollection.getEarliestUTCTimestamp());
        this.endDateTime = new Date(this.workoutCollection.getLatestUTCTimestamp());
        this.triggerDateChange = true;
    },
    initDatepicker: function(startDate, endDate){
        this.$(".datepicker-el").datepicker({
            format: 'DD, M d',
            startDate: startDate,
            endDate: endDate
        });
    },
    dateChanged: function(evt){
        if(this.triggerDateChange){
            if (evt.date){
                this.trigger(this.EVENTS.DATE_CHANGED, evt.date.getDay());
            }
        }
    },
    refreshEl: function(){
        // necessary because datepicker contents are populated outside of our immediate control
        this.$el = $(this.$el.selector);
        this.delegateEvents();
    },
    selectToday: function(){
        var datepickerStartDate = this.getStartDateFromDatepicker();
        var selectedMonth = datepickerStartDate.getMonth();
        var selectedYear = datepickerStartDate.getYear();
        var now = new Date();

        if (selectedYear === now.getYear() && selectedMonth === now.getMonth()){
            this.selectDate(now);
        } else {
            this.$(".datepicker-el").datepicker('setDate', now);
            this.$(".datepicker-el").datepicker('update');
            var self = this;
            setTimeout(function(){
                self.selectDate(now);
            }, 0);
        }
    },
    selectFirstAvailableDay: function(){
        /* this is hacky but the bootstrap datepicker doesn't appear to expose
            * this through their API for inline datepickers.  Replace if there's
            * a better way */
        var enabledDaysSelector = this.$(".datepicker td.day:not(.disabled):not(.new):not(.old)");
        if(enabledDaysSelector.length > 0){
            $(enabledDaysSelector[0]).click();
        }
    },
    selectDayOfMonth: function(dayOfMonth){
        /* this is hacky but the bootstrap datepicker doesn't appear to expose
            * this through their API for inline datepickers.  Replace if there's
            * a better way */
        var enabledDaysSelector = this.$(".datepicker td.day:not(.disabled):not(.new):not(.old)");
        enabledDaysSelector.each(function(index, dayElement){
            var dayNumber = parseInt(dayElement.innerHTML, 10);
            if(dayNumber === dayOfMonth){
                $(dayElement).click();
            }
        });
    },
    selectDate: function(date){
        this.$(".datepicker-el").datepicker('setDate', date);
        this.$(".datepicker-el").datepicker('update');
        var dayNumber = date.getDate();
        this.selectDayOfMonth(dayNumber);
    },
    getStartDateFromDatepicker: function(){
        var selector = this.$(".datepicker .datepicker-switch");
        if (selector.length === 0){
            return new Date();
        }
        var dateString = selector[0].innerHTML;
        return new Date(Date.parse(dateString));
    },
    render: function(){
        this.$el.html(this.template());
        this.initDatepicker(this.startDateTime, this.endDateTime);
        return this;
    }
});


LiftingView = Backbone.View.extend({
    initialize: function(workoutModel){
        this.workoutModel = workoutModel;
        this.template = _.template($("#lifting-view").html());
    },
    render: function(){
        this.$el.html(this.template());
        var workoutComponents = this.workoutModel.get("workout_components");
        for(var i=0; i<workoutComponents.length; i++){
            this.$el.append(new WorkoutComponentView(workoutComponents[i]).render().el);
        }
        return this;
    }
});


WorkoutComponentView = Backbone.View.extend({
    events: {
        "click .exercise-block": "clickExercise"
    },
    initialize: function(workoutComponentJSON){
        this.template = _.template($("#workout-component-view").html());
        this.workoutComponentJSON = workoutComponentJSON;
    },
    clickExercise: function(evt){
        var elId = evt.target.id;
        var videoEl = this.$("#video_" + elId);
        $(".exercise-video").hide();
        videoEl.show();
    },
    render: function(){
        this.$el.html(this.template(this.workoutComponentJSON));
        return this;
    }
});


CardioView = Backbone.View.extend({
    initialize: function(userModel, cardioJSON, cardioLevel){
        this.template = _.template($("#cardio-view").html());
        this.cardioJSON = cardioJSON;
        this.cardioLevel = cardioLevel;
        this.maxHeartRate = userModel.get("max_heart_rate");
    },
    _getCardioLevelDisplayString: function(){
        if(this.cardioLevel === 1){
            return "Light Cardio";
        } else if (this.cardioLevel === 2){
            return "Medium Cardio";
        } else if (this.cardioLevel === 3){
            return "Heavy Cardio";
        } else {
            return "";
        }
    },
    _getZoneMeta: function(){
        var zoneMeta = {
            "zone1": null,
            "zone2": null,
            "zone3": null
        }
        for(var i=0; i<this.cardioJSON.length; i++){
            var zone = this.cardioJSON[i].zone;
            var zoneKey = "zone" + zone.toString();
            zoneMeta[zoneKey] = {
                minutes: parseInt(this.cardioJSON[i].minutes, 10),
                seconds: parseInt(parseFloat(this.cardioJSON[i].minutes) / 60.0, 10),
                minHeartRate: parseInt(parseFloat(this.cardioJSON[i].min_heart_rate) * this.maxHeartRate / 100.0, 10),
                maxHeartRate: parseInt(parseFloat(this.cardioJSON[i].max_heart_rate) * this.maxHeartRate / 100.0, 10)
            }
        }
        return zoneMeta;
    },
    _getTotalTime: function(){
        var totalTime = 0.0;
        for(var i=0; i<this.cardioJSON.length; i++){
            totalTime += this.cardioJSON[i].minutes;
        }
        return totalTime;
    },
    _getMaxBPM: function(){
        return 100.0;
        var maxBPM = 0;
        for(var i=0; i<this.cardioJSON.length; i++){
            var bpm = (this.cardioJSON[i].max_heart_rate + this.cardioJSON[i].min_heart_rate) / 2.0;
            if(bpm > maxBPM){
                maxBPM = bpm;
            }
        }
        return maxBPM;
    },
    _getCardioBlocks: function(){
        /* will return ordered list of zone, height%, width% */
        var totalTime = this._getTotalTime();
        var maxBPM = this._getMaxBPM();
        var widthOfCardioDisplayPercent = 90.0;
        var cardioBlocks = [];
        for(var i=0; i<this.cardioJSON.length; i++){
            var zone = this.cardioJSON[i].zone;
            var zoneKey = "zone" + zone.toString();
            var percentOfTotal = parseFloat(this.cardioJSON[i].minutes) * widthOfCardioDisplayPercent / totalTime;
            if(percentOfTotal < 3.0){
                percentOfTotal = 3.0;
            }
            var bpm = (this.cardioJSON[i].max_heart_rate + this.cardioJSON[i].min_heart_rate) / 2.0;
            var height = bpm / maxBPM;
            height *= height;
            height *= 100.0;
            cardioBlocks.push({
                zoneClass: zoneKey,
                widthPercent: percentOfTotal,
                heightPercent: height
            });
        }
        return cardioBlocks;
    },
    render: function(){
        this.$el.html(this.template({
            cardioLevel: this._getCardioLevelDisplayString(),
            zoneMeta: this._getZoneMeta(),
            totalTime: this._getTotalTime(),
            cardioBlocks: this._getCardioBlocks()
        }));
        return this;
    }
});


WorkoutMetaView = Backbone.View.extend({
    initialize: function(userModel){
        this.userModel = userModel;
        this.template = _.template($("#meta-view").html());
    },
    render: function(){
        var phaseNames = [];
        var phases = this.userModel.get("goal").phases;
        for(var i=0; i<phases.length; i++){
            phaseNames.push(phases[i].phase.title);
        }
        this.$el.html(this.template({
            weekInPhase: this.userModel.get("current_week_in_phase"),
            phaseNames: phaseNames,
            currentPhase: this.userModel.get("phase").title,
            currentGoal: this.userModel.get("goal").title,
            totalWeeksInPhase: this.userModel.get("total_weeks_in_phase"),
        }));
        return this;
    }
});


GoalView = AbstractView.extend({
    events: {
        "click .member-container": "selectGoal",
        "mouseenter .member-container": "addSelected",
        "mouseleave .member-container": "removeSelected"
    },
    initialize: function(model, returnHome){
        this.returnHome = returnHome;
        this.model = model;
        this.template = _.template($("#goal-view").html());
        this.goalJSON = [];
        this.getGoalData();
        this.aws_static = $("#aws_static").val();
    },
    getElement: function(evt){
        var element = $(evt.target);
        var goalRegEx = new RegExp("goal");
        while(!goalRegEx.test(element.attr("id"))){
            element = element.parent();
        }
        return element;
    },
    addSelected: function(evt){
        var element = this.getElement(evt);
        element.addClass("selected");
    },
    removeSelected: function(evt){
        var element = this.getElement(evt);
        element.removeClass("selected");
    },
    selectGoal: function(evt){
        var element = this.getElement(evt);
        var goalId = parseInt(element.attr("id").split("_")[1], 10);
        this.$(".row").hide();
        this.$(".loading-icon").show();
        var self = this;
        // TODO replace this with this.model.save()
        $.ajax({
            url: '/api/user/',
            data: {
                username: Parse.User.current().get("username"),
                goal_id: goalId
            },
            cache: false,
            dataType: 'json',
            traditional: true,
            type: 'POST',
            success: function(data){
                if(self.returnHome){
                    Backbone.history.navigate('', {trigger: true});
                } else {
                    Backbone.history.navigate('!schedule', {trigger: true});
                }
            },
            error: function(data){
                self.$(".loading-icon").hide();
                self.$(".row").show();
                alert("error");
            }
        });
    },
    getGoalData: function(){
        var self = this;
        $.ajax({
            url: '/api/goals/',
            cache: false,
            dataType: 'json',
            traditional: true,
            type: 'GET',
            success: function(response){
                self.goalJSON = response;
                self.render();
            },
            error: function(data){
            }
        });
    },
    render: function(options){
        this.$el.html(this.template({
            goalMatrix: listToColumnMatrix(this.goalJSON, 3)
        }));
        this.postRender(options);
        return this.$el;
    }
});

GlobalView = Backbone.View.extend({
    el: ".content-area",
    initialize: function(){
        this.currentPage = null;
    },
    goto: function (view) {

        var previous = this.currentPage || null;
        var next = view;

        if (previous) {
            previous.transitionOut(function () {
                previous.remove();
            });
        }

        next.render({ page: true });
        this.$el.append( next.$el );
        next.transitionIn();
        this.currentPage = next;
    }
});

LoginStateView = Backbone.View.extend({
    el: $("#login-state"),
    events: {
        "click a": "toggleLogInState"
    },
    initialize: function(model){
        this.model = model;
    },
    updateLoginState: function(){
        this.authenticated = (Parse.User.current() !== null);
        if(this.authenticated && _.indexOf(Parse.User.current().get("username"), "@") === -1){
            facebookGetMe();
        }
        if(this.authenticated){
            this.model.fetch();
        }
        this.render();
    },
    toggleLogInState:function(){
        if(this.authenticated){
            Parse.User.logOut()
            this.authenticated = false;
            $('.profile-circular').hide();
            this.render();
            Backbone.history.navigate('', {trigger: true});
        } else {
            Backbone.history.navigate('!login', {trigger: true});
        }
    },
    render: function(){
        if(this.authenticated){
            this.$el.html("<a href='javascript:void(0);'>Log Out <i class='icon-signout'></i></a></li>");
        } else {
            this.$el.html("<a href='javascript:void(0);'>Log In <i class='icon-signin'></i></a></li>");
        }
    }
});


User = Backbone.Model.extend({
    url: function(){
        if(!Parse.User.current()){
            return null;
        }
        return '/api/user/?username=' + Parse.User.current().get('username');
    },
    initialize: function(){
        this.listenTo(this, 'sync', function(){
        });
    },
    hasEquipmentId: function(equipmentId){
        return _.indexOf(this.get('equipment_ids') || [], equipmentId) > -1;
    },
    hasDayEnabled: function(isoweekday){
        return _.indexOf(this.get('enabled_days') || [], isoweekday) > -1;
    },
    save: function(attrs, options) {
        this.set("username", Parse.User.current().get("username"));
        Backbone.Model.prototype.save.call(this, attrs, options);
    }
});


Workout = Backbone.Model.extend({
});


WorkoutCollection = Backbone.Collection.extend({
    url: function(){
        if(!Parse.User.current()){
            return null;
        }
        return '/api/workout/?username=' + Parse.User.current().get('username');
    },
    initialize: function(){
        this.isoweekday_to_workout = {};
        var self = this;
        this.listenTo(this, 'sync', function(){
            self._mapIsoweekdayToWorkout();
        });
    },
    model: Workout,
    _mapIsoweekdayToWorkout: function(){
        var self = this;
        this.each(function(model){
            var isoweekday = model.get("js_isoweekday");
            if(isoweekday === null || isoweekday === undefined){
                return;
            }
            var key = isoweekday.toString();
            self.isoweekday_to_workout[key] = model;
        });
    },
    getWorkoutForDay: function(isoweekday){
        var key = isoweekday.toString();
        return this.isoweekday_to_workout[key] || null;
    },
    getEarliestUTCTimestamp: function(){
        // FIXME this can be done better with underscore
        var minTimestamp = null;
        this.each(function(model){
            var timestamp = model.get("utc_date_timestamp");
            if (!minTimestamp || timestamp < minTimestamp){
                minTimestamp = timestamp;
            }
        });
        return minTimestamp;
    },
    getLatestUTCTimestamp: function(){
        var maxTimestamp = null;
        this.each(function(model){
            var timestamp = model.get("utc_date_timestamp");
            if (!maxTimestamp || timestamp > maxTimestamp){
                maxTimestamp = timestamp;
            }
        });
        return maxTimestamp;
    }
});

IndexRouter = Backbone.Router.extend({
    routes: {
        "!confirmation/:email": "confirmEmail",
        "!signup": "signup",

        "!goal/:returnHome": "goal",
        "!goal": "goal",

        "!equipment/:returnHome": "equipment",
        "!equipment": "equipment",

        "!fitnesslevel/:returnHome": "fitnessLevel",
        "!fitnesslevel": "fitnessLevel",

        "!schedule/:returnHome": "schedule",
        "!schedule": "schedule",

        "!login": "login",
        "!payment": "payment",
        "!workout": "workout",
        "": "defaultRoute"
    },
    initialize: function(){
        this.model = new User();
        this.loggedIn = false;
        this.globalView = new GlobalView();
        this.loginStateView = new LoginStateView(this.model);
        this.loginStateView.updateLoginState();
    },
    workout: function(){
        redirectIfLoggedOut();
        this.workoutView = new WorkoutView(this.model);
        this.globalView.goto(this.workoutView);
    },
    login: function(){
        var self = this;
        this.loginView = new LoginView(this.model, function(){
            self.loginStateView.updateLoginState();
        });
        this.globalView.goto(this.loginView);
    },
    confirmEmail: function(email){
        this.templateView = new TemplateView("#confirm-view", {email: email});
        this.globalView.goto(this.templateView);
    },
    payment: function(){
        redirectIfLoggedOut();
        this.paymentView = new PaymentView(this.model);
        this.globalView.goto(this.paymentView);
    },
    goal: function(returnHome){
        redirectIfLoggedOut();
        this.goalView = new GoalView(this.model, returnHome);
        this.globalView.goto(this.goalView);
    },
    equipment: function(returnHome){
        redirectIfLoggedOut();
        this.equipmentView = new EquipmentView(this.model, returnHome);
        this.globalView.goto(this.equipmentView);
    },
    fitnessLevel: function(returnHome){
        redirectIfLoggedOut();
        this.fitnessLevelView = new FitnessLevelView(this.model, returnHome);
        this.globalView.goto(this.fitnessLevelView);
    },
    schedule: function(returnHome){
        redirectIfLoggedOut();
        this.scheduleView = new ScheduleView(this.model, returnHome);
        this.globalView.goto(this.scheduleView);
    },
    signup: function(){
        var self = this;
        this.signUpView = new SignUpView(this.model, function(){
            self.loginStateView.updateLoginState();
        });
        this.globalView.goto(this.signUpView);
    },
    defaultRoute: function(path){
        removeHash();
        if(!Parse.User.current()){
            this.landingView = new LandingView(this.model);
            this.globalView.goto(this.landingView);
        } else {
            this.dashboardView = new DashboardView(this.model);
            this.globalView.goto(this.dashboardView);
        }
    }
});
