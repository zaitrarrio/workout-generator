function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
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

TemplateView = Backbone.View.extend({
    el: "#button-fill-area",
    initialize: function(){
        this.template = null;
    },
    updateTemplate: function(templateSelector){
        this.template = _.template($(templateSelector).html());
    },
    render: function(){
        var goBackHTML = '<a id="close-button" style="margin-top: 5px; font-size: 18px;" href="#" class="button large alt cancel">Go Back</a>'
        this.$el.html(this.template() + goBackHTML);
        window.scrollTo(0, 300);
        return this;
    }
});


IndexRouter = Backbone.Router.extend({
    routes: {
        "": "defaultRoute"
    },
    initialize: function(options){
        this.devMode = options.devMode;
        this.loggedIn = false;
    },
    defaultRoute: function(path){
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
