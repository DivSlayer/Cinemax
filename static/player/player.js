// TODO: Activate Subtitle Track after implementing Elements
import { AudioClass } from "./audio_class.js";

class Player {
    constructor(element_id, options = {}) {
        this.player = document.getElementById(`${element_id}`);
        this.textTracks = [];
        this.collections = [];
        this.audioTracks = [];
        this.activatedAudio = 0;
        this.audio = undefined;
        this.firstPlay = true;
        this.elementsHandler();
        this.setOptions(options);
        this.refreshCollections();
        if (this.collections.length > 0) {
            this.collectionButtons();
            this.collectionItem();
        }
        //    TimeEvents
        this.timeButtons();
        this.timeRange();
        this.timeText();
        this.additionalButtons();
        this.overlayHandler();
        this.volumeHandler();
        this.keyboardEvents();
        this.touchEvents();
        this.resume();
    }

    touchEvents() {
        let overlay = this.playerContainer.querySelector('.overlay');
        let startX = 0;
        let startY = 0;
        let currentX = 0;
        let currentY = 0;
        let goingUpX = true;
        let goingUpY = true;
        let differenceX = 0;
        let differenceY = 0;

        overlay.ontouchstart = (event) => {
            startX = event.targetTouches[0].clientX;
            startY = event.targetTouches[0].clientY;
        }

        overlay.ontouchmove = (event) => {
            if (goingUpY) {
                if (event.targetTouches[0].clientY > currentY) {
                    startY = event.targetTouches[0].clientY;
                    differenceY = 0;
                    goingUpY = false;
                }
            } else {
                if (event.targetTouches[0].clientY < currentY) {
                    startY = event.targetTouches[0].clientY
                    differenceY = 0
                    goingUpY = true;
                }
            }
            currentY = event.targetTouches[0].clientY;
            let totalHeight = document.body.offsetHeight;
            differenceY = startY - currentY;
            let heightPercentage = Math.ceil((differenceY / totalHeight) * 100);
            if (40 <= Math.abs(heightPercentage) <= 100) {
                if (Math.abs(differenceY) > Math.abs(differenceX)) {
                    if (this.audio) {
                        let old_volume = this.audio.volume;
                    } else {
                        let old_volume = this.player.volume;
                    }
                    let new_vol = old_volume + (heightPercentage / 100);
                    this.changeVolume(new_vol);
                }
            }
            if (goingUpX) {
                if (event.targetTouches[0].clientX < currentX) {
                    startX = event.targetTouches[0].clientX;
                    differenceX = 0;
                    goingUpX = false;
                }
            } else {
                if (event.targetTouches[0].clientX > currentX) {
                    startX = event.targetTouches[0].clientX
                    differenceX = 0
                    goingUpX = true;
                }
            }
            currentX = event.targetTouches[0].clientX;
            let totalWidth = document.body.offsetWidth;
            differenceX = currentX - startX;
            let widthPercentage = Math.ceil((differenceX / totalWidth) * 100);
            if (40 <= Math.abs(widthPercentage) <= 100) {
                if (Math.abs(differenceX) > Math.abs(differenceY)) {
                    let old_currentTime = this.player.currentTime;
                    let total_time = this.player.duration;
                    let seek_value = (widthPercentage / 100) * 60;
                    let new_time_per = (old_currentTime + seek_value) / this.player.duration * 100;
                    this.changeTime(new_time_per);
                }

            }
        }
    }

    resume() {
        let first_play = true;
        this.player.addEventListener('play', () => {
            if (first_play === true) {
                if (localStorage.getItem(this.player.src + 'duration') === null) {
                    localStorage.setItem(this.player.src + 'duration', this.player.duration);
                }
                let previousTime = localStorage.getItem(this.player.src);
                if (previousTime !== null) {
                    let duration = localStorage.getItem(this.player.src + 'duration');
                    if (duration !== null) {
                        let percent = parseInt(previousTime) / parseInt(duration) * 100;
                        this.changeTime(percent);
                        this.changeState();
                    }
                }
            }
            first_play = false;
        });
    }

