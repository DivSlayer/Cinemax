class AudioClass {
          constructor(player_container) {
                    this.player_container = player_container;
                    this.audio = undefined;
                    this.setElement();
                    return this.audio;
          }

          setElement() {
                    let audio_el = document.createElement('audio');
                    audio_el.setAttribute('hidden' ,'');
                    this.player_container.append(audio_el);
                    this.audio = audio_el;
          }

}


export {AudioClass}