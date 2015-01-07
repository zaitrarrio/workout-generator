function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}
function removeHash () {
    history.pushState("", document.title, window.location.pathname
        + window.location.search);
}

function facebookGetMe(){
    var self = this;
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

FitnessLevelView = AbstractView.extend({
    events: {
        "click .save": "save"
    },
    initialize: function(model){
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
            Backbone.history.navigate('!equipment', {trigger: true});
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
    initialize: function(model){
        this.model = model;
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
    initialize: function(model){
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
        this.model.set("available_equipment", this._getCheckedEquipmentIds());

        var self = this;
        this.model.once('sync', function(){
            self.$(".loading-icon").show();
            Backbone.history.navigate('!payment', {trigger: true});
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
                        alert("stripe success");
                        console.log(response);
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

GoalView = AbstractView.extend({
    events: {
        "click .member-container": "selectGoal",
        "mouseenter .member-container": "addSelected",
        "mouseleave .member-container": "removeSelected"
    },
    initialize: function(model){
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
    initialize: function(model){
        this.model = model;
        this.updateLoginState();
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
         return '/api/user/?username=' + Parse.User.current().get('username');
    },
    initialize: function(){
        this.listenTo(this, 'sync', function(){
        });
    },
    hasEquipmentId: function(equipmentId){
        return _.indexOf(this.get('available_equipment'), equipmentId) > -1;
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
        this.model = new User();
        this.devMode = options.devMode;
        this.loggedIn = false;
        this.globalView = new GlobalView();
        this.loginStateView = new LoginStateView(this.model);
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
        this.paymentView = new PaymentView(this.model);
        this.globalView.goto(this.paymentView);
    },
    goal: function(){
        this.goalView = new GoalView(this.model);
        this.globalView.goto(this.goalView);
    },
    equipment: function(){
        this.equipmentView = new EquipmentView(this.model);
        this.globalView.goto(this.equipmentView);
    },
    fitnessLevel: function(){
        this.fitnessLevelView = new FitnessLevelView(this.model);
        this.globalView.goto(this.fitnessLevelView);
    },
    schedule: function(){
        this.scheduleView = new ScheduleView(this.model);
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
        this.landingView = new LandingView(this.model);
        this.globalView.goto(this.landingView);
    }
});