    keyboardEvents() {
        window.onkeyup = (e) => {
            e.preventDefault();
            let keyCode = e.keyCode;
            console.log(keyCode);
            if (keyCode === 37) {
                let current = this.player.currentTime;
                let duration = this.player.duration;
                let percent = ((current - 10) / duration) * 100;
                if (current > 10) {
                    this.changeTime(percent);
                }
            }
            if (keyCode === 39) {
                let current = this.player.currentTime;
                let duration = this.player.duration;
                let percent = ((current + 10) / duration) * 100;
                if ((duration - current) > 10) {
                    this.changeTime(percent);
                }
            }
            if (keyCode === 32) {
                this.changeState(true);
            }
            if (keyCode === 38) {
                if (this.audio) {
                    if (this.audio.volume <= 0.9) {
                        this.changeVolume(this.audio.volume + 0.1);
                    }
                } else {
                    if (this.player.volume <= 0.9) {
                        this.changeVolume(this.player.volume + 0.1);
                    }
                }
            }
            if (keyCode === 40) {
                if (this.audio) {
                    if (this.audio.volume >= 0.1) {
                        this.changeVolume(this.audio.volume - 0.1);
                    }
                } else {
                    if (this.player.volume >= 0.9) {
                        this.changeVolume(this.player.volume - 0.1);
                    }
                }
            }
        }
    }

    additionalButtons() {
        this.playerContainer.querySelector('#expand-btn').addEventListener('click', () => {
            let elem = document.documentElement;
            if (document.fullscreenEnabled) {
                if (document.fullscreenElement === null) {
                    elem.requestFullscreen();
                } else {
                    document.exitFullscreen()
                }
            } else {
                console.error('Your browser cannot use fullscreen right now');
            }
        });
    }

    overlayHandler() {
        let hovered = false;
        let funcTimeOut;
        this.playerContainer.addEventListener('mousemove', () => {
            hovered = true;
            if (funcTimeOut) {
                clearTimeout(funcTimeOut);
            }
            funcTimeOut = setTimeout(function () {
                hovered = false;
            }, 1500);
        });
        this.playerContainer.addEventListener('mouseenter', () => {
            hovered = true;
            if (funcTimeOut) {
                clearTimeout(funcTimeOut);
            }
            funcTimeOut = setTimeout(() => {
                hovered = false;
            }, 1500)
        });
        this.playerContainer.addEventListener('mouseleave', () => {
            hovered = true;
            if (funcTimeOut) {
                clearTimeout(funcTimeOut);
            }
            funcTimeOut = setTimeout(() => {
                hovered = false;
            }, 1500);

        });
        this.player.addEventListener('timeupdate', () => {
            if (!this.player.paused) {
                if (hovered === false) {
                    this.playerContainer.querySelector('.overlay').classList.add('hide');
                    this.playerContainer.style.cursor = 'none';
                } else {
                    this.playerContainer.querySelector('.overlay').classList.remove('hide');
                    this.playerContainer.style.cursor = 'auto';
                }
            }
        });
    }

    changeVolume(integer) {
        let volumeProgress = this.playerContainer.querySelector('#volume-progress');
        let volumeInput = this.playerContainer.querySelector('#volume_range');
        let volumeBtn = this.playerContainer.querySelector('#volume-btn');
        if (integer === 0) {
            volumeBtn.querySelector('i').className = "far fa-volume-mute";
        } else {
            volumeBtn.querySelector('i').className = "far fa-volume";
        }
        if (this.audio) {
            this.audio.volume = integer;
        } else {
            this.player.volume = integer;
        }
        volumeInput.value = integer * 100;
        volumeProgress.querySelector('.passed').style.width = `${integer * 100}%`;
    }

    volumeHandler() {
        let volumeProgress = this.playerContainer.querySelector('#volume-progress');
        let volumeInput = this.playerContainer.querySelector('#volume_range');
        let volumeBtn = this.playerContainer.querySelector('#volume-btn');
        if (this.audio) {
            volumeInput.value = this.audio.volume * 100;
            volumeProgress.querySelector('.passed').style.width = `${this.audio.volume * 100}%`;
        } else {
            volumeInput.value = this.player.volume * 100;
            volumeProgress.querySelector('.passed').style.width = `${this.player.volume * 100}%`;
        }
        this.playerContainer.querySelector('.volume').addEventListener('mouseenter', () => {
            volumeProgress.classList.add('full');
        });
        this.playerContainer.querySelector('.volume').addEventListener('mouseleave', () => {
            volumeProgress.classList.remove('full');
        });
        volumeInput.addEventListener('change', () => {
            let integer = volumeInput.value / 100;
            this.changeVolume(integer);
        });
        volumeInput.addEventListener('input', () => {
            volumeProgress.querySelector('.passed').style.width = `${volumeInput.value}%`;
        });
        volumeBtn.addEventListener('click', () => {
            if (this.audio) {
                if (this.audio.volume === 0) {
                    this.changeVolume(1);
                } else {
                    this.changeVolume(0);
                }
            } else {
                if (this.player.volume === 0) {
                    this.changeVolume(1);
                } else {
                    this.changeVolume(0);
                }
            }
        })
    }

