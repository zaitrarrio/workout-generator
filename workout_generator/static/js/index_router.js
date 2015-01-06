function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
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

/*
FormulaView = Backbone.View.extend({
    el: "#button-fill-area",
    events: {
        "change #reps": "changeReps",
        "change #weight": "changeWeight",
        "change #percent": "changePercent",
        "keyup #reps": "changeReps",
        "keyup #weight": "changeWeight",
        "keyup #percent": "changePercent"
    },
    initialize: function(){
        this.template = _.template($("#formulas").html());
        this.reps = 0;
        this.weight = 0;
        this.average = 0.0;
        this.percent = 0.0;
    },
    changeReps: function(evt){
        // TODO input validation
        this.reps = $("#reps").val();
        if (this.reps === ""){
            this.reps = 1;
        }
        this.reps = parseInt(this.reps, 10);
        this.renderFormulas();
    },
    changePercent: function(evt){
        this.percent = this.$("#percent").val();
        if(this.percent === ""){
            this.percent = 0.0;
        }
        this.percent = parseFloat(this.percent, 10);
        this.renderEstimate();
    },
    changeWeight: function(evt){
        this.weight = $("#weight").val();
        if (this.weight === ""){
            this.weight = 0;
        }
        this.weight = parseInt(this.weight, 10);
        this.renderFormulas();
    },
    nflTest: function(reps, weight){
        if (weight !== 225){
            return null;
        }
        return (226.7 + (7.1 * reps)).toFixed(2);
    },
    brzycki: function(reps, weight){
        return (100 * weight / (102.78 - (2.78 * reps))).toFixed(2);
    },
    oConnor: function(reps, weight){
        return ((1 + (0.025 * reps)) * weight).toFixed(2);
    },
    mississippi: function(reps, weight){
        if(reps < 4 || reps > 10){
            return null;
        }
        if(reps <= 6){
            return ((1.12 * weight) + (5.09 * reps) - 24.62).toFixed(2);
        }
        return ((1.16 * weight) + (1.68 * reps) - 1.89).toFixed(2);
    },
    epley: function(reps, weight){
        return ((1 + (0.0333 * reps)) * weight).toFixed(2);
    },
    lander: function(reps, weight){
        return (weight / (1.013 - 0.0267123 * reps)).toFixed(2);
    },
    lombardi: function(reps, weight){
        return (Math.pow(reps, 0.10) * weight).toFixed(2);
    },
    unknown: function(reps, weight){
        return ((weight * 0.03 * reps) + weight).toFixed(2);
    },
    mayhew: function(reps, weight){
        return (100 * weight) / (52.2 + 41.9 * Math.pow(2.71828, reps * -0.055));
    },
    wathen: function(reps, weight){
        return (100 * weight) / (48.8 + 53.8 * Math.pow(2.71828, reps * -0.075));
    },
    nsca: function(reps, weight){
        // TODO this function is shit
        if(reps > 10){
            return null;
        }
        var coefficient = 1.0;
        if (reps === 2){
            coefficient = 1.035;
        }
        if (reps === 3){
            coefficient = 1.08;
        }
        if (reps === 4){
            coefficient = 1.115;
        }
        if (reps === 5){
            coefficient = 1.15;
        }
        if (reps === 6){
            coefficient = 1.18;
        }
        if (reps === 7){
            coefficient = 1.22;
        }
        if (reps === 8){
            coefficient = 1.255;
        }
        if (reps === 9){
            coefficient = 1.29;
        }
        if (reps === 10){
            coefficient = 1.325;
        }
        return weight * coefficient;
    },
    renderFormulas: function(){
        var selectorToFunction = [
            ["nfl-test", this.nflTest],
            ["brzycki", this.brzycki],
            ["mississippi", this.mississippi],
            ["epley", this.epley],
            ["nsca", this.nsca],
            ["mayhew", this.mayhew],
            ["lombardi", this.lombardi],
            ["lander", this.lander],
            ["wathen", this.wathen],
            ["oconnor", this.oConnor],
            ["unknown", this.unknown]
        ];
        var sum = 0.0;
        var count = 0;
        var max = 0;
        var min = 50000;
        for(var i=0; i < selectorToFunction.length; i++){
            var selector = selectorToFunction[i][0];
            var func = selectorToFunction[i][1];

            var estimatedWeight = func(this.reps, this.weight);
            if (estimatedWeight !== null){
                estimatedWeight = parseFloat(estimatedWeight, 10).toFixed(2);
                sum = sum + parseFloat(estimatedWeight, 10);
                this.$("#" + selector +" #fill").html(estimatedWeight + " lbs");
                count++;
                if (estimatedWeight > max){
                    max = estimatedWeight;
                }
                if (estimatedWeight < min){
                    min = estimatedWeight;
                }
            }
            else{
                this.$("#" + selector +" #fill").html("");
            }
        }
        this.average = (sum / count).toFixed(2);
        this.$("#min #fill").html(min + " lbs");
        this.$("#max #fill").html(max + " lbs");
        this.$("#average #fill").html(this.average + " lbs");
        this.renderEstimate();
    },
    renderEstimate: function(){
        this.average = parseFloat(this.average, 10);
        var estimate = (this.average * this.percent / 100.0).toFixed(2);
        this.$("#estimate").html(estimate + " lbs");
    },
    render: function(){
        window.scrollTo(0, 300);
        this.$el.html(this.template());
        this.reps = parseInt($("#reps").val(), 10);
        this.weight = parseInt($("#weight").val(), 10);
        this.percent = parseInt($("#percent").val(), 10);
        this.renderFormulas();
    }
});
*/

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
        "click .facebook-button": "clickFacebook"
    },
    initialize: function($el, model){
        this.template = _.template($("#sign-up-view").html());
    },
    clickFacebook: function(){
        Parse.FacebookUtils.logIn("email", {
            success: function(user) {
                if (!user.existed()) {
                    alert("User signed up and logged in through Facebook!");
                } else {
                    alert("User logged in through Facebook!");
                }
                console.log(Parse.User.current().get("username"));
            },
            error: function(user, error) {
                alert("User cancelled the Facebook login or did not fully authorize.");
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
                        alert("error");
                        if (_.isFunction(callback)) {
                            callback();
                        }
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
    initialize: function(){
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

FitnessLevelView = AbstractView.extend({
    events: {
        "click .save": "save"
    },
    initialize: function(){
        this.template = _.template($("#fitness-level-view").html());
    },
    save: function(){
        this.$(".save").hide();
        this.$(".loading-icon").show();
        var self = this;
        $.ajax({
            url: '/api/user/',
            data: {
            },
            cache: false,
            dataType: 'json',
            traditional: true,
            type: 'POST',
            success: function(data){
                self.$(".loading-icon").show();
                Backbone.history.navigate('!equipment', {trigger: true});
            },
            error: function(data){
                alert("error");
            }
        });
    },
    render: function(options){
        this.$el.html(this.template());
        this.postRender(options);
        var self = this;
        setTimeout(function() {
            new Powerange(self.$(".slider-fitness")[0], {
                step: 1 ,
                min: 1,
                start: 20,
                hideRange: true,
                max: 100
            });
            new Powerange(self.$(".slider-experience")[0], {
                step: 1 ,
                min: 1,
                start: 20,
                hideRange: true,
                max: 100
            });
        }, 0);
    }
});


ScheduleView = AbstractView.extend({
    events: {
        "click .save": "save"
    },
    initialize: function(){
        this.template = _.template($("#schedule-view").html());
    },
    save: function(){
        this.$(".save").hide();
        this.$(".loading-icon").show();
        var self = this;
        $.ajax({
            url: '/api/user/',
            data: {
            },
            cache: false,
            dataType: 'json',
            traditional: true,
            type: 'POST',
            success: function(data){
                self.$(".loading-icon").show();
                Backbone.history.navigate('!fitnesslevel', {trigger: true});
            },
            error: function(data){
                alert("error");
            }
        });
    },
    render: function(options){
        this.$el.html(this.template());
        this.$("[name='toggle-switch']").bootstrapSwitch();
        return this.postRender(options);
    }
});

EquipmentView = AbstractView.extend({
    events: {
        "click .save": "save"
    },
    initialize: function(){
        this.template = _.template($("#equipment-view").html());
        this.availableEquipmentJSON = [];
        this.getEquipmentData();
    },
    save: function(){
        this.$(".save").hide();
        this.$(".loading-icon").show();
        var self = this;
        $.ajax({
            url: '/api/user/',
            data: {
            },
            cache: false,
            dataType: 'json',
            traditional: true,
            type: 'POST',
            success: function(data){
                self.$(".loading-icon").show();
                Backbone.history.navigate('!payment', {trigger: true});
            },
            error: function(data){
                alert("error");
            }
        });
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
    render: function(options){
        this.$el.html(this.template({
            equipmentMatrix: listToColumnMatrix(this.availableEquipmentJSON, 3)
        }));
        this.$("[name='toggle-switch']").bootstrapSwitch();
        return this.postRender(options);
    }
});

PaymentView = AbstractView.extend({
    initialize: function(){
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
                self.$("#accounts-spinner").show();
                $.ajax({
                    url: '/api/payment/',
                    data: {
                        tokenId: token.id,
                        tokenEmail: token.email
                    },
                    cache: false,
                    dataType: 'json',
                    traditional: true,
                    type: 'POST',
                    contentType: 'application/x-www-form-urlencoded;charset=utf-8',
                    success: function(response){
                        var userInfoResponse = response;
                        window.purchaseFlow = false;
                        self.creditsAdded = true;
                        self.populatePage(userInfoResponse);
                        self.$("#accounts-spinner").hide();
                    },
                    error: function(data){
                        alert("error");
                        self.$("#accounts-spinner").hide();
                    }
                });
            }
        });

        handler.open({
            name: 'WorkoutGenerator.net',
            description: 'Workout Generator monthly subscription',
            amount: 500
        });
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
    initialize: function(callback){
        this.callback = callback;
        this.template = _.template($("#login-view").html());
    },
    login: function(){
        var email = this.$(".email-input").val();
        var password = this.$(".password-input").val();

        var self = this;
        Parse.User.logIn(email, password, {
            success: function(){
                Backbone.history.navigate('', {trigger: true});
                self.callback();
            },
            error: function(){
                self.$(".error-area").html("That username and password combination does not exist.");
            }
        });
    },
    facebookLogin: function(){
        Parse.FacebookUtils.logIn("email", {
            success: function(user) {
                if (!user.existed()) {
                    alert("User signed up and logged in through Facebook!");
                } else {
                    alert("User logged in through Facebook!");
                }
                console.log(Parse.User.current().get("username"));
            },
            error: function(user, error) {
                alert("User cancelled the Facebook login or did not fully authorize.");
            }
        });
    },
    render: function(options){
        this.$el.html(this.template(this.renderData));
        return this.postRender(options);
    }
});

GoalView = AbstractView.extend({
    events: {
        "click .member-container": "selectGoal",
        "mouseenter .member-container": "addSelected",
        "mouseleave .member-container": "removeSelected"
    },
    initialize: function(){
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
        $.ajax({
            url: '/api/user/',
            data: {
                goal_id: goalId
            },
            cache: false,
            dataType: 'json',
            traditional: true,
            type: 'POST',
            success: function(data){
                Backbone.history.navigate('!schedule', {trigger: true});
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
    initialize: function(){
        this.updateLoginState();
    },
    updateLoginState: function(){
        this.authenticated = (Parse.User.current() !== null);
        this.render();
    },
    toggleLogInState:function(){
        if(this.authenticated){
            Parse.User.logOut()
            this.authenticated = false;
            this.render();
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

IndexRouter = Backbone.Router.extend({
    routes: {
        "!confirmation/:email": "confirmEmail",
        "!signup": "signup",
        "!goal": "goal",
        "!equipment": "equipment",
        "!fitnesslevel": "fitnessLevel",
        "!schedule": "schedule",
        "!login": "login",
        "!payment": "payment",
        "": "defaultRoute"
    },
    initialize: function(options){
        this.devMode = options.devMode;
        this.loggedIn = false;
        this.globalView = new GlobalView();
        this.loginStateView = new LoginStateView();
    },
    login: function(){
        var self = this;
        this.loginView = new LoginView(function(){
            self.loginStateView.updateLoginState();
        });
        this.globalView.goto(this.loginView);
    },
    confirmEmail: function(email){
        this.templateView = new TemplateView("#confirm-view", {email: email});
        this.globalView.goto(this.templateView);
    },
    payment: function(){
        this.paymentView = new PaymentView();
        this.globalView.goto(this.paymentView);
    },
    goal: function(){
        this.goalView = new GoalView();
        this.globalView.goto(this.goalView);
    },
    equipment: function(){
        this.equipmentView = new EquipmentView();
        this.globalView.goto(this.equipmentView);
    },
    fitnessLevel: function(){
        this.fitnessLevelView = new FitnessLevelView();
        this.globalView.goto(this.fitnessLevelView);
    },
    schedule: function(){
        this.scheduleView = new ScheduleView();
        this.globalView.goto(this.scheduleView);
    },
    signup: function(){
        this.signUpView = new SignUpView();
        this.globalView.goto(this.signUpView);
    },
    defaultRoute: function(path){
        this.landingView = new LandingView();
        this.globalView.goto(this.landingView);
        if (this.loggedIn){
            // this.uploadVideoButtonView.render();
        }
        else {
            // this.facebookButtonView.render();
        }
        if (this.devMode){
            // this.forceStart();
        }
    },
    updateProfilePicture: function(){
        FB.api('/v2.1/me/picture?redirect=false', function(response){
            var profilePictureUrl = response.data.url;
            $('.profile-circular').css({'background-image':'url(' + profilePictureUrl +')'});
        });
    },
    facebookGetMe: function(){
        return;
        var self = this;
        FB.api('/v2.1/me?fields=id,email', function(response) {
            var facebook_id = response.id;
            var facebookEmail = response.email || '';
            window.facebook_id = facebook_id;
            $.ajax({
                url: '/api/login/',
                data: {
                    facebook_email: facebookEmail,
                    facebook_service_id: facebook_id
                },
                cache: false,
                dataType: 'json',
                traditional: true,
                type: 'POST',
                success: function(data){
                    self.loggedIn = true;
                    $("#account-link").show();
                    var currentRoute = self.routes[Backbone.history.fragment];
                    if (currentRoute === "defaultRoute"){
                        self.uploadVideoButtonView.render();
                    }
                },
                error: function(data){
                    alert("error");
                }
            });
        });
    },
    facebookStatusChangeCallback: function(response){
        if (response.status === 'connected') {
            this.facebookGetMe();
            this.updateProfilePicture();
        } else if (response.status === 'not_authorized') {
            this.loggedIn = false;
            // logged into Facebook but not app
        } else {
            this.loggedIn = false;
            // not logged in
        }
    },
    forceStart: function(){
        /* hacky dev case */
        // TODO make this unavailable in prod
        var self = this;
        var facebook_id = 1000000;
        $("#account-link").show();
        $.ajax({
            url: '/api/login/',
            data: {
                facebook_service_id: facebook_id,
                facebook_email: ''
            },
            cache: false,
            dataType: 'json',
            traditional: true,
            type: 'POST',
            success: function(data){
                self.loggedIn = true;
                self.uploadVideoButtonView.render();
            },
            error: function(data){
                alert("error");
            }
        });
    }
});
