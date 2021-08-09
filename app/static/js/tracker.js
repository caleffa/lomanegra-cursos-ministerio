/**
 * Inicializa el reproductor de vimeo para un video específico y trackea el progreso
 *
 * @param vimeo_id Id del video en VIMEO
 * @param container_id id del elemento del DOM donde insertar el reproductor de VIMEO.
 * @constructor
 */
var VimeoTracker = function(video_id, vimeo_id, container_id, domain, onWatchedFull, onWatchedFullAfterLoading) {
    var self = this;
    self.video_id = video_id;
    self.vimeo_id = vimeo_id;
    self.container_id = container_id;
    self.video_traking_id = undefined;

    // Variables para pegarle al endpoint
    self._csrftoken = Cookies.get("csrftoken");
    self._sessionid = Cookies.get("sessionid");
    self._get_tracking_endpoint = 'https://' + domain + '/api/track/vp/video/' + self.video_id + '/';
    self._endpoint = 'https://' +domain + '/api/track/vp/'; // Debe completarse con le id del tracking
    self._watchedFullOnLoad = false;


    self.options = {
        id: self.vimeo_id,
        //width: 640,
        loop: false,
        byline: false,
        color: "f70f1f",
        title: false,
        transparent: false
    };
    self.watched = [];
    self.currentTime = 0;
    self.currentTimeExact = 0.0;
    self._intervalPeriod = 15000;
    self.intervalHandler = undefined;
    self.watchedFull = false;
    self.continueFrom = 0;

    self._tryLoad = function() {
        return $.getJSON(self._get_tracking_endpoint).done(function(data){
            // console.log(data);
            self.video_traking_id = data.id;
            self._endpoint = self._endpoint + self.video_traking_id + '/';
            self.watched = data.parts_watched;
            self.watchedFull = data.watched_full;
            self.continueFrom = data.continue_from;

            if(self.watchedFull) {
                self._watchedFullOnLoad = true;
            }
            if(self.watchedFull) {
                self.onWatchedFull();
            }

            self._initialize(self.continueFrom);
        });
    };

    self.load = function() {
        self._tryLoad().fail(function(xhr, status, error) {
            console.log('Se ha producido un error al intentar obtener el estado del tracking', [xhr, status, error]);
            console.log('Reintentando');
            // Intento nuevamente
            self._tryLoad().fail(function (xhr, status, error) {
                // Informar al usuario
                var msg = 'Se ha producido un error al intentar obtener el estado del tracking por segunda vez';
                console.log(msg, [xhr, status, error]);
                $('#errorModal').modal('show');
            });
        });
    };

    // Events handlers
    self.vimeoTimeUpdateEventHandler = function(data) {
        // console.log('Time update ', data);

        var seconds = Math.trunc(data.seconds);

        if ((data.seconds - self.currentTimeExact) < 1 || self.currentTimeExact === 0) {
            self.currentTimeExact = data.seconds;
        }

        if (seconds > (self.currentTime + 1)) {
            return;
        }
        
        self.currentTime = seconds;

        self.watched.push(seconds);
        self.watched = _.uniq(self.watched);

        // console.log(data);
        // console.log(self.watched);
    };
    self.vimeoPlayEventHandler = function() {
        console.log("played the video!");

        self._clearPeriodicUpdate();
        self.intervalHandler = setInterval(self.regularUpdateHandler, self._intervalPeriod);
    };
    self._clearPeriodicUpdate = function() {
        if(self.intervalHandler) {
            clearInterval(self.intervalHandler);
            self.intervalHandler = undefined;
        }
    };
    self.vimeoPauseEventHandler = function() {
        self._clearPeriodicUpdate();

        self._update();
        console.log("paused the video!");
    };
    self.vimeoPlayEndedHandler = function() {
        self._update();
    };

    self.regularUpdateHandler = function() {
        console.log('regular update!');
        self._update();
    };
    self.vimeoSeekingHandler = function(data) {
        console.log('Seeeking ', data);

        var seconds = Math.trunc(data.seconds);

        if((_.indexOf(self.watched, seconds) === -1) || (data.seconds > self.currentTimeExact)) {
            console.log('You shall not pass!')
            self.player.setCurrentTime(Math.max(self.currentTime - 2, 0)).then(function(time) {
                self.currentTime = time;
                // console.log('current time: ', time);
            });
        } else {
            // console.log('Ok Balrog, move along...');
        }
        // console.log('Seeking ', data);

    };
    self.vimeoSeekedHandler = function(data) {
        console.log('Seeked ', data);
    };

    if(!onWatchedFull) {
        self.onWatchedFull = function() {
            console.log('Watched Full');
        };
    } else {
        self.onWatchedFull = onWatchedFull;
    }

    if(!onWatchedFullAfterLoading) {
        self.onWatchedFullAfterLoading = function () {};
    } else {
        self.onWatchedFullAfterLoading = onWatchedFullAfterLoading;
    }


    self._initialize = function(continueFrom) {
        console.log('continue from: ', continueFrom);
        // Setup player
        self.player = new Vimeo.Player(self.container_id, options);

        // Setup events handlers
        self.player.on("play", self.vimeoPlayEventHandler);
        self.player.on("pause", self.vimeoPauseEventHandler);
        self.player.on('timeupdate', self.vimeoTimeUpdateEventHandler);
        self.player.on('ended', self.vimeoPlayEndedHandler);
        // self.player.on('seeked', self.vimeoSeekedHandler);

        self.player.setCurrentTime(continueFrom).then(function(time) {
            console.log('current time: ', time);
            self.currentTime = time;
            self.player.on('seeking', self.vimeoSeekingHandler);
        });
    };

    self._pause = function() {
        if(self.player) {
            self.player.off("pause");
            self.player.pause();
            self._clearPeriodicUpdate();
            self.player.on("pause", self.vimeoPauseEventHandler);
        }
    };

    self._tryUpdate = function() {
       return $.ajax(self._endpoint, {
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", Cookies.get("csrftoken"));
            },
            data: {
                id: self.video_traking_id,
                parts_watched:  self.watched,
                last_part_watched: self.currentTime
            },
            traditional: true,
            method: 'PATCH',
            timeout: 5000,
        }).done(function(data){
            self.watchedFull = data.watched_full;
            if(self.watchedFull) {
                self.onWatchedFull();

                if(!self._watchedFullOnLoad) {
                    // Se ejecuta a lo sumo una vez
                    self._watchedFullOnLoad = true;
                    self.onWatchedFullAfterLoading();
                }
            }
        });
    };
    
    self._update = function() {
        self._tryUpdate().fail(function (xhr, status, error) {
            console.log('Se ha producido un error al intentar actualizar el estado del tracking', [xhr, status, error]);
            console.log('Reintentando');
            // Intento nuevamente
            self._tryUpdate().fail(function (xhr, status, error) {
                // Informar al usuario
                var msg = 'Se ha producido un error al intentar actualizar el estado del tracking por segunda vez';
                console.log(msg, [xhr, status, error]);
                self._pause();
                $('#errorModal').modal('show');
            });
        });
    };

    self.load();
};