    //Set Options
    setOptions(options, reset = false) {
        for (const key in options) {
            if (Object.hasOwnProperty.call(options, key)) {
                let element = options[key];
                if (key === 'collections') {
                    this.setCollections(element);
                } else if (key === 'audios') {
                    if (element.length) {
                        this.setAudios(element, reset);
                    }
                } else if (key === 'subtitles') {
                    if (element.length) {
                        this.setSubtitles(element, reset);
                    }
                }
            }
        }
        if (this.textTracks.length > 0) {
            this.refreshSub();
            this.subtitleButtons();
            this.SubItemEvents();
        }
        if (this.audioTracks.length > 0) {
            this.refreshAudio();
            this.audioButtons();
            this.audioItemEvent();
        }

        if (this.collections.length === 0) {
            this.player.src = options.src;
        }
    }

    setSubtitles(subtitles, reset = false) {
        if (reset === true) {
            this.textTracks = [];
        }
        subtitles.forEach(subtitle => {
            this.textTracks.push(subtitle);
        });
        this.setSubtitlesElements();
    }

    setSubtitlesElements() {
        this.player.querySelectorAll('track').forEach(track => {
            track.remove();
        });
        this.textTracks.forEach(subtitle => {
            let track = document.createElement('track');
            track.label = 'Persian';
            track.src = subtitle.vtt;
            track.lang = 'Persian';
            this.player.append(track);
        });
    }

    activateSubtitle(integer = 0) {
        if (this.player.textTracks.length > 0) {
            let subtitles = this.playerContainer.querySelectorAll('#subtitles .subs-flat li');
            let textTracks = this.player.textTracks;
            let subBtn = this.playerContainer.querySelector('#subtitles-btn i');
            subtitles.forEach(subtitle => {
                subtitle.classList.remove('active');
            });
            for (let i = 0; i < textTracks.length; i++) {
                const track = textTracks[i];
                track.mode = 'disabled';
            }
            if (integer !== 0) {
                for (let i = 0; i < textTracks.length; i++) {
                    const track = textTracks[i];
                    track.mode = 'disabled';
                }
                textTracks[integer - 1].mode = 'showing';
                subBtn.className = 'fas fa-closed-captioning';
            } else {
                subBtn.className = 'far fa-closed-captioning';
            }
            subtitles[integer].classList.add('active');
        }
    }

    setAudios(audios, reset = false) {
        if (reset === true) {
            this.audioTracks = [];
        }
        audios.forEach(audio => {
            this.audioTracks.push(audio);
        });
        this.activateAudio();
    }

    activateAudio(integer = 0) {
        this.activatedAudio = integer;
        if (typeof this.audio !== 'undefined') {
            this.audio.pause();
            this.audio = undefined;
        }
        if (this.audioTracks.length > 0) {
            this.player.volume = 0;
            this.audio = new AudioClass(this.playerContainer);
            this.audio.src = this.audioTracks[integer].src;
            this.changeState();
        }
    }

    changeState(change_current = false) {
        let audio_ok = true;
        let video_ok = true;
        this.changeAudioTime(this.player.currentTime);
        if (this.firstPlay === false && change_current === true) {
            if (this.player.paused === true) {
                this.player.play();
                if (this.audio) {
                    this.audio.play();
                }

                this.changePlayBtnsClasses(false);
            } else {
                this.player.pause();
                if (this.audio) {
                    this.audio.pause();
                }
                this.changePlayBtnsClasses(true);
            }
        }
        let pausedBefore = this.player.paused;
        this.player.onwaiting = () => {
            video_ok = false;
            console.log('heelo');
            this.playerContainer.querySelector('#big-play-btn').classList.add('spin');
        }
        if (this.audio) {
            this.audio.onwaiting = () => {
                audio_ok = false;
            }
        }
        this.player.onplaying = () => {
            video_ok = true;
            if (audio_ok === true && video_ok === true) {
                this.playerContainer.querySelector('#big-play-btn').classList.remove('spin');
                if (pausedBefore === true) {
                    this.player.pause();
                    this.audio.pause();
                    this.changePlayBtnsClasses(true);
                } else {
                    this.player.play();
                    if (typeof this.audio !== 'undefined') {
                        this.audio.play();
                    }
                    this.changePlayBtnsClasses(false);
                }
            } else {
                this.player.pause();
            }
        }
        if (this.audio) {
            this.audio.onplaying = () => {
                audio_ok = true;
                if (audio_ok === true && video_ok === true) {
                    this.playerContainer.querySelector('#big-play-btn').classList.remove('spin');
                    if (pausedBefore === true) {
                        this.player.pause();
                        this.audio.pause();
                        this.changePlayBtnsClasses(true);
                    } else {
                        this.player.play();
                        this.audio.play();
                        this.changePlayBtnsClasses(false);
                    }
                } else {
                    this.audio.pause();
                }
            }
        }
        this.firstPlay = false;
    }

    changeAudioTime(time) {
        let pausedBefore = this.player.paused;
        if (this.audio) {
            this.audio.currentTime = time;
        }
    }

    setCollections(collections, reset = false) {
        if (reset === true) {
            this.collections = [];
        }
        collections.forEach(collection => {
            this.collections.push(collection);
        });
        this.activateCollection();

    }

    activateCollection(integer = 0) {
        if (this.collections.length > 0) {
            let selected = this.collections[integer];
            this.player.pause();
            if (typeof this.audio !== 'undefined') {
                this.audio.pause();
            }
            this.audio = undefined;
            this.player.currentTime = 0;
            this.player.src = selected.src;
            this.setOptions(selected, true);
            this.refreshAudio();
            this.refreshSub();
            if (this.textTracks.length > 0) {
                this.refreshSub();
                this.subtitleButtons();
                this.SubItemEvents();
            }
            if (this.audioTracks.length > 0) {
                this.refreshAudio();
                this.audioButtons();
                this.audioItemEvent();
            }

        }
    }

    //Events
    // Player
    timeButtons() {
        let big_play_btn = this.playerContainer.querySelector('#big-play-btn');
        let sm_play_btn = this.playerContainer.querySelector('#sm-play-btn');
        let status = this.player.paused;
        big_play_btn.addEventListener('click', () => {
            this.changeState(true);
        });
        sm_play_btn.addEventListener('click', () => {
            this.changeState(true);
        });
    }

    changePlayBtnsClasses(paused) {
        let big_play_btn = this.playerContainer.querySelector('#big-play-btn');
        let sm_play_btn = this.playerContainer.querySelector('#sm-play-btn');
        let pause_class = 'far fa-pause';
        let play_class = 'far fa-play';
        if (paused === true) {
            big_play_btn.querySelector('i').className = play_class;
            sm_play_btn.querySelector('i').className = play_class;
        } else {
            big_play_btn.querySelector('i').className = pause_class;
            sm_play_btn.querySelector('i').className = pause_class;
        }

    }

    timeRange() {
        let progress_input = this.playerContainer.querySelector('#progress_range');
        let passed = this.playerContainer.querySelector('#time-progress .passed');
        let isSeeking = false;
        this.player.addEventListener('timeupdate', () => {
            if (localStorage.getItem(this.player.src)) {
                if (parseInt(localStorage.getItem(this.player.src)) < this.player.currentTime) {
                    localStorage.setItem(this.player.src, this.player.currentTime);
                }
            } else {
                localStorage.setItem(this.player.src, this.player.currentTime);
            }
            if (isSeeking === false) {
                let percent = (this.player.currentTime / this.player.duration) * 100;
                passed.style.width = `${percent}%`;
                progress_input.value = percent;
            }
        });
        progress_input.addEventListener('change', () => {
            isSeeking = false;
            let percent = progress_input.value;
            this.changeTime(percent);

        });
        progress_input.addEventListener('input', () => {
            isSeeking = true;
            let percent = progress_input.value;
            passed.style.width = `${percent}%`;
        });
    }

    timeText() {
        this.player.addEventListener('timeupdate', () => {
            let currentTime = this.player.currentTime;
            let totalTime = this.player.duration;
            this.playerContainer.querySelector('#current-time').innerHTML = this.msToTime(currentTime);
            this.playerContainer.querySelector('#remained-time').innerHTML = this.msToTime(totalTime - currentTime);
        });
    }

    changeTime(time_percent) {
        let pausedBefore = this.player.paused;
        let converted_time = (time_percent / 100) * this.player.duration;
        let progress_input = this.playerContainer.querySelector('#progress_range');
        let passed = this.playerContainer.querySelector('#time-progress .passed');
        try {
            this.player.currentTime = converted_time;
        }   
        catch(err) {
            this.player.currentTime = 0;
        }
        progress_input.value = time_percent;
        passed.style.width = `${time_percent}%`;
        this.changeState();
    }

    msToTime(s) {
        let hours = Math.floor(s / 3600);
        let minutes = Math.floor((s - (hours * 3600)) / 60);
        let seconds = Math.floor(s - (hours * 3600) - (minutes * 60));
        if (hours === 0) {
            return minutes.toString().padStart(2, '0') + ":" + seconds.toString().padStart(2, '0');
        } else {
            return hours.toString().padStart(2, '0') + ':' + minutes.toString().padStart(2, '0') + ":" + seconds.toString().padStart(2, '0');
        }
    }

    // Subtitle
    subtitleButtons() {
        let subBtn = this.playerContainer.querySelector('#subtitles-btn');
        let sub_page = this.playerContainer.querySelector('#subtitles');
        subBtn.addEventListener('click', () => {
            sub_page.classList.add('show');
        });
        this.playerContainer.querySelector('#exit-subtitles').addEventListener('click', () => {
            this.playerContainer.querySelector('#subtitles').classList.remove('show');
        });
    }

    SubItemEvents() {
        let subtitles = document.querySelectorAll('#subtitles .subs-flat li');
        subtitles.forEach(subtitle => {
            subtitle.addEventListener('click', () => {
                let parentEl = this.playerContainer.querySelector('.subtitles .subs-flat .list');
                let index = Array.from(parentEl.children).indexOf(subtitle);
                this.activateSubtitle(index);
            });
        });
    }

    // Audio

    audioButtons() {
        let audiosBtn = this.playerContainer.querySelector('#audios-btn');
        let audiosPage = this.playerContainer.querySelector('#audios');
        audiosBtn.addEventListener('click', () => {
            audiosPage.classList.add('show');
        });
        this.playerContainer.querySelector('#exit-audios').addEventListener('click', () => {
            this.playerContainer.querySelector('#audios').classList.remove('show');
        });
        this.activateAudio();
    }

    audioItemEvent() {
        let audios = this.playerContainer.querySelectorAll('#audios li');
        audios.forEach(audio => {
            audio.addEventListener('click', () => {
                let parentEl = this.playerContainer.querySelector('#audios .list');
                let index = Array.from(parentEl.children).indexOf(audio);
                this.activateAudio(index);
                audios.forEach(audio => {
                    audio.classList.remove('active');
                });
                audios[this.activatedAudio].classList.add('active');
            });
        });
    }

    // Collections

    collectionButtons() {
        let collectionBtn = this.playerContainer.querySelector('#collections-btn');
        let collection_page = this.playerContainer.querySelector('#collections');
        collectionBtn.addEventListener('click', () => {
            collection_page.classList.add('show');
        });
        this.playerContainer.querySelector('#exit-collections').addEventListener('click', () => {
            this.playerContainer.querySelector('#collections').classList.remove('show');
        });
    }

    collectionItem() {
        let collections = this.playerContainer.querySelectorAll('#collections .list li');
        collections.forEach(collection => {
            collection.addEventListener('click', () => {
                let parentEl = this.playerContainer.querySelector('#collections .list');
                let index = Array.from(parentEl.children).indexOf(collection);
                this.disableAllCollections();
                this.activateCollection(index);
                collection.classList.add('active');
            });
        });
    }

    disableAllCollections() {
        let collections = this.playerContainer.querySelectorAll('#collections .list li');
        collections.forEach(element => {
            element.classList.remove('active');
        });
    }

    //Elements
    refreshCollections() {
        let bottom_element = this.playerContainer.querySelector('.bottom');
        if (this.collections.length > 0) {
            if (document.getElementById('collections-btn')) {
                document.getElementById('collections-btn').remove();
            }
            let subs_btn = this.makeBottomBtn('collections-btn', '<i class="far fa-album-collection"></i>', 'btn-sm');
            bottom_element.append(subs_btn);
        }
        if (this.collections.length > 0) {
            if (document.getElementById('collections')) {
                document.getElementById('collections').remove();
            }
            let collection_items = [];
            for (let i = 0; i < this.collections.length; i++) {
                let element = this.collections[i];
                if (i === 0) {
                    let item_list = this.makeFlatItem(element.title, null, null, true);
                    collection_items.push(item_list);
                } else {
                    let item_list = this.makeFlatItem(element.title);
                    collection_items.push(item_list);
                }
            }
            let collection_flat = this.makeFlatList(null, 'قسمت ها', collection_items, false);
            let collection_page = this.makeItemsPage('collections', 'collections', 'exit-collections', [collection_flat]);
            collection_page.append(collection_flat);
            this.playerContainer.append(collection_page);
        }
    }

    refreshSub() {
        let bottom_element = this.playerContainer.querySelector('.bottom');
        if (this.player.textTracks.length > 0) {
            if (document.getElementById('subtitles-btn')) {
                document.getElementById('subtitles-btn').remove();
            }
            let subs_btn = this.makeBottomBtn('subtitles-btn', '<i class="far fa-closed-captioning"></i>', 'btn-sm');
            bottom_element.append(subs_btn);
        }
        if (this.player.textTracks.length > 0) {
            if (document.getElementById('subtitles')) {
                document.getElementById('subtitles').remove();
            }
            let sub_items = [];
            for (let i = 0; i < player.textTracks.length; i++) {
                let element = player.textTracks[i];
                let item_list = this.makeFlatItem(element.label);
                sub_items.push(item_list);
            }
            let font_items = [];
            font_items.push(this.makeFlatItem('کوچک', '', 'small-font', true))
            font_items.push(this.makeFlatItem('متوسط', '', 'med-font',))
            font_items.push(this.makeFlatItem('بزرگ', '', 'big-font',))
            let sub_flat_list = this.makeFlatList('subs-flat', 'زیرنویس ها', sub_items, true);
            let fonts_flat_list = this.makeFlatList('fonts', 'اندازه فونت', font_items,);
            let sub_page = this.makeItemsPage('subtitles', 'subtitles', 'exit-subtitles', [sub_flat_list, fonts_flat_list]);
            sub_page.append(sub_flat_list);
            sub_page.append(fonts_flat_list);
            this.playerContainer.append(sub_page);
        }

    }

    refreshAudio() {
        let bottom_element = this.playerContainer.querySelector('.bottom');
        if (document.getElementById('audios-btn')) {
            document.getElementById('audios-btn').remove();
        }

        if (document.getElementById('audios')) {
            document.getElementById('audios').remove();
        }

        if (this.audioTracks.length > 0) {
            let audios_btn = this.makeBottomBtn('audios-btn', '<i class="far fa-microphone"></i>', 'btn-sm');
            bottom_element.append(audios_btn);
        }
        if (this.audioTracks.length > 0) {
            let audio_items = [];
            for (let i = 0; i < this.audioTracks.length; i++) {
                let element = this.audioTracks[i];
                if (i === 0) {
                    let item_list = this.makeFlatItem(element.label, null, null, true);
                    audio_items.push(item_list);
                } else {
                    let item_list = this.makeFlatItem(element.label);
                    audio_items.push(item_list);
                }
            }
            let audio_flat_list = this.makeFlatList('audios', 'انتخاب زبان فیلم', audio_items);
            let audio_page = this.makeItemsPage('audios', 'audios', 'exit-audios', [audio_flat_list]);
            audio_page.append(audio_flat_list);
            this.playerContainer.append(audio_page);
        }
    }

    elementsHandler() {
        let video_copy = this.player.outerHTML;
        let parent = this.player.parentElement;
        let video_index = Array.from(parent.children).indexOf(video_copy);
        let player_container = document.createElement('div');
        player_container.className = 'player-container';
        let video_container = document.createElement('div');
        video_container.className = 'video';
        video_container.innerHTML = video_copy;
        player_container.append(video_container);
        let overlay = document.createElement('div');
        overlay.className = "overlay";
        let play_btn = this.makeBottomBtn('big-play-btn', '<i class="far fa-play"></i>', 'play-btn');
        let spinner = document.createElement('div');
        spinner.className = 'spinner';
        play_btn.append(spinner);
        overlay.append(play_btn);
        let bottom_element = document.createElement('div');
        bottom_element.className = 'bottom';
        let pause_btn = this.makeBottomBtn('sm-play-btn', '<i class="far fa-play"></i>', 'btn-sm');
        bottom_element.append(pause_btn);
        let volume_element = document.createElement('div');
        volume_element.className = 'volume';
        let volume_button = this.makeBottomBtn('volume-btn', '<i class="far fa-volume"></i>', 'btn-sm');
        volume_element.append(volume_button);
        let volume_progress = document.createElement('div');
        volume_progress.className = 'progress-bar';
        volume_progress.id = 'volume-progress';
        volume_progress.innerHTML = `<input type="range" name="range" id="volume_range" value="0" max="100"><i class="passed"></i>`;
        volume_element.append(volume_progress);
        bottom_element.append(volume_element);
        let currentEl = document.createElement('span');
        currentEl.className = 'current-time';
        currentEl.id = 'current-time';
        currentEl.style.minWidth = '50px';
        currentEl.innerText = "00:00";
        bottom_element.append(currentEl);
        let time_prog_el = document.createElement('div');
        time_prog_el.className = 'progress-bar';
        time_prog_el.id = 'time-progress';
        time_prog_el.innerHTML = ' <input type="range" name="range" id="progress_range" value="0" max="100"> <i class="passed"></i>';
        bottom_element.append(time_prog_el);
        let totalEl = document.createElement('span');
        totalEl.className = 'remained-time';
        totalEl.id = 'remained-time';
        totalEl.style.minWidth = '50px';
        totalEl.innerText = "00:00";
        bottom_element.append(totalEl);
        let settings_btn = this.makeBottomBtn('settings-btn', '<i class="far fa-gear"></i>', 'btn-sm');
        bottom_element.append(settings_btn);
        let expand_btn = this.makeBottomBtn('expand-btn', '<i class="fa fa-expand"></i>', 'btn-sm');
        bottom_element.append(expand_btn);
        overlay.append(bottom_element);
        player_container.append(overlay);
        let settings_el = document.createElement('div');
        settings_el.className = 'function settings';
        player_container.append(settings_el);
        this.player.remove();
        parent.insertBefore(player_container, parent.children[video_index + 1]);
        this.player = player_container.getElementsByTagName('video')[0];
        this.playerContainer = player_container;
    }

    makeBottomBtn(element_id, html, className = null) {
        let btn = document.createElement('button');
        if (className) {
            btn.className = `btn ${className}`;
        } else {
            btn.className = 'btn';
        }
        btn.id = element_id;
        btn.innerHTML = html;
        return btn;
    }

    makeFlatItem(label, className = null, element_id = null, active = false) {
        let item = document.createElement('li');
        if (active === true) {
            item.className = 'item active';
        } else {
            item.className = 'item';
        }
        if (element_id !== null) {
            item.id = element_id;
        }
        if (className) {
            item.classList.add(className);
        }
        let name_span = document.createElement('span');
        name_span.innerText = label;
        item.append(name_span);
        return item;

    }

    makeFlatList(className, header, items, withNone = false) {
        let flat_list = document.createElement('div');
        flat_list.className = `flat-list ${className}`;
        let title = document.createElement('h3');
        title.className = "header";
        title.innerText = header;
        flat_list.append(title);
        let flat_list_items = document.createElement('ul');
        flat_list_items.className = 'list';
        if (withNone === true) {
            let none_item = document.createElement('li');
            none_item.className = 'item active';
            let none_span = document.createElement('span');
            none_span.innerText = 'هیچکدام';
            none_item.append(none_span);
            flat_list_items.append(none_item);
        }

        for (let i = 0; i < items.length; i++) {
            let element = items[i];
            flat_list_items.append(element);
        }
        flat_list.append(flat_list_items);
        return flat_list;
    }

    makeItemsPage(class_name, element_id, exit_id, flat_lists) {
        let page = document.createElement('div');
        page.className = `function ${class_name}`
        page.id = element_id;
        let exit_el = document.createElement('div');
        exit_el.className = 'exit';
        let back_span = document.createElement('span');
        back_span.innerText = 'بازگشت';
        exit_el.append(back_span);
        let exit_sub_btn = document.createElement('button');
        exit_sub_btn.className = 'btn btn-sm';
        exit_sub_btn.id = exit_id;
        exit_sub_btn.innerHTML = '<i class="far fa-arrow-right"></i>';
        exit_el.append(exit_sub_btn);
        page.append(exit_el);
        for (let i = 0; i < flat_lists; i++) {
            page.append(flat_lists[i]);
        }
        return page;

    }

}

export { Player }